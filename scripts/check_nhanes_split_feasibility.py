#!/usr/bin/env python3
"""NHANES の pseudo-PSU 非重複3群分割について集計だけで実現性を検査する。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

FILES = ("BMX_L.xpt", "DEMO_L.xpt")
ITEMS = {
    "BMXHT": ("BMIHT", {3}),
    "BMXWT": ("BMIWT", {3, 4}),
    "BMXBMI": (("BMIHT", "BMIWT"), {"BMIHT": {3}, "BMIWT": {3, 4}}),
    "BMXWAIST": ("BMIWAIST", set()),
    "BMXHIP": ("BMIHIP", set()),
}
INPUT_SETS = {
    "age_hw": ("BMXHT", "BMXWT"),
    "age_h_bmi": ("BMXHT", "BMXBMI"),
    "age_w_bmi": ("BMXWT", "BMXBMI"),
    "age_bmi": ("BMXBMI",),
}
TASKS = {"waist": "BMXWAIST", "hip": "BMXHIP"}
GROUPS = ("training", "validation", "sealed_final_test")


def usable(frame: pd.DataFrame, variable: str) -> pd.Series:
    """Bゲート実行1の相互排他的分類のうち usable だけを返す。"""
    config = ITEMS[variable]
    ok = frame[variable].notna()
    if variable == "BMXBMI":
        comments, holds = config
        for comment in comments:
            ok &= ~frame[comment].isin(holds[comment])
    else:
        comment, holds = config
        ok &= ~frame[comment].isin(holds)
    return ok


def count_domains(frame: pd.DataFrame) -> dict:
    adult = frame["RIDAGEYR"].ge(20)
    result: dict[str, object] = {
        "examined_unweighted_n": len(frame),
        "adult_unweighted_n": int(adult.sum()),
        "adult_RIAGENDR_raw_code_counts": {
            str(code): int((adult & frame["RIAGENDR"].eq(code)).sum()) for code in (1, 2)
        },
        "complete_case_counts": {},
    }
    for task, target in TASKS.items():
        result["complete_case_counts"][task] = {}
        for set_id, inputs in INPUT_SETS.items():
            complete = adult & usable(frame, target)
            for variable in inputs:
                complete &= usable(frame, variable)
            result["complete_case_counts"][task][set_id] = {
                "overall": int(complete.sum()),
                **{str(code): int((complete & frame["RIAGENDR"].eq(code)).sum()) for code in (1, 2)},
            }
    return result


def validate_keys(bmx: pd.DataFrame, demo: pd.DataFrame) -> pd.DataFrame:
    for name, frame in zip(FILES, (bmx, demo), strict=True):
        if frame["SEQN"].isna().any() or frame["SEQN"].duplicated().any():
            raise SystemExit(f"{name}: SEQN に欠損または重複があるため停止")
    joined = bmx.merge(demo, on="SEQN", how="inner", validate="one_to_one")
    if len(joined) != len(bmx):
        raise SystemExit("full examined sampleをDEMOへ一対一結合できないため停止")
    return joined


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, default=Path("data/raw/nhanes/2021-2023"))
    parser.add_argument(
        "--manifest", type=Path, default=Path("data/manifests/nhanes_2021_2023_split_feasibility.json")
    )
    args = parser.parse_args()
    paths = {name: args.input_dir / name for name in FILES}
    if absent := [str(path) for path in paths.values() if not path.is_file()]:
        raise SystemExit(f"生データが存在しないため停止: {absent}")
    bmx = pd.read_sas(paths["BMX_L.xpt"], format="xport", encoding="utf-8")
    demo = pd.read_sas(paths["DEMO_L.xpt"], format="xport", encoding="utf-8")
    required_bmx = {"SEQN", "BMDSTATS", *ITEMS, "BMIHT", "BMIWT", "BMIWAIST", "BMIHIP"}
    required_demo = {"SEQN", "RIDAGEYR", "RIAGENDR", "WTMEC2YR", "SDMVSTRA", "SDMVPSU"}
    missing = {"BMX_L.xpt": sorted(required_bmx - set(bmx)), "DEMO_L.xpt": sorted(required_demo - set(demo))}
    if any(missing.values()):
        raise SystemExit(f"必須列が存在しないため停止: {missing}")
    joined = validate_keys(bmx, demo)
    for column, expected in (("RIAGENDR", {1, 2}), ("SDMVSTRA", set(range(173, 188))), ("SDMVPSU", {1, 2})):
        if joined[column].isna().any() or set(joined[column].astype(int)) - expected:
            raise SystemExit(f"{column}: 欠損または未確認コードがあるため停止")

    strata = sorted(joined["SDMVSTRA"].astype(int).unique())
    # 結果を参照しない構造診断候補。層を丸ごと順番に3群へ配り、比率・seedの正式採用はしない。
    allocation = {stratum: GROUPS[index % 3] for index, stratum in enumerate(strata)}
    joined["diagnostic_group"] = joined["SDMVSTRA"].astype(int).map(allocation)
    psu_rows = []
    for (stratum, psu), part in joined.groupby(["SDMVSTRA", "SDMVPSU"], sort=True):
        psu_rows.append({
            "SDMVSTRA": int(stratum),
            "SDMVPSU": int(psu),
            "diagnostic_group": allocation[int(stratum)],
            **count_domains(part),
        })
    stratum_psu_counts = joined.groupby("SDMVSTRA")["SDMVPSU"].nunique()
    if not stratum_psu_counts.eq(2).all() or len(psu_rows) != 30:
        raise SystemExit("想定した15層×2 pseudo-PSU構造と一致しないため停止")

    group_results = {}
    assigned_cells = []
    for group in GROUPS:
        part = joined[joined["diagnostic_group"].eq(group)]
        cells = set(zip(part["SDMVSTRA"].astype(int), part["SDMVPSU"].astype(int)))
        assigned_cells.extend((group, *cell) for cell in cells)
        counts = count_domains(part)
        all_domains_positive = all(
            values[code] > 0
            for task in counts["complete_case_counts"].values()
            for values in task.values()
            for code in ("1", "2")
        )
        group_results[group] = {
            "retained_stratum_count": int(part["SDMVSTRA"].nunique()),
            "retained_pseudo_psu_count": len(cells),
            "design_degrees_of_freedom_psu_minus_strata": len(cells) - int(part["SDMVSTRA"].nunique()),
            "single_psu_stratum_count": int((part.groupby("SDMVSTRA")["SDMVPSU"].nunique() == 1).sum()),
            "missing_original_stratum_count": len(strata) - int(part["SDMVSTRA"].nunique()),
            "all_task_raw_code_input_set_cells_positive": all_domains_positive,
            **counts,
        }
    unique_cells = {(stratum, psu) for _, stratum, psu in assigned_cells}
    overlap_count = len(assigned_cells) - len(unique_cells)
    uncovered_count = len(psu_rows) - len(unique_cells)
    if overlap_count or uncovered_count:
        raise RuntimeError("診断候補でpseudo-PSUの重複または未割当を検出")

    manifest = {
        "schema_version": 1,
        "scope": "aggregate pseudo-PSU split feasibility inspection; no model fitting or individual output",
        "source_files": list(FILES),
        "join": {"key": "SEQN", "validation": "one_to_one", "full_examined_row_count": len(joined)},
        "full_examined_design": {
            "stratum_count": len(strata),
            "pseudo_psu_count": len(psu_rows),
            "design_degrees_of_freedom_psu_minus_strata": len(psu_rows) - len(strata),
            "pseudo_psu_counts_by_stratum": {str(int(k)): int(v) for k, v in stratum_psu_counts.items()},
        },
        "pseudo_psu_aggregate_counts": psu_rows,
        "diagnostic_candidate": {
            "status": "feasibility candidate only; not adopted; final-test values were not evaluated",
            "rule": "sort public SDMVSTRA codes ascending and assign whole strata cyclically to training, validation, sealed_final_test",
            "seed": None,
            "target_ratios": None,
            "pseudo_psu_overlap_count": overlap_count,
            "unassigned_pseudo_psu_count": uncovered_count,
            "individual_cross_group_count": 0,
            "groups": group_results,
            "structural_result": "each group has five complete strata, ten pseudo-PSUs, and nominal PSU-minus-strata df=5",
        },
        "feasibility_conclusion": {
            "three_way_nonoverlap_and_positive_complete_cases": all(
                result["all_task_raw_code_input_set_cells_positive"] for result in group_results.values()
            ),
            "physical_subset_has_two_psus_in_each_retained_stratum": all(
                result["single_psu_stratum_count"] == 0 for result in group_results.values()
            ),
            "design_based_variance_method_confirmed": False,
            "overall_status": "undecided",
            "reason": "the aggregate candidate satisfies structural necessary conditions, but an official method for split-specific design variance, empty strata, and single-PSU handling has not been adopted",
        },
        "prohibited_processing_performed": {
            "model_training_regression_prediction_or_baseline": False,
            "imputation_value_change_winsorization_or_outlier_removal": False,
            "individual_rows_seqn_list_or_individual_assignment_saved": False,
            "gate_status_change": False,
        },
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(args.manifest)


if __name__ == "__main__":
    main()
