# Bella's AI Signal Daily

給行銷人與品牌決策者使用的 AI 趨勢行動日報網站。每天上午 7 點整理 AI 產業與工具資訊，並轉譯成數位行銷、品牌策略、內容行銷、社群經營與媒體廣告可用的策略判斷與行動建議。

## 專案特色

- 以「日報日期」做年 / 月 / 日篩選。
- 支援桌機與手機閱讀。
- 內容分為大事件、工具更新、值得追蹤的趨勢、應用切角彙整。
- 每則重點提供 What / So What / Now What。
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
- `config/sources.json`：自動化新聞來源、追蹤公司與 AI 關鍵字設定。
- `VERSIONING.md`：版本號、大改版、中改版、小改版規則。
- `CHANGELOG.md`：版本記錄與修改內容回溯。
- `robots.txt`：搜尋引擎索引規則。
- `sitemap.xml`：搜尋引擎提交用 sitemap。
- `llms.txt`：給 AI 搜尋與研究工具讀取的網站定位、內容結構與引用說明。

## 自動更新

`.github/workflows/daily-digest.yml` 預設每天 UTC 23:00 執行，對應台北時間 07:00。流程會抓取來源 feed、篩選 AI 相關新聞、用 OpenAI API 生成日報 JSON，再提交到 GitHub Pages。

需要在 GitHub repository secrets 設定：

```text
OPENAI_API_KEY
```

可選擇在 GitHub repository variables 設定：

```text
OPENAI_MODEL
```

若沒有候選新聞、沒有 `OPENAI_API_KEY` 或 AI 產文未通過品質檢查，流程會停止並保留上一份有效日報，不會發布空日報。

目前 `數位時代` 與 `AI 郵報` 尚未啟用自動抓取：`數位時代` 公開 RSS 於 2026-07-10 測試回傳 404，`AI 郵報` 尚未設定穩定公開來源。後續可改用搜尋 API 或確認穩定 feed 後重新啟用。

## 搜尋與分析

- 正式網址：https://hibellayu.github.io/bella-ai-signal-daily/
- GA4 Measurement ID：`G-8CQ9L4MXNL`
- SEO 基礎設定：title、description、canonical、Open Graph、Twitter Card、structured data。
- AI 搜尋引用輔助：`llms.txt`。
- 目前 GA4 會先收集網站到訪、頁面瀏覽、捲動與外連點擊等資料。若要在前台顯示每日到訪人數，下一階段需串接 GA4 Data API，並透過 GitHub Actions 產生公開 JSON。
