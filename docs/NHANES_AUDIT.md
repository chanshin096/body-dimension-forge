# NHANES 2021–2023 データ出典監査（第1段階）

## 1. 監査範囲と判定語

- 調査日: 2026-07-28
- 対象: NHANES August 2021–August 2023 の身体計測 `BMX_L`、人口統計・標本ウェイト `DEMO_L`、身体計測手順書、および同 cycle の分析案内。
- 情報源: 指定どおり `wwwn.cdc.gov` 上の CDC/NCHS 公式資料だけを使用した。記憶、第三者資料、他ドメインは事実確認に使用していない。
- この第1段階監査時点では、生データ `BMX_L.xpt` / `DEMO_L.xpt` はダウンロードもリポジトリへの追加もしておらず、確認したレコード数はコードブック掲載の度数によった。その後の取得・構造検査は [`NHANES_INTAKE_2021_2023.md`](NHANES_INTAKE_2021_2023.md) に分離して記録し、生データは引き続きリポジトリへ追加しない。
- **確認済み**: 上記公式資料に明記された事実。
- **未確認**: 許可された資料で根拠を確認できなかった事項。
- **判断保留**: 事実は確認したが、本プロジェクトでの採否に追加検討が必要な事項。

## 2. 調査・配布・対象集団

### 確認済み

1. 正式な調査名は **National Health and Nutrition Examination Survey**、公開 cycle の表記は **August 2021–August 2023**、収集期間は2021年8月から2023年8月である。身体計測ファイル名は **Body Measures (BMX_L)**、人口統計ファイル名は **Demographic Variables and Sample Weights (DEMO_L)** である。出典: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/BMX_L.htm および https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/DEMO_L.htm
2. 配布元は米国 **Centers for Disease Control and Prevention (CDC), National Center for Health Statistics (NCHS)** である。身体計測手順書は身体計測 component の資金が NCHS のみにより提供されたとも記す。出典: https://wwwn.cdc.gov/nchs/data/nhanes/public/2021/manuals/2021-Anthropometry-Procedures-Manual-508.pdf
3. cycle の標本は、米国の **civilian noninstitutionalized population** からの、層化・クラスター化された4段階標本を用いて全国推計を行う設計である。一方、パンデミック環境への対応で race/Hispanic origin・income による person-level oversampling がなくなり、年齢による oversampling が加わった。特定の人口統計 subgroup は以前の cycle より参加者が少なく、精度低下が見込まれるため、「全人口を無条件に代表する」とは扱わない。出典: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/DEMO_L.htm
4. `BMX_L` は同 cycle の **examined survey participants 全員**を含み、身体計測 protocol 自体に medical、安全その他の除外はなかった。車椅子利用者は実行可能な範囲で測定された。出典: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/BMX_L.htm
5. `BMX_L` は **8,860レコード**である。これは `BMDSTATS` のコード1～4の掲載度数 8,235 + 147 + 409 + 69（累計8,860、欠損0）から確認した値であり、測定値が完全な人数ではない。出典: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/BMX_L.htm
6. ファイル間の個人結合キーは respondent sequence number **`SEQN`** で、`BMX_L` と `DEMO_L` の双方に存在する。出典: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/BMX_L.htm および https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/DEMO_L.htm
7. 年齢は screening interview 時の満年齢 **`RIDAGEYR`**、性別区分はコードブック上 “Gender” の **`RIAGENDR`** を `DEMO_L` から結合できる。`RIDAGEYR` は80歳以上が disclosure 対策で80に top-code される。20歳未満では exam 時月齢 **`RIDEXAGM`** もある。身体計測 protocol は screening interview 時年齢で決まり、screening と exam の間に数週の差があり得る。出典: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/DEMO_L.htm および https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/BMX_L.htm

### 判断保留

- 本プロジェクトの対象は成人だが `BMX_L` は全年齢を含む。成人部分集合の定義、80歳以上の top-code、年齢・性別区分のモデル上の扱いは、採用判断と分析計画で別途決める。
- 公開 `RIAGENDR` の2区分を、本プロジェクト仕様の「統計モデル上の男性／女性区分」にどう対応づけ、利用者へどう説明するかは未決定である。

## 3. 身体項目

| 項目 | 有無・変数 | 単位 | 公開ファイルの対象年齢 | 値の性質 | 確認状態・出典 |
| --- | --- | --- | --- | --- | --- |
| 身長 | あり: `BMXHT` (Standing Height) | cm | 男女とも2～150歳 | stadiometer による測定値（条件により補正または手動読取） | **確認済み**: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/BMX_L.htm および https://wwwn.cdc.gov/nchs/data/nhanes/public/2021/manuals/2021-Anthropometry-Procedures-Manual-508.pdf |
| 体重 | あり: `BMXWT` | kg | 男女とも0～150歳（all ages） | digital scale、必要時 portable scales による測定値 | **確認済み**: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/BMX_L.htm および https://wwwn.cdc.gov/nchs/data/nhanes/public/2021/manuals/2021-Anthropometry-Procedures-Manual-508.pdf |
| BMI | あり: `BMXBMI` | kg/m² | 男女とも2～150歳 | **直接測定ではない**。kg体重÷m身長²で計算し、小数1桁へ丸めた値 | **確認済み**: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/BMX_L.htm |
| ウエスト | あり: `BMXWAIST` | cm | 男女とも2～150歳 | abdominal/waist circumference の測定値 | **確認済み**: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/BMX_L.htm |
| ヒップ | あり: `BMXHIP` | cm | 男女とも12～150歳 | hip/buttocks circumference の測定値 | **確認済み**: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/BMX_L.htm |
| 胸囲 | `BMX_L` の component description と codebook に該当変数なし | — | — | 「NHANES全体に存在しない」とまでは断定しない | **確認済み（`BMX_L` 内に限る）**: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/BMX_L.htm |

対象年齢の上限150歳はコードブックの `Target` 表示を転記したもので、実レコードに150歳の参加者がいることを意味しない。

## 4. 測定位置・姿勢・方法

以下は **確認済み**。すべての手順の出典: https://wwwn.cdc.gov/nchs/data/nhanes/public/2021/manuals/2021-Anthropometry-Procedures-Manual-508.pdf

| 項目 | 測定位置・姿勢・方法 |
| --- | --- |
| 身長 | 2歳以上で自立立位が可能な参加者を stadiometer で測る。体重を両足へ均等にかけ、足底を台につけ、踵を合わせ、つま先を約60度外へ向け、背板に沿って直立する。頭は耳道から眼窩下縁の線が床と平行な Frankfort horizontal plane に合わせ、正面を見る。head piece で髪を圧縮し、最大限高く立って深呼吸を保った状態で取得する。頭・肩甲骨・臀部・踵の全点が体型上接触しない場合もあり、姿勢を満たせなければ `Not straight` comment を付ける。髪飾りや靴を外せない場合は ruler で補正量を測り ISIS が adjusted height を計算する。機器障害時は背板側面の tape を読む。 |
| 体重 | 標準 MEC gown（下着以外は gown、乳児は diaper）で、digital scale 中央に立ち、手を体側に置き正面を向き、表示安定後に取得する。自立できない乳幼児は成人を tare して抱いて測る。必要時は portable scale を使う。靴を脱がない場合は無効として `Could Not Obtain`、street clothes や medical appliance がある取得値には comment を付ける。 |
| BMI | 独立した測定姿勢・位置はない。測定された kg 体重と m 身長から `weight / height²` を計算し、小数1桁へ丸める。 |
| ウエスト | 腕を交差して両手を反対側の肩へ置く。右腸骨の最上外側縁直上を触診して水平線を引き、midaxillary line と交差させる。その印の高さで tape を水平（床と平行）に一周させ、皮膚を圧迫しない程度に密着させる。通常呼気終末に0.1 cm単位で読む。いわゆる最細部や臍位置ではない。 |
| ヒップ | 腕を交差して両手を反対側の肩へ置く。exam pants の側面の余分な布をまとめ、側面から見た臀部の最大突出部を定める。そこを通る水平面で tape を床と平行かつ密着させ、通常呼気終末に0.1 cm単位で読む。骨盤の特定点やウエスト位置ではない。 |

## 5. 欠損・測定不能・品質管理

### 確認済み

- component status はコードブックの変数名 **`BMDSTATS`**（本文中に `BMXSTATS` 表記もある）で、1=年齢群に必要なデータが完全、2=身長・体重のみ、3=その他の部分検査、4=身体計測データなし。実装時はコードブック上の変数名 `BMDSTATS` を採用し、本文表記差は資料上の不整合として注意する。出典: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/BMX_L.htm
- 数値変数の `.` は missing である。掲載件数は `BMXWT` 106、`BMXHT` 361、`BMXBMI` 389、`BMXWAIST` 670、`BMXHIP` 2,084。年齢非対象者も同じ全8,860レコード中の missing 度数に含まれるため、これを一律に測定失敗とは解釈しない。出典: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/BMX_L.htm
- comment 変数は `BMIWT`、`BMIHT`、`BMIWAIST`、`BMIHIP`。code 1 は Could not obtain。`BMIWT` はさらに code 3=Clothing、4=Medical appliance、`BMIHT` は code 3=Not straight を持つ。comment 側の `.` は「comment なし」を含み得るため、測定値欠損と同義に扱わない。分析前に各 comment code を確認するよう公式文書が指示する。出典: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/BMX_L.htm
- limb amputation の参加者の体重は missing に設定された。妊娠者を含むが、開示対策により一部妊娠者の body measures は公開されない。出典: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/BMX_L.htm
- 値は過去データに基づく年齢または年齢・gender 群の1/99 percentile 外を review し、非現実的と判断した値を削除した。元の値は変更せず、imputation はない。極端値を機械的に異常とせず、分布と分析目的に応じて包含可否を検討するよう記載される。出典: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/BMX_L.htm
- QC は訓練、監督、直接観察、data review、expert examiner との比較、機器校正、入力時の範囲警告を含む。ただし、これを本用途での精度保証や誤差量の根拠とはしない。出典: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/BMX_L.htm および https://wwwn.cdc.gov/nchs/data/nhanes/public/2021/manuals/2021-Anthropometry-Procedures-Manual-508.pdf

## 6. 利用条件・引用

### 確認済み

- `BMX_L` と `DEMO_L` は公式ページで public data file / public use demographics file と記載され、各ページに文書・コードブックと `.xpt` への導線がある。出典: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/BMX_L.htm および https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/DEMO_L.htm
- `DEMO_L` の References は survey の推奨書誌情報として次を掲載する: Terry AL, Chiappa MM, McAllister J, Woodwell DA, Graber JE. *Plan and operations of the National Health and Nutrition Examination Survey, August 2021–August 2023.* National Center for Health Statistics. Vital Health Stat 1(66). 2024. DOI は同ページ参照。出典: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/DEMO_L.htm
- 本プロジェクトで引用する場合は、少なくとも上記 survey report に加え、使用した `BMX_L` / `DEMO_L` の文書名、cycle、CDC/NCHS、公式URL、参照日、および測定定義に用いた Procedures Manual を明記する。これは出典追跡可能性を確保するための本監査上の方針であり、CDC が指定した唯一の引用形式だとは主張しない。

### 未確認

- ナビゲーションには “Data User Agreement” があるが、リンク先は許可された `wwwn.cdc.gov` ではなく、`wwwn.cdc.gov` 上の同等パスは404であった。指定された情報源制約を守るためリンク先本文を参照しておらず、再配布、商用利用、帰属表示等の詳細利用条件は **確認不能／未確認**。出典（リンクの存在）: https://wwwn.cdc.gov/nchs/nhanes/analyticguidelines.aspx
- 公開データセット固有の必須 citation wording は、閲覧した `wwwn.cdc.gov` 資料では **未確認**。

## 7. 標本ウェイトと統計モデル

### 確認済み

- 身体計測分析には **NHANES examination sample weights** を使うよう `BMX_L` が明記する。`DEMO_L` は2021–2023の全分析で目的に応じ `WTINT2YR` または `WTMEC2YR` を使うよう記し、body measures は MEC examination のため **`WTMEC2YR`** が該当する。分散推定用に `SDMVSTRA` と `SDMVPSU` も公開される。出典: https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/BMX_L.htm および https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2021/DataFiles/DEMO_L.htm
- したがって、母集団について記述・推論する統計モデルでは、ウェイトだけでなく層化・クラスタリングを含む複雑標本設計を分析計画に組み込む必要がある。単純無作為標本として扱わない。cycle overview は nonresponse、weighting、variance estimation、subgroup sample size を検討するよう案内する。出典: https://wwwn.cdc.gov/nchs/nhanes/continuousnhanes/overviewbrief.aspx?Cycle=2021-2023

### 判断保留

- アバターの個別寸法補完モデルに survey weights をどう組み込むか、目的母集団・損失関数・評価設計を定めていないため **未決定**。ウェイトを使うとの公式指示だけから、モデル方式や係数は作らない。

## 8. アバター向け身体寸法補完への適性と限界

### 確認できた適性

- 身長、体重、ウエスト、ヒップが同一参加者キーで提供され、年齢・公開性別区分・MEC weight と結合できる。
- cm / kg で標準化された測定手順と comment/status が公開され、ウエストとヒップの位置を区別できる。
- BMI が直接測定ではなく身長・体重からの計算値だと明確で、入力値と派生値を区別できる。

### 問題点・限界

- `BMX_L` に胸囲を確認できず、現行仕様の胸囲補完をこのファイル単独では構築できない。
- ウエストは腸骨稜直上、ヒップは臀部最大突出部という医療・調査用プロトコルであり、衣服・3Dアバター・他データセットの同名寸法と同一とは限らない。
- 対象は米国 civilian noninstitutionalized population の標本であり、世界のアバター利用者、施設人口、特定集団へ無条件に一般化できない。subgroup の標本数・精度にも注意が必要である。
- 欠損、年齢による非対象、測定不能、衣服・medical appliance、姿勢、車椅子、amputation、妊娠、公開時の top-code・非開示がある。
- 公開値に imputation はなく、欠損補完モデルの学習対象をどう定義するかは別の設計判断になる。
- 公式QCの存在は、アバター用途での予測精度を保証しない。生データ分析と外部評価を実施していないため、精度は **未確認**。
- 医療診断・健康評価用途への適合性は評価しておらず、本プロジェクトの仕様上も対象外である。

### 結論（判断保留）

NHANES は候補として有用な構造を持つが、利用条件、胸囲の別出典との定義整合、対象母集団、欠損処理、標本設計、モデル評価を解決していない。**第1段階の結果だけでは正式採用せず、監査中とする。** 推定式、係数、仮データ、モデルは作成していない。

## 9. 未確認事項一覧

- Data User Agreement 本文に基づく詳細利用条件（許可ドメイン制約のため確認不能）。
- データセット固有の必須 citation wording。
- NHANES の他 component における胸囲の有無（今回は `BMX_L` を監査し、存在を推定していない）。
- 成人部分集合を用いた項目別 complete-case 数、分布、相関、精度（生データを分析していない）。
- アバター用途の許容誤差、外部妥当性、モデル選択、係数。
- ANSUR II の内容、利用条件、NHANES との測定定義の整合（今回は未調査）。
