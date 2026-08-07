# NHANES 2021–2023 分割後survey評価方式の検証（Bゲート実行5）

## 1. 範囲と結論

本書は、Bゲート実行4のPSU非重複3群**構造診断候補**について、次の二方式を公式資料とR `survey`の実挙動で比較した記録である。

- **A**: 正の`WTMEC2YR`を持つfull examined sampleで15層・30 pseudo-PSUのdesignを定義し、群をdomain/subpopulationとして指定する。
- **B**: 群に含まれる行だけを取り出し、5層・10 pseudo-PSUの別designを物理的に定義する。

**NHANES公式手順に適合する候補はAであり、Bは不採用とする。** NCHSは、subpopulationのTaylor分散には正の分析ウェイトを持つ全観測とdomain indicatorが必要で、解析procedureの前に行を削除してはならないと明記する。BはR上で計算できても、この要件を満たさず、元の標本から10層を除いたものを米国人口に対する新しい確率標本とみなせる公式根拠もない。機械的計算可能性を設計妥当性へ読み替えない。

ただし、**Aを3-way評価方式として正式採用したわけではない**。各群がmasked variance stratumで定義され、元15層中10層にdomain観測がなく、群ごとの自由度が5しかない。NCHS資料は一般的なsubpopulation解析を支持するが、公開pseudo-stratumを学習・検証・封印試験の割当キーにすること、またそのdomain推定を予測性能の母集団推論に使うことを公式に承認してはいない。nested resampling、誤差統計ごとのlinearized variable、精度・提示基準も未決定である。したがってBゲート実行4の結論「構造候補は確認したが3-way方式の正式成立は未決定」、モデル学習停止、5項目の**A可・B保留・C保留**を維持する。

本工程ではモデル、回帰、予測、目的変数の評価、MAE/RMSE値、個人結果を作成していない。

## 2. 公式根拠（2026-08-07確認）

### 2.1 CDC/NCHS

根拠はCDC/NCHS公式の[NHANES Variance Estimation Module](https://wwwn.cdc.gov/nchs/nhanes/tutorials/varianceestimation.aspx)である。

1. NHANESの分散推定にはウェイトだけでなくpseudo-stratum `SDMVSTRA` とpseudo-PSU `SDMVPSU`が必要であり、NCHSはTaylor series linearizationを推奨する。
2. subpopulation/domainの点推定にはdomain内観測だけで足りるが、Taylor分散には分析ウェイトが正の**全観測**とdomain indicatorが必要である。domain人数はPSUごとに標本間で変動するため、先に行削除すると人数を固定として扱い、平均の変動を過小評価し得る。
3. NCHSは解析procedure実行前にrecordをdrop/deleteせず、software固有のsubpopulation/domain機能を使うよう明記する。したがってAを採用候補、Bを不採用とした。
4. 設計自由度は通常`PSU数 − stratum数`で、2年cycle全体は`30 − 15 = 15`。subgroupでは**対象観測を含む**PSU数と層数に基づける。今回の各群は10 PSU・5層なので、CI・検定に用いる候補自由度は5である。
5. softwareはsubgroupで減少した自由度を自動補正しない場合があるため、PSU・層を別途数え、CIへ正しい自由度を渡す必要がある。

NCHS資料は「domainに1件もない層」をエラーにするとは述べていない。対象観測を含む層・PSUでsubgroup自由度を数えるよう指示しており、全designを保持したdomain指定が公式経路である。空domain層は点推定へ寄与せず、今回のR実装では警告なく処理された。ただし、空層を捨てた新しい物理designが妥当になるという意味ではない。

stratum内pseudo-PSUについて、Taylor分散は第一段抽出単位間の変動を使う。今回の候補は保持した各層に2 PSUを残すためsingle/lonely PSUは生じない。一方、層内2 PSUを群に分ける代案は各群にsingle-PSU層を作るので採用しない。NCHSの今回確認した資料はsingle-PSUに対する便宜的分散補正を指定していない。

### 2.2 R `survey`公式仕様

採用候補ソフトウェアの根拠はCRANの[`survey` reference manual](https://cran.r-project.org/package=survey)およびpackage同梱helpである。

- `svydesign(ids=..., strata=..., weights=..., nest=TRUE, data=...)`はTaylor linearization用designを定義する。PSUコード1/2が層間で再利用されるため`nest=TRUE`を明示する。
- `subset()`のsurvey-design methodは、元designの情報を保持してsubpopulationを作る公式package interfaceである。
- `degf()`は通常、第一段cluster数からstratum数を引いたdesign degrees of freedomを返す。ただしNCHSが警告するsubgroup自由度との一致を実データで別途確認する。
- `svymean()`はweighted meanとdesign-based varianceを、`svyquantile()`はsurvey-weighted quantileと対応CIを扱う。今回の分位点テストでは、NCHS式で別計数した群自由度5を`df=5`として明示した。
- `options("survey.lonely.psu")`はsingle-PSU層の処理を制御する。今回はNCHSが特定補正を指定していないため、便宜的な`adjust`、`average`、`remove`、`certainty`を採用せず、`"fail"`で停止させる。

実行版はmanifestに固定記録する。本検証環境ではRと各packageの版を自動取得しているため、別環境で版が変わればmanifest差分として検出する。

## 3. 設計統計と将来の誤差統計に必要な条件

| 統計 | design-based計算の条件 | 本工程で行ったこと |
| --- | --- | --- |
| weighted mean / proportion | full examined design、適切なMEC weight、層、PSU、domain、Taylor分散、subgroup df | 成人indicatorの集計をメモリ内で計算し、値を保存せずSE/CIが有限かだけ保存 |
| weighted quantile | 同じdesignとdomain、`survey`が実装するquantile CI法、正しいsubgroup df | 年齢中央値を動作probeにし、値を保存せずCI作成可否だけ保存 |
| MAE | 許可後に、固定済み予測から`abs(observed-predicted)`をlinearized survey variableとしてdomain内で`svymean`相当に評価 | **未実施**。予測自体を作っていない |
| MSE / RMSE | squared errorのsurvey meanとその設計分散が必要。RMSEのCIには平方根変換を反映するdelta method等を事前固定 | **未確定・未実施** |
| その他の誤差統計 | 統計ごとにTaylor linearization可能性、非滑らか統計のCI法、低自由度での提示可否を公式software仕様から固定 | **未確定** |

ウェイトだけを使う計算、SRSのSE、個人ランダム分割、独自ウェイト調整は代替にならない。欠損/QC後の対象も、許可後はfull designから項目別indicatorを重ねたdomainにする。

## 4. 再現可能な構造テスト

正本は[`check_nhanes_split_survey_evaluation.R`](../scripts/check_nhanes_split_survey_evaluation.R)と[`nhanes_2021_2023_split_survey_evaluation.json`](../data/manifests/nhanes_2021_2023_split_survey_evaluation.json)である。Bゲート実行4と同じく、公開層コード昇順で層全体を3群へ循環割当した。割当の正式採用ではない。

各群についてAとBはいずれも、design作成、`degf()`、weighted meanのSE/CI、weighted quantileのCIが機械的に成立した。各群は5層・10 PSU、空domain層10、single-PSU層0で、`degf()`はA/Bとも5、lonely-PSU warningは0だった。動作probeのweighted meanとSEはA/Bで一致した。この一致は、群が層全体で構成される今回の特殊な候補におけるsoftware挙動であり、Bの公式妥当性を示さない。

manifestは個人行、`SEQN`、割当一覧、estimate、SE、CI、quantileを保存せず、作成可否、有限性、警告、等値性だけを保存する。したがって封印最終試験の性能・予測値・目的変数分布を開封していない。

## 5. 採用・不採用・停止条件

### 採用候補

- 将来survey評価が許可された場合の唯一の候補は、**A: full examined design + split domain**。
- CIではNCHS式で対象観測を含むPSU・層から数えた群自由度5を明示し、software既定値に無条件で依存しない。
- lonely PSUは`fail`とし、発生時に便宜的補正へ自動移行せず停止する。

### 不採用

- **B: 5層・10 PSUの物理部分design**。Rで動くことは採用理由にならず、NCHSのno-delete/domain手順に反する。
- `survey.lonely.psu`の便宜的補正、空層を埋めるpseudo-record、ウェイト再正規化、欠落10層を無視した全米一般化。
- `degf(full)=15`を群CIへそのまま使うこと。NCHSのsubgroup式は今回5を要求する。

### 未確認・停止

- masked variance strataによる3群が予測評価domainとして科学的に妥当か、各群が対象母集団性能を代表できるかは**未確認**。
- 低い自由度5で必要なMAE/RMSE/quantile/coverageを提示可能とする基準、nested resampling法、fold構成、予測区間法は**未確定**。
- これらを公式根拠と用途要件で事前決定できなければ3-way方式は不成立として停止する。
- それまではモデル学習、性能評価、封印最終試験の開封へ進まない。

## 6. 再実行

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-analysis.txt
.venv/bin/python scripts/download_nhanes_raw.py
Rscript scripts/check_nhanes_split_survey_evaluation.R
```

公式XPTからmanifestが完全一致すること、R/package版、3群すべての構造・自由度・警告・計算可否、禁止出力falseを確認する。

## 7. Bゲート実行6による正式判断

Bゲート実行6で、AがR/NCHSのdomain実装候補であることと、固定3-wayが科学的評価設計として妥当であることを区別し、固定3-way方式を不採用（判定C）とした。df=5の計算可否は採用根拠とせず、このsplitで性能評価を実行しない。現行判断、代替候補、封印・停止条件は [`NHANES_EVALUATION_DESIGN_DECISION_2021_2023.md`](NHANES_EVALUATION_DESIGN_DECISION_2021_2023.md) を正本とする。
