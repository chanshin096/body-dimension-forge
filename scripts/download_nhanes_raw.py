#!/usr/bin/env python3
"""CDC/NCHS 公式配布元から受入検査対象の NHANES 生データを取得する。"""

from __future__ import annotations

import argparse
import os
import urllib.parse
import urllib.request
from pathlib import Path


FILES = {
    "BMX_L.xpt": "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/BMX_L.xpt",
    "DEMO_L.xpt": "https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/DEMO_L.xpt",
}
ALLOWED_HOST = "wwwn.cdc.gov"


class OfficialOnlyRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        if urllib.parse.urlparse(newurl).hostname != ALLOWED_HOST:
            raise RuntimeError(f"CDC/NCHS 公式ドメイン外へのリダイレクトを拒否: {newurl}")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def download(url: str, destination: Path, overwrite: bool) -> None:
    if urllib.parse.urlparse(url).hostname != ALLOWED_HOST:
        raise RuntimeError(f"許可されていない取得元: {url}")
    if destination.exists() and not overwrite:
        print(f"既存ファイルを維持: {destination}")
        return

    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".part")
    opener = urllib.request.build_opener(OfficialOnlyRedirectHandler())
    request = urllib.request.Request(url, headers={"User-Agent": "body-dimension-forge/nhanes-intake"})
    try:
        with opener.open(request, timeout=120) as response, temporary.open("wb") as output:
            if response.geturl() != url:
                print(f"公式ドメイン内リダイレクト: {url} -> {response.geturl()}")
            while chunk := response.read(1024 * 1024):
                output.write(chunk)
        os.replace(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)
    print(f"取得完了: {destination}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("data/raw/nhanes/2021-2023"))
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    for filename, url in FILES.items():
        download(url, args.output_dir / filename, args.overwrite)


if __name__ == "__main__":
    main()
