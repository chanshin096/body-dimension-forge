#!/usr/bin/env Rscript

# Bゲート実行4の構造候補についてsurvey designの機械的挙動だけを検査する。
# 予測、モデル学習、目的変数の性能評価は行わない。

suppressPackageStartupMessages({
  library(haven)
  library(jsonlite)
  library(survey)
})

args <- commandArgs(trailingOnly = TRUE)
input_dir <- if (length(args) >= 1) args[[1]] else "data/raw/nhanes/2021-2023"
output_path <- if (length(args) >= 2) args[[2]] else "data/manifests/nhanes_2021_2023_split_survey_evaluation.json"

bmx <- read_xpt(file.path(input_dir, "BMX_L.xpt"))
demo <- read_xpt(file.path(input_dir, "DEMO_L.xpt"))
required_bmx <- c("SEQN")
required_demo <- c("SEQN", "RIDAGEYR", "WTMEC2YR", "SDMVSTRA", "SDMVPSU")
if (!all(required_bmx %in% names(bmx)) || !all(required_demo %in% names(demo))) {
  stop("必須列が存在しないため停止")
}
if (anyNA(bmx$SEQN) || anyDuplicated(bmx$SEQN) || anyNA(demo$SEQN) || anyDuplicated(demo$SEQN)) {
  stop("SEQNに欠損または重複があるため停止")
}
d <- merge(bmx[required_bmx], demo[required_demo], by = "SEQN", all.x = TRUE, sort = FALSE)
if (nrow(d) != nrow(bmx) || anyNA(d$WTMEC2YR) || any(d$WTMEC2YR <= 0)) {
  stop("full examined sampleを正のMEC weight付きで一対一結合できないため停止")
}

strata <- sort(unique(as.integer(d$SDMVSTRA)))
if (length(strata) != 15L || any(table(d$SDMVSTRA, d$SDMVPSU) == 0L)) {
  stop("想定した15層×2 pseudo-PSU構造と一致しないため停止")
}
groups <- c("training", "validation", "sealed_final_test")
allocation <- setNames(groups[(seq_along(strata) - 1L) %% 3L + 1L], strata)
d$diagnostic_group <- unname(allocation[as.character(as.integer(d$SDMVSTRA))])
d$adult_indicator <- as.numeric(d$RIDAGEYR >= 20)

# NCHSのfull examined design + domain手順。lonely PSUの便宜的調整は指定しない。
options(survey.lonely.psu = "fail")
full <- svydesign(
  ids = ~SDMVPSU, strata = ~SDMVSTRA, weights = ~WTMEC2YR,
  nest = TRUE, data = d
)

capture_check <- function(expr) {
  warnings <- character()
  value <- withCallingHandlers(
    tryCatch(expr, error = function(e) e),
    warning = function(w) {
      warnings <<- c(warnings, conditionMessage(w))
      invokeRestart("muffleWarning")
    }
  )
  list(value = value, warnings = unique(warnings), ok = !inherits(value, "error"))
}

inspect_group <- function(group) {
  domain <- subset(full, diagnostic_group == group)
  part <- d[d$diagnostic_group == group, , drop = FALSE]
  physical_result <- capture_check(svydesign(
    ids = ~SDMVPSU, strata = ~SDMVSTRA, weights = ~WTMEC2YR,
    nest = TRUE, data = part
  ))
  if (!physical_result$ok) stop(conditionMessage(physical_result$value))
  physical <- physical_result$value

  domain_mean <- capture_check(svymean(~adult_indicator, domain, na.rm = TRUE))
  physical_mean <- capture_check(svymean(~adult_indicator, physical, na.rm = TRUE))
  domain_quantile <- capture_check(svyquantile(
    ~RIDAGEYR, domain, quantiles = 0.5, ci = TRUE, interval.type = "mean",
    df = 5, na.rm = TRUE
  ))
  physical_quantile <- capture_check(svyquantile(
    ~RIDAGEYR, physical, quantiles = 0.5, ci = TRUE, interval.type = "mean",
    df = 5, na.rm = TRUE
  ))
  mean_equal <- domain_mean$ok && physical_mean$ok &&
    isTRUE(all.equal(coef(domain_mean$value), coef(physical_mean$value), tolerance = 1e-12)) &&
    isTRUE(all.equal(SE(domain_mean$value), SE(physical_mean$value), tolerance = 1e-12))

  list(
    retained_strata = length(unique(part$SDMVSTRA)),
    retained_pseudo_psus = nrow(unique(part[c("SDMVSTRA", "SDMVPSU")])),
    empty_original_strata = length(strata) - length(unique(part$SDMVSTRA)),
    single_psu_strata = sum(table(part$SDMVSTRA) > 0 &
      vapply(split(part$SDMVPSU, part$SDMVSTRA), function(x) length(unique(x)), integer(1)) == 1L),
    full_design_domain = list(
      design_created = TRUE,
      degf_reported_by_survey = degf(domain),
      weighted_mean_se_finite = domain_mean$ok && all(is.finite(SE(domain_mean$value))),
      weighted_mean_ci_mechanically_available = domain_mean$ok && all(is.finite(confint(domain_mean$value, df = 5))),
      weighted_quantile_ci_mechanically_available = domain_quantile$ok,
      warnings = unique(c(domain_mean$warnings, domain_quantile$warnings))
    ),
    physical_subset_design = list(
      design_created = physical_result$ok,
      degf_reported_by_survey = degf(physical),
      weighted_mean_se_finite = physical_mean$ok && all(is.finite(SE(physical_mean$value))),
      weighted_mean_ci_mechanically_available = physical_mean$ok && all(is.finite(confint(physical_mean$value, df = 5))),
      weighted_quantile_ci_mechanically_available = physical_quantile$ok,
      warnings = unique(c(physical_result$warnings, physical_mean$warnings, physical_quantile$warnings))
    ),
    domain_and_physical_weighted_mean_and_se_equal = mean_equal
  )
}

results <- setNames(lapply(groups, inspect_group), groups)
manifest <- list(
  schema_version = 1,
  scope = "survey design implementation check only; no model, prediction, target evaluation, or individual output",
  software = list(
    R = R.version.string,
    survey = as.character(packageVersion("survey")),
    haven = as.character(packageVersion("haven")),
    jsonlite = as.character(packageVersion("jsonlite"))
  ),
  design_definition = list(
    full = "svydesign(ids=~SDMVPSU, strata=~SDMVSTRA, weights=~WTMEC2YR, nest=TRUE, data=full examined sample)",
    domain = "subset(full_design, diagnostic_group == group)",
    physical = "same svydesign call using only rows assigned to group",
    survey_lonely_psu = getOption("survey.lonely.psu"),
    quantile_ci = "svyquantile interval.type=mean with explicitly supplied subgroup df=5"
  ),
  full_examined_design = list(
    rows = nrow(d), strata = length(strata), pseudo_psus = nrow(unique(d[c("SDMVSTRA", "SDMVPSU")])),
    degf_reported_by_survey = degf(full)
  ),
  groups = results,
  observed_software_behavior = list(
    all_designs_created = all(vapply(results, function(x) x$full_design_domain$design_created && x$physical_subset_design$design_created, logical(1))),
    all_reported_degf_equal_5 = all(vapply(results, function(x) x$full_design_domain$degf_reported_by_survey == 5 && x$physical_subset_design$degf_reported_by_survey == 5, logical(1))),
    any_lonely_psu_warning = any(vapply(results, function(x) length(x$full_design_domain$warnings) + length(x$physical_subset_design$warnings) > 0, logical(1))),
    all_simple_statistics_mechanically_available = all(vapply(results, function(x) x$full_design_domain$weighted_mean_se_finite && x$full_design_domain$weighted_quantile_ci_mechanically_available && x$physical_subset_design$weighted_mean_se_finite && x$physical_subset_design$weighted_quantile_ci_mechanically_available, logical(1))),
    all_domain_physical_mean_se_equal = all(vapply(results, function(x) x$domain_and_physical_weighted_mean_and_se_equal, logical(1)))
  ),
  interpretation = list(
    official_nhanes_compatible_candidate = "full examined design plus domain/subpopulation (A)",
    physical_subset_status = "not adopted: mechanical success does not establish an NHANES-valid population design after ten original strata are removed",
    three_way_method_status = "undecided",
    gate_status_change = FALSE
  ),
  prohibited_output = list(
    estimates_standard_errors_confidence_limits_or_quantiles_saved = FALSE,
    model_training_prediction_or_performance_evaluation = FALSE,
    individual_rows_seqn_or_assignments_saved = FALSE
  )
)

dir.create(dirname(output_path), recursive = TRUE, showWarnings = FALSE)
write_json(manifest, output_path, auto_unbox = TRUE, pretty = TRUE, null = "null")
cat(output_path, "\n")
