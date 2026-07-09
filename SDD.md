# Bella's AI Signal Daily SDD

建立日期：2026-07-09（台北時間）

## 系統定位

本專案是獨立於既有 `bella-ai-news` 的個人 AI 趨勢日報網站，資料夾名稱為 `bella-ai-signal-daily`。第一版採用靜態網站架構，讓 GitHub Pages 或任意靜態主機都能部署。

## 模組

- `index.html`：網站入口與基本結構。
- `styles.css`：響應式版面與視覺樣式。
- `app.js`：讀取 manifest、日期篩選、日報渲染。
- `data/digests/manifest.json`：可用日報日期索引。
- `data/digests/YYYY-MM-DD.json`：每日結構化日報。
- `scripts/generate_daily_digest.py`：每日產生或補齊日報資料的入口腳本。
- `.github/workflows/daily-digest.yml`：每日 07:00 台北時間排程。

## 資料流

1. GitHub Actions 在 UTC 23:00 執行，對應台北時間 07:00。
2. 腳本計算日報日期。
3. 腳本產生 `data/digests/YYYY-MM-DD.json`。
4. 腳本更新 `data/digests/manifest.json`。
5. GitHub Actions commit 變更。
6. 靜態網站讀取 manifest，預設顯示最新日報。

## 日期邏輯

- UI 篩選使用「日報日期」。
- `reportDate` 是日報產出日，例如 `2026-07-09`。
- `coverageDate` 是主要新聞資料日期，例如 `2026-07-08`。
- 台灣媒體可依 `coverageDate 00:00-23:59` 收集。
- 國際媒體直接依來源網站顯示的發布日期篩選，不做時區換算。

## 資料 Schema

每日 JSON 主要欄位：

- `reportDate`
- `coverageDate`
- `generatedAt`
- `headline`
- `summary`
- `sourcePolicy`
- `trackedEntities`
- `scoringPolicy`
- `sections`

每則事件主要欄位：

- `title`
- `summary`
- `analysis`
- `sources`
- `score`
- `tags`
- `what`
- `soWhat`
- `nowWhat`

`sources` 應使用陣列，並明確顯示媒體名稱：

- `name`：媒體名稱，例如 iThome、數位時代、TechCrunch。
- `publishedDate`：來源發布日期。
- `url`：來源連結。

前端需將每個媒體名稱直接渲染成各自連結，不使用單一「查看來源」按鈕。

`analysis` 用於較完整的觀點闡述，至少 1-2 段，避免只複述新聞摘要。

`applications` 區塊以前端條列方式呈現，不使用一般新聞卡片。

## 前端狀態

- `availableDigests`：manifest 內所有日報日期。
- `selectedDate`：目前選擇的日報日期。
- `currentDigest`：目前渲染的日報內容。

## 錯誤狀態

- manifest 載入失敗：顯示資料讀取失敗。
- 選定日期無資料：顯示這天還沒有 AI 日報。
- 單篇 JSON 載入失敗：顯示該日報尚未建立或讀取失敗。

## 高風險區域

- 各新聞網站抓取格式不同，後續需逐步接 RSS、官方 API 或搜尋 API。
- 自動摘要需避免長篇複製原文，必須以解讀與短摘要為主。
- GitHub Actions 若沒有設定 token 或權限，可能無法自動 commit。
