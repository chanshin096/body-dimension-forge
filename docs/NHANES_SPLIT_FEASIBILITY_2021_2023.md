# NHANES 2021–2023 PSU非重複分割の実現性確認（Bゲート実行4）

## 1. 範囲と結論

本書は、[`NHANES_PREDICTION_EVALUATION_PLAN_2021_2023.md`](NHANES_PREDICTION_EVALUATION_PLAN_2021_2023.md) のPSU非重複3群分割を、公式 `BMX_L.xpt` と `DEMO_L.xpt` の集計構造で検査した記録である。モデル、回帰、係数、予測、ベースラインは計算していない。個人値、`SEQN` 一覧、個人別割当も保存していない。

**結論は「構造候補を1件確認したが、3-way方式の正式な成立判定は未決定」であり、モデル学習へ進んではならない。** 診断候補はPSU非重複、全PSUの一意割当、全課題・生コード・入力セットで正のcomplete case件数、各群5層×2 PSUを満たした。一方、分割後のdesign-based分散をどのdesign/domain定義で算出するか、欠落する10層の扱い、nested resampling、single-PSU処理を公式根拠とソフトウェア検証で確定していない。候補確認は方式採用、B通過または最終試験開封を意味しない。

## 2. データと検査方法

- 既存の [`download_nhanes_raw.py`](../scripts/download_nhanes_raw.py) でCDC/NCHS公式配布元から取得し、Git対象外の `data/raw/nhanes/2021-2023/` だけに保存した。
- `SEQN` の欠損・重複が双方で0であることを先に検査し、inner one-to-one結合を行った。BMXの8,860 examined recordsがすべて一対一結合された。
- 分割母集団は課題、成人domain、生コード、QC complete caseの作成前に、full examined designの `SDMVSTRA` と `SDMVPSU` の組で固定した。
- QC「使用可能」は [`NHANES_MISSING_QC_POLICY_2021_2023.md`](NHANES_MISSING_QC_POLICY_2021_2023.md) の既決定規則をそのまま再実装した。補完、値変更、再計算、外れ値除外はない。
- 再実行手順と全PSU別集計の正本は [`check_nhanes_split_feasibility.py`](../scripts/check_nhanes_split_feasibility.py) と [`nhanes_2021_2023_split_feasibility.json`](../data/manifests/nhanes_2021_2023_split_feasibility.json) である。

## 3. full examined design

| examined件数 | 層数 | 層ごとのpseudo-PSU数 | pseudo-PSU総数 | 構造自由度（PSU−層） |
| ---: | ---: | --- | ---: | ---: |
| 8,860 | 15 | 全15層で2 | 30 | 15 |

各pseudo-PSUの非加重件数、成人件数、生コード1/2別件数、課題×4入力セットのcomplete case件数はmanifestの `pseudo_psu_aggregate_counts` に集約した。pseudo-PSUのexamined件数は206～410、成人件数は113～301であり、全30 PSUの成人生コード1/2はいずれも正の件数だった。この範囲を性能や目的値を見た選択には使用していない。

## 4. 構造診断候補

存在確認だけのため、公開層コードを昇順に並べ、**層を分割せず**3群へ循環割当する決定的候補を検査した。層内2 PSUを異なる群へ分ける案は、物理部分標本でsingle-PSU層を作るため不採用とした。この候補の目標比率は未設定、seedは未使用であり、正式採用候補の選定ではない。

| 診断群 | examined | 成人 | 生コード1 | 生コード2 | 保持層 | 保持PSU | PSU−層 | single-PSU層 | 欠落層 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 学習役割 | 2,961 | 2,000 | 876 | 1,124 | 5 | 10 | 5 | 0 | 10 |
| 検証役割 | 2,858 | 1,969 | 881 | 1,088 | 5 | 10 | 5 | 0 | 10 |
| 封印最終試験役割 | 3,041 | 2,095 | 963 | 1,132 | 5 | 10 | 5 | 0 | 10 |

全30 pseudo-PSUは過不足なくちょうど1群へ属し、pseudo-PSU重複0、未割当0、個人の群跨ぎ0だった。個人別割当表は作成・保存していない。

### 4.1 QC「使用可能」complete case

この実データでは各課題内で4入力セットの件数が一致したが、一般則とは扱わない。

| 課題 | 診断群 | 4入力セット各々の全体 | 生コード1 | 生コード2 |
| --- | --- | ---: | ---: | ---: |
| ウエスト | 学習役割 | 1,810 | 797 | 1,013 |
| ウエスト | 検証役割 | 1,844 | 827 | 1,017 |
| ウエスト | 封印最終試験役割 | 1,934 | 895 | 1,039 |
| ヒップ | 学習役割 | 1,804 | 794 | 1,010 |
| ヒップ | 検証役割 | 1,840 | 825 | 1,015 |
| ヒップ | 封印最終試験役割 | 1,933 | 893 | 1,040 |

この表は目的値・予測値・性能指標を含まず、指定された可用件数だけである。最終試験役割の性能や分布を実質的に開封していない。

## 5. 成立条件、弱点、不成立条件

### 確認できた成立条件

1. pseudo-PSU単位なら全行を一意に3群へ割り当てられる。
2. 層を丸ごと割り当てる候補では、各保持層に2 PSUが残り、single-PSU層は0となる。
3. 3群すべてにウエスト、ヒップ、生コード1/2、4入力セットのQC complete caseが残る。
4. 各群の構造値 `PSU−strata` は5と算出できる。

### 候補の制約と弱点

- 各群は元の15層のうち10層を欠く。各群を物理的な独立survey designとすることがNCHSのdomain方針と整合するかは未確認である。
- full examined designを維持して群をdomain indicatorにする場合、群内観測が0の層・PSUを含む分散計算の挙動と自由度の定義を候補ソフトで未検証である。
- 名目自由度5で各課題・生コード・年齢帯・foldのSE/CIが安定・算出可能かは件数だけでは決定できない。
- この単一候補は比率やバランスの最適性を示さない。結果を見たseed・比率・fold選択は実施していない。
- nested grouped resamplingで外側・内側foldにも2 PSU/保持層を保てるかは未検査である。

### 不成立となる条件

- 3群それぞれに**元の全15層かつ層内2 PSU**を物理的に要求するなら、各層には2 PSUしかないため不成立である。
- 層内の2 PSUを複数群へ分け、各群の物理部分標本だけでdesignを作るならsingle-PSU層または層欠落が生じる。
- 公式guidanceまたは採用ソフトが、5完全層候補やfull-design domain評価を許容しない、SE/CIを再現できない、または必須domainを評価不能とする場合は不成立である。

## 6. 未確認事項と次の人間判断

1. R `survey` 等の版を固定し、full design＋split domainと物理部分標本のどちらが公式guidanceに適合するかを確認する。
2. 空domain層、single-PSU、自由度、CI、weighted quantileを含む分散法を正式決定する。便宜的設定を置かない。
3. nested resamplingのfold数、群比率、割当アルゴリズム、バランス制約を性能結果を見る前に人間が承認する。
4. 名目自由度5と必須の生コード・年齢domainで評価可能性を満たす最小条件を公式手法と用途要件から決める。
5. 診断候補を採用するか、別候補を事前規則で比較するか、または3-way計画を不成立とするかを決める。

以上が決まるまで3-way分割は**未決定**、B/Cは**保留**のままであり、モデル学習へ進んではならない。

## 7. 再実行

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements-analysis.txt
.venv/bin/python scripts/download_nhanes_raw.py
.venv/bin/python scripts/check_nhanes_split_feasibility.py
```

同じ公式XPTから生成したmanifestがGit上の正本と完全一致することを確認する。生データはGitへ追加しない。
