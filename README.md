# Bella's AI Signal Daily

給行銷人與品牌決策者使用的 AI 趨勢行動日報網站。每天上午 7 點整理 AI 產業與工具資訊，並轉譯成數位行銷、品牌策略、內容行銷、社群經營與媒體廣告可用的策略判斷與行動建議。

## 專案特色

- 以「日報日期」做年 / 月 / 日篩選。
- 支援桌機與手機閱讀。
- 內容分為大事件、工具更新、值得追蹤的趨勢、應用切角彙整。
- 每則重點提供 What / So What / Now What。
- 每份日報新增 AEO 內容欄位：`answerSummary`、`promptTargets`、`aeoEntities`、`citationClaims`，讓內容不只被搜尋引擎收錄，也更容易被 AI 搜尋理解與引用。
- 自動產文必須通過策略深度品質閘門：What 解釋結構變化、So What 分析角色與連鎖影響、Now What 提供具體數量與可見產出；未通過會自動重寫一次，仍不合格則停止發布。
- 第一版使用 `gpt-4.1-mini` 控制成本；只有未通過品質閘門時，才改用 `gpt-4.1` 重寫，以兼顧日常費用與策略內容穩定度。
- 應用切角固定從品牌策略、數位行銷、內容行銷、社群應用、媒體廣告與團隊流程跨新聞統整，不逐則重述新聞。
- 預留 GitHub Actions 每天 07:00 台北時間自動更新。

## 本機開啟

```bash
cd /Users/bella2022/Desktop/Bella-Agent/bella-ai-signal-daily
python3 -m http.server 4173
```

打開：

```text
http://localhost:4173
```

## 資料格式

- `data/digests/manifest.json`：日報清單。
- `data/digests/YYYY-MM-DD.json`：每日完整內容。
- `config/sources.json`：自動化新聞來源、追蹤公司與 AI 關鍵字設定。來源支援 RSS / Atom，也支援少量公開 HTML 列表來源作為補充。
- `VERSIONING.md`：版本號、大改版、中改版、小改版規則。
- `CHANGELOG.md`：版本記錄與修改內容回溯。
- `docs/COPYRIGHT_RISK_POLICY.md`：版權、來源引用、示範資料與 SEO 收錄風險控管規則。
- `docs/AEO_MEASUREMENT_PLAYBOOK.md`：AEO 成效驗證框架與每月追蹤方式。
- `data/aeo/prompt-library.json`：AEO Prompt Library 初始假設版，整理可追蹤的使用者提問與意圖分群，後續需經跨 Answer Engine 測試再升級成正式追蹤版。
- `robots.txt`：搜尋引擎索引規則。
- `sitemap.xml`：搜尋引擎提交用 sitemap。
- `llms.txt`：給 AI 搜尋與研究工具讀取的網站定位、內容結構與引用說明。
- `daily/index.html`：日報列表頁，提供所有有效日報的回查入口。
- `daily/YYYY-MM-DD/index.html`：每日靜態 HTML 頁，提供搜尋引擎與 AI 搜尋工具直接讀取。
- `scripts/static_site.py`：由日報 JSON 產生日報列表頁、每日靜態頁與 sitemap。

## 自動更新

`.github/workflows/daily-digest.yml` 預設每天 UTC 22:30 執行，對應台北時間 06:30，為 GitHub 排程與 Pages 部署預留緩衝。流程會抓取來源 feed / 公開 HTML 列表、篩選 AI 相關新聞、用 OpenAI API 生成日報 JSON，再提交到 GitHub Pages。

需要回補特定日期時，可在 GitHub Actions 手動執行 `Daily AI Signal`，並於 `report_date` 輸入 `YYYY-MM-DD`。未填日期時，流程會產生當日日報。

需要在 GitHub repository secrets 設定：

```text
OPENAI_API_KEY
```

可選擇在 GitHub repository variables 設定：

```text
OPENAI_MODEL
```

若沒有候選新聞、沒有 `OPENAI_API_KEY` 或 AI 產文未通過品質檢查，流程會失敗並保留上一份有效日報，不會發布空日報。GitHub Actions 會顯示紅燈，避免把「未發布」誤判為成功。

每日排程會在台北時間 06:30 啟動，預留 GitHub Actions 排程延遲與部署時間，目標是在 07:00 前完成。成功生成後會一併提交日報 JSON、每日靜態頁、日報列表與 `sitemap.xml`。

生成內容遵循來源風險控管：RSS / Atom 摘要只截取短片段供判斷，產文不可複製或翻譯來源段落，並以行銷策略觀點重新撰寫。示範日報與標記 `noindex` 的資料不會進入每日靜態頁與 sitemap。

產生有效日報後，流程會同步重建：

- `daily/YYYY-MM-DD/index.html`
- `daily/index.html`
- `sitemap.xml`

目前 `數位時代` 與 `AI 郵報` 尚未啟用自動抓取：`數位時代` 公開 RSS 於 2026-07-10 測試回傳 404，`AI 郵報` 尚未設定穩定公開來源。後續可改用搜尋 API 或確認穩定 feed 後重新啟用。

AIBase 已作為補充來源，用來補中國 AI 模型、工具、平台與應用生態。`AIBase AI News` 優先收單篇新聞，`AIBase AI Daily` 僅作為補漏候選；選文時會降低單一補充來源上限，避免二次彙整內容主導整份日報。

## 搜尋與分析

- 正式網址：https://hibellayu.github.io/bella-ai-signal-daily/
- 每日靜態頁會輸出 `Article` structured data 與來源 citation；AEO Prompt 與可引用摘要保留在資料層，不直接顯示成前台技術區塊。
- AEO 驗證採用 `Prompt -> Visibility -> Citation -> Referral -> Conversion` 框架，不以單一 Prompt 或單一 Answer Engine 判斷成敗。
- GA4 Measurement ID：`G-8CQ9L4MXNL`
- SEO 基礎設定：title、description、canonical、Open Graph、Twitter Card、structured data。
- AI 搜尋引用輔助：`llms.txt`。
- 日報列表頁：`/daily/`。
- 每日靜態頁：`/daily/YYYY-MM-DD/`。
- 內容使用聲明：本站內容為 AI 趨勢整理、評論與行銷應用解讀；新聞來源與原文著作權屬各原媒體與作者所有。若需完整內容，請閱讀原文。
- 目前 GA4 會先收集網站到訪、頁面瀏覽、捲動與外連點擊等資料。若要在前台顯示每日到訪人數，下一階段需串接 GA4 Data API，並透過 GitHub Actions 產生公開 JSON。

手動重建靜態頁：

```bash
python3 scripts/static_site.py
```
