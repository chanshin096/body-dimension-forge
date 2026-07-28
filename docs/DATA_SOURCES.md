# データ出典候補

公開人体計測データの採用可否を判断するための記録表。詳細と出典は [NHANES 監査](NHANES_AUDIT.md) を参照する。

| データ名 | 配布元 | 調査年 | 対象集団 | 人数 | 項目 | 測定方法 | 単位 | 利用条件 | 引用方法 | 採否 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| National Health and Nutrition Examination Survey (NHANES), August 2021–August 2023／Body Measures (`BMX_L`) | CDC, National Center for Health Statistics (NCHS) | 2021年8月～2023年8月 | 米国の civilian noninstitutionalized population を対象とする標本。身体計測ファイルは同期間の examined survey participants を収録 | 8,860レコード（`BMDSTATS` 度数の累計） | 身長、体重、計算BMI、ウエスト、ヒップ。胸囲は `BMX_L` に確認できない | MECで訓練済み health technician が標準化手順・校正機器を用いて測定。詳細は監査文書参照 | kg、cm、kg/m² | **未確認**（許可された公式ドメイン内で Data User Agreement 本文を確認できなかった） | 調査報告の書誌情報は確認済み。公開データセット固有の指定形式は**未確認** | **監査中（未採用）** |
| ANSUR II | 未確定 | 未確定 | 未確定 | 未確定 | 胸囲などの候補 | 未確定 | 未確定 | 未確定 | 未確定 | 未確定（今回未調査） |

## NHANES で参照した公式 URL

- 身体計測データ文書・コードブック: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/BMX_L.htm
- 人口統計・標本ウェイトデータ文書・コードブック: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/DEMO_L.htm
- NHANES Anthropometry Procedures Manual 2021: https://wwwn.cdc.gov/nchs/data/nhanes/public/2021/manuals/2021-Anthropometry-Procedures-Manual-508.pdf
- 2021–2023 cycle overview and analytic guidance: https://wwwn.cdc.gov/nchs/nhanes/continuousnhanes/overviewbrief.aspx?Cycle=2021-2023
- Survey Methods and Analytic Guidelines: https://wwwn.cdc.gov/nchs/nhanes/analyticguidelines.aspx

## 調査時の確認事項

- 測定定義が目的に合うか。
- 対象集団が成人・人間・現実に近い体型という対象範囲に合うか。
- cm、kg単位へ変換する場合の根拠が明確か。
- 利用条件がアプリ開発と公開に適合するか。
- 引用方法が明確か。
- 精度評価に必要な項目が含まれるか。
