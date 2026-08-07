# NHANES 2021–2023 複雑標本設計・ウェイト方針

## 1. 目的・状態・正本

本書は、NHANES August 2021–August 2023 の `RIDAGEYR >= 20` を対象に、身長 `BMXHT`、体重 `BMXWT`、BMI `BMXBMI`、ウエスト `BMXWAIST`、ヒップ `BMXHIP` を今後分析する際の複雑標本設計方針を定める（Bゲート実行2）。詳細な検査件数の正本は [`data/manifests/nhanes_2021_2023_survey_design.json`](../data/manifests/nhanes_2021_2023_survey_design.json) であり、本書へ重複掲載しない。

これは分析方法の一部を決めるだけで、モデル、推定式、係数を作成・採用せず、5項目の **A可・B保留・C保留を変更しない**。胸囲、ANSUR II、Webアプリ、配布形態も対象外である。

## 2. 公式根拠

2026-08-06 に次の CDC/NCHS 公式資料本文へ接続して確認した。第三者資料は使用していない。

1. [DEMO_L documentation](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/DEMO_L.htm): `WTMEC2YR` は “Full sample 2-year MEC exam weight”、`SDMVSTRA` は masked variance pseudo-stratum、`SDMVPSU` は masked variance pseudo-PSU。15層・30 PSU（各層2 PSU）、2021–2023の分析では目的に応じ2年ウェイトを使うこと、対象母集団とcycle固有の設計変更を確認した。
2. [BMX_L documentation](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/BMX_L.htm): body measures は MEC examination component であり、分析に examination sample weights を使うことを確認した。
3. [NHANES Weighting Module](https://wwwn.cdc.gov/nchs/nhanes/tutorials/weighting.aspx): ウェイトは複雑抽出、非回答、post-stratificationを反映し、分析中で最小の対象に適用されるウェイトを選ぶこと、加重・非加重推定は一致しないことを確認した。
4. [NHANES Variance Estimation Module](https://wwwn.cdc.gov/nchs/nhanes/tutorials/varianceestimation.aspx): Taylor series linearization、層・PSU・ウェイトの指定、成人等を事前に行削除せず domain/subpopulation として扱うこと、Rでは全 examined designを作ってから survey design object を subset することを確認した。
5. [2021–2023 cycle overview](https://wwwn.cdc.gov/nchs/nhanes/continuousnhanes/overviewbrief.aspx?Cycle=2021-2023): 代表性、nonresponse、分散推定、subgroupの精度、cycle結合への注意を確認した。

## 3. 採用する設計

| 要素 | 採用方針 | 理由・意味 |
| --- | --- | --- |
| 標本ウェイト | `WTMEC2YR` を**配布値のまま**使用する | 5項目はMEC身体計測であり、正式名称は full sample 2-year MEC exam weight。抽出確率、非回答調整、post-stratificationを反映する。 |
| 層化 | `SDMVSTRA` | 公開用にmaskされた分散推定用pseudo-stratum。単純無作為標本扱いを避ける。 |
| クラスタリング | `SDMVPSU` を `SDMVSTRA` 内にネスト | 公開用pseudo-PSU。PSU番号は層間で再利用されるため、PSU単独を大域一意IDと扱わない。 |
| 成人 | full examined sample（正の `WTMEC2YR`）でdesignを定義後、`RIDAGEYR >= 20` をdomain/subpopulation指定 | 成人行だけを先に削除すると分散を誤る可能性があるという公式手順に従う。 |
| `RIAGENDR` | 公式コード `1`、`2` ごとに別domainとして扱い、生コードのまま表示する | コード別分析でもfull designを保持する。無条件結合はしない。本工程では名称を付けない。 |
| 欠損・QC後 | 項目別の分析対象indicatorをdomain条件へ追加し、`WTMEC2YR` を再正規化・再調整しない | NCHS提供ウェイトを自己加工せず、全examined designの情報を分散推定に残す。項目欠損に対する新しい非回答調整ウェイトは公式提供されていないため、独自作成しない。 |
| 分散 | ウェイト・層・PSUとdomainを扱えるsurvey procedureを使用する。Taylor linearizationを既定候補とする | 公式tutorialが示す設計ベースの分散推定。分位点等で利用ソフトが対応する設計ベース手法を使う。 |

ウェイト再正規化は**不採用**である。再正規化しても平均等の点推定が変わらない場合があることを加工の根拠にせず、母集団totalや標準誤差への影響、公式調整の意味を損なう可能性を避ける。欠損が選択的である場合の残余バイアスは、再正規化で解決したとは扱わず限界として報告する。

## 4. 統計量別の必須反映範囲

| 今後の処理 | 必須方針 | 非加重結果の位置づけ |
| --- | --- | --- |
| 平均・割合・total | `WTMEC2YR`、`SDMVSTRA`、`SDMVPSU`、domainを反映し、標準誤差または信頼区間も併記 | 件数・データQCだけ。母集団推定として表示しない。なお欠損項目の人口totalをウェイト合計から作ることは不採用。 |
| 分位点 | survey-weighted quantileと設計対応の分散・信頼区間を用いる | 標本分布の補助診断だけ。代表値として採用しない。 |
| 分布 | 加重割合・加重CDF等を用い、設計ベースの不確実性を付す | histogram等を使う場合も「非加重標本」と明記する。 |
| 回帰 | 将来実施が許可された場合、母集団関連の推論にはsurvey-weighted/design-based procedureを使用し、設計ベース標準誤差を用いる | 非加重回帰を正式結果・感度分析の代用にしない。本工程では回帰を実施しない。 |
| モデル評価 | 将来の採用試験では、対象母集団性能を称する指標にexam weightを反映し、層・PSUを保つ再標本化または設計対応の不確実性評価を事前に確定する | 非加重指標は標本内の補足に限定。分割法・具体的指標・採用閾値は**未確定**であり、本工程では評価しない。 |

## 5. 表示・保存・公開方針

- `n` / `unweighted_n` は観測行の**非加重件数**、estimateは**加重推定値**として別フィールド・別列へ保存する。件数にウェイトを掛けた値を「人数」や「件数」と表示しない。
- 加重推定には対象cycle、domain、使用ウェイト、層、PSU、標準誤差または信頼区間を伴わせる。非加重件数と加重推定値を同一列へ混在させない。
- Git保存可は、変数の存在・型・欠損・符号・確認済みコード別件数、設計セル数、非加重集計、方針metadataなど個人を復元しない集計に限る。本manifestには個人行、`SEQN`、`SEQN`一覧、個別ウェイト値を保存しない。
- 将来の外部公開候補は、開示と推定信頼性を別途確認した集計済み非加重件数、および不確実性を伴う加重推定値に限る。小標本・不安定推定の具体的抑制基準は本工程で**未確認**であるため、外部公開可とは判定しない。microdata、個別ウェイト、加工済み個人行は保存・公開対象外とする。

## 6. 代表性・一般化範囲

設計どおり分析した単一cycleの推定対象は、NHANES August 2021–August 2023 の調査期間における**米国の civilian noninstitutionalized population**のうち screening interview時点で20歳以上、かつ各身体計測の分析条件を満たすdomainである。`RIAGENDR`別ではその生コードdomainに限定する。施設入所者、米国外人口、別時代、個人への予測、身体計測対象外・欠損者へ自動一般化しない。

2021–2023はパンデミック対応でrace/Hispanic origin・incomeによるperson-level oversamplingを行わず、年齢oversamplingを追加した。特定subgroupは以前より人数が少なく精度低下が見込まれる。2017–March 2020との間には15か月の未観測期間があり、前cycleとの結合・trend推定は本方針の対象外である。80歳以上の `RIDAGEYR` は80へtop-codeされるため、高齢者内の細分化にも一般化しない。

## 7. 停止条件

スクリプトは次のいずれかでmanifestを書かず停止する。

1. 必須ファイル・列がない、`SEQN` が欠損・重複、BMX全examined recordをDEMOへ一対一結合できない。
2. `WTMEC2YR`、`SDMVSTRA`、`SDMVPSU` が非数値、欠損、または `WTMEC2YR <= 0`（examined design内）。
3. `RIAGENDR` が公式確認済みの1/2以外または欠損、`SDMVSTRA` が173–187以外、`SDMVPSU` が1/2以外または欠損。
4. 成人全体件数と `RIAGENDR` 生コード別件数の加算が一致しない。

未知コードを見つけた場合、既知コードへ丸めたり併合せず、対象cycleの公式documentationで意味を再確認する。公式根拠を確認できるまで判断保留とする。

## 8. 不採用案・影響・未確認・再確認条件

### 採用

- `WTMEC2YR` + `SDMVSTRA` + `SDMVPSU`、full examined designからのdomain analysis。
- adult、`RIAGENDR`、項目別QC対象をdomain indicatorで表す。
- 加重推定と非加重件数の明示的分離。

### 不採用

- `WTINT2YR`（身体計測より広いinterview sample用）、equal weight、ウェイト無視、ウェイトだけで層・PSUを無視。
- 成人・生コード・complete case行をdesign作成前に物理削除する方法。
- 欠損/QC後のウェイト再正規化、独自nonresponse調整、ウェイトのwinsorize・scale。
- `RIAGENDR=1/2` の無条件結合、非加重値を母集団推定として表示すること。

### 影響範囲

今後の5項目の記述統計・分位点・分布・許可後の回帰とモデル評価の分析インターフェース、保存schema、停止検査に適用する。既存QC分類、値、ゲート判定、モデル、Webアプリ、胸囲、ANSUR II、公開可否は変更しない。

### 未確認と再確認条件

- 使用するsurvey software、分位点CI法、single-PSU処理、回帰・モデル評価の具体的手法、分割方法、採用閾値は未確定。分析実装前に公式資料とソフトウェア仕様を照合して決定する。
- 項目欠損によるnonresponse biasの大きさ、個別domain推定の精度、外部公開の抑制基準は未確認。加重基礎推定を実施できる工程で評価し、公式NCHS presentation standardを確認する。
- 新cycle、別component、cycle結合、新たなsubsample変数を追加する場合は、最小対象componentのウェイトとcycle固有guidanceを公式資料で再監査する。

## 9. 再実行

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-analysis.txt
.venv/bin/python scripts/download_nhanes_raw.py
.venv/bin/python scripts/summarize_nhanes_survey_design.py
```

同一の公式XPTから生成したmanifestがGit上の正本と完全一致することを確認する。生データはGitへ追加しない。
