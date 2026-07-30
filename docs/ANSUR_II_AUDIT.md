# ANSUR II データ出典監査（第2段階・再調査）

## 1. 監査範囲と判定語

- 初回調査日: 2026-07-29
- 再調査日: 2026-07-30
- 使用した情報源は `ph.health.mil` と `www.army.mil` の公式資料だけである。
- 現行公式ページ候補: https://ph.health.mil/topics/workplacehealth/ergo/Pages/Anthropometric-Database.aspx
- 米陸軍公式記事: https://www.army.mil/article/188601/for_good_measure_natick_releases_raw_data_from_army_wide_anthropometric_survey
- **確認済み**: 正常取得できた米陸軍公式記事本文に明記された事実。
- **未確認**: 許可された公式資料本文から根拠を取得できなかった事項。
- **判断保留**: 公式事実を確認できても、本プロジェクトでの採否に追加検討が必要な事項。

TLS証明書検証は無効化していない。許可ドメイン外へのリンクは閲覧していない。生データの取得・追加、個票の統計分析、モデル学習、推定式・係数・Webアプリの作成は行っていない。

## 2. 接続結果

### 現行Anthropometric Databaseページ: 接続不能

- 接続日時: **2026-07-30 03:34:17 UTC**
- 使用URL: https://ph.health.mil/topics/workplacehealth/ergo/Pages/Anthropometric-Database.aspx
- HTTPS接続では最終応答が **HTTP 503 Service Unavailable** となった。応答本文は上流接続時の `CERTIFICATE_VERIFY_FAIL` を示した。クライアント側のTLS証明書検証を無効化していない。
- このため、公式ページ本文、同ページ掲載の **ANSUR II Database Memorandum for Record**、変数説明、配布ファイルのリンクおよび利用条件を取得できなかった。

### 米陸軍公式記事: 接続成功

- 接続日時: **2026-07-30 03:34:17–03:34:19 UTC**
- 使用URL: https://www.army.mil/article/188601/for_good_measure_natick_releases_raw_data_from_army_wide_anthropometric_survey
- HTTPSで **HTTP 200 OK** の公式記事本文を取得した。記事は Jane Benson and Joseph Parham, NSRDEC による “For good measure -- Natick releases raw data from Army-wide anthropometric survey”（2017-05-31）である。出典: https://www.army.mil/article/188601/for_good_measure_natick_releases_raw_data_from_army_wide_anthropometric_survey

初回に使用した旧経路 `https://ph.health.mil/topics/healthsurv/epidemiology/Pages/Anthropometric-Database.aspx` は今回の事実確認には使用せず、現行URLで再試行した。

## 3. 調査・実施主体・対象集団

| 調査事項 | 監査結果 | 判定・出典 |
| --- | --- | --- |
| 正式な調査名 | **2012 Army-wide Anthropometric Survey**。記事は略称を **ANSUR II** とする | **確認済み**: https://www.army.mil/article/188601/for_good_measure_natick_releases_raw_data_from_army_wide_anthropometric_survey |
| 実施主体 | Natick Soldier Research, Development and Engineering Center（NSRDEC）の専門家とcontractorsが実施 | **確認済み**: https://www.army.mil/article/188601/for_good_measure_natick_releases_raw_data_from_army_wide_anthropometric_survey |
| 調査期間 | 記事は「2012 survey」とする。開始・終了年月日は未確認 | **一部確認済み／一部未確認**: https://www.army.mil/article/188601/for_good_measure_natick_releases_raw_data_from_army_wide_anthropometric_survey |
| 対象集団 | 全米のSoldiers数千人。現役・予備役等の内訳、抽出方法、年齢範囲は未確認 | **一部確認済み／一部未確認**: https://www.army.mil/article/188601/for_good_measure_natick_releases_raw_data_from_army_wide_anthropometric_survey |
| 男性公開データ件数 | **4,082** | **確認済み**: https://www.army.mil/article/188601/for_good_measure_natick_releases_raw_data_from_army_wide_anthropometric_survey |
| 女性公開データ件数 | **1,986** | **確認済み**: https://www.army.mil/article/188601/for_good_measure_natick_releases_raw_data_from_army_wide_anthropometric_survey |
| 身体測定項目数 | **93 body measurements**を収集。記事は3D surface scansも収集したとする | **確認済み**: https://www.army.mil/article/188601/for_good_measure_natick_releases_raw_data_from_army_wide_anthropometric_survey |
| 個人識別用変数 | 未確認。記事が述べるdemographic dataは匿名結合キーの名称・性質を示さない | **未確認**: 現行公式ページ／変数説明は接続不能 |
| 年齢・性別 | 公開raw dataにdemographic dataとして **age** と **gender** が含まれる。正式変数名、型、コード、年齢基準日は未確認 | **存在のみ確認済み**: https://www.army.mil/article/188601/for_good_measure_natick_releases_raw_data_from_army_wide_anthropometric_survey |

記事は調査対象をSoldiersと明記する。軍務への選抜、身体要件、年齢・職種構成、非回答および標本設計を確認できていないため、米国一般成人や世界の一般成人を代表するとは扱わない。出典: https://www.army.mil/article/188601/for_good_measure_natick_releases_raw_data_from_army_wide_anthropometric_survey

## 4. 測定項目監査

米陸軍記事は例示項目の存在を確認できるが、変数説明を取得できないため、正式変数名、保存単位、姿勢、ランドマークおよび測定手順は推測しない。

| 目的項目 | 有無・記事上の名称 | 正式変数名 | 保存単位 | 定義 | 判定・出典 |
| --- | --- | --- | --- | --- | --- |
| 身長 | あり: **stature** | 未確認 | 未確認 | 直接測定93項目の例として掲載。ただし姿勢等は未確認 | **存在のみ確認済み**: https://www.army.mil/article/188601/for_good_measure_natick_releases_raw_data_from_army_wide_anthropometric_survey |
| 体重 | あり: **weight** | `weightkg`か否か未確認 | 未確認 | 直接測定か自己申告か、衣服条件、保存形式は未確認 | **存在のみ確認済み**: https://www.army.mil/article/188601/for_good_measure_natick_releases_raw_data_from_army_wide_anthropometric_survey |
| 胸囲 | あり: **chest circumference** | 未確認 | 未確認 | 呼吸状態、姿勢、測定位置、テープ経路は未確認 | **存在のみ確認済み**: https://www.army.mil/article/188601/for_good_measure_natick_releases_raw_data_from_army_wide_anthropometric_survey |
| ウエスト | 記事本文の例示にはない | 未確認 | 未確認 | `omphalion`を含む位置・定義は未確認 | **未確認** |
| ヒップ周囲候補 | 記事本文の例示にはない | 未確認 | 未確認 | buttock circumferenceの有無・定義は未確認 | **未確認** |
| ヒップ幅候補 | 記事本文の例示にはない | 未確認 | 未確認 | hip breadthの有無・定義は未確認 | **未確認** |
| BMI | 記事本文に記載なし | 未確認 | 未確認 | 収録変数か派生値かを含め未確認 | **未確認** |

### 胸囲・ウエスト・ヒップの区別

- 記事で存在が確認できた `chest circumference`を日本語の「バスト」と同一視しない。呼吸相、姿勢、測定高、乳房を含むテープ経路は公式変数説明を取得するまで**未確認**である。
- `omphalion`の変数・測定点は未確認である。臍、臍を通る水平面、最細部、腸骨稜のいずれかを推測で割り当てない。
- `buttock circumference`のような周囲長と`hip breadth`のような直線幅は異なる。どちらも存在自体が未確認で、仕様上の「ヒップ周囲」へ割り当てない。

## 5. 保存単位、欠損、品質管理

### 確認済み

- 米陸軍記事はNSRDEC researchersがデータ取得にstrict guidelines and controlsを用いたと説明する。ただし具体的なQCコード、誤差量、再測定手順は示さない。出典: https://www.army.mil/article/188601/for_good_measure_natick_releases_raw_data_from_army_wide_anthropometric_survey

### 未確認

- `weightkg`を含む正式変数名と、体重がkgそのものか符号化値かという保存形式。
- 長さ、周囲長、幅の保存単位と、cm・kgへの換算係数、丸め、精度。
- 欠損、異常値、測定不能、適用外、拒否、品質管理の値・コード。
- 編集、補完、外れ値処理、測定者間誤差、3D scan由来変数の扱い。

上記はMemorandumと変数説明に接続できるまで、換算・除外・補完を行わない。

## 6. 男女別データと一般化

### 確認済み

- 公開件数は男性4,082、女性1,986で異なる。出典: https://www.army.mil/article/188601/for_good_measure_natick_releases_raw_data_from_army_wide_anthropometric_survey

### 判断保留

- 男女別配布ファイルの構造と測定項目差は未確認である。件数差もあるため、男性・女性データを無条件に結合しない。
- 記事の`gender`を仕様の「統計モデル上の男性／女性区分」にどう対応させるかは、正式変数名とコードが未確認のため未決定。
- Soldiersのデータであり、一般成人、他国人口、全年齢、アバター利用者への代表性は確認できない。

## 7. 公開範囲、利用条件、引用

### 確認済み

- 2017年の米陸軍記事は、男性4,082件・女性1,986件のraw dataが当時“available to the public”になったと報じる。記事掲載の配布先は許可ドメイン外なので閲覧しておらず、2026年現在の配布継続性は未確認。出典: https://www.army.mil/article/188601/for_good_measure_natick_releases_raw_data_from_army_wide_anthropometric_survey
- 監査で参照した記事は、Jane Benson and Joseph Parham, NSRDEC, “For good measure -- Natick releases raw data from Army-wide anthropometric survey,” 2017-05-31, U.S. Armyである。出典: https://www.army.mil/article/188601/for_good_measure_natick_releases_raw_data_from_army_wide_anthropometric_survey

### 未確認

- 再配布、商用利用、改変、帰属、免責、個人情報に関する具体的利用条件。
- Memorandum記載の条件と、データセット固有の必須引用形式。
- 記事が案内する技術報告・配布先は許可ドメイン外のため参照していない。

したがって、記事の「public」を根拠に無条件の再利用・再配布が許可されるとは断定しない。

## 8. NHANESとの測定定義比較

| 項目 | NHANES 2021–2023で確認済みの定義 | ANSUR II | 比較判定 |
| --- | --- | --- | --- |
| 身長 | `BMXHT`、立位身長、cm | statureの存在のみ確認、定義・単位未確認 | **判断保留** |
| 体重 | `BMXWT`、digital scale等による測定、kg | weightの存在のみ確認、測定方法・単位未確認 | **判断保留** |
| BMI | `BMXBMI`、体重kg÷身長m²の計算値 | 収録有無未確認 | **判断保留** |
| ウエスト | `BMXWAIST`、右腸骨稜最上外側縁直上、通常呼気終末 | 存在・位置・呼吸相とも未確認 | **判断保留** |
| ヒップ | `BMXHIP`、臀部最大突出部を通る周囲長、通常呼気終末 | 周囲長／幅、位置とも未確認 | **判断保留** |
| 胸囲 | 対象`BMX_L`に該当変数なし | chest circumferenceの存在のみ確認、定義未確認 | **比較不能** |

同名・類似名だけでは定義一致の証拠にならない。ANSUR IIの変数説明を取得し、位置、姿勢、呼吸相、機器、衣服、単位、欠損処理を照合するまで、NHANESと統合しない。

## 9. アバター向け身体寸法補完への適性と限界

### 確認できた候補適性

- 同じ公開raw dataにage、genderと、stature、weight、chest circumferenceを含むbody measurementsがあると記事が明記するため、胸囲を含む寸法補完の**候補**にはなり得る。出典: https://www.army.mil/article/188601/for_good_measure_natick_releases_raw_data_from_army_wide_anthropometric_survey
- 記事は93 body measurementsと3D surface scansを収集したとする。ただし本プロジェクトで使える変数の組合せや品質を保証するものではない。出典: https://www.army.mil/article/188601/for_good_measure_natick_releases_raw_data_from_army_wide_anthropometric_survey

### 問題点・限界

- 胸囲の定義、単位、欠損・QCを確認できず、現段階では補完モデルの学習根拠にできない。
- ウエスト、ヒップ周囲、BMIの存在と定義を確認できない。
- 対象はSoldiersで、一般成人やアバター利用者への一般化可能性と精度は未確認。
- 男女別件数が異なり、測定項目構成も未確認である。
- 現在の配布範囲、利用条件、引用要件が未確認である。
- 医療・健康・美容用途への適合性は評価せず、そのような用途に使えるとは記載しない。

## 10. 結論

ANSUR IIには米陸軍公式記事で`chest circumference`の存在が確認でき、**胸囲候補として公式変数説明の再監査まで進める価値はある**。ただし測定定義、保存単位、欠損・QC、利用条件、NHANESとの整合を確認できていないため、生データ取得・統計分析・モデル設計へは進めず、**正式採用せず監査中**を維持する。男性データと女性データも無条件に結合しない。

## 11. 未確認事項

1. 調査の開始・終了日、標本抽出、年齢範囲、Soldiersの構成。
2. 個人結合キー、age・genderの正式変数名とコード。
3. 全93項目の正式変数名、単位、測定定義。
4. 胸囲の呼吸相・姿勢・位置、ウエストの`omphalion`、臀部周囲長とhip breadth。
5. `weightkg`を含む保存形式とcm・kgへの換算。
6. 欠損、異常値、測定不能、品質管理コード。
7. 男女別ファイルの構造差と結合可否、一般成人への一般化可能性。
8. 2026年現在の配布範囲、具体的利用条件、必須引用方法。
9. NHANESとの定義整合とアバター用途での精度。
