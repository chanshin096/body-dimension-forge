# NHANES 2021–2023 生データ取得・受入検査（Aゲート実行1）

## 1. 実施範囲

- 実施日時: 2026-08-04（UTC）
- 情報源: CDC/NCHS 公式ドメイン `wwwn.cdc.gov` のみ
- 対象: `BMX_L.xpt`、`DEMO_L.xpt`
- 実施内容: 公式生データの取得、XPT 読み込み、ファイル構造・必須列・`SEQN` の存在確認
- 機械可読な正本: [`data/manifests/nhanes_2021_2023_intake.json`](../data/manifests/nhanes_2021_2023_intake.json)

この検査はA「解析開始」で許可された内容確認に限定した。結合可能性は双方にキーが存在することだけで判定し、レコード結合は行っていない。成人抽出、欠損値処理、前処理方針の決定、統計値・相関の算出、グラフ、モデル、推定式、係数の作成は行っていない。B「モデル採用」およびC「完成品搭載・配布」の状態は変更していない。

## 2. 再実行手順

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-analysis.txt
.venv/bin/python scripts/download_nhanes_raw.py
.venv/bin/python scripts/inspect_nhanes_raw.py
```

既存ファイルを公式配布物で置き換える場合だけ、ダウンロードに `--overwrite` を付ける。ダウンロードスクリプトは取得元とリダイレクト先のホストを `wwwn.cdc.gov` に制限する。生データは `data/raw/nhanes/2021-2023/` に保存されるが、`.gitignore` によりGit管理対象外である。manifest は検査の再実行時に更新される。

## 3. 取得・検査結果

| ファイル | 正式な取得URL | 取得日時（UTC） | サイズ | SHA-256 | 読み込み | 行数 | 列数 |
| --- | --- | --- | ---: | --- | --- | ---: | ---: |
| `BMX_L.xpt` | https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/BMX_L.xpt | 2026-08-04T04:09:02.479726+00:00 | 1,563,200 bytes | `44440c416d9ad709e8b1708a5975378ab4d5b18edc39eb5015c2ae7186500170` | 成功 | 8,860 | 22 |
| `DEMO_L.xpt` | https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/DEMO_L.xpt | 2026-08-04T04:09:03.123726+00:00 | 2,582,160 bytes | `ca4374a158b493b8b0163e1388da21d57a18d1b9cecff2aa4e2fa2bec494fe23` | 成功 | 11,933 | 27 |

### `BMX_L.xpt` 列名一覧

`SEQN`, `BMDSTATS`, `BMXWT`, `BMIWT`, `BMXRECUM`, `BMIRECUM`, `BMXHEAD`, `BMIHEAD`, `BMXHT`, `BMIHT`, `BMXBMI`, `BMDBMIC`, `BMXLEG`, `BMILEG`, `BMXARML`, `BMIARML`, `BMXARMC`, `BMIARMC`, `BMXWAIST`, `BMIWAIST`, `BMXHIP`, `BMIHIP`

必須列 `SEQN`, `BMXHT`, `BMXWT`, `BMXBMI`, `BMXWAIST`, `BMXHIP`, `BMDSTATS`, `BMIHT`, `BMIWT`, `BMIWAIST`, `BMIHIP` はすべて存在した。

### `DEMO_L.xpt` 列名一覧

`SEQN`, `SDDSRVYR`, `RIDSTATR`, `RIAGENDR`, `RIDAGEYR`, `RIDAGEMN`, `RIDRETH1`, `RIDRETH3`, `RIDEXMON`, `RIDEXAGM`, `DMQMILIZ`, `DMDBORN4`, `DMDYRUSR`, `DMDEDUC2`, `DMDMARTZ`, `RIDEXPRG`, `DMDHHSIZ`, `DMDHRGND`, `DMDHRAGZ`, `DMDHREDZ`, `DMDHRMAZ`, `DMDHSEDZ`, `WTINT2YR`, `WTMEC2YR`, `SDMVSTRA`, `SDMVPSU`, `INDFMPIR`

必須列 `SEQN`, `RIDAGEYR`, `RIAGENDR`, `WTMEC2YR`, `SDMVSTRA`, `SDMVPSU` はすべて存在した。

## 4. 照合結果と停止条件

- `BMX_L.xpt` の8,860行は既存のNHANES監査記録にある8,860レコードと一致した。
- 既存監査に記録された対象列と品質・comment列は実ファイルに存在した。
- `SEQN` は両ファイルに存在したため、キーの構造上の結合可能性を確認できた。ただし、値の一意性・重複・対応件数は検査せず、結合も実行していない。
- 公式URLからの取得、XPT読み込み、必須列、既存監査との照合に停止条件は発生しなかった。受入検査結果は「可」であるが、これは今回の構造検査の合格だけを意味し、BまたはCの通過やデータの正式採用を意味しない。

## 5. 未実施・未確定

- 成人抽出、欠損・QCの除外または補完、統計区分、男女データの結合判断、前処理は未実施・未決定。
- 件数以外の統計値、分布、相関、モデル評価は未算出。
- 詳細利用条件、完成品への搭載、公開、商用利用、再配布の可否は未確認のままであり、Cは保留。
- 次工程へ進む前に、目的と許可範囲を改めてゲートに照らし、成人抽出、欠損・QC、複雑標本設計を決定する工程がBの判定作業として明示的に許可されていることを確認する。
