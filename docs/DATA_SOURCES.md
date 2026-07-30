# データ出典候補

公開人体計測データの採用可否を判断するための記録表。詳細と出典は [NHANES 監査](NHANES_AUDIT.md) および [ANSUR II 監査](ANSUR_II_AUDIT.md) を参照する。

| データ名 | 配布元 | 調査年 | 対象集団 | 人数 | 項目 | 測定方法 | 単位 | 利用条件 | 引用方法 | 採否 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| National Health and Nutrition Examination Survey (NHANES), August 2021–August 2023／Body Measures (`BMX_L`) | CDC, National Center for Health Statistics (NCHS) | 2021年8月～2023年8月 | 米国の civilian noninstitutionalized population を対象とする標本。身体計測ファイルは同期間の examined survey participants を収録 | 8,860レコード（`BMDSTATS` 度数の累計） | 身長、体重、計算BMI、ウエスト、ヒップ。胸囲は `BMX_L` に確認できない | MECで訓練済み health technician が標準化手順・校正機器を用いて測定。詳細は監査文書参照 | kg、cm、kg/m² | **未確認**（許可された公式ドメイン内で Data User Agreement 本文を確認できなかった） | 調査報告の書誌情報は確認済み。公開データセット固有の指定形式は**未確認** | **監査中（未採用）** |
| 2012 Army-wide Anthropometric Survey (ANSUR II) | Natick Soldier Research, Development and Engineering Center (NSRDEC) の専門家とcontractors | 2012年（開始・終了月日は未確認） | 全米のSoldiers数千人。内訳、抽出方法、年齢範囲、一般成人への代表性は未確認 | 男性4,082件、女性1,986件 | 93 body measurementsと3D surface scans。記事でstature、weight、chest circumference等を例示。ウエスト、ヒップ、BMIは未確認 | strict guidelines and controlsとの記事記載はあるが、項目別定義は未確認 | 保存単位・換算方法とも未確認 | 2017年記事は当時publicとするが、具体的条件と現在の配布状況は未確認 | 米陸軍記事の書誌情報は確認済み。データ固有形式は未確認 | **監査中（未採用）** |

## NHANES で参照した公式 URL

- 身体計測データ文書・コードブック: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/BMX_L.htm
- 人口統計・標本ウェイトデータ文書・コードブック: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/DEMO_L.htm
- NHANES Anthropometry Procedures Manual 2021: https://wwwn.cdc.gov/nchs/data/nhanes/public/2021/manuals/2021-Anthropometry-Procedures-Manual-508.pdf
- 2021–2023 cycle overview and analytic guidance: https://wwwn.cdc.gov/nchs/nhanes/continuousnhanes/overviewbrief.aspx?Cycle=2021-2023
- Survey Methods and Analytic Guidelines: https://wwwn.cdc.gov/nchs/nhanes/analyticguidelines.aspx

## ANSUR II で参照した公式 URL

- Defense Centers for Public Health, Anthropometric Database（現行URL、2026-07-30はHTTP 503で本文取得不能）: https://ph.health.mil/topics/workplacehealth/ergo/Pages/Anthropometric-Database.aspx
- U.S. Army, “For good measure -- Natick releases raw data from Army-wide anthropometric survey”（2017-05-31、本文取得済み）: https://www.army.mil/article/188601/for_good_measure_natick_releases_raw_data_from_army_wide_anthropometric_survey

米陸軍記事から正式調査名、実施主体、2012年調査、対象がSoldiersであること、男女別公開件数、93項目、stature・weight・chest circumference等の存在を確認した。一方、現行Anthropometric Databaseページ、Memorandum、変数説明は取得できず、測定定義、保存単位、欠損・QC、具体的利用条件は未確認である。詳細は [ANSUR II 監査](ANSUR_II_AUDIT.md) を参照する。

## 調査時の確認事項

- 測定定義が目的に合うか。
- 対象集団が成人・人間・現実に近い体型という対象範囲に合うか。
- cm、kg単位へ変換する場合の根拠が明確か。
- 利用条件がアプリ開発と公開に適合するか。
- 引用方法が明確か。
- 精度評価に必要な項目が含まれるか。
