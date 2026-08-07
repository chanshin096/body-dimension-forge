# NHANES 2017–March 2020 独立最終試験候補の受入・構造・測定互換性監査（Bゲート実行8）

## 1. 範囲と判定

2026-08-07に、CDC/NCHS公式配布物 `P_BMX` と `P_DEMO` を、成人 `RIDAGEYR >= 20` の第0.1版ウエスト `BMXWAIST`・ヒップ `BMXHIP` 独立最終試験**候補**として監査した。性能、目的値の値・分布、個人値、`SEQN`一覧は閲覧・出力・保存していない。

**判定は B「条件付きで成立するが未解決事項あり」**とする。必須列、cycle内一意結合、成人および生 `RIAGENDR` code domainのdesign寄与、2017/2019–2020/2021の測定構成概念は成立する。一方、cycle間同一人物ゼロは公式確認できず、封印方式・一回評価規則・評価指標・採否閾値、development内design-aware選択法、Cゲートの最終利用許諾は未確定である。正式採用、封印済み、最終試験実施可能、B/C通過とはしない。Bゲート実行6・7の「両方が事前承認されるまでモデル学習へ進まない」を維持する。

## 2. 公式生データの受入

公式取得元は [P_BMX XPT](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/P_BMX.xpt) と [P_DEMO XPT](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/P_DEMO.xpt)、codebookは [P_BMX documentation](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/P_BMX.htm) と [P_DEMO documentation](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/P_DEMO.htm) である。取得物は `data/raw/`（Git除外）だけに置いた。

| ファイル | 取得日時（UTC） | bytes | SHA-256 | 行×列 | XPT読込 | `SEQN` |
| --- | --- | ---: | --- | ---: | --- | --- |
| `P_BMX.xpt` | 2026-08-07T15:10:09.078515+00:00 | 2,520,640 | `7038d0da3169420a4a3cbaec09ac586a701b38e1c7b925431b60e13ac24fed66` | 14,300×22 | 正常 | 欠損0、重複行0、一意14,300 |
| `P_DEMO.xpt` | 2026-08-07T15:10:09.762515+00:00 | 3,614,720 | `2e46c6c26bf77cd8989f64011ace12cbf42c0f3e03414eb59acc5328c8f87913` | 15,560×29 | 正常 | 欠損0、重複行0、一意15,560 |

全列名・型はmanifestに保存した。`P_BMX`: `SEQN, BMDSTATS, BMXWT, BMIWT, BMXRECUM, BMIRECUM, BMXHEAD, BMIHEAD, BMXHT, BMIHT, BMXBMI, BMDBMIC, BMXLEG, BMILEG, BMXARML, BMIARML, BMXARMC, BMIARMC, BMXWAIST, BMIWAIST, BMXHIP, BMIHIP`。`P_DEMO`: `SEQN, SDDSRVYR, RIDSTATR, RIAGENDR, RIDAGEYR, RIDAGEMN, RIDRETH1, RIDRETH3, RIDEXMON, DMDBORN4, DMDYRUSZ, DMDEDUC2, DMDMARTZ, RIDEXPRG, SIALANG, SIAPROXY, SIAINTRP, FIALANG, FIAPROXY, FIAINTRP, MIALANG, MIAPROXY, MIAINTRP, AIALANGA, WTINTPRP, WTMECPRP, SDMVPSU, SDMVSTRA, INDFMPIR`。

one-to-one inner joinは14,300行、`P_BMX`のみ0、`P_DEMO`のみ1,260であり、body-measure参加者にdemographicsを結合できる。これは結合安全性の検査であり、`SEQN`値自体は保存していない。

## 3. 必須変数と公式コード

必須10変数は実データに全て存在した。`RIDAGEYR`はscreening時の年齢、`RIAGENDR`は公式の生コード（1 Male、2 Female）、`BMXHT`はstanding height (cm)、`BMXWT`はweight (kg)、`BMXBMI`はweight kg / height m²、`BMXWAIST`・`BMXHIP`は各circumference (cm) である。`WTMECPRP`は統合pre-pandemic MEC examination weight、`SDMVSTRA`・`SDMVPSU`はmasked variance strata/PSUである。特別weightを2017–2018部分または2019–March 2020部分へ流用しない。

body measureの構造変数は `BMDSTATS`（1 Complete、2 Partial、3 Not done、4 MEC examでno eligible participants）と、`BMIHT`, `BMIWT`, `BMIWAIST`, `BMIHIP` である。公式codebookではcomment 1=Could not obtain、身長comment 3=Not straight、体重comment 3=Clothing、4=Medical appliance、ウエスト/ヒップcomment 1=Could not obtainである。存在する生コードと件数だけを保存し、独自の意味付けや値変更はしていない。`BMXBMI`は公式派生値を使う候補であり再計算・丸め直しをしない。

## 4. 2017・2019–2020・2021手順の独立照合

公式 [2017 manual](https://wwwn.cdc.gov/nchs/data/nhanes/public/2017/manuals/2017_Anthropometry_Procedures_Manual.pdf)、2019–2020 procedure manualsページが配布する [2020-labelled manual](https://wwwn.cdc.gov/nchs/data/nhanes/public/2019/manuals/2020-Anthropometry-Procedures-Manual-508.pdf)、[2021 manual](https://wwwn.cdc.gov/nchs/data/nhanes/public/2021/manuals/2021-Anthropometry-Procedures-Manual-508.pdf) を独立取得し本文を照合した。「2019手順書」は公式配布ファイル名が `2020-...` であるため、名前を推測で変更しない。

| 観点 | 2017 | 2019–2020 | 2021 | 影響判定 |
| --- | --- | --- | --- | --- |
| 身長 | MEC stadiometer、最大垂直長、Frankfort plane等、0.1 cm | 同じ | 同じ | `BMXHT`入力は構成概念・姿勢・精度が互換 |
| 体重 | MEC内蔵digital scale、kg、標準MEC gown、衣服時CL comment | 同じ | 同じ | `BMXWT`入力は互換。衣服commentを無視しない |
| ウエスト | 右腸骨稜の最上外側縁直上をmidaxillary lineで標識、床と平行、皮膚を圧迫せず、通常呼気終末、0.1 cm | 同じ | 同じ | `BMXWAIST`目的は互換 |
| ヒップ | exam pantsの余剰布をfold、臀部最大突出部、床と平行、通常呼気終末、0.1 cm | 同じ | 同じ | `BMXHIP`目的は互換 |
| 衣服・姿勢 | gown、身長の立位、周囲長の立位 | 同じ | 同じ | 本質差なし。commentで例外を保持 |
| status/comment | component status、測定別commentをISISへ記録 | 同じ構造 | 同じ構造 | public codebookのcycle別codeを使用 |
| QA/QC | 訓練、直接観察、data review、gold-standard比較、scale/stadiometer calibration | 同じ | 同じ | 本質差なし |

章立て、図番号、清掃用品等の編集差はあるが、対象4測定の機器種別、ランドマーク、姿勢、呼吸相、単位・読取精度、衣服条件、QA/QCにモデル入力・目的変数の意味を変える差を確認しなかった。したがって「変数名が同じだから」ではなく手順本文により**測定互換**とする。ただし機器の個体差や時点差がゼロという意味ではなく、過去cycleへのtransportability試験という限界は残る。

## 5. 成人・課題別構造

full examined designを先に定義し、以下は `RIDAGEYR >= 20` および生 `RIAGENDR` codeのdomain/subpopulationとして数えた。weight再正規化はしていない。

| domain | 正のweight | strata | stratum–PSU pairs | lonely PSU strata | HT / WT / BMI利用可 | waist利用可 | hip利用可 | waist / hip status・comment除外候補 |
| --- | ---: | ---: | ---: | ---: | --- | ---: | ---: | --- |
| 成人全体 | 8,544 | 24 | 49 | 0 | 8,395 / 8,402 / 8,381 | 8,055 | 8,067 | 737 / 737 |
| `RIAGENDR=1` | 4,135 | 24 | 49 | 0 | 4,061 / 4,066 / 4,051 | 3,938 | 3,936 | 323 / 323 |
| `RIAGENDR=2` | 4,409 | 24 | 49 | 0 | 4,334 / 4,336 / 4,330 | 4,117 | 4,131 | 414 / 414 |

成人全体の `BMDSTATS` 生コード件数は1: 7,908、2: 247、3: 267、4: 122。comment非欠損は `BMIHT` 124、`BMIWT` 318、`BMIWAIST` 349、`BMIHIP` 339である。「除外候補」はcomponent非completeまたは該当入力・目的commentありの保守的構造フラグで、正式除外規則ではない。目的値は非欠損件数だけを調べ、値・平均・範囲・分位点・分布を調べていない。全domainで24層49 pairsが寄与しlonely PSUはないが、これは将来固定するcomplete-case評価domainの分散推定成立を先取りしない。

## 6. cycle間再参加

NHANESの公式sample design資料、analytic guidance、participant向け資料を確認したが、2017–March 2020参加者が2021–2023へ再選定されることを制度上絶対に排除する記述は確認できなかった。したがって、**別cycle・別標本だが、同一人物が絶対にゼロであることは公式確認できない**。個人ID照合、cycle横断の`SEQN`比較、再識別は行っていない。

## 7. 利用条件

[NCHS Data User Agreement](https://www.cdc.gov/nchs/policy/data-user-agreement.html) と公式public-use配布を確認した。public-use統計解析は、再識別、個人・施設への接触、識別情報のリンク、識別につながる開示等を行わずDUAに従う条件で可能と解する。派生モデル作成、モデル成果物公開、Webアプリ搭載、商用利用を個別に明示許諾する記述、および元XPTの第三者再配布条件は今回確認できず**未確認**である。一般的なpublic accessをこれらの個別許諾へ拡張解釈しない。Cゲートで用途、配布形態、帰属・免責、最新規約を法務・運用面から再確認するため、本工程では最終利用許諾判断をしない。

## 8. 停止事項と成果物

manifestは [`data/manifests/nhanes_2017_2020_final_test_audit.json`](../data/manifests/nhanes_2017_2020_final_test_audit.json)、再現スクリプトは [`scripts/audit_nhanes_2017_2020_final_test.py`](../scripts/audit_nhanes_2017_2020_final_test.py) である。生データ、目的値、`SEQN`値は含まない。モデル学習、回帰、係数推定、予測、性能計算、欠損補完、値変更、外れ値処理、winsorization、weight再正規化、B/C通過、最終試験開封は全て未実施である。

次工程へは、(1) development内design-aware選択法、(2) 本候補の正式採否、(3) 封印・一回評価・指標・閾値・失敗時停止、(4) Cゲート利用条件、を性能も目的値も見ず事前固定するまで進まない。
