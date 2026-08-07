#!/usr/bin/env python3
"""P_BMX/P_DEMO の個人値を出力せず、独立最終試験候補の構造を監査する。"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


FILES = {
    "P_BMX.xpt": "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/P_BMX.xpt",
    "P_DEMO.xpt": "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/P_DEMO.xpt",
}
REQUIRED = {
    "P_BMX.xpt": ["SEQN", "BMDSTATS", "BMXHT", "BMIHT", "BMXWT", "BMIWT", "BMXBMI", "BMXWAIST", "BMIWAIST", "BMXHIP", "BMIHIP"],
    "P_DEMO.xpt": ["SEQN", "RIDAGEYR", "RIAGENDR", "WTMECPRP", "SDMVSTRA", "SDMVPSU"],
}
INPUTS = ["RIDAGEYR", "RIAGENDR", "BMXHT", "BMXWT", "BMXBMI"]


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as source:
        while block := source.read(1024 * 1024):
            value.update(block)
    return value.hexdigest()


def key_result(frame: pd.DataFrame) -> dict:
    key = frame["SEQN"]
    return {
        "present": True,
        "missing_count": int(key.isna().sum()),
        "duplicate_row_count": int(key.duplicated(keep=False).sum()),
        "unique_count": int(key.nunique(dropna=True)),
    }


def codes(series: pd.Series) -> dict[str, int]:
    result = {}
    for value, count in series.value_counts(dropna=False).items():
        label = "missing" if pd.isna(value) else str(int(value)) if float(value).is_integer() else str(value)
        result[label] = int(count)
    return dict(sorted(result.items()))


def domain_summary(domain: pd.DataFrame) -> dict:
    positive = domain[domain["WTMECPRP"] > 0]
    psus = positive[["SDMVSTRA", "SDMVPSU"]].dropna().drop_duplicates()
    psu_per_stratum = psus.groupby("SDMVSTRA")["SDMVPSU"].nunique()
    result = {
        "row_count": len(domain),
        "positive_WTMECPRP_count": len(positive),
        "contributing_SDMVSTRA_count": int(psus["SDMVSTRA"].nunique()),
        "contributing_stratum_psu_pair_count": len(psus),
        "lonely_PSU_stratum_count": int((psu_per_stratum == 1).sum()),
        "input_non_missing_counts": {name: int(positive[name].notna().sum()) for name in INPUTS},
        "BMXWAIST_non_missing_count": int(positive["BMXWAIST"].notna().sum()),
        "BMXHIP_non_missing_count": int(positive["BMXHIP"].notna().sum()),
        "BMDSTATS_code_counts": codes(positive["BMDSTATS"]),
        "comment_code_counts": {name: codes(positive[name]) for name in ("BMIHT", "BMIWT", "BMIWAIST", "BMIHIP")},
        "status_or_comment_exclusion_candidate_counts": {
            "waist_task": int(((positive["BMDSTATS"] != 1) | positive[["BMIHT", "BMIWT", "BMIWAIST"]].notna().any(axis=1)).sum()),
            "hip_task": int(((positive["BMDSTATS"] != 1) | positive[["BMIHT", "BMIWT", "BMIHIP"]].notna().any(axis=1)).sum()),
        },
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, default=Path("data/raw/nhanes/2017-2020"))
    parser.add_argument("--manifest", type=Path, default=Path("data/manifests/nhanes_2017_2020_final_test_audit.json"))
    args = parser.parse_args()

    frames, file_results = {}, []
    for filename, url in FILES.items():
        path = args.input_dir / filename
        frame = pd.read_sas(path, format="xport", encoding="utf-8")
        frames[filename] = frame
        missing = sorted(set(REQUIRED[filename]) - set(frame.columns))
        file_results.append({
            "filename": filename, "official_url": url,
            "retrieved_at_utc": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
            "file_size_bytes": path.stat().st_size, "sha256": digest(path),
            "xpt_read_success": True, "row_count": len(frame), "column_count": len(frame.columns),
            "columns": list(frame.columns), "column_types": {name: str(kind) for name, kind in frame.dtypes.items()},
            "required_columns": REQUIRED[filename], "missing_required_columns": missing,
            "seqn_integrity": key_result(frame),
        })
    bmx, demo = frames["P_BMX.xpt"], frames["P_DEMO.xpt"]
    if any(item["missing_required_columns"] for item in file_results):
        raise SystemExit("必須列が不足しているため停止")
    if any(item["seqn_integrity"][name] for item in file_results for name in ("missing_count", "duplicate_row_count")):
        raise SystemExit("SEQN integrityを満たさないため停止")
    joined = demo.merge(bmx, on="SEQN", how="inner", validate="one_to_one")
    adult = joined[joined["RIDAGEYR"] >= 20]
    domains = {"adult": adult}
    domains.update({f"adult_RIAGENDR_{int(code)}": part for code, part in adult.groupby("RIAGENDR")})

    manifest = {
        "schema_version": 1,
        "audit": "NHANES 2017-March 2020 independent final-test candidate structural audit (B-gate execution 8)",
        "inspected_at_utc": datetime.now(timezone.utc).isoformat(),
        "files": file_results,
        "join_integrity": {
            "key": "SEQN", "validation": "one_to_one", "joined_row_count": len(joined),
            "P_BMX_only_key_count": int(len(set(bmx.SEQN) - set(demo.SEQN))),
            "P_DEMO_only_key_count": int(len(set(demo.SEQN) - set(bmx.SEQN))), "joinable": True,
        },
        "design_principle": {"full_examined_design_retained": True, "domains_used": True, "physical_subdesign_created": False, "weight_renormalized": False},
        "domains": {name: domain_summary(frame) for name, frame in domains.items()},
        "qc_structure": {"component_status": "BMDSTATS", "item_comments": ["BMIHT", "BMIWT", "BMIWAIST", "BMIHIP"], "official_codebook_interpretation_required": True},
        "measurement_compatibility": {"2017_2019_2021": "compatible_for_version_0.1_candidates_no_material_procedure_difference_identified", "same_name_only_assumption": False},
        "unconfirmed": ["cycle間の同一人物が絶対にゼロであること", "CゲートのWebアプリ搭載・商用利用・成果物公開・元データ再配布の最終許諾", "封印方式、一回評価規則、評価指標、採否閾値", "development内design-aware選択法"],
        "prohibited_processing_performed": {"target_values_or_distribution_output": False, "SEQN_values_saved": False, "imputation_or_value_change": False, "outlier_processing_or_winsorization": False, "model_fit_regression_prediction_or_performance": False, "weight_renormalization": False, "gate_B_or_C_pass": False, "final_test_opened": False},
        "final_decision": "B: 条件付きで成立するが未解決事項あり",
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(args.manifest)


if __name__ == "__main__":
    main()
