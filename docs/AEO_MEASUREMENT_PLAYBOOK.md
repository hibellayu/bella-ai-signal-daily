# AEO 成效驗證與內容優化手冊

建立日期：2026-08-27（台北時間）

## 目的

Bella's AI 趨勢日報的 AEO 目標不是只增加關鍵字，而是讓 Answer Engine 在回答行銷人常見問題時，能理解本站定位、信任內容來源，並在適合情境中引用每日靜態頁。

## Prompt Library 狀態

目前 `data/aeo/prompt-library.json` 是 `v0.1 初始假設版`，不是最終版。

這版 Prompt Library 是依三個來源建立：

- AEO 方法：從 Keyword Thinking 轉向 Intent + Prompt Thinking。
- 網站定位：給行銷人、品牌決策者、內容行銷、社群與媒體廣告工作者閱讀。
- 內容主題：AI 搜尋、AEO、GEO、品牌能見度、AI Agent、AI 影音、內容行銷、社群應用、媒體廣告與行銷工作流。

因此它的角色是「測試假設」，不是已驗證策略。後續要透過跨 Answer Engine 測試與 GA4 referral 觀察，才決定哪些 Prompt 保留、合併、刪除或擴充。

## Prompt Library 設計流程

1. 定義想被誰找到：行銷人、品牌決策者、內容工作者、社群經營者、媒體廣告工作者。
2. 定義他們會問 AI 的真實問題，而不是只列關鍵字。
3. 將問題分成 intent cluster：Informational、Commercial、Comparison、Brand、Problem / Solution、Use Case。
4. 每個 cluster 先放 3-5 題作為假設，避免一開始就建立太大的清單。
5. 每月選 10-20 題跨 Google AI、ChatGPT、Perplexity、Gemini 測試。
6. 根據 Visibility、Citation、Referral、Conversion 決定下一版 Prompt Library。

## 升級成 v1 的條件

- Bella 已確認目標受眾與提問情境。
- 每個 intent cluster 至少有 5 題，且不是同義句堆疊。
- 至少完成 1 輪跨 Answer Engine 測試。
- 每題都有 Visibility / Citation / Referral 記錄。
- 能指出哪些 Prompt 真的有機會讓本站被看見或引用。

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
