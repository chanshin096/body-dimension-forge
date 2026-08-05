#!/usr/bin/env python3
"""NHANES の結合安全性と年齢候補別の欠損・QC件数を集計する。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


FILES = ("BMX_L.xpt", "DEMO_L.xpt")
ITEMS = {
    "BMXHT": ["BMIHT"],
    "BMXWT": ["BMIWT"],
    "BMXBMI": ["BMIHT", "BMIWT"],
    "BMXWAIST": ["BMIWAIST"],
    "BMXHIP": ["BMIHIP"],
}
DESIGN_VARIABLES = ("WTMEC2YR", "SDMVSTRA", "SDMVPSU")
REQUIRED_BMX = {"SEQN", "BMDSTATS", *ITEMS, *(c for columns in ITEMS.values() for c in columns)}
REQUIRED_DEMO = {"SEQN", "RIDAGEYR", "RIAGENDR", *DESIGN_VARIABLES}


def scalar(value: object) -> str:
    """コード値を意味付けせず、安定した文字列へ変換する。"""
    if pd.isna(value):
        return "missing"
    number = float(value)
    return str(int(number)) if number.is_integer() else format(number, "g")


def code_counts(series: pd.Series) -> dict[str, int]:
    counts = series.value_counts(dropna=False)
    return {scalar(code): int(count) for code, count in sorted(counts.items(), key=lambda x: scalar(x[0]))}


def key_check(frame: pd.DataFrame) -> dict[str, int | bool]:
    present = "SEQN" in frame.columns
    if not present:
        return {"present": False, "missing_count": 0, "duplicate_row_count": 0, "unique_count": 0}
    key = frame["SEQN"]
    return {
        "present": True,
        "missing_count": int(key.isna().sum()),
        "duplicate_row_count": int(key.duplicated(keep=False).sum()),
        "unique_count": int(key.nunique(dropna=True)),
    }


def item_summary(frame: pd.DataFrame, column: str) -> dict:
    total = len(frame)
    available = int(frame[column].notna().sum())
    missing = total - available
    return {
        "target_count": total,
        "non_missing_count": available,
        "missing_count": missing,
        "availability_rate": available / total if total else None,
        "comment_code_counts": {comment: code_counts(frame[comment]) for comment in ITEMS[column]},
        "bmdstats_code_counts": code_counts(frame["BMDSTATS"]),
    }


def group_summary(frame: pd.DataFrame) -> dict:
    groups = {"overall": frame}
    for code, group in frame.groupby("RIAGENDR", dropna=False):
        groups[f"RIAGENDR={scalar(code)}"] = group
    return {
        label: {
            "target_count": len(group),
            "items": {column: item_summary(group, column) for column in ITEMS},
        }
        for label, group in groups.items()
    }


def design_summary(frame: pd.DataFrame) -> dict:
    result = {
        column: {
            "present": column in frame.columns,
            "missing_count": int(frame[column].isna().sum()),
            "code_counts": code_counts(frame[column]),
        }
        for column in ("SDMVSTRA", "SDMVPSU")
    }
    weight = frame["WTMEC2YR"]
    result["WTMEC2YR"] = {
        "present": True,
        "missing_count": int(weight.isna().sum()),
        # ウェイト値そのものは個票に近いので保存せず、符号区分の件数だけを残す。
        "value_class_counts": {
            "positive": int((weight > 0).sum()),
            "zero": int((weight == 0).sum()),
            "negative": int((weight < 0).sum()),
        },
    }
    return result


def validate_summaries(age_candidates: dict) -> None:
    for candidate in age_candidates.values():
        overall = candidate["groups"]["overall"]["target_count"]
        gender_total = sum(
            group["target_count"] for label, group in candidate["groups"].items() if label != "overall"
        )
        if overall != gender_total:
            raise RuntimeError("RIAGENDR コード別件数が全体件数と一致しないため停止")
        for group in candidate["groups"].values():
            for item in group["items"].values():
                if item["non_missing_count"] + item["missing_count"] != item["target_count"]:
                    raise RuntimeError("項目の非欠損件数と欠損件数が対象人数に一致しないため停止")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, default=Path("data/raw/nhanes/2021-2023"))
    parser.add_argument(
        "--manifest", type=Path, default=Path("data/manifests/nhanes_2021_2023_join_qc_summary.json")
    )
    args = parser.parse_args()

    paths = {name: args.input_dir / name for name in FILES}
    missing_files = [str(path) for path in paths.values() if not path.is_file()]
    if missing_files:
        raise SystemExit(f"生データが存在しないため停止（download_nhanes_raw.py で取得）: {missing_files}")

    bmx = pd.read_sas(paths["BMX_L.xpt"], format="xport", encoding="utf-8")
    demo = pd.read_sas(paths["DEMO_L.xpt"], format="xport", encoding="utf-8")
    missing_columns = {
        "BMX_L.xpt": sorted(REQUIRED_BMX - set(bmx.columns)),
        "DEMO_L.xpt": sorted(REQUIRED_DEMO - set(demo.columns)),
    }
    if any(missing_columns.values()):
        raise SystemExit(f"必須列が存在しないため停止: {missing_columns}")

    bmx_key = key_check(bmx)
    demo_key = key_check(demo)
    common = set(bmx["SEQN"].dropna()) & set(demo["SEQN"].dropna())
    bmx_only = set(bmx["SEQN"].dropna()) - set(demo["SEQN"].dropna())
    demo_only = set(demo["SEQN"].dropna()) - set(bmx["SEQN"].dropna())
    safe = all(
        check["present"] and check["missing_count"] == 0 and check["duplicate_row_count"] == 0
        for check in (bmx_key, demo_key)
    )
    if not safe:
        raise SystemExit(f"SEQN に欠損または重複があり、安全に結合できないため停止: {bmx_key}, {demo_key}")

    joined = bmx.merge(demo, on="SEQN", how="inner", validate="one_to_one")
    if len(joined) != len(common):
        raise RuntimeError("結合行数が共通キー件数と一致しないため停止")

    candidates = {
        "all_ages": joined,
        "age_18_or_older": joined[joined["RIDAGEYR"] >= 18],
        "age_20_or_older": joined[joined["RIDAGEYR"] >= 20],
    }
    age_candidates = {
        name: {
            "filter": expression,
            "groups": group_summary(frame),
            "sample_design_variables": design_summary(frame),
        }
        for (name, frame), expression in zip(
            candidates.items(), ("none", "RIDAGEYR >= 18", "RIDAGEYR >= 20"), strict=True
        )
    }
    validate_summaries(age_candidates)

    manifest = {
        "schema_version": 1,
        "scope": "aggregate join-safety, adult-candidate, missingness, and QC counts only",
        "source_files": list(FILES),
        "pre_join_checks": {
            "BMX_L.xpt": {"row_count": len(bmx), **bmx_key},
            "DEMO_L.xpt": {"row_count": len(demo), **demo_key},
            "common_key_count": len(common),
            "bmx_only_key_count": len(bmx_only),
            "demo_only_key_count": len(demo_only),
            "safe_to_join": safe,
        },
        "join": {"performed": True, "type": "inner", "validation": "one_to_one", "row_count": len(joined)},
        "age_candidates": age_candidates,
        "decisions": {
            "adult_age_threshold": "undecided",
            "RIAGENDR_combination": "undecided",
            "missing_and_qc_handling": "undecided",
            "gate_B": "pending",
            "gate_C": "pending",
        },
        "prohibited_processing": {
            "imputation": False,
            "row_or_outlier_removal": False,
            "weighting_or_population_estimation": False,
            "correlation_regression_model_or_coefficients": False,
            "individual_rows_or_key_values_saved": False,
        },
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(args.manifest)


if __name__ == "__main__":
    main()
