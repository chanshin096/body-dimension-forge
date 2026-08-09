# NHANES 2021–2023 development内モデル選択・内部評価方式の設計監査（Bゲート実行9）

## 1. 範囲、非実施事項、判定

本書は、第0.1版のウエスト `BMXWAIST`・ヒップ `BMXHIP` 課題について、NHANES August 2021–August 2023のdevelopment内だけでモデル、入力セット、前処理、変数およびhyperparameterを比較・選択する方式を監査する正本である。前提は、full examined sampleで `WTMEC2YR`、`SDMVSTRA`、`SDMVPSU` を指定し、成人、生 `RIAGENDR` code、項目別QC対象をdomain/subpopulationとする15 strata・30 pseudo-PSUのdesignである。

**最終判定は C「第0.1版で正式採用できるdevelopment内選択・内部評価方式はないため停止」**とする。これは「方式が永久に存在しない」という判定ではなく、公開masked designが各stratum原則2 PSUしか持たない条件で、候補選択の情報漏洩を防ぎ、対象母集団性能のdesign-based内部評価を成立させる方式について、NCHS公式根拠と使用software仕様を今回確認できなかったという判定である。名称だけのdesign-aware CVやsurvey bootstrapを採用しない。

この監査ではデータを読み込まず、モデル学習、係数推定、予測、目的値・分布・性能の閲覧または算出を行っていない。NHANES 2017–March 2020候補は開封せず、その目的値、分布、性能を参照していない。生データ、個人値、`SEQN`または一覧、split/replicate assignmentも保存していない。5項目のA可・B保留・C保留、最終試験候補の「条件付き・正式未採用」は変更しない。

## 2. 確認した公式根拠と根拠の限界

2026-08-07時点で次を確認対象とした。

1. [NHANES Variance Estimation Module](https://wwwn.cdc.gov/nchs/nhanes/tutorials/varianceestimation.aspx) は、公開用masked variance stratum・PSU、適切なweight、Taylor linearizationを用い、subpopulationを解析前に物理削除せず全標本とdomain indicatorをprocedureへ渡すよう示す。
2. [DEMO_L documentation](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/DEMO_L.htm) は `WTMEC2YR`、`SDMVSTRA`、`SDMVPSU` の役割と、このcycleが15 masked strata・30 masked PSU（各stratum 2 PSU）を持つことを示す。
3. [NHANES Weighting Module](https://wwwn.cdc.gov/nchs/nhanes/tutorials/weighting.aspx) は、weightが選択確率、非回答およびpost-stratificationを反映することと、最小の分析対象componentに対応するweightを選ぶことを示す。
4. R [`survey` reference manual](https://cran.r-project.org/package=survey) の `svydesign`、`subset.survey.design`、`as.svrepdesign`、`bootweights`、`withReplicates` の仕様を調査対象とした。同packageはTaylor design、domain subset、BRR/JKn/bootstrap等のreplicate designとreplicate統計を実装する。一方、その仕様は、NHANESの公開masked PSUをtraining/validationへ割り当てること、候補モデルのout-of-sample errorを推定すること、または前処理を含むnested model selectionを正当化するNHANES専用手順ではない。

NCHS資料で確認できるのは、主として母集団記述量・回帰等のdesign-based推定と分散推定である。今回必要な「同一development内で学習を反復し、未使用観測へ予測して、多数候補を選ぶ」手順、masked PSU用fold構成、候補差の不確実性、選択後のoptimismについて、NCHSが承認する公式手順は確認できなかった。replicate-weight法は標本分散推定法であり、replicateをそのままvalidation foldと呼べるという根拠にはならない。この区別を推測で埋めない。

## 3. 成立条件

正式候補には少なくとも次を同時に要求する。

- full examined designを保持し、成人・生code・QC complete caseは物理削除でなくdomainとする。配布weightを変更・再正規化しない。
- resamplingの単位は個人でなく `(SDMVSTRA, SDMVPSU)` とし、同じPSUの人をtrainingとvalidationへ跨がせない。公開PSU番号はstratum内で解釈する。
- validation側で対象母集団性能とその不確実性を称するなら、全15 strataを扱い、各寄与stratumでPSU間変動を推定できることを事前に示す。lonely PSUの便宜補正、full-design df=15の流用、空層のpseudo-record補完はしない。
- imputation、scaling、変換、QCの候補処理、変数選択、hyperparameter tuning、baseline目的値要約は、各反復のtraining部分だけでfitする。validation目的値を前処理・停止・候補追加・閾値変更へ使わない。
- 課題×生codeごとに候補集合、主順位、tie rule、全反復、乱数seed、失敗時処理、候補差の推定・CI法、softwareと版を結果閲覧前に固定する。反復を独立標本数として扱わない。
- developmentで単一候補を固定した後だけfull developmentで一度refitし、独立最終試験候補を承認済み手順で一度だけ使う。最終試験結果からdevelopment方式や候補を選び直さない。

## 4. 候補方式の比較

| 候補 | 長所・成立し得る点 | このdesignでの問題 | 判定 |
| --- | --- | --- | --- |
| 個人random split / 通常K-fold | 実装は容易 | 同一PSUを両側へ跨がせ、層化・cluster相関を無視する。通常の独立同分布foldの根拠がなく、full design/domain原則にも適合しない | **不採用** |
| 層内で一方のPSUをvalidation、他方をtrainingにするbalanced half-sample / 2-fold | 全strataを両側へ含め、PSU非重複にできる | 各側は1 PSU/stratumとなり全15 strataがlonely PSUになる。片側だけから層内PSU間分散を推定できない。対になるhalf-sampleをreplicate varianceに使うことと、片側を代表的validation sampleとして扱うことは別である | **不採用** |
| 上記half-sampleの向きを反復するrepeated split / repeated CV | PSUごとの評価機会を増やせる可能性 | 30 PSUしかなく同じPSUと目的値を繰返し選択に使う。反復しても各foldのlonely PSUとdesign df問題は消えず、反復間相関、候補選択optimism、CI法の公式根拠もない | **不採用** |
| stratum単位grouped K-fold / leave-strata-out | 保持stratumでは2 PSUを一緒に保てる | validationは一部strataだけとなり、公開weightが校正された全母集団の確率標本とは確認できない。欠落strata、低い `#PSU-#strata`、下位domainを伴い、Bゲート実行6で不採用の固定3-way問題をfold名で復活させる | **不採用** |
| PSU cluster bootstrapのin-bag/OOB評価 | cluster相関を意識し、反復学習を構成できる可能性 | PSUを復元抽出すると、2 PSU/stratumではOOB側が0、1または2 PSUとなり、空/lonely strataが生じる。OOB weight、母集団性能、候補比較、domain、dfのNHANES公式手順を確認できない | **不採用** |
| Rao–Wu等のsurvey bootstrap / BRR / jackknife replicate weights | strata・PSUに基づく標本分散推定を実装できる。将来、固定済み統計の分散検討候補にはなり得る | replicate weightsは同一標本からのvariance estimation用で、非zero weight観測をtraining、zero/downweighted観測をvalidationと読み替える仕様ではない。`as.svrepdesign`が計算可能でも、前処理を含むout-of-sample model selectionの妥当性は証明しない。NCHS提供replicate weightsも本cycleに確認していない | **内部評価として不採用**（固定済み最終統計の分散法としても未決定） |
| full-development survey-weighted fit＋AIC等のdesign-based model comparison | designを物理分割せず、対応する限定的なsurvey regressionならfull designを維持できる | out-of-sample予測評価ではなく、任意の前処理・入力セット・algorithm・hyperparameterを共通尺度で比較できない。選択後optimismやMAE/RMSEを直接扱わず、対応モデルとsoftware定義も未固定 | **今回の代替には不採用** |
| 候補を外部根拠だけで一つに事前固定し、内部選択なしでfull development fit | data-driven selection leakageを避け、designを切断しない | 今回求める複数候補の内部比較を実施しない別計画である。候補固定の外部根拠、前処理、hyperparameter、最終評価規則が未確定 | **別案として未決定** |

15×2という構造では、「両側に全strataを残す」と「各側で2 PSU/stratumを残す」と「PSU非重複」を同時に満たせない。bootstrapという名称、反復回数の増加、lonely PSU optionの変更は、存在しないPSU間情報を追加しない。したがって計算可能性を科学的採用根拠にしない。

## 5. 情報漏洩と選択手順の監査

同じdevelopmentを使うこと自体は、独立最終試験を一度だけ使う方針と矛盾しない。しかし、内部評価方式が成立した場合でも、最終的に選ぶ全てをresampling loopへ入れる必要がある。

- **各training内だけ**: 欠損処理のfit、標準化、変換、特徴生成、変数選択、hyperparameter探索、早期停止、baselineの加重中央値。
- **validationだけ**: 事前固定した候補の予測誤差を一回生成する用途。validation目的値を見て候補集合、前処理、入力、探索範囲、反復数、seed、指標、CI、domainを変更しない。
- **全development refit**: 選択規則で単一候補を確定した後だけ、固定済みpipelineを全developmentへfitする。これは内部性能の新しい推定ではない。
- **独立最終試験**: データ受入、封印、指標・CI・数値閾値を別途承認後、単一候補を一度だけ評価する。不合格後の再選択・再試験は禁止する。

通常CVの内側loopを追加しても、外側foldのdesignが成立しない問題を解消しない。逆に、全developmentで変数やhyperparameterを選んでから同じデータをcross-validationする手順は選択情報をvalidationへ漏らすため不採用である。

## 6. 正式採否、禁止事項、停止条件

### 6.1 第0.1版の正式採否

正式採用方式は**なし**。よってfold数、bootstrap種別、replicate数、seed、lonely PSU処理、df、比較CI、モデル候補、入力候補またはhyperparameterを仮決めしない。固定3-wayを復活させず、モデル学習へ進まない。

### 6.2 禁止事項

- 個人random split、通常K-fold、strata/PSUを無視するresampling、同一PSUのtraining/validation跨ぎ。
- 1 PSU/stratumのfoldをlonely PSU補正で救済すること、foldのdfへfull designの15を流用すること。
- 一部strata foldを全米成人の独立確率標本と表示すること、固定3-wayをrepeated/grouped CVとして再導入すること。
- replicate weightsを根拠なしにvalidation foldまたは独立データと読み替えること。
- resampling前に全developmentの目的値を使って前処理、変数選択、hyperparameter範囲、baselineまたは停止規則をfitすること。
- 2017–March 2020の目的値・分布・性能を閲覧し、方式選択、閾値、候補数または採否判断へ使うこと。
- 生データ、個人値、`SEQN`一覧、個人のfold/replicate割当、予測または係数を成果物へ保存すること。

### 6.3 次工程へ進むための確認事項

次工程もモデル学習ではない。次のいずれかについて、人間がモデル実行前の独立判断として承認するまで停止する。

1. **内部方式を再検討する場合**: NCHSまたは同等に権威ある一次方法論が、公開masked 15×2 design、full-sample domain、候補選択を同時に扱う具体的方法を示すこと。fold/replicateの作り方、training/validation weight、全必須domain、lonely/empty strata、design df、候補差・選択後optimism、CI、反復依存、software版をtoy dataで目的値非閲覧検証し、結果を見る前に固定する。
2. **内部選択を行わない案へ変更する場合**: モデル族、入力、前処理、hyperparameterを外部根拠だけで単一仕様に固定する理由と、不採用候補を記録し、「内部評価なし」という限界を明示した新しい事前計画を承認する。今回の監査だけでその仕様を作らない。
3. いずれの場合も、独立最終試験候補について残る封印、一回評価、指標別design-based CI、数値閾値、同一人物非重複の扱い、利用条件を別途解決する。development方式の承認だけで最終試験を開封しない。

必要根拠が得られなければ本判定Cを維持し、Bゲートは保留のまま停止する。将来方式が承認されても、この監査だけでデータ採用ゲートB/Cを変更しない。
