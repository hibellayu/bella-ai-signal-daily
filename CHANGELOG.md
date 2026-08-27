# Bella's AI Signal Daily 版本記錄

本檔案用來記錄每次版本調整的原因、修改內容與回溯資訊。版本號規則請參考 `VERSIONING.md`。

## v0.18.1｜2026-08-27

版本類型：小改版

### 修改原因

v0.18.0 將 AEO 內容結構直接顯示在前台，包含「AI 可引用摘要」、「本日可回答的提問」、「來源支撐重點」與每則新聞的「可引用重點」。Bella 確認網站第一優先是給行銷人閱讀，這些標註看起來像後台 SEO / AEO 說明，會破壞日報閱讀體驗。

### 修改內容

- 前台移除「AI 可引用摘要」整個區塊。
- 前台移除每則新聞的「可引用重點」標註。
- 保留 AEO 資料欄位、Prompt Library、Measurement Playbook、`llms.txt` 與 structured data citation。
- 每日靜態頁移除不可見的 Question / Answer `mainEntity`，避免 structured data 與前台可見內容不一致。
- Footer 版本升為 `v0.18.1`，版本日期維持 2026/08/27。

### 驗證

- `python3 -m py_compile scripts/generate_daily_digest.py scripts/static_site.py`
- `python3 scripts/static_site.py`
- 檢查首頁與每日靜態頁不再出現 `AI 可引用摘要`、`本日可回答的提問`、`可引用重點`，並確認 Footer 顯示 `v0.18.1`。

## v0.18.0｜2026-08-27

版本類型：中改版

### 修改原因

Bella 參考 AEO 實驗案例後，確認 AI 日報不應只做 SEO 關鍵字與靜態頁收錄，而要能對應真實使用者提問，並建立可驗證的 AEO 成效框架。現有網站已有 `llms.txt`、靜態頁、structured data 與 GA4，但缺少 Prompt Library、可引用摘要、來源支撐重點與跨 Answer Engine 的追蹤邏輯。

### 修改內容

- 產文 Prompt 新增 AEO 寫作規則：從 Intent + Prompt Thinking 出發，不只做 Keyword Thinking。
- 日報 JSON 新增 `answerSummary`、`promptTargets`、`aeoEntities`、`citationClaims` 欄位。
- 每則非應用切角新聞新增 `citationClaim`，整理適合被 AI 引用的來源支撐重點。
- 前台與每日靜態頁新增「AI 可引用摘要」，顯示本日可回答的提問與來源支撐重點。
- 每日靜態頁 Article structured data 補上 `mentions`、`citation` 與 Question / Answer 型態的 `mainEntity`。
- 新增 `data/aeo/prompt-library.json`，作為 AEO Prompt Library 初版。
- 新增 `docs/AEO_MEASUREMENT_PLAYBOOK.md`，定義 Prompt、Visibility、Citation、Referral、Conversion 五層衡量方式。
- 修正策略補句分類順序，避免 Agent / 影音 / 治理題目被誤套成 AI 搜尋與品牌能見度補句。
- 更新 `llms.txt`、README、PRD 與 VERSIONING。
- Footer 版本升為 `v0.18.0`，版本日期更新為 2026/08/27。

### 驗證

- `python3 -m py_compile scripts/generate_daily_digest.py scripts/static_site.py`
- `python3 scripts/static_site.py`
- `python3 -m json.tool data/aeo/prompt-library.json >/dev/null`
- 檢查首頁與每日靜態頁是否包含 `AI 可引用摘要`、`本日可回答的提問`、`可引用重點`、`v0.18.0` 與 structured data citation。

## v0.17.3｜2026-08-26

版本類型：小改版

### 修改原因

2026/08/26 早上排程有正常啟動，但 Daily AI Signal workflow 失敗，前台因此停留在 2026/08/25。失敗原因不是 API 額度、GitHub Actions 版本或前台讀取問題，而是產文通過 2 次生成與 2 次修補後，仍有部分 `analysis`、`What`、`So What` 未達審文長度與策略深度門檻，導致 `data/digests/2026-08-26.json` 未被寫入。

### 修改內容

- 新增 `MIN_ANALYSIS_PARAGRAPH_LENGTH`、`MIN_WHAT_LENGTH`、`MIN_SO_WHAT_LENGTH` 常數，集中管理策略欄位品質門檻。
- 新增 `strengthen_digest_strategy_fields` 後處理流程，在正式驗證前補強過短的 `analysis`、`What`、`So What`。
- 依議題類型補強策略脈絡：AI 影音 / 創意工具、AI 搜尋與能見度、AI Agent / 工作流、AI 治理、算力 / 基礎設施與一般行銷應用。
- 保留原本審文門檻，不允許低品質或空日報發布。
- Footer 版本升為 `v0.17.3`，版本日期更新為 2026/08/26。

### Non-scope

- 本版不降低 `analysis`、`What`、`So What` 的最低字數。
- 本版不改變新聞收錄排序規則。
- 本版不處理個別來源網站 403 或 timeout，該類問題仍由來源多元化與候選補位處理。

### 驗證

- `python3 -m py_compile scripts/generate_daily_digest.py scripts/static_site.py`
- `PYTHONPATH=scripts python3 - <<'PY' ...`，確認短欄位可被補強並通過 `validate_digest`。
- `python3 scripts/generate_daily_digest.py --report-date 2026-08-26 --dry-run`
- `/Users/bella2022/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node --check app.js`
- `python3 scripts/static_site.py`
- 重新觸發 Daily AI Signal workflow：`32925586406`
- 確認 `data/digests/2026-08-26.json` 已生成，`manifest.latest` 更新為 `2026-08-26`。
- 確認正式網址首頁與 `/daily/2026-08-26/` 均顯示 2026/08/26 日報。

### 對應 commit

- `901fd1b Strengthen digest strategy field validation`
- `847a094 chore: generate daily AI signal`

## v0.17.2｜2026-08-21

版本類型：小改版

### 修改原因

GitHub Actions 執行時出現 Node.js 20 deprecated 警告。雖然目前不影響日報生成與部署，但這代表 workflow 依賴的 action runtime 已進入汰換期，未來可能從警告變成阻塞，因此提前處理自動化維護。

### 修改內容

- 將 Daily AI Signal workflow 的 `actions/checkout` 由 `v4` 升級為 `v7`。
- 將 `actions/setup-python` 由 `v5` 升級為 `v7`。
- 將 `stefanzweifel/git-auto-commit-action` 由 `v5` 升級為 `v7`。
- Footer 版本升為 `v0.17.2`，版本日期維持 2026/08/21。

### Non-scope

- 本版不調整日報內容生成邏輯。
- 本版不處理 GitHub Pages 內部部署流程出現的 `actions/upload-artifact` 警告，因該步驟不是本專案 workflow 直接定義，需等 GitHub Pages 官方流程更新。

### 驗證

- `python3 -m py_compile scripts/generate_daily_digest.py scripts/static_site.py`
- `python3 scripts/static_site.py`
- 手動觸發 Daily AI Signal workflow：`32461432582`
- 確認 workflow 使用 `actions/checkout@v7`、`actions/setup-python@v7`、`stefanzweifel/git-auto-commit-action@v7`。
- 確認 Daily AI Signal workflow 成功完成 checkout、Python setup、生成與提交流程，並未再出現 Node.js 20 deprecated annotation。

### 對應 commit

- `ed42160 Upgrade daily workflow actions`
- `1112f2a chore: generate daily AI signal`

## v0.17.1｜2026-08-21

版本類型：小改版

### 修改原因

完成 OpenAI API 付款後，手動觸發 2026/08/21 日報生成，API 已可正常呼叫，但 GitHub Actions 仍失敗。原因不是額度不足，而是內容審稿規則判定多則 `Now What / 具體行動` 過短，缺少「數量」與「完成標準」，因此在 2 次生成與 2 次修補後仍拒絕發佈。

### 修改內容

- 新增 `MIN_NOW_WHAT_LENGTH` 常數，統一管理 `Now What / 具體行動` 的最低長度要求。
- 新增 `strengthen_digest_actions` 後處理流程，在生成與修補後、正式驗證前，檢查每則新聞的具體行動是否足夠原子化。
- 依新聞角度自動補上完成標準，例如 AI 影音輸出素材測試表、Agent / 工作流輸出流程小卡、搜尋 / GEO 輸出能見度檢查表、算力 / 晶片輸出工具依賴清單。
- 保留原本審文門檻，不因為產不出日報就降低品質要求。
- Footer 版本升為 `v0.17.1`，版本日期維持 2026/08/21。

### Non-scope

- 本版不放寬 `analysis`、`What`、`So What` 的深度門檻。
- 本版不允許空日報或低品質日報發佈。
- 本版不處理個別來源網站的 403 問題，該問題已由其他來源候選補位，非本次失敗主因。

### 驗證

- `python3 -m py_compile scripts/generate_daily_digest.py scripts/static_site.py`
- `PYTHONPATH=scripts python3 - <<'PY' ...`，確認各類保底行動文字皆超過 `MIN_NOW_WHAT_LENGTH`，且含有具體數量。
- `python3 scripts/generate_daily_digest.py --report-date 2026-08-21 --dry-run`
- `/Users/bella2022/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node --check app.js`
- `python3 scripts/static_site.py`
- 待驗證：重新觸發 GitHub Actions 生成 2026/08/21 日報。

### 對應 commit

- `531e2f6 Fix short action validation for daily digest`
- `e3b9ef0 chore: update daily digest`

## v0.17.0｜2026-08-21

版本類型：中改版

### 修改原因

日報盤點後發現，許多 AI 新知會先在社群擴散，例如 Claude Managed Agents + AG-UI、Seedance 2.5 等題材。原本系統主要依 RSS / 媒體發布日期收集，容易漏掉「原文不是當日發布、但當日社群重新熱議」的內容，也缺少 AI 影音 / 創意工具的獨立判讀面向，導致短影音、素材生成、廣告多版本與創意提案工作流的變化被 SEO、模型安全或產業新聞壓過。

### 修改內容

- 新增 `socialSignals` 設定區，將社群熱議內容作為候選雷達，但正式來源仍使用官方、產品部落格或可信來源 URL。
- 新增 Claude Managed Agents + AG-UI、Seedance 2.5 兩則社群訊號候選，分別回查 CopilotKit Blog 與 ByteDance Seed 官方來源。
- 新增 `creativeVideo` 策略角度，中文標籤為「AI 影音 / 創意工具」。
- 選文保障新增 AI 影音 / 創意工具最低覆蓋，避免相關題材被一般產業新聞擠掉。
- 擴充追蹤工具與關鍵字：Seedance、Kling、Runway、Pika、Veo、Dreamina、CapCut、Sora、HeyGen、ElevenLabs、AG-UI、Generative UI、AI video、短影音等。
- 產文 prompt 補上社群訊號使用規則：社群只作為「今天大家在討論什麼」的提醒，不可直接當事實來源；必須回到官方或可信來源撰寫。
- 產文 prompt 補上 AI 影音工作流判讀：需說明工具改變的是發想、腳本、分鏡、素材、剪輯、版本測試或投放哪一段流程。
- Footer 版本升為 `v0.17.0`，版本日期更新為 2026/08/21。

### Non-scope

- 本版不直接登入或爬 Threads、Instagram、X 等社群平台。
- 本版不把社群貼文內容當作正式新聞來源。
- 本版先採可控的手動 / 半自動社群訊號候選池，後續再評估 API、RSS、公開搜尋或監測工具。

### 驗證

- `python3 -m json.tool config/sources.json >/dev/null`
- `python3 -m py_compile scripts/generate_daily_digest.py scripts/static_site.py`
- `python3 scripts/generate_daily_digest.py --report-date 2026-08-21 --dry-run`
- `/Users/bella2022/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node --check app.js`
- `python3 scripts/static_site.py`
- 確認 2026/08/21 dry-run 候選由 35 則增加為 37 則，並成功選入 Seedance 2.5 與 Claude Managed Agents + AG-UI。

### 對應 commit

- `c5256b7 Add social signal radar for AI daily`

## v0.16.1｜2026-08-19

版本類型：小改版

### 修改原因

Google 已可透過 `site:hibellayu.github.io/bella-ai-signal-daily` 找到網站，但一般搜尋 `Bella's AI 趨勢日報` 時容易被 Bella.tw、Instagram、Threads 等既有內容壓住。問題不是索引被阻擋，而是新站品牌實體訊號與外部關聯還不夠明確。

### 修改內容

- 首頁新增「關於 Bella's AI 趨勢日報」區塊，明確說明本站定位、讀者、內容型態與四層判讀框架。
- 首頁 WebSite structured data 補上 `sameAs`，關聯 Bella.tw、Instagram 與 GitHub 專案。
- structured data 補上 `about` 主題，強化 AI 趨勢日報、數位行銷、品牌策略、內容行銷、AI 搜尋與 GEO 的語意訊號。
- `llms.txt` 補上相關實體、主要站名、英文別名、內容類型與主要讀者。
- Footer 版本升為 `v0.16.1`，版本日期維持 2026/08/19。

### 驗證

- `python3 -m py_compile scripts/generate_daily_digest.py scripts/static_site.py`
- `/Users/bella2022/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node --check app.js`
- `python3 scripts/static_site.py`
- 確認首頁 HTML 已包含「關於 Bella's AI 趨勢日報」、`sameAs`、`Generative Engine Optimization`、`site-identity` 與 Footer `v0.16.1`。

### 對應 commit

- `664c07b Strengthen homepage SEO identity signals`

## v0.16.0｜2026-08-19

版本類型：中改版

### 修改原因

新聞來源盤點後發現，目前日報對中國 AI 生態的覆蓋不足，容易漏掉 Qwen / 千問、豆包、DeepSeek、Kimi、MiniMax、智譜、阿里、騰訊、字節跳動、小紅書等模型、工具、平台與應用動態。AIBase 的公開頁面可讀且 robots 允許抓取，但其日報屬於二次彙整內容，因此應作為補充來源，不可主導整份日報。

### 修改內容

- 新增公開 HTML 列表來源解析能力，支援無 RSS / Atom 的公開列表頁。
- 新增 `AIBase AI News` 補充來源，優先抓取單篇 `/tw/news/{id}`。
- 新增 `AIBase AI Daily` 補充來源，僅作為中國 AI 生態漏網議題的補漏候選。
- 補充來源選文上限調低為 2 則，避免二次彙整或單一來源主導日報。
- 擴充追蹤公司 / 工具與 AI 關鍵字：Qwen、Alibaba、Tencent、ByteDance、Doubao、Zhipu、MiniMax、Xiaohongshu、通義千問、千問、豆包、阿里、騰訊、字節跳動、小紅書、智譜、中國 AI、國產大模型等。
- 產文 prompt 補上中國 AI 生態的判讀規則，要求從模型選型、內容生成工具、社群 / 電商入口、廣告分發與深度工作者工作流角度判斷，不可只因為是中國公司就收錄。
- 更新 PRD 與 README，記錄 AIBase 的補充來源定位與來源風險控管。
- Footer 版本升為 `v0.16.0`，版本日期維持 2026/08/19。

### 驗證

- `python3 -m json.tool config/sources.json >/dev/null`
- `python3 -m py_compile scripts/generate_daily_digest.py scripts/static_site.py`
- `python3 scripts/generate_daily_digest.py --report-date 2026-08-19 --dry-run`
- `python3 scripts/generate_daily_digest.py --report-date 2026-08-20 --dry-run`
- 確認 2026/08/20 dry-run 中 `AIBase AI News` 可進入候選與選文，且補充來源最多只選 2 則。

### 對應 commit

- `a3ea29c Add AIBase supplemental China AI sources`

## v0.15.2｜2026-08-19

版本類型：小改版

### 修改原因

UAT 發現左側資訊卡完全移除主標後，桌機版少了一個能快速辨識當日趨勢主軸的視覺錨點。左側仍需要一個大標題，但不應重複右側「今日策略判讀」的摘要內容。

### 修改內容

- 左側資訊卡在 `Report Info` 下方新增當日日報趨勢大標，來源使用 digest 的 `headline`。
- 左側仍不顯示摘要文字，避免和「今日策略判讀」重複。
- 互動版日期切換時同步更新左側趨勢大標。
- Footer 版本升為 `v0.15.2`，版本日期維持 2026/08/19。

### 驗證

- `python3 -m py_compile scripts/generate_daily_digest.py scripts/static_site.py`
- `/Users/bella2022/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node --check app.js`
- `python3 scripts/static_site.py`
- 確認首頁與 2026/08/19 靜態頁左欄已顯示當日 `headline`，未恢復摘要文字，右側仍保留「今日策略判讀」，Footer 顯示 `v0.15.2`。

### 對應 commit

- `ac9aa67 Restore sidebar trend headline`

## v0.15.1｜2026-08-19

版本類型：小改版

### 修改原因

UAT 發現左側資訊卡的主標與摘要，和內容區新增的「今日策略判讀」重複，造成桌機版視覺焦點分散。既然策略判讀已成為主要內容入口，左側應回到工具型資訊，不再放判讀摘要。

### 修改內容

- 移除左側資訊卡的日報主標與摘要。
- 左側 `Today's Signal` 改為 `Report Info`，保留日期、資料日期、生成時間、本日收錄、判讀框架、收錄優先順序與區塊導覽。
- 互動版 `app.js` 補上左側標題摘要節點不存在時的防呆。
- Footer 版本升為 `v0.15.1`，版本日期維持 2026/08/19。

### 驗證

- `python3 -m py_compile scripts/generate_daily_digest.py scripts/static_site.py`
- `/Users/bella2022/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node --check app.js`
- `python3 scripts/static_site.py`
- 確認首頁與 2026/08/19 靜態頁左欄已改為 `Report Info`，不再出現 `digestTitle` / `digestSummary`，右側仍保留「今日策略判讀」。

### 對應 commit

- `a0a778b Remove duplicate sidebar digest summary`

## v0.15.0｜2026-08-19

版本類型：中改版

### 修改原因

網站已具備四層影響框架與行銷策略選題邏輯，但前台資訊結構仍以日期、收錄順序與新聞區塊為主，讀者不容易在第一眼理解「今天為什麼選這些資訊」以及本站如何把 AI 新聞轉成行銷決策判讀。另有兩個一致性問題：前台固定顯示「收錄上限 10-14 則資訊」容易與實際新聞數混淆，`llms.txt` 的第五項評分邏輯仍寫成來源與時效性，與前台分數彈窗不一致。

### 修改內容

- 內容區最上方新增「今日策略判讀」，從日報摘要或 `strategyTakeaways` 產出 3-4 點決策摘要。
- 側欄新增「判讀框架」，顯示國際事件與產業格局、品牌端、使用者端 / 深度工作者、一般社會大眾四層影響框架。
- 側欄「收錄上限」改為實際收錄數，例如 `新聞判讀 6 則｜應用切角 6 則`。
- 生成 prompt 新增 `strategyTakeaways` 與每則新聞 `impactAngles`，讓未來資料可保留判讀角度。
- 靜態日報頁分數改為可展開的分數拆解，避免 SEO / AI 搜尋主要讀到靜態頁時缺少評分說明。
- 互動版日期篩選排除 `isDemo` / `noindex` 日報，避免測試資料出現在可選日期。
- `llms.txt` 修正第五項評分邏輯為指定追蹤公司 / 工具相關性，並補上四層影響框架。
- Footer 版本升為 `v0.15.0`，版本日期維持 2026/08/19。

### 驗證

- `python3 -m py_compile scripts/generate_daily_digest.py scripts/static_site.py`
- `/Users/bella2022/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node --check app.js`
- `python3 scripts/static_site.py`
- 靜態頁與首頁確認已顯示 `今日策略判讀`、`判讀框架`、`新聞判讀 6 則｜應用切角 6 則` 與 `v0.15.0`。
- 確認 `2026/07/08` demo / noindex 日報未出現在 `daily/index.html` 與 `sitemap.xml`。

### 對應 commit

- 待提交

## v0.14.0｜2026-08-19

版本類型：中改版

### 修改原因

8 月日報盤點發現兩個內容策略問題：部分日期因來源資訊不足而無法產出，且已生成內容雖有 AI 趨勢解讀，但容易偏向產業新聞與品牌能見度議題，與數位行銷、內容行銷、社群、媒體廣告、深度工作者工作流與一般大眾使用情境的關聯不夠穩定。問題核心不只在產文 prompt，而是來源池與候選新聞選題分佈仍偏科技產業媒體。

### 修改內容

- 新增可穩定讀取的行銷、搜尋、社群與國際 AI 來源：Marketing AI Institute、Search Engine Land、Search Engine Roundtable、Social Media Today、The Decoder、AI News、Ars Technica。
- 新增 `ANGLE_TERMS` 與 `ANGLE_LABELS`，將候選新聞標記為國際事件與產業格局、品牌端、使用者端 / 深度工作者、一般社會大眾、數位行銷 / 內容 / 社群 / 廣告等策略角度。
- 新增 `MIN_ANGLE_COVERAGE`，候選選文時優先保留多元角度，避免高分產業新聞或單一來源把每日候選名額全部吃掉。
- 產文 prompt 新增 `angleBuckets`，要求模型依策略角度選題，不可只挑產業格局或品牌能見度新聞。
- PRD 補上行銷 / 搜尋 / 社群來源，以及每日選題需涵蓋多元策略角度的規格。
- Footer 版本升為 `v0.14.0`，版本日期更新為 2026/08/19。

### 驗證

- `python3 -m py_compile scripts/generate_daily_digest.py scripts/static_site.py`
- `python3 -m json.tool config/sources.json >/dev/null`
- `python3 scripts/generate_daily_digest.py --report-date 2026-08-19 --dry-run`
- `python3 scripts/static_site.py`
- 2026/08/19 dry run 收集 37 則 AI 相關候選，選入 18 則；候選新增 Search Engine Land、Search Engine Roundtable、The Decoder、MIT Technology Review 等搜尋、SEO、工作流與國際觀點來源。
- 最終選入候選角度分佈：產業 12、品牌 6、數位行銷 / 內容 / 社群 / 廣告 9、工作流 4、一般大眾 1。

### 對應 commit

- 待提交

## v0.13.1｜2026-07-24

版本類型：小改版

### 修改原因

UAT 發現分數說明彈窗顯示錯誤：前台標示產業重大性、數位行銷影響、內容 / 搜尋 / 社群 / 媒體廣告影響、工具可用性為 0-5 分，指定追蹤公司 / 工具相關性為 0-3 分，但 2026/07/24 重新生成資料中出現 7、8、9、10 等超出量尺的分項，總分也出現 38、49 分。原因是模型在新版生成時改用接近 0-10 制評分，而程式缺少分數範圍驗證與自動校正。

### 修改內容

- 新增 `SCORE_LIMITS`，統一分數規格：四個主要面向 0-5 分，追蹤相關性 0-3 分，總分最高 23 分。
- 新增 `normalize_digest_scores`，生成與修補後會先把模型分數正規化再驗證與寫檔。
- 新增 `validate_digest` 分數檢查：分項必須是整數、不可超出上限、`total` 必須等於分項加總。
- 前台 `app.js` 新增分數顯示防呆，分數 badge 與彈窗都會依正確量尺重新計算。
- 批次校正既有正式日報分數，避免切換舊日期時仍出現超標分數。
- Footer 版本升為 `v0.13.1`，版本日期維持 2026/07/24。

### 驗證

- `python3 -m py_compile scripts/generate_daily_digest.py scripts/static_site.py`
- `python3 scripts/static_site.py`
- 批次檢查所有正式日報分項皆在量尺內，且總分等於五個分項加總。
- 2026/07/24 Claude 語音工具更新分數校正為 `4 + 4 + 4 + 4 + 2 = 18 分`。

### 對應 commit

- `Fix score scale normalization`

## v0.13.0｜2026-07-24

版本類型：中改版

### 修改原因

v0.12.0 擴充 MarTech、Semrush、HubSpot 與 AI visibility 來源後，2026/07/24 日報雖然補到行銷策略訊號，但內容過度集中在品牌能見度與 MarTech 治理，忽略 AI 對國際事件、產業格局、深度工作者工作流與一般大眾使用習慣的影響。日報需要更像行銷主管的策略雷達，而不是單一品牌議題週報。

### 修改內容

- 新增「四層影響框架」作為選題與解讀基準：國際事件與產業格局、品牌端、使用者端 / 深度工作者、一般社會大眾。
- Prompt 明確要求大事件不可被品牌能見度、GEO、MarTech 或工具比較題占滿。
- 大事件若有候選，至少收錄 1 則非純品牌能見度事件，例如平台 / 模型 / 算力 / 資安 / AI Agent 風險 / 語音或健康等大眾入口。
- 工具更新新增工作流視角，要求說明工具如何進入實際工作流程或日常使用，而不是只從品牌採用角度書寫。
- 趨勢區新增跨層歸納要求，至少覆蓋品牌端以外的工作流、大眾使用、治理、算力或平台競爭。
- `scoringPolicy` 補上 `impactFramework`，讓資料檔可回溯本版本的內容判斷框架。
- Footer 版本升為 `v0.13.0`，版本日期維持 2026/07/24。

### 驗證

- `python3 -m py_compile scripts/generate_daily_digest.py scripts/static_site.py`
- `python3 scripts/static_site.py`
- `python3 scripts/generate_daily_digest.py --report-date 2026-07-24 --dry-run`
- 2026/07/24 dry run 仍可收集 19 則候選、送 18 則進入生成，候選同時包含品牌能見度、MarTech、Claude 語音、OpenAI Health、AegisAI 資安、Gemini 用戶規模與 AMD / NVIDIA 算力題。

### 對應 commit

- `Add four-layer impact framework`

## v0.12.1｜2026-07-24

版本類型：小改版

### 修改原因

v0.12.0 重新觸發 2026/07/24 日報時，來源擴充與候選選文已生效，但模型在初稿、重寫與一次修補後，仍有 1 則趨勢的 Now What 未達 60 字發布門檻，導致整份日報停止發布。這不是來源問題，而是修補層對小型文字深度問題的容錯不足。

### 修改內容

- 修補次數由 1 次提高為 2 次。
- 修補 prompt 補強 Now What 過短時的重寫規格：90-120 字、兩句以內、保留明確數量、起始素材與完成產出。
- Footer 版本升為 `v0.12.1`，版本日期維持 2026/07/24。

### 驗證

- `python3 -m py_compile scripts/generate_daily_digest.py scripts/static_site.py`
- `python3 scripts/generate_daily_digest.py --report-date 2026-07-24 --dry-run`

### 對應 commit

- `Add second digest repair attempt`

## v0.12.0｜2026-07-24

版本類型：中改版

### 修改原因

2026/07/24 與另一份 AI 日報對照後發現，本站已能自動產出日報，但候選新聞池偏向大型科技媒體與大平台事件，較少收錄 MarTech、AI 搜尋能見度、品牌內容信任、CRM / 客服自動化與工具治理等更貼近行銷決策的題材。問題核心不在版面或產文深度，而是上游來源與評分邏輯仍以泛 AI 新聞為主，導致行銷應用訊號容易被產業大新聞擠掉。

### 修改內容

- 新增來源：MarTech、Semrush Blog、HubSpot Marketing Blog、OpenAI News、Google AI Blog。
- 擴充追蹤實體：HubSpot、Semrush、Substack、Samsung、AMD、NVIDIA、Moonshot AI、Kimi、DeepSeek。
- 擴充 AI 與行銷策略關鍵字：AI Agent、MarTech、CRM、GEO、Generative Engine Optimization、AI visibility、brand visibility、內容透明、AI governance、開源模型、GPU、算力等。
- 選文評分新增行銷策略訊號加權，讓 AI 搜尋、品牌能見度、MarTech 工具、內容信任、客服 / CRM 自動化、資安治理與供應鏈風險更容易進入候選。
- 新增來源多樣性選文邏輯，避免同一天候選被單一媒體或單一平台事件過度占滿。
- 修正英文關鍵字命中方式，避免 `AI` 誤命中 achievement、available 等單字片段，降低不相關文章進入候選的風險。
- Prompt 補上「多來源同事件合併」與「行銷決策訊號」判讀規則，降低重複收錄並強化品牌、內容、搜尋、社群、媒體廣告與團隊流程的策略解讀。
- Footer 版本升為 `v0.12.0`，版本日期更新為 2026/07/24。

### 驗證

- 來源 RSS 連線測試：MarTech、Semrush Blog、HubSpot Marketing Blog、OpenAI News、Google AI Blog 可讀取。
- 2026/07/24 dry run 候選由 11 則提升為 19 則，新增 MarTech、Semrush Blog、HubSpot Marketing Blog 等行銷相關候選，並排除英文 `AI` 片段誤命中的不相關文章。

### 對應 commit

- `Improve marketing source selection`

## v0.11.0｜2026-07-15

版本類型：中改版

### 修改原因

2026/07/15 排程有成功執行，也收集到 23 則 AI 候選新聞，但第二次重寫後仍有 1 則新聞的 `analysis` 未達「2 段且每段至少 70 字」標準，導致整份日報被品質閘門擋下。原設計只有初稿與一次完整重寫，對可修正的小型文字深度問題缺少最後修補層，造成內容接近合格但無法出刊。

### 修改內容

- 新增 `repair_digest_with_openai`：當初稿與完整重寫仍未通過時，將目前 JSON、候選新聞與驗證錯誤交給高階模型做最後修補。
- 修補 Prompt 明確要求保留既有中繼資料、只依候選新聞修正、補齊 analysis / What / So What / Now What 與六大應用切角。
- 保留品質閘門：修補後仍不合格才停止發布，不降低內容標準。
- Workflow 自動提交範圍補上 `index.html`，確保 SEO 版首頁會跟著每日最新日報更新。
- Footer 版本升為 `v0.11.0`，版本日期更新為 2026/07/15。

### 驗證

- `python3 -m py_compile scripts/generate_daily_digest.py scripts/static_site.py`
- `python3 scripts/static_site.py`
- 手動回補 2026/07/15 日報並確認正式站 latest 更新。

### 對應 commit

- `Add digest repair pass`

## v0.10.0｜2026-07-12

版本類型：中改版

### 修改原因

網站已具備基本 sitemap、robots、GA4 與靜態日報頁，但根首頁仍以 JavaScript 載入內容，搜尋摘要容易抓到「載入中」與空狀態文字；同時缺少 favicon 與社群分享預覽圖，連結分享時品牌識別不足。為了讓網站更容易被搜尋引擎與 AI 搜尋工具理解，需要把最新日報內容預先輸出在首頁，並補齊分享與結構化資料。

### 修改內容

- `scripts/static_site.py` 新增根首頁產生流程，首頁會預渲染最新一日日報內容，JavaScript 仍保留日期篩選互動。
- 每日靜態頁、日報列表與首頁新增 `meta keywords`、`og:image`、`twitter:image` 與 `summary_large_image`。
- Article / WebSite / CollectionPage JSON-LD 新增 `image`、`keywords` 與更明確的 `about` 主題資料。
- 每日 description 自動壓縮，避免搜尋結果摘要過長。
- 新增品牌 favicon：`assets/favicon.svg`、`assets/favicon-32.png`、`assets/apple-touch-icon.png`、`assets/icon-512.png`。
- 新增社群分享預覽圖：`assets/og-image.png`，尺寸為 1200 x 630。
- Footer 版本升為 `v0.10.0`，靜態資源版本升為 `20260712a`。

### 驗證

- `python3 -m py_compile scripts/static_site.py`
- `python3 scripts/static_site.py`
- 確認首頁、日報列表與 2026/07/12 日報頁皆有 favicon、OG image、Twitter image、keywords 與 JSON-LD image。
- 確認首頁 HTML 不再包含「載入中」作為初始內容。
- 確認圖片尺寸：favicon 32 x 32、apple touch icon 180 x 180、OG image 1200 x 630。

### 對應 commit

- `Add SEO preview assets`

## v0.9.1｜2026-07-12

版本類型：小改版

### 修改原因

2026/07/12 日報的應用切角只產出品牌策略、數位行銷、內容行銷與團隊流程，缺少社群應用與媒體廣告；2026/07/11 也缺少團隊流程。原因不是當天完全沒有可延伸的社群、廣告或流程脈絡，而是原規格允許模型從六大面向中選 4 至 6 個，導致模型把部分面向併入數位行銷或其他分類，未獨立呈現行銷人需要的完整判讀框架。

### 修改內容

- 應用切角改為固定產出六大面向：品牌策略、數位行銷、內容行銷、社群應用、媒體廣告、團隊流程。
- Prompt 明確要求即使當天沒有直接對應某個面向的新聞，也要從當日 AI 趨勢推論該面向的行銷應用變化。
- 品質驗證器新增固定六面向檢查，缺少任一面向或多出非標準面向都會停止發布。
- 補齊 2026/07/11 日報的團隊流程應用切角。
- 補齊 2026/07/12 日報的社群應用與媒體廣告兩個應用切角。
- Footer 版本升為 `v0.9.1`。

### 驗證

- `python3 -m py_compile scripts/generate_daily_digest.py scripts/static_site.py`
- `python3 - <<'PY' ... validate_digest(...)`
- `python3 scripts/static_site.py`
- 確認 2026/07/10、2026/07/11、2026/07/12 應用切角皆包含完整六大面向。

### 對應 commit

- `Require all application angles`

## v0.9.0｜2026-07-12

版本類型：中改版

### 修改原因

2026/07/11 與 2026/07/12 首次由正式 API 自動生成後，雖然 JSON 欄位、內容數量與來源皆符合技術驗證，但 What / So What / Now What 退化為短句與泛泛建議，應用切角也變成逐則新聞摘要。原流程只驗證格式存在，沒有把策略深度納入發布條件，造成「自動化成功」與「內容可用」之間的落差。

### 修改內容

- 強化 Prompt，明確定義 What 的結構變化、So What 的角色與連鎖影響、Now What 的原子行動要素。
- Now What 必須包含明確起點、具體數量、實際動作與可見產出，不接受只有「檢視、評估、探索、嘗試」的泛泛建議。
- 應用切角固定從品牌策略、數位行銷、內容行銷、社群應用、媒體廣告與團隊流程選擇，並要求跨新聞統整。
- 新增文字長度、段落、具體數量、固定應用面向、來源重複等品質檢查。
- 第一次生成未通過品質閘門時，將錯誤原因交給模型完整重寫一次；第二次仍不合格則停止發布。
- 深度內容輸出較長，OpenAI 請求逾時由 90 秒調整為 240 秒，避免完整回應尚未返回就中止流程。
- 依首次正式驗證校準品質規則：Now What 最低發布門檻為 70 字，Prompt 目標仍維持 80–180 字；趨勢區可引用其他區塊來源進行跨事件歸納，但同一區塊不得重複來源湊數。
- So What 的最低發布門檻校準為 60 字，Prompt 目標仍維持 75–180 字；避免已具角色與連鎖影響的內容因少量字數差異被誤擋，舊版短句仍無法通過。
- 採用分級模型策略：第一版維持 `gpt-4.1-mini`；只有品質不合格時，第二版才使用 `gpt-4.1` 完整重寫，避免為了讓小模型通過而持續降低內容標準。
- Prompt 加入 2026/07/10 已確認內容作為合格深度範例，讓模型學習策略推論層次與原子行動顆粒度；API 明確提供 16,000 tokens 輸出空間，避免長篇 JSON 區塊不完整。
- Now What 最低發布門檻最終校準為 60 字，並同時保留明確數量、實際動作與可見產出的結構檢查；生成目標仍維持 80–180 字。
- Now What 新增任意期限檢查，禁止「幾天內、幾週內、幾個月內」等人為截止時間；行動改以明確起點與完成產出驅動。
- 任意期限檢查補齊「小時、日、天、週、月」格式；2026/07/12 的 6 則具體行動經人工編輯，改以可見產出作為完成標準。
- Footer 版本升為 `v0.9.0`。
- 重新生成 2026/07/11 與 2026/07/12 日報。

### 驗證

- `python3 -m py_compile scripts/generate_daily_digest.py scripts/static_site.py`
- 2026/07/10 人工深化內容可通過新品質閘門。
- 舊版 2026/07/11、2026/07/12 內容會因策略深度不足而被品質閘門拒絕。
- 重新生成兩日日報後，確認所有內容通過品質閘門、靜態頁可讀取且正式站 manifest 最新日期正確。

### 對應 commit

- `Add strategy quality gates to daily digest`

## v0.8.0｜2026-07-12

版本類型：中改版

### 修改原因

原本的 GitHub Actions 手動執行只能產生執行當天的日報，無法回補因金鑰缺失而漏刊的 2026/07/11。為了讓自動化具備可維運性，需要讓同一套正式流程支援指定日期重跑。

### 修改內容

- `Daily AI Signal` 手動執行新增 `report_date` 欄位，格式為 `YYYY-MM-DD`。
- 有填日期時產生指定日報；未填時維持產生當日日報。
- README 補上 06:30 排程緩衝與指定日期回補方式。
- Footer 版本升為 `v0.8.0`，版本日期維持 2026/07/12。

### 驗證

- Workflow YAML 可解析。
- 不填 `report_date` 時仍呼叫預設生成流程。
- 填入 `report_date` 時會傳入 `--report-date` 產生指定日期。
- 依序以正式 GitHub Actions 回補 2026/07/11 與 2026/07/12，結果記錄於本版本後續調整。

### 對應 commit

- `Add dated digest backfill workflow`

### 後續驗證結果

- 2026/07/12 完成 OpenAI API 額度設定後，指定日期回補流程已可正常呼叫 `gpt-4.1-mini`。
- 2026/07/11 日報成功生成 10 則內容：大事件 4 則、工具更新 1 則、值得追蹤的趨勢 1 則、應用切角 4 則。
- 2026/07/12 日報成功生成 13 則內容：大事件 4 則、工具更新 2 則、值得追蹤的趨勢 2 則、應用切角 5 則。
- GitHub Pages 部署成功；正式站 manifest 的最新日期為 2026/07/12，兩日靜態頁與 sitemap 皆可正常讀取。
- OpenAI API 採用手動預付額度，自動加值維持關閉；額度用完時 workflow 會因 API quota 錯誤明確失敗。

## v0.7.1｜2026-07-12

版本類型：小改版

### 修改原因

2026/07/11 與 2026/07/12 的 GitHub Actions 排程皆有執行，但因 repository 未設定 `OPENAI_API_KEY`，產生器跳過發布後仍回傳成功，造成 workflow 顯示綠燈、正式站卻停在 7/10。此外，自動提交範圍只包含日報 JSON，沒有涵蓋每日靜態頁、日報列表與 sitemap。

### 修改內容

- 排程由台北時間 07:00 提前至 06:30 啟動，預留 GitHub Actions 延遲與 Pages 部署時間。
- Workflow 新增 `OPENAI_API_KEY` 前置檢查；未設定時直接失敗並顯示明確錯誤。
- 產生器遇到 API Key 缺失、候選內容不足或空日報時改為非零退出，不再顯示假成功。
- 自動提交範圍擴大為日報 JSON、每日靜態頁、日報列表與 `sitemap.xml`。
- Footer 版本升為 `v0.7.1`，版本日期更新為 2026/07/12。
- 更新 README、PRD 與 VERSIONING。

### 驗證

- `python3 -m py_compile scripts/generate_daily_digest.py scripts/static_site.py`
- 無 `OPENAI_API_KEY` 執行產生器時，流程以非零狀態結束且不修改日報資料。
- `python3 scripts/static_site.py` 可重建每日靜態頁、日報列表與 sitemap。
- Workflow YAML 可解析，且提交範圍包含 `data/digests/*.json`、`daily` 與 `sitemap.xml`。

### 對應 commit

- `Fix daily digest automation failures`

## v0.7.0｜2026-07-10

版本類型：中改版

### 修改原因

網站已開始做 SEO 與 AI 搜尋引用，需要補上資料來源與內容使用風險控管，避免日報摘要或示範資料被搜尋引擎視為正式新聞內容，也降低內容過度接近來源表達的風險。

### 修改內容

- 來源摘要送入模型前改為短截取，上限為 220 字元。
- 產文 prompt 新增版權風險控管規則：不得複製來源文章句子、不得翻譯來源段落、必須以行銷策略觀點重新撰寫。
- 新增 `docs/COPYRIGHT_RISK_POLICY.md`，記錄來源引用、摘要、示範資料、SEO 收錄與下架修正流程。
- Footer 新增內容使用聲明，說明本站是趨勢整理、評論與行銷應用解讀，新聞來源與原文著作權屬各原媒體與作者所有。
- 將 2026/07/08 與 2026/07/09 示範日報標記為 `isDemo: true`、`noindex: true`。
- 靜態頁產生器排除 `isDemo` 與 `noindex` 日報，讓示範資料不進入 `/daily/` 列表、每日靜態頁與 sitemap。
- Footer 版本升為 `v0.7.0`。
- 更新 README、PRD、VERSIONING 與 `llms.txt`。

### 驗證

- `python3 scripts/static_site.py`
- `python3 -m py_compile scripts/static_site.py scripts/generate_daily_digest.py`
- `sitemap.xml` XML 可解析，且只包含首頁、`/daily/` 與正式日報 `/daily/2026-07-10/`。
- `/daily/2026-07-09/` 已不再產生，示範日報不進 SEO 靜態頁。

### 對應 commit

- `Add copyright and source risk controls`

### 後續調整

- 依使用者要求，重新將 2026/07/09 日報納入靜態頁、日報列表與 sitemap。
- 2026/07/08 空示範資料仍維持 `isDemo` / `noindex`，不進入 SEO 靜態頁。

## v0.6.0｜2026-07-10

版本類型：中改版

### 修改原因

每日靜態頁已上線，但還需要一個穩定的內容索引入口，讓讀者、Google 與 AI 搜尋工具能從列表頁發現所有有效日報，形成更完整的內部連結結構。

### 修改內容

- 新增日報列表頁：`/daily/`。
- 列表頁顯示所有有效日報的日期、主標、摘要與區塊數量。
- 列表頁加入 CollectionPage structured data。
- 首頁 Header 新增「日報列表」連結。
- 每日靜態頁 Header 新增「日報列表」與「互動版日報」導覽。
- `sitemap.xml` 新增 `/daily/` 條目。
- Footer 版本升為 `v0.6.0`。
- 更新 README、PRD 與 VERSIONING。

### 驗證

- `python3 scripts/static_site.py`
- `python3 -m py_compile scripts/static_site.py scripts/generate_daily_digest.py`
- `/daily/index.html` structured data JSON 可解析。
- `sitemap.xml` XML 可解析，且包含 `/daily/`、`/daily/2026-07-10/`、`/daily/2026-07-09/`。
- 空日報 `2026-07-08` 未進入列表與 sitemap。

### 對應 commit

- `338f1c6 Add daily archive page for SEO`

## v0.5.0｜2026-07-10

版本類型：中改版

### 修改原因

網站已完成 GA4 與 Search Console 基礎設定，但日報主要內容仍由前端 JavaScript 讀取 JSON 後渲染。為了提升 Google 收錄與 AI 搜尋引用機率，需要讓每份日報都有可直接讀取的靜態 HTML 頁。

### 修改內容

- 新增 `scripts/static_site.py`，由日報 JSON 產生每日靜態頁。
- 產生每日頁路徑：`/daily/YYYY-MM-DD/`。
- 每日頁包含完整日報內容、來源連結、評分、What / So What / Now What 與應用切角。
- 每日頁加入獨立 title、description、canonical、Open Graph、Twitter Card、GA4 tag 與 Article structured data。
- `sitemap.xml` 改為由腳本產生，收錄首頁與有效每日頁。
- 空日報不產生靜態頁、不進 sitemap，避免形成薄內容。
- 自動化日報產生器在成功寫入 JSON 與 manifest 後，會同步重建靜態頁與 sitemap。
- Footer 版本升為 `v0.5.0`。
- manifest title 由 `Bella's AI Signal` 改為 `Bella's AI 趨勢日報`。

### 驗證

- `python3 scripts/static_site.py`
- `python3 -m py_compile scripts/static_site.py scripts/generate_daily_digest.py`
- 每日頁 structured data JSON 可解析。
- `sitemap.xml` XML 可解析。
- 產生 `daily/2026-07-10/index.html` 與 `daily/2026-07-09/index.html`。
- 空日報 `2026-07-08` 未進入 sitemap。

### 對應 commit

- `769fb29 Add static daily pages for SEO`

## v0.4.0｜2026-07-10

版本類型：中改版

### 修改原因

開始讓網站具備被搜尋、被 AI 搜尋理解與被 GA4 量測的基礎條件。這次新增的能力會影響網站曝光、資料分析與後續內容成長判斷，因此升為中改版。

### 修改內容

- 在 GA4 個人帳戶 `夏日時光` 下建立 `Bella's AI 趨勢日報` GA4 資源。
- 建立 Web stream：`https://hibellayu.github.io/bella-ai-signal-daily/`。
- 導入 GA4 Measurement ID：`G-8CQ9L4MXNL`。
- 補上 SEO head：title、description、robots、canonical、Open Graph、Twitter Card。
- 新增 WebSite structured data，協助搜尋引擎理解網站定位。
- 新增 `robots.txt`，允許搜尋引擎索引並指向 sitemap。
- 新增 `sitemap.xml`，先收錄首頁。
- 新增 `llms.txt`，說明網站定位、內容結構、評分邏輯與引用建議。
- Footer 版本升為 `v0.4.0`。
- 更新 README、PRD 與 VERSIONING 版本說明。

### 驗證

- GA4 Web stream 已建立，Measurement ID 為 `G-8CQ9L4MXNL`。
- `index.html` 已包含 GA4 tag 與 SEO metadata。
- `robots.txt`、`sitemap.xml`、`llms.txt` 已建立。
- 下一階段需等待 GitHub Pages 部署後，以正式網址確認 head、GA4 tag 與新檔案可被讀取。

### 對應 commit

- `8ef4e0d Add GA4 and SEO discovery foundation`

## v0.3.3｜2026-07-10

版本類型：小改版

### 修改原因

需要讓讀者理解每則新聞分數的來源，同時將品牌主標改成更直覺的中文定位，降低 `Signal` 一詞造成的理解成本。

### 修改內容

- Header 品牌主標改為 `Bella's AI 趨勢日報`。
- 英文副標維持 `Daily brief for marketing decisions`，並在手機版顯示。
- 桌機版品牌主標字級加大一級。
- 每則新聞分數旁新增 `i` icon。
- 點擊 `i` icon 會開啟分數說明彈窗，包含評分規則與該則新聞各項分數加總。
- Footer 版本升為 `v0.3.3`。

### 驗證

- Header 顯示 `Bella's AI 趨勢日報`。
- 手機版不再隱藏英文副標。
- 分數旁顯示 `i` icon，點擊可看到該則新聞分數拆解與總分公式。

### 對應 commit

- `ec225d1 Add score explanation dialog and rename brand`

## v0.3.2｜2026-07-10

版本類型：小改版

### 修改原因

Footer 原本使用「更新日期」，容易和日報日期、資料日期或生成時間混淆。改成「版本日期」，明確表示這是網站版本推送日期。

### 修改內容

- Footer 文案改為：`© 2026 Bella Yu. All rights reserved. Codex 協作開發｜版本 v0.3.2｜版本日期 2026/07/10`。
- 版本由 `v0.3.1` 升為 `v0.3.2`。
- 更新 PRD 與 VERSIONING 目前版本說明。

### 驗證

- Footer 顯示 `版本 v0.3.2｜版本日期 2026/07/10`。
- Header 維持不顯示版本資訊。

### 對應 commit

- `ce74ba6 Clarify footer version date`

## v0.3.1｜2026-07-10

版本類型：小改版

### 修改原因

Header 中間的版本資訊在電腦版閱讀體驗上干擾品牌與日期篩選動線；手機版雖可接受，但為了維持一致性，改為電腦與手機都統一放在 Footer。

### 修改內容

- 移除 Header 版本資訊。
- Footer 改為統一顯示 copyright、Codex 協作資訊、版本號與更新日期。
- 版本由 `v0.3.0` 升為 `v0.3.1`。
- 更新 PRD 與版本規則目前版本說明。

### 驗證

- 前台 Header 不再顯示版本資訊。
- Footer 顯示 `© 2026 Bella Yu. All rights reserved. 本站由 Codex 協作開發｜v0.3.1｜更新日期 2026/07/10`。

### 對應 commit

- `c88c2b0 Move version metadata to footer`

## v0.3.0｜2026-07-10

版本類型：中改版

### 修改原因

開始落實正式自動化生成流程，避免每日排程只產生空白日報骨架。同時補上網站版本資訊與版權資訊，方便管理與辨識目前網站狀態。

### 修改內容

- 新增 Header 版本資訊：`本站由 Codex 協作開發｜v0.3.0｜更新日期 2026/07/10`。
- 新增 Footer copyright：`© 2026 Bella Yu. All rights reserved. 本站由 Codex 協作開發。`
- 新增 `VERSIONING.md`，定義大改版、中改版、小改版規則。
- 新增 `config/sources.json`，管理新聞來源、追蹤公司與 AI 關鍵字。
- 重寫 `scripts/generate_daily_digest.py`，建立 feed 收集、日期過濾、初步評分、OpenAI 產文、JSON 品質檢查與發布流程。
- 更新 GitHub Actions，支援 `OPENAI_API_KEY` 與可選 `OPENAI_MODEL`。
- 補上防呆：沒有 API key、候選新聞不足、AI 產文失敗或 JSON 不合格時，不發布空日報。

### 驗證

- `python3 -m json.tool config/sources.json`
- `python3 -m py_compile scripts/generate_daily_digest.py`
- `python3 scripts/generate_daily_digest.py --report-date 2026-07-10 --dry-run`
- 無 `OPENAI_API_KEY` 時確認不會覆蓋既有日報。
- GitHub Pages 部署成功。
- 正式站確認 Header / Footer 顯示正常。

### 對應 commit

- `4d1abc5 Add automated AI digest generation pipeline`

### 後續提醒

- 需在 GitHub repository secrets 設定 `OPENAI_API_KEY`，下一次排程才會真正進入 AI 產文。
- `數位時代` 與 `AI 郵報` 尚未有穩定公開來源，暫時停用；後續可改用搜尋 API 或確認 feed 後啟用。

## v0.2.2｜2026-07-10

版本類型：小改版

### 修改原因

Now What 的「本週行動」語氣太像高層級目標，行動門檻偏高。調整為「具體行動」，並用原子習慣邏輯降低開始難度。

### 修改內容

- `Now What` 中文標題由「本週行動」改為「具體行動」。
- 7/9、7/10 日報的 `nowWhat` 改為小步、低負擔、可立即開始的行動建議。
- PRD 補充 Now What 內容原則：不使用「本週可以做什麼」作為固定句型，優先設計第一步行動。

### 驗證

- JSON 格式檢查通過。
- `app.js` 語法檢查通過。
- 正式站確認不再顯示「本週行動」。

### 對應 commit

- `b7dad14 Refine Now What into atomic actions`

## v0.2.1｜2026-07-10

版本類型：小改版

### 修改原因

GitHub Actions 成功產生 7/10 日報，但內容為空，造成首頁顯示 0 則資訊。需要立即補內容並加入空日報防呆。

### 修改內容

- 補上 2026-07-10 日報內容。
- 新增空日報不上線防呆：產生器若沒有任何 section items，不寫入日報、不更新 manifest。
- 新增 `docs/AUTOMATION_POSTMORTEM_2026-07-10.md`，記錄空資料事件根因與後續改善方向。

### 驗證

- JSON 格式檢查通過。
- Python 語法檢查通過。
- 本機與正式站確認 7/10 日報不再是空內容。

### 對應 commit

- `e36ee02 Fix empty 7/10 digest and add publish guard`

## v0.2.0｜2026-07-09

版本類型：中改版

### 修改原因

網站初版完成後，需要建立更明確的個人品牌感、閱讀質感與日報內容深度。

### 修改內容

- 調整整體配色為深灰、棕色與深紅重點色。
- 調整桌機與手機字級規格。
- 來源媒體名稱改為直接連到文章來源。
- 移除單一「查看來源」按鈕。
- What / So What / Now What 增加中文寓意標題。
- 應用切角改為條列式呈現。
- 內容語氣由 Bella 個人視角改為行銷人與品牌決策者視角。

### 驗證

- 正式站多輪視覺與文案檢查通過。
- GitHub Pages 部署成功。

### 對應 commit

- `51f2077 Refine digest copy for marketing strategists`
- `6e894f7 Reduce sidebar typography scale`
- `e9d353a Tune sidebar and application typography`
- `f1a2a12 Adjust briefing typography hierarchy`
- `9f45147 Refine typography and source links`
- `bdff930 Apply dark editorial visual system`

## v0.1.0｜2026-07-09

版本類型：中改版

### 修改原因

建立 Bella's AI Signal Daily 的 MVP，先完成可閱讀的靜態網站與日報資料結構。

### 修改內容

- 建立靜態網站首頁。
- 建立年 / 月 / 日篩選。
- 建立日報 JSON 與 manifest 結構。
- 建立四個內容區塊：大事件、工具更新、值得追蹤的趨勢、應用切角彙整。
- 預留 GitHub Actions 每日 07:00 自動更新流程。

### 驗證

- 本機網站可開啟。
- 日期篩選可切換。
- GitHub Pages 可部署。

### 對應 commit

- 初始 MVP 相關 commits。
