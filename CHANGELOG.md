# Bella's AI Signal Daily 版本記錄

本檔案用來記錄每次版本調整的原因、修改內容與回溯資訊。版本號規則請參考 `VERSIONING.md`。

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

- `73e2395 Add GA4 and SEO discovery foundation`

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
