#!/usr/bin/env python3
"""成人 NHANES 5項目の欠損・測定状態・QC方針用集計を生成する。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

ITEMS = {
    "BMXHT": {"comments": ["BMIHT"], "hold_codes": {"BMIHT": [3]}},
    "BMXWT": {"comments": ["BMIWT"], "hold_codes": {"BMIWT": [3, 4]}},
    "BMXBMI": {"comments": ["BMIHT", "BMIWT"], "hold_codes": {"BMIHT": [3], "BMIWT": [3, 4]}},
    "BMXWAIST": {"comments": ["BMIWAIST"], "hold_codes": {}},
    "BMXHIP": {"comments": ["BMIHIP"], "hold_codes": {}},
}
KNOWN_CODES = {
    "BMDSTATS": {1, 2, 3, 4},
    "BMIHT": {1, 3},
    "BMIWT": {1, 3, 4},
    "BMIWAIST": {1},
    "BMIHIP": {1},
}
FILES = ("BMX_L.xpt", "DEMO_L.xpt")


def scalar(value: object) -> str:
    """コードへ意味を付けず安定した文字列にする。"""
    if pd.isna(value):
        return "missing"
    if isinstance(value, str):
        return value
    number = float(value)
    return str(int(number)) if number.is_integer() else format(number, "g")


def counts(series: pd.Series) -> dict[str, int]:
    result = series.value_counts(dropna=False)
    return {scalar(code): int(n) for code, n in sorted(result.items(), key=lambda pair: scalar(pair[0]))}


def summarize_item(frame: pd.DataFrame, variable: str, config: dict) -> dict:
    value = frame[variable]
    missing = value.isna()
    could_not_obtain = pd.Series(False, index=frame.index)
    quality_hold = pd.Series(False, index=frame.index)
    for comment in config["comments"]:
        could_not_obtain |= frame[comment].eq(1)
        quality_hold |= frame[comment].isin(config["hold_codes"].get(comment, []))

    # 優先順位を固定し、全カテゴリを相互排他的にする。
    category = pd.Series("usable", index=frame.index, dtype="string")
    category.loc[value.notna() & quality_hold] = "hold_comment_on_value"
    category.loc[missing & frame["BMDSTATS"].eq(4)] = "exclude_no_body_measures"
    category.loc[missing & ~frame["BMDSTATS"].eq(4)] = "hold_other_missing"
    category.loc[missing & could_not_obtain] = "exclude_could_not_obtain"

    result = {
        "target_count": len(frame),
        "value_state_counts": {"non_missing": int(value.notna().sum()), "missing": int(missing.sum())},
        "processing_category_counts": counts(category),
        "comment_code_counts": {comment: counts(frame[comment]) for comment in config["comments"]},
        "component_status_code_counts": counts(frame["BMDSTATS"]),
        "non_target_count": 0,
        "other_special_value_count": int(value.isin([float("inf"), float("-inf")]).sum()),
    }
    if sum(result["processing_category_counts"].values()) != len(frame):
        raise RuntimeError(f"{variable}: 処理カテゴリ件数が対象件数と一致しない")
    if result["value_state_counts"]["non_missing"] + result["value_state_counts"]["missing"] != len(frame):
        raise RuntimeError(f"{variable}: 値状態件数が対象件数と一致しない")
    return result


def group_summary(frame: pd.DataFrame) -> dict:
    groups = {"overall": frame}
    groups.update({f"RIAGENDR={scalar(code)}": part for code, part in frame.groupby("RIAGENDR", dropna=False)})
    output = {
        label: {"target_count": len(part), "items": {v: summarize_item(part, v, c) for v, c in ITEMS.items()}}
        for label, part in groups.items()
    }
    if output["overall"]["target_count"] != sum(v["target_count"] for k, v in output.items() if k != "overall"):
        raise RuntimeError("RIAGENDR 生コード別件数が全体件数と一致しない")
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, default=Path("data/raw/nhanes/2021-2023"))
    parser.add_argument("--manifest", type=Path, default=Path("data/manifests/nhanes_2021_2023_missing_qc_policy.json"))
    args = parser.parse_args()
    paths = {name: args.input_dir / name for name in FILES}
    absent = [str(path) for path in paths.values() if not path.is_file()]
    if absent:
        raise SystemExit(f"生データが存在しないため停止: {absent}")

    bmx = pd.read_sas(paths["BMX_L.xpt"], format="xport", encoding="utf-8")
    demo = pd.read_sas(paths["DEMO_L.xpt"], format="xport", encoding="utf-8")
    required_bmx = {"SEQN", "BMDSTATS", *ITEMS, *(x for c in ITEMS.values() for x in c["comments"])}
    required_demo = {"SEQN", "RIDAGEYR", "RIAGENDR"}
    if missing_columns := {"BMX_L.xpt": sorted(required_bmx - set(bmx)), "DEMO_L.xpt": sorted(required_demo - set(demo))}:
        if any(missing_columns.values()):
            raise SystemExit(f"必須列が存在しないため停止: {missing_columns}")
    for name, frame in (("BMX_L.xpt", bmx), ("DEMO_L.xpt", demo)):
        if frame["SEQN"].isna().any() or frame["SEQN"].duplicated().any():
            raise SystemExit(f"{name}: SEQN に欠損または重複があるため停止")

    joined = bmx.merge(demo[["SEQN", "RIDAGEYR", "RIAGENDR"]], on="SEQN", how="inner", validate="one_to_one")
    adults = joined[joined["RIDAGEYR"] >= 20].copy()
    unknown_codes = {
        column: sorted(set(adults[column].dropna().astype(int)) - expected)
        for column, expected in KNOWN_CODES.items()
    }
    if any(unknown_codes.values()):
        raise SystemExit(f"公式資料で意味を確認していないコードがあるため停止: {unknown_codes}")
    manifest = {
        "schema_version": 1,
        "scope": "aggregate missingness, measurement-status, comment, and provisional QC policy counts only",
        "source_files": list(FILES),
        "population_filter": "RIDAGEYR >= 20",
        "grouping": "RIAGENDR raw codes kept separately; no labels inferred and no unconditional combination",
        "category_precedence": [
            "exclude_could_not_obtain",
            "exclude_no_body_measures",
            "hold_other_missing",
            "hold_comment_on_value",
            "usable",
        ],
        "groups": group_summary(adults),
        "policy": {
            "usable": "non-missing value with no confirmed quality-affecting comment",
            "exclude_could_not_obtain": "missing value with relevant comment code 1",
            "exclude_no_body_measures": "missing value with BMDSTATS code 4",
            "hold_other_missing": "missing value not assigned to either confirmed exclusion category",
            "hold_comment_on_value": "non-missing value with BMIHT code 3 or BMIWT code 3/4, as applicable",
            "non_target": "zero for all five items because official target ages include RIDAGEYR >= 20; screening/exam age timing remains a documented limitation",
            "outliers": "no automatic removal; no additional range rule applied",
        },
        "prohibited_processing": {
            "imputation": False,
            "mean_replacement": False,
            "estimated_imputation": False,
            "automatic_outlier_removal": False,
            "model_formula_or_coefficients": False,
            "individual_rows_or_seqn_values_saved": False,
        },
        "gate_B": "pending",
        "gate_C": "pending",
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(args.manifest)


if __name__ == "__main__":
    main()
