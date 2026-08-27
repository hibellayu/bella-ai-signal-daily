# AEO 成效驗證與內容優化手冊

建立日期：2026-08-27（台北時間）

## 目的

Bella's AI 趨勢日報的 AEO 目標不是只增加關鍵字，而是讓 Answer Engine 在回答行銷人常見問題時，能理解本站定位、信任內容來源，並在適合情境中引用每日靜態頁。

## 核心框架

```text
Prompt -> Visibility -> Citation -> Referral -> Conversion
```

- Prompt：要追蹤的是真實使用者提問，不只是關鍵字。
- Visibility：AI 回答中是否出現本站或 Bella's AI 趨勢日報。
- Citation：AI 是否把本站頁面列為來源。
- Referral：GA4 是否看得到 AI 來源流量。
- Conversion：目前先以回訪、閱讀日報、點擊來源連結與案例展示使用為主要結果。

## 每月驗證方式

每月選 10-20 個 Prompt，分別到 Google AI、ChatGPT、Perplexity、Gemini 測試。

記錄欄位：

- 測試日期
- Engine
- Prompt
- Intent
- 是否出現 Bella's AI 趨勢日報
- 出現位置：主要答案、來源之一、順帶提及、未出現
- 是否引用 URL
- 引用頁：首頁、日報列表、每日靜態頁
- AI 回答摘要
- GA4 是否有對應 referral
- 下一步內容修正

## 內容調整原則

- 每份日報必須先回答「今天 AI 趨勢對行銷人有什麼影響？」
- 每份日報必須保留 5-8 個 `promptTargets`，讓內容可對應真實提問。
- 每份日報必須保留 `answerSummary`，作為 AI 搜尋可引用摘要。
- 每份日報必須保留 `citationClaims`，把觀點接回來源支撐重點。
- 每則新聞必須有 `citationClaim`，避免只有評論而缺少可驗證主張。

## 判讀提醒

單一 Prompt 沒有被引用，不代表 AEO 失敗；單一 Engine 引用，也不代表 AEO 成功。需要用 Prompt Cluster 與跨 Engine 觀察，累積趨勢後再判斷。
