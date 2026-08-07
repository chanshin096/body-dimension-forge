#!/usr/bin/env python3
"""NHANES 2021--2023 身体計測分析用の標本設計検査を集計する。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


FILES = ("BMX_L.xpt", "DEMO_L.xpt")
DESIGN_VARIABLES = ("WTMEC2YR", "SDMVSTRA", "SDMVPSU")
KNOWN_CODES = {
    "RIAGENDR": {1, 2},
    "SDMVSTRA": set(range(173, 188)),
    "SDMVPSU": {1, 2},
}


def code_counts(series: pd.Series) -> dict[str, int]:
    """個人識別子やウェイト値を出力せず、確認済みコードの件数を返す。"""
    values = series.astype(int).value_counts().sort_index()
    return {str(code): int(count) for code, count in values.items()}


def validate_codes(frame: pd.DataFrame) -> None:
    for column, expected in KNOWN_CODES.items():
        if frame[column].isna().any():
            raise SystemExit(f"{column}: 欠損を検出したため停止")
        observed = set(frame[column].astype(int))
        if unknown := sorted(observed - expected):
            raise SystemExit(f"{column}: 公式資料で未確認のコードを検出したため停止: {unknown}")


def group_counts(frame: pd.DataFrame) -> dict[str, int]:
    result = {"overall": len(frame)}
    result.update({f"RIAGENDR={code}": count for code, count in code_counts(frame["RIAGENDR"]).items()})
    if result["overall"] != sum(count for label, count in result.items() if label != "overall"):
        raise RuntimeError("RIAGENDR 生コード別件数の合計が全体件数と一致しないため停止")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, default=Path("data/raw/nhanes/2021-2023"))
    parser.add_argument(
        "--manifest", type=Path, default=Path("data/manifests/nhanes_2021_2023_survey_design.json")
    )
    args = parser.parse_args()
    paths = {name: args.input_dir / name for name in FILES}
    if absent := [str(path) for path in paths.values() if not path.is_file()]:
        raise SystemExit(f"生データが存在しないため停止: {absent}")

    bmx = pd.read_sas(paths["BMX_L.xpt"], format="xport", encoding="utf-8")
    demo = pd.read_sas(paths["DEMO_L.xpt"], format="xport", encoding="utf-8")
    required = {"SEQN", "RIDAGEYR", "RIAGENDR", *DESIGN_VARIABLES}
    if missing := sorted(required - set(demo.columns)):
        raise SystemExit(f"DEMO_L.xpt: 必須列が存在しないため停止: {missing}")
    if "SEQN" not in bmx:
        raise SystemExit("BMX_L.xpt: SEQN が存在しないため停止")
    for name, frame in (("BMX_L.xpt", bmx), ("DEMO_L.xpt", demo)):
        if frame["SEQN"].isna().any() or frame["SEQN"].duplicated().any():
            raise SystemExit(f"{name}: SEQN に欠損または重複があるため停止")

    examined = bmx[["SEQN"]].merge(demo[list(required)], on="SEQN", how="inner", validate="one_to_one")
    if len(examined) != len(bmx):
        raise SystemExit("BMX と DEMO の全 examined record を一対一結合できないため停止")
    for column in DESIGN_VARIABLES:
        if not pd.api.types.is_numeric_dtype(examined[column]):
            raise SystemExit(f"{column}: 数値型でないため停止")
        if examined[column].isna().any():
            raise SystemExit(f"{column}: examined record に欠損があるため停止")
    weight = examined["WTMEC2YR"]
    if (weight <= 0).any():
        raise SystemExit("WTMEC2YR: examined record にゼロまたは負値があるため停止")
    validate_codes(examined)

    adults = examined[examined["RIDAGEYR"] >= 20]
    manifest = {
        "schema_version": 1,
        "scope": "aggregate survey-design validation counts and adopted analysis policy only",
        "source_files": list(FILES),
        "population_filter": "RIDAGEYR >= 20 as a survey domain; full examined design retained for variance estimation",
        "design": {
            "weight": "WTMEC2YR",
            "strata": "SDMVSTRA",
            "cluster": "SDMVPSU",
            "weight_modification": "none; no renormalization after domain, item-missing, or QC selection",
            "variance": "design-based method supporting strata, PSU, weight, and domain estimation",
        },
        "validation": {
            "examined_record_count": len(examined),
            "adult_domain_counts": group_counts(adults),
            "variables": {
                column: {
                    "present": True,
                    "numeric_dtype": bool(pd.api.types.is_numeric_dtype(examined[column])),
                    "valid_count": int(examined[column].notna().sum()),
                    "missing_count": int(examined[column].isna().sum()),
                }
                for column in DESIGN_VARIABLES
            },
            "WTMEC2YR_value_class_counts": {
                "positive": int((weight > 0).sum()),
                "zero": int((weight == 0).sum()),
                "negative": int((weight < 0).sum()),
            },
            "SDMVSTRA_code_counts": code_counts(examined["SDMVSTRA"]),
            "SDMVPSU_code_counts": code_counts(examined["SDMVPSU"]),
            "stratum_psu_cell_count": int(examined[["SDMVSTRA", "SDMVPSU"]].drop_duplicates().shape[0]),
        },
        "output_policy": {
            "unweighted_counts_are_labeled_separately": True,
            "weighted_estimates_require_variance_or_uncertainty": True,
            "individual_rows_seqn_or_weight_values_saved": False,
            "public_output": "aggregate counts and disclosure-reviewed weighted estimates only; no microdata",
        },
        "prohibited_processing": {
            "weight_renormalization_or_scaling": False,
            "imputation_outlier_removal_regression_correlation_model_or_coefficients": False,
            "individual_rows_seqn_or_weight_values_saved": False,
        },
        "gate_B": "pending",
        "gate_C": "pending",
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(args.manifest)


if __name__ == "__main__":
    main()
