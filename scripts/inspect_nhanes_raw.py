#!/usr/bin/env python3
"""NHANES XPT の構造だけを検査し、機械可読 manifest を生成する。"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from download_nhanes_raw import FILES


REQUIRED_COLUMNS = {
    "BMX_L.xpt": [
        "SEQN", "BMXHT", "BMXWT", "BMXBMI", "BMXWAIST", "BMXHIP",
        "BMDSTATS", "BMIHT", "BMIWT", "BMIWAIST", "BMIHIP",
    ],
    "DEMO_L.xpt": ["SEQN", "RIDAGEYR", "RIAGENDR", "WTMEC2YR", "SDMVSTRA", "SDMVPSU"],
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def inspect(path: Path, url: str) -> dict:
    result = {
        "filename": path.name,
        "source_url": url,
        "retrieved_at_utc": datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat(),
        "file_size_bytes": path.stat().st_size,
        "sha256": sha256(path),
        "read_success": False,
        "read_error": None,
    }
    try:
        frame = pd.read_sas(path, format="xport", encoding="utf-8")
        columns = list(frame.columns)
        required = REQUIRED_COLUMNS[path.name]
        result.update({
            "row_count": len(frame),
            "column_count": len(columns),
            "columns": columns,
            "required_columns": required,
            "missing_required_columns": [name for name in required if name not in columns],
            "seqn_present": "SEQN" in columns,
            "read_success": True,
        })
    except Exception as exc:
        result["read_error"] = f"{type(exc).__name__}: {exc}"
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, default=Path("data/raw/nhanes/2021-2023"))
    parser.add_argument("--manifest", type=Path, default=Path("data/manifests/nhanes_2021_2023_intake.json"))
    args = parser.parse_args()

    files = []
    for filename, url in FILES.items():
        path = args.input_dir / filename
        if not path.is_file():
            raise SystemExit(f"対象ファイルが存在しないため停止: {path}")
        files.append(inspect(path, url))

    manifest = {
        "schema_version": 1,
        "inspection_scope": "download and structural intake inspection only",
        "inspected_at_utc": datetime.now(timezone.utc).isoformat(),
        "files": files,
        "join_key_check": {
            "key": "SEQN",
            "present_in_all_files": all(item.get("seqn_present", False) for item in files),
            "join_performed": False,
        },
        "prohibited_processing_performed": False,
        "acceptance_passed": all(
            item["read_success"] and not item.get("missing_required_columns", ["inspection failed"])
            for item in files
        ),
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(args.manifest)
    if not manifest["acceptance_passed"] or not manifest["join_key_check"]["present_in_all_files"]:
        raise SystemExit("受入条件を満たさないため停止。manifest を確認してください。")


if __name__ == "__main__":
    main()
