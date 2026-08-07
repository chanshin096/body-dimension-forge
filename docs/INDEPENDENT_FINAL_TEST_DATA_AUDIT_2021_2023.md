# 独立最終試験データ候補の成立性監査（Bゲート実行7）

## 1. 目的、範囲、結論

本書は、NHANES August 2021–August 2023 の full examined survey design（15層・30 masked pseudo-PSU）を分割せず development に使う第0.1版のウエスト `BMXWAIST`・ヒップ `BMXHIP` 課題について、**development から独立した封印最終試験データを確保できるか**だけを、2026-08-07時点の公式資料で監査する正本である。モデル学習、回帰、係数推定、予測、性能計算、目的変数分布比較、生データ取得、個人値または `SEQN` の保存は行っていない。

**最終判定は B「条件付き候補はあるが追加監査が必要」**とする。

- **第一候補**: NHANES 2017–March 2020 pre-pandemic の `P_BMX`＋`P_DEMO`。必要な目的・入力変数、公式の特別MECウェイト、24 masked strata・49 masked PSU、全国推論用の一体のpublic-use標本が存在する。2017年手順書と2021年手順書の該当手順は本文上整合する。ただし、2019年手順書の独立再照合と、個票を受領せずに行った本監査では確認できない成人・生コード・課題別の利用可能件数、QCコード集合、設計寄与状況、ファイル完全性、同一人物のcycle間再参加排除が残るため、まだ正式採用・封印済みとはしない。
- **代替候補**: NHANES 2017–2018 の `BMX_J`＋`DEMO_J`。同じ必要変数と測定手順、2-year MEC weight、15層・30 PSUを持つが、第一候補より古く小さい標本である。`P_*`はこのcycleを内包するため、両方を別々の最終試験として併用しない。
- **不採用**: ANSUR IIはSoldiers標本で一般成人のsurvey weight・公開標本設計を確認できず、目的変数定義も未確認である。米国 civilian noninstitutionalized adult population 向けの最終試験にはしない。
- **現時点で利用不能**: 2025–2026 NHANESには公式の調査・手順ページがあるが、公式public-useデータ一覧に `BMX`・demographicsファイルは公開されていない。将来公開を「利用可能」と先取りしない。

この判定は独立データの**成立可能性**を認めるだけで、データ、モデル、評価設計またはB/Cゲートの採用ではない。Bゲート実行6の「独立最終試験データとdevelopment内選択法の両方を事前承認できるまでモデル学習へ進まない」を維持する。

## 2. 公式根拠と確認方法

### 2.1 NHANES公式資料

- 2017–March 2020 body measures: [P_BMX documentation](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/P_BMX.htm)
- 同 demographics・特別ウェイト・masked variance units: [P_DEMO documentation](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/P_DEMO.htm)
- 2017–2018 body measures: [BMX_J documentation](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/BMX_J.htm)
- 同 demographics・2-yearウェイト・masked variance units: [DEMO_J documentation](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2017/DataFiles/DEMO_J.htm)
- development側の比較基準: [BMX_L](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/BMX_L.htm)、[DEMO_L](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/DEMO_L.htm)
- 手順書: [2017 Anthropometry Procedures Manual](https://wwwn.cdc.gov/nchs/data/nhanes/public/2017/manuals/2017_Anthropometry_Procedures_Manual.pdf)、[2021 Anthropometry Procedures Manual](https://wwwn.cdc.gov/nchs/data/nhanes/public/2021/manuals/2021-Anthropometry-Procedures-Manual-508.pdf)。`P_BMX`は2017–2018および2019–2020手順書を公式参照先とする。
- cycle一覧・公開ファイル: [NHANES examination data list](https://wwwn.cdc.gov/nchs/nhanes/search/datapage.aspx?Component=Examination)、[2025–2026 cycle page](https://wwwn.cdc.gov/nchs/nhanes/continuousnhanes/default.aspx?Cycle=2025-2026)
- 分析・利用規則: [NHANES Analytic Guidelines](https://wwwn.cdc.gov/nchs/nhanes/analyticguidelines.aspx)、[NCHS Data User Agreement](https://www.cdc.gov/nchs/policy/data-user-agreement.html)

公式HTMLの変数表、analytic notes、公式PDFの該当測定節を読んだ。ファイル名や変数名の一致だけでは判定していない。public-use個票は取得せず、値、分布、件数または性能を調べていない。

### 2.2 ANSUR II公式資料

- [U.S. ArmyのANSUR II公開記事](https://www.army.mil/article/188601/for_good_measure_natick_releases_raw_data_from_army_wide_anthropometric_survey)
- [Defense Centers for Public Healthの配布ページ候補](https://ph.health.mil/topics/workplacehealth/ergo/Pages/Anthropometric-Database.aspx)

後者の本文・Memorandum・変数説明は既存監査で取得不能であり、公式記事で確認できる範囲を越えて補わない。詳細は [`ANSUR_II_AUDIT.md`](ANSUR_II_AUDIT.md) を参照する。

## 3. 候補比較

| 候補 | 調査時期・対象母集団 | 年齢と必要変数 | 測定互換性 | design・ウェイト・母集団推論 | public-use・条件 | developmentとの独立性 | 判定 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **NHANES 2017–March 2020 pre-pandemic** `P_BMX`＋`P_DEMO` | 2017年から2020年3月。米国 civilian noninstitutionalized population の全国代表標本として、未完了の2019–2020単独標本を2017–2018と統合 | body measuresは全年齢を収録。身長2歳以上、ウエスト2歳以上、ヒップ12歳以上。成人候補は `RIDAGEYR >= 20`。`BMXHT`, `BMXWT`, `BMXBMI`, `BMXWAIST`, `BMXHIP`あり | cm、kg、kg/m²。ウエストは右腸骨稜最上外側縁直上・通常呼気終末・0.1 cm、ヒップは臀部最大突出部・通常呼気終末・0.1 cm。2017と2021の公式手順本文は一致。2019手順も採用前に版・差分を独立再照合する | `WTMECPRP`, `SDMVSTRA`, `SDMVPSU`。24層・49 PSU（各層2–3 PSU）。特別ウェイトは**統合標本全体だけ**に使用。2019–March 2020単独または2017–2018部分へ流用不可。full design＋成人等のdomainで全国推論可能 | 公式XPTと文書がpublic。NCHS DUA（再識別・接触等の禁止を含む）の遵守が必要。完成品搭載・商用利用・再配布はCゲートで別途確認 | 2021–2023とは別収集期間・別public-use cycle。標本レコードの混在はない。同一人物の再参加が制度上排除されるかは未確認で、公開識別子照合による推測は禁止 | **第一候補・条件付き** |
| **NHANES 2017–2018** `BMX_J`＋`DEMO_J` | 2017–2018、米国 civilian noninstitutionalized population | 上記と同じ目的・入力候補、対象年齢 | 2017手順と2021手順の該当節は一致 | `WTMEC2YR`, `SDMVSTRA`, `SDMVPSU`。15層・30 PSU、各層2 PSU。full design＋domainで当該2年間の全国推論 | public-use、NCHS DUA遵守 | 2021–2023とは別cycle。ただし`P_*`の構成部分なので両候補間は重複する | **代替候補・条件付き** |
| **2015–2016等のより古いcontinuous NHANES** | 同じNHANES対象母集団だが時点差が拡大 | 公式一覧でbody measures、demographicsを公開。cycle別に目的・入力を再確認する必要 | cycle別手順の全照合は本工程で未実施 | cycle固有のMEC weight・MVUを使う必要 | public-use、NCHS DUA遵守 | 2021–2023とは別cycle | **優先しない**。より近く、必要事項を確認できた`P_*`/2017–2018があるため。必要時は別監査 |
| **NHANES 2025–2026** | 現行の将来/最新調査cycleページは存在 | 2026-08-07時点の公式public-use一覧に必要な `BMX`・demographicsファイルなし。変数・標本構造・ウェイトを受領不能 | 手順ページの存在だけでは公開データの互換性を確定しない | 公開design変数・ウェイトなし | データ未公開 | 将来は別時点となり得るが、現在は封印対象を取得できない | **現時点で利用不能**。公開後に新版として再監査 |
| **ANSUR II** | 2012 Army-wide Anthropometric Survey。対象は全米のSoldiers | 記事でage, stature, weightの存在のみ。ウエスト、ヒップ周囲、BMI、年齢範囲は未確認 | ウエスト・ヒップの存在、単位、ランドマーク、姿勢、呼吸相が未確認 | 米国一般成人用の確率抽出design、層、PSU、一般成人ウェイトを確認できない。一般成人へのsurvey inference不可 | 2017年記事はraw dataがpublicとするが、現行配布と具体条件は未確認 | 収集時期・標本は別だが、独立性だけでは対象母集団差を救済しない | **不採用** |
| **その他のCDC/NCHS等の公的データ** | 本工程の公式検索で、必要な両目的変数・入力・一般成人標本designを一式確認できる追加候補なし | 未確定 | 未確定 | 未確定 | 未確定 | 未確定 | **候補を推測で追加しない** |

## 4. 第一候補の成立条件監査

### 4.1 取得元、対象、時期、年齢

`P_BMX.xpt`と`P_DEMO.xpt`はNCHSの公式public-use配布物である。COVID-19により2019–2020の30 locations中18 locationsで停止したため、その部分だけは全国代表ではない。NCHSは2017–2018と統合し特別weightを作った **2017–March 2020 pre-pandemic全体**を全国代表標本とする。したがって、`P_*`から年次・部分cycleを切り出した評価は不採用とする。

第0.1版と同じ成人domain候補は公開 `RIDAGEYR >= 20` である。body measuresの公式対象年齢は身長・ウエストが2歳以上、ヒップが12歳以上なので成人domainは項目の対象範囲内にある。`RIAGENDR`はdevelopment計画と同じく、公式生コード別domainとして無条件に結合しない。

### 4.2 目的変数と入力候補

| 役割 | `P_*`変数 | 定義・単位 | 2021–2023との対応 |
| --- | --- | --- | --- |
| 入力 | `RIDAGEYR` | screening時年齢、年 | 同じ公開概念。top-code等のcycle固有コードは受入時に再確認 |
| 入力 | `BMXHT` | standing height、cm | 同じ名称・単位・MEC anthropometry。機器差を含む手順書全体差分は受入前に固定 |
| 入力 | `BMXWT` | weight、kg | 同上。衣服commentも含めQCコード集合を再確認 |
| 入力候補 | `BMXBMI` | kg/m²。kg体重÷m身長²、小数1桁 | developmentと同じ公式派生定義。再計算・丸め直しをしない |
| 目的 | `BMXWAIST` | waist circumference、cm | 手順互換性を下記で確認 |
| 目的 | `BMXHIP` | hip circumference、cm | 手順互換性を下記で確認 |

### 4.3 測定手順互換性

2017と2021の公式Anthropometry Procedures Manualの該当節を文単位で照合した結果、少なくとも次の本質的定義は一致する。

- **ウエスト**: 参加者の右側で右腸骨稜を触診し、最上外側縁直上へ水平線を引き、midaxillary lineで交差させる。テープを床と平行・皮膚を圧迫しない密着状態に置き、通常呼気終末に0.1 cm単位で読む。
- **ヒップ**: exam pantsの余剰布を抑え、側面から見た臀部最大突出部へ水平にテープを置き、床と平行・密着状態で通常呼気終末に0.1 cm単位で読む。
- いずれもMECで訓練済みhealth technicianとrecorderが測定し、校正・観察・gold-standard comparisonを含むQA/QCを行う。

よって2017–2018部分と2021–2023の**測定構成概念・ランドマーク・単位は互換**と判断する。一方、`P_*`は2019–March 2020も含むため、正式採用前に公式2019手順書を取得し、該当節、機器、衣服、comment/statusコードの差分を同じ方法で記録する。変数名の一致だけを根拠にこの残件を省略しない。

### 4.4 標本設計、ウェイト、母集団推論

`P_DEMO`は24 masked variance strata・49 masked PSUs（各層2–3 PSU）と `WTMECPRP` を公開する。body measuresはMEC examination componentなのでinterview weightではなく `WTMECPRP` を候補とする。designは全examined sampleで定義し、その後に成人、生コード、QC complete caseをdomainとして扱う。ウェイトを再正規化せず、行削除した物理部分designを全国標本とみなさない。

このdesignにより推論できるのは、NCHSが当該特別weightで代表させる**2017–March 2020 pre-pandemicの米国civilian noninstitutionalized population**における、事前固定した対象domainの性能である。2021–2023母集団そのもの、2026年人口、institutionalized persons、米国外人口への直接推論ではない。

### 4.5 独立性と封印可能性

`P_*`と`*_L`は別の収集期間・public-use cycleであり、development行を再分割したものではない。この意味で標本・時点を分離できる。しかし次を未確認のまま「封印済み」「完全に同一人物ゼロ」と表示しない。

1. NHANESの抽出・参加規則がcycle間の同一人物再参加を制度上排除するという公式記述。
2. public-use `SEQN`はcycle内結合キーであり、cycleを越えた本人照合根拠には使わない。個人値やID一覧を保存せず、再識別も試みない。
3. 最終試験担当者、保存場所、アクセス権、暗号鍵、取得前hash、開封日時、一回実行の手順は未確定である。

したがって本監査では「独立最終試験を構成できる有力な別cycle」とまで判断し、正式な封印・採用は追加監査後とする。

## 5. 過去データで2021–2023モデルを評価する意味と限界

過去cycleを最終試験にすると、developmentと同じ時点からの無作為なholdout性能ではなく、**後の時点で作ったモデルを、パンデミック前の別標本・別母集団時点へ外挿したtransportability/reproducibility**を調べることになる。

- 利点は、目的値を見ない別cycle、独立した標本抽出、全国推論用designを使い、同じ測定構成概念についてdevelopment内optimismから分離した試験を構成できることである。
- 時間の向きは通常のprospective validationと逆である。過去で良好でも将来の利用者で良好とは保証しない。
- 年齢・体格・人口構成、nonresponse、oversampling、pandemic前後、2021–2023で更新されたsample design・exam procedureの影響が混在し得る。これは性能を見て補正する理由にはせず、一般化範囲の差として事前記録する。
- `P_*`特別weightで得る母集団性能と`*_L`の2021–2023性能は異なる時点を代表する。両cycleのウェイトを混合・再校正せず、同じ母集団性能の反復測定とも呼ばない。
- 不合格後に目的値を見てモデル、入力、QC、閾値、指標、domain、CIを変え、同じ過去cycleを再試験に使うことは禁止する。

したがって、第一候補採用時の表示可能範囲は「2017–March 2020 pre-pandemicの米国civilian noninstitutionalized adultsに対する外部・時点移送試験」であり、「現在・将来の全米成人一般に検証済み」ではない。

## 6. 候補別の明確な不採用・非優先理由

### 6.1 2017–2018を第一候補にしない理由

測定・design上は代替候補になり得るが、`P_*`より短い期間・小さい設計で、時点もわずかに遠い。さらに`P_*`へ全件が含まれるため、片方の目的値または性能を見た後にもう片方を「独立な第二最終試験」とすることはできない。`P_*`が構造・精度要件を満たさないと**性能を見る前**に判明した場合だけ、理由を記録して2017–2018へ切り替える。

### 6.2 より古いNHANESを優先しない理由

古いほど時点差、手順・機器・変数・oversampling差の追加監査が必要になる。より近い公式候補が成立し得る現在、目的値を見ずに古いcycleを増やしてtest候補を選択する利益がない。将来必要になれば、cycleごとの両目的、全入力、manual、design、weightを別工程で監査する。

### 6.3 将来/最新cycleを現在採用しない理由

調査ページや手順書の存在はpublic-useデータの公開を意味しない。必要なbody measures、demographics、design variables、weightsが公式配布され、cycle固有の測定・分析資料を監査できるまで利用可能と判定しない。公開後に第一候補を変更する場合も、既存候補の結果を見て選ばない。

### 6.4 ANSUR IIを不採用とする理由

対象はSoldiersで、軍務選抜・身体要件・年齢構成を持つ可能性がある。米国一般成人を代表するsurvey weight、層、PSUを確認できないため、一般成人向け母集団性能をdesign-basedに評価できない。さらにウエスト・ヒップ周囲の存在、正式変数、単位、ランドマーク、呼吸相、QC、現行利用条件も未確認である。仮に同名変数が後に見つかっても、軍人標本を一般成人最終試験へそのまま転用しない。軍人という別対象集団へのtransportability試験は別目的であり、本工程の最終試験を代替しない。

## 7. 未確認事項と追加監査

第一候補を正式採用する前に、目的値・分布・性能を閲覧しない担当者が次を完了し、個人値を含まないmanifestと文書をcommitする。

1. 公式 `P_BMX.xpt`・`P_DEMO.xpt` のURL、取得日時、サイズ、SHA-256、列名、型、一意結合可能性を受入検査する。
2. `RIDAGEYR`, `RIAGENDR`, 5 body-measure変数、各comment/status、`WTMECPRP`, `SDMVSTRA`, `SDMVPSU`の存在と公式コードを照合する。
3. 2019 Anthropometry Procedures Manualを公式元から取得し、2017・2021との目的・入力測定、機器、衣服、精度、QC差分を記録する。
4. 値や分布を保存せず、成人×生コード×課題×事前入力セットについて、正のweightを持つQC利用可能件数、寄与層・PSU、single/lonely PSUリスクだけを構造監査する。必要精度条件は結果を見る前に定める。
5. `P_*`全体だけに `WTMECPRP`を適用し、full design後domainとする解析仕様、指標別CI法・自由度・失敗条件を事前固定する。
6. cycle間の再参加可否についてNCHS公式記述を確認する。確認不能なら「標本cycleは別だが同一人物ゼロは未確認」という限界を維持し、人為的な本人照合をしない。
7. NCHS DUA、引用、取得・加工・モデル成果物の搭載、公開、商用利用、再配布をCゲートで別途判断する。
8. test custodian、アクセス分離、暗号化保存、hash、開封承認、単一候補・一回評価、失敗後の廃止規則をcommitで固定する。

## 8. 次工程へ進む条件と停止条件

### 独立最終試験候補を承認できる条件

- 上記追加監査が目的値・分布・性能を見ずに完了する。
- `P_*`の両課題・全必須domainで、公式designと事前評価を実行できる構造が確認される。
- 測定差、時点差、一般化範囲、独立性の限界を人間が受容する。
- 封印・一回評価規則と全採否基準がデータ開封前に承認される。

### 維持する停止条件

- **development内のdesign-aware選択法と独立最終試験の両方が事前承認されるまでモデル学習へ進まない。**
- 第一候補の目的変数、目的値分布または性能を見て、第一/代替cycle、QC、入力、domain、指標、CI、閾値を選ばない。
- `P_*`の2019部分だけを使わない。`P_*`と2017–2018を独立な二試験と数えない。
- 将来cycleを公開前に利用可能としない。ANSUR IIを一般成人代表標本としない。
- 本工程をB/Cゲート通過と扱わず、5項目のA可・B保留・C保留を変更しない。

次工程はモデル学習ではない。まず第一候補の**目的値非閲覧の構造・手順・利用条件監査**と、別工程でdevelopment内選択法を確定し、両方を同一の事前評価計画として人間が承認する。いずれかが不成立なら評価設計の確定を停止する。
