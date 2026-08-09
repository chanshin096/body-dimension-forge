#!/usr/bin/env Rscript

# Bゲート実行9の目的値非閲覧toy検査案。replicate weight構造だけを調べる。
# withCrossval自体のtest判定、fit/predict、loss集約を検証するものではない。
suppressPackageStartupMessages(library(survey))

if (!exists("withCrossval", asNamespace("survey"), inherits = FALSE)) {
  stop("installed survey does not provide withCrossval")
}

toy <- expand.grid(row_in_psu = 1:2, psu = 1:2, stratum = 1:15)
toy$weight <- 1
design <- svydesign(
  ids = ~psu,
  strata = ~stratum,
  weights = ~weight,
  data = toy,
  nest = TRUE
)

inspect_replicates <- function(type, expected_test_psus, expected_training_psus) {
  rep_design <- as.svrepdesign(design, type = type, compress = FALSE)
  analysis_weights <- weights(rep_design, type = "analysis")
  if (is.null(dim(analysis_weights))) {
    stop(type, ": replicate analysis weights are not a matrix")
  }

  psu_key <- interaction(toy$stratum, toy$psu, drop = TRUE)
  psu_levels <- levels(psu_key)
  per_replicate <- lapply(seq_len(ncol(analysis_weights)), function(j) {
    by_psu <- vapply(psu_levels, function(key) {
      values <- analysis_weights[psu_key == key, j]
      if (length(unique(values)) != 1L) {
        stop(type, ": a PSU has mixed replicate weights")
      }
      values[[1L]]
    }, numeric(1))
    zero <- abs(by_psu) <= sqrt(.Machine$double.eps)
    if (sum(zero) != expected_test_psus || sum(!zero) != expected_training_psus) {
      stop(type, ": unexpected training/test PSU counts")
    }
    c(test_psus = sum(zero), training_psus = sum(!zero))
  })

  counts <- do.call(rbind, per_replicate)
  list(
    type = type,
    replicates = ncol(analysis_weights),
    design_degrees_of_freedom = degf(rep_design),
    all_test_psus = unique(counts[, "test_psus"]),
    all_training_psus = unique(counts[, "training_psus"]),
    scale = rep_design$scale,
    rscales_length = length(rep_design$rscales)
  )
}

result <- list(
  scope = "15 strata x 2 PSU toy replicate structure only; no model, target, prediction, loss, individual ID, or NHANES data",
  r_version = R.version.string,
  survey_version = as.character(packageVersion("survey")),
  withCrossval_exists = TRUE,
  jkn = inspect_replicates("JKn", 1L, 29L),
  brr = inspect_replicates("BRR", 15L, 15L)
)

cat(paste(capture.output(dput(result)), collapse = "\n"), "\n")
