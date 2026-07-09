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

## 自動更新

`.github/workflows/daily-digest.yml` 預設每天 UTC 23:00 執行，對應台北時間 07:00。第一版腳本會產生日報資料骨架，後續可接 RSS、搜尋 API 或 AI 生成流程。
