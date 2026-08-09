# NHANES 2021–2023 development内モデル選択・内部評価方式の設計監査（Bゲート実行9・追加検証）

## 1. 範囲、非実施事項、再判定

本書は、第0.1版のウエスト `BMXWAIST`・ヒップ `BMXHIP` 課題について、NHANES August 2021–August 2023のdevelopment内だけでモデル、入力セット、前処理、変数およびhyperparameterを比較・選択する方式を監査する正本である。前提は、full examined sampleで `WTMEC2YR`、`SDMVSTRA`、`SDMVPSU` を指定し、成人、生 `RIAGENDR` code、項目別QC対象をdomain/subpopulationとする15 strata・30 pseudo-PSUのdesignである。

初回監査はreplicate weightsを分散推定用途だけと捉え、内部validationへの読み替えに根拠がないとして判定Cとした。しかし、R `survey` の現行公式manualには **`withCrossval`: “Crossvalidation using replicate weights”** があり、essentially zero replicate weightのclusterをtest、残りをtrainingとしてfitする専用interfaceを明記する。この仕様に照らすと、一律の不採用理由は誤りであるため撤回する。

**追加検証後の最終判定は B「replicate-weight cross-validationは有力候補だが、実行環境・実装・一次方法論・loss集約を追加検証するまで正式採用しない」**とする。`withCrossval`＋JKnは15×2 stratified designでも各replicateで1 PSUをtestにできるため、従来の固定foldをTaylor designとして別々に評価する問題とは異なる。BRRも2 PSU/stratumという構造に適合し得る。一方、現在の実行環境では利用可能なR/surveyを正常に構成できず、現行実装の実行確認、引用一次方法論、domainの実挙動、MAE/RMSEと候補差の推論、完全なpipeline nestingを確認できていない。計算可能性を推測してAにしない。

この監査ではNHANESデータを読み込まず、モデル学習、係数推定、予測、目的値・分布・性能の閲覧または算出を行っていない。NHANES 2017–March 2020候補は開封していない。生データ、個人値、`SEQN`または一覧、split/replicate assignmentも保存していない。5項目のA可・B保留・C保留、最終試験候補の「条件付き・正式未採用」は変更しない。

## 2. NCHS根拠とsurvey側根拠を分けた評価

### 2.1 CDC/NCHS公式資料から確認できること

1. [NHANES Variance Estimation Module](https://wwwn.cdc.gov/nchs/nhanes/tutorials/varianceestimation.aspx) は、公開用masked variance stratum・PSU、適切なweight、Taylor linearizationを用い、subpopulationを解析前に物理削除せず全標本とdomain indicatorをprocedureへ渡すよう示す。
2. [DEMO_L documentation](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/DEMO_L.htm) は `WTMEC2YR`、`SDMVSTRA`、`SDMVPSU` の役割と、このcycleが15 masked strata・30 masked PSU（各stratum 2 PSU）を持つことを示す。
3. [NHANES Weighting Module](https://wwwn.cdc.gov/nchs/nhanes/tutorials/weighting.aspx) は、weightが選択確率、非回答およびpost-stratificationを反映することと、最小の分析対象componentに対応するweightを選ぶことを示す。

NCHS資料には公開masked variance unitsを予測CVに使用する明示的な禁止を確認できない。一方、`withCrossval`、JKn/BRRによるモデル選択、候補差、選択後optimismをNHANES向けに承認する記述も確認できない。**NCHS専用手順がないことだけを不採用理由にはせず**、weight・masked design・domain・一般化に関するNCHSの制約と、replicate-weight CVの方法論的妥当性を別々に審査する。

### 2.2 R survey公式仕様から確認できること

R [`survey` reference manual](https://cran.r-project.org/package=survey) の `withCrossval`、`as.svrepdesign`、`svrepdesign`、`weights.svyrep.design` を対象とする。

- `withCrossval` はreplicate weightごとにessentially zero weightのclusterをtest set、それ以外をtraining setとして、training用functionとprediction用functionを呼び出す専用interfaceである。JK1/JKnはcluster-level cross-validationに非常に近く、bootstrap replicate weightsはcross-validation用bootstrapに類似すると公式説明にある。よって「replicate weightsはvalidationへ使う仕様がない」という初回記述は撤回する。
- `as.svrepdesign()` はstratified designにJKnを使用できる。JKnでは各stratum内のPSUを順にdeleteするreplicateが候補となり、15×2なら30 replicateが想定される。各replicateのtestは削除された1 PSU、trainingは残り29 PSUであり、同一replicate内で同じPSUが両方へ跨がる構造ではない。
- BRRは原則として各stratumに2 PSUを持つdesignを対象とする。各replicateでは各stratumの一方がessentially zeroとなるため、test 15 PSU・training 15 PSUのhalf-sample型になる。JKnとBRRでtest setとtraining setの大きさ、学習安定性、loss集約は異なり、同じ方式として混ぜない。
- bootstrapではzero-weightになるPSU数がreplicateごとに一定とは限らない。空または過小な課題×生code×QC domain、全PSUが正weightでtestがないreplicate、同じPSUの複数回選択を停止検査する必要がある。

公式manualが引用する一次方法論の正確な書誌、前提、選択誤差の推論範囲と現行function実装本文は、今回のネットワーク制限により独立取得できず**未確認**である。manual要約だけを一次方法論確認済みと表示しない。

## 3. 実行環境と再現検査の状態

2026-08-09に開始時環境を確認したところ、`R` と `Rscript` は存在せず、したがってinstalled `survey` versionと `withCrossval` の存在は **該当なし（package未導入）** だった。Ubuntu package candidateはR 4.3.3、`r-cran-survey` 4.2-1であるが、CRAN現行版とは限らず、4.2-1に`withCrossval`があることも確認できていない。導入を試みたが外部package取得はHTTP 403で完了しなかった。途中取得物・OS packageは成果物へ含めない。

現行CRAN版への更新・導入は**候補**に留め、repositoryの依存版を勝手に変更しない。正式検査ではR本体、`survey` version、`packageDescription("survey")`、`exists("withCrossval", asNamespace("survey"), inherits=FALSE)`、`formals()`、package同梱help、function body、引用文献を同一環境で保存する。

[`check_survey_crossval_structure.R`](../scripts/check_survey_crossval_structure.R) を、NHANESの目的値を使わない15 strata×2 PSU toy designの構造検査として追加した。これは次をfail-closedで検査するが、現環境ではR/survey不在のため**未実行**であり、出力manifestも作成しない。

1. R・survey versionと`withCrossval`の存在。
2. JKn/BRR replicate weight matrixでPSU内weightが一様であること。
3. JKnの各replicateがtest 1 PSU・training 29 PSU、BRRがtest 15 PSU・training 15 PSUとなり、同じPSUが両方へ跨がらないこと。
4. replicate数、`degf()`、scale/rscales、zero判定閾値だけを集計し、行、ID、目的値、予測、lossを保存しないこと。

## 4. lonely PSU、domain、weight、dfの再監査

`withCrossval`でJKnのtest側が1 PSUである事実は残る。しかし、この1 PSUを独立したTaylor-linearization survey designとして評価し、そのfold固有SEを求める方式ではない。replicate-weight CVは、replicate schemeが順に除いたclusterへの予測を作り、それらを元のsampling weightおよびreplicate構造に沿って集約する考え方である。このため、従来の「test foldがlonely PSUだから直ちに計算不能」という反論はそのまま適用できず、`survey.lonely.psu`補正でtest foldを救済する必要もない。

ただし、次は未解決である。

- full examined sampleからreplicate designを作成してからadult、生code、課題別QCをdomain化する順序を維持できるか、`withCrossval`内のtraining/prediction functionへdomain外行をどう渡すかを実装で確認していない。先に物理削除しない。
- `WTMEC2YR`をsampling weightsとして保持し、training fitとtest lossの両方へどのweightが渡るか、replicate weightsのzero tolerance、Fay係数、scale/rscalesを確認していない。独自再正規化はしない。
- `degf(repdesign)`はreplicate weight matrixのrankに基づく推論自由度であり、個々のtest setの `#PSU-#strata` ではない。通常Taylor foldのdfを流用しない一方、候補差や最終loss CIへどのdfを用いるかは未決定である。
- domain内でtest対象が0件となるreplicate、training内で入力が定数・欠損となるreplicate、fit失敗の扱いを全課題×生code×入力セットについて目的値非閲覧で検査していない。

## 5. preprocessing、候補選択、loss

`withCrossval`がtraining用functionとprediction用functionを反復呼出しできることは、任意pipelineが自動的に漏洩安全になることを意味しない。正式候補化には次を満たすwrapperのtoy testが必要である。

- imputationのfit、scaling、変換、特徴生成、変数選択、hyperparameter tuning、early stopping、baselineの加重中央値を各replicateのtraining clusterだけから作る。
- test目的値をtraining function、inner tuning、候補追加、探索範囲、停止規則へ渡さない。hyperparameterも選ぶ場合は、outer replicateと独立性を保つinner design-aware選択を構成できるか、または候補gridを外部根拠で固定してouter lossだけで単一候補を選ぶ手順を事前決定する。
- `withCrossval`の戻り値が、全観測に対するout-of-replicate predictionなのか、replicate別prediction/lossなのかを現行実装で確認し、同じ観測の反復利用と依存を無視しない。

MAEは各test predictionから `abs(observed-predicted)` を作り、元のsampling weightで母平均lossを集約できる可能性がある。MSEも同様だが、RMSEの平方根変換、SE/CI、候補間MAE/RMSE差、複数候補から最小を選んだ後のoptimismについて、`withCrossval`が直接保証する範囲は未確認である。absolute/squared lossを渡せるという計算可能性だけで、正式な候補比較法・CI法とはしない。分位点loss、coverage、課題×生codeの全必須指標も別途確認する。

## 6. 候補方式の再比較

| 候補 | 再監査結果 | 判定 |
| --- | --- | --- |
| 個人random split / 通常K-fold | cluster相関・層化を無視し同一PSUを跨がせる | **不採用** |
| 固定PSU half-sample / repeated splitをTaylor foldとして評価 | foldごとのlonely PSU、反復依存、固定3-way再導入の問題が残る | **不採用** |
| stratum単位grouped K-fold | 一部strataしかない標本を全母集団評価へ一般化できない | **不採用** |
| `withCrossval`＋JKn | 公式にcluster-level CVに近い。全体replicate構造でlossを集約するためTaylor lonely-PSU foldとは異なる。15×2でPSU非跨ぎの可能性が高い | **有力候補・追加検証** |
| `withCrossval`＋BRR | 2 PSU/stratumへ構造的に適合し、全strataから一方ずつtestにする | **候補・JKnとの差と学習安定性を追加検証** |
| `withCrossval`＋bootstrap | CV bootstrapに類似する公式説明はあるが、zero cluster数、空domain、重複、方式別weightが未確認 | **候補・追加検証** |
| full-development AIC等 | out-of-sample lossや任意algorithmの共通比較ではない | **今回の代替には不採用** |
| 内部選択なし・外部根拠で単一仕様固定 | leakageを避ける別計画だが根拠・仕様未確定 | **別案として未決定** |

## 7. 正式採否、禁止事項、停止条件

### 7.1 第0.1版の正式採否

判定Bであり、**正式採用方式はまだない**。JKnを第一検証候補、BRRとbootstrap系を比較候補とするが、fold数、replicate数、zero tolerance、Fay係数、seed、df、loss/候補差のCI、model、入力またはhyperparameterを仮決めしない。モデル学習へ進まない。

### 7.2 禁止事項

- replicate-weight CV全体を、通常Taylor foldのlonely PSUだけを理由に一律不採用にすること。
- 逆に、`withCrossval`が存在する、またはtoyで動くことだけを正式採用の根拠にすること。
- 個人random split、通常K-fold、strata/PSU無視、同一PSUの同一replicate内training/test跨ぎ、固定3-wayの再導入。
- package version・function body・引用方法論を確認せず、JKn、BRR、bootstrapを同じものとして扱うこと。
- domain行の事前削除、weight再正規化、test foldのTaylor df流用、lonely PSU便宜補正。
- resampling前に全developmentの目的値を使って前処理、変数選択、hyperparameter、baselineまたは停止規則をfitすること。
- 2017–March 2020の目的値・分布・性能を閲覧し、方式選択、閾値または採否へ使うこと。
- 生データ、個人値、`SEQN`一覧、個人のreplicate割当、予測または係数を成果物へ保存すること。

### 7.3 AまたはCへ進む前の停止条件

次を全て結果閲覧前に確認するまでBで停止する。

1. 承認された隔離環境へ現行R/surveyを版固定して導入し、`withCrossval`のhelp、source、引用一次方法論を独立照合する。既存環境を無断更新しない。
2. toy 15×2 designで付属scriptを実行し、JKn/BRRのreplicate数、zero cluster、PSU非跨ぎ、sampling/replicate weight、`degf`を確認する。bootstrapも方式を特定して別検査する。
3. full examined design＋domainの順序、空domain、fit失敗、zero tolerance、scale/rscalesをfail-closedで検査する。
4. preprocessing・feature selection・hyperparameter tuningをtrainingだけに閉じ込めるwrapperと、nested選択または事前固定gridのどちらを使うかをtoy testで固定する。
5. MAE、MSE/RMSE、候補差、選択後optimism、CI/df、tie rule、全必須domain、software failureの事前規則を一次方法論と実装で承認する。
6. 独立最終試験候補の封印、一回評価、数値閾値、同一人物非重複の扱い、利用条件を別途解決する。development方式の承認だけで最終試験を開封しない。

以上が成立すればAへの変更を改めて判断する。理論または実装が成立しない、全必須domainでPSU非跨ぎ・loss集約を保証できない場合はCを判断する。本追加監査だけでデータ採用ゲートB/Cを変更しない。
