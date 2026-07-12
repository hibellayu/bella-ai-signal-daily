# Bella's AI Signal Daily 版本記錄

本檔案用來記錄每次版本調整的原因、修改內容與回溯資訊。版本號規則請參考 `VERSIONING.md`。

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
