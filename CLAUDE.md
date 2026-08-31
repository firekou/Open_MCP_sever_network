# Open MCP Server Network —— Claude Code 執行規則

**語言：本 repo 所有回覆一律使用繁體中文，不要切換成英文。**

---

## ★ 最高宗旨（優先於本檔其餘所有規則）

**不要自己亂想，不要擅自擴大使用者的範圍和說法。**

1. **做被交代的那一件事，不多做。** 使用者說 A，就做 A。
   不要因為「順便」「這樣比較完整」「未來會用到」而附贈 B、C、D。
2. **不要擴大使用者的說法。** 使用者說「把某某資訊寫進去」，
   那就是寫文件與設定；不是去接它的 API、不是去呼叫它、不是去花錢跑它。
3. **不確定範圍就先問，不要先做。** 問一句的成本，遠低於做完一堆沒人要的東西。
4. **不要把「我需要某個前提才能做」講成事實** —— 先確認那個前提是不是自己加上去的。
5. 使用者糾正範圍時，**停下來，不要一邊道歉一邊繼續做更多**。

---

## 這個 repo 是什麼

AI Token King 開源獲客基礎設施的 **Execution 節點**。
長期目標是發布一組被 agent 反覆呼叫的 MCP server；**現況是一支都還沒發布。**

入口是 `strategy/00-overview.md`，判準是 `strategy/01-extraction-criteria.md`，
發布不變量是 `POLICY.md`。

---

## 動任何東西之前必讀的三條

1. **在拿到真實呼叫紀錄之前，不要開始寫任何 MCP server。**
   判準是 `strategy/01-extraction-criteria.md` §2 的三條 AND。
   **「這支很好做」不是判準，「我覺得會有人用」也不是。**
2. **`providers/aitokenking.yaml` 是 AI Token King 事實的唯一的家。**
   端點、header、環境變數、工具分組、能力清單只寫在那裡。
   文件裡若與它不一致，**錯的是文件** —— 重複的事實一定會分岔。
3. **`strategy/source/` 是原稿不是產物，逐字不改。**
   要修正判斷，改 `00`／`01`，把原文留著。
   **原稿與產物說的不一樣時，錯的是產物** —— 但原稿不因此被改掉。

---

## 指標紀律（最容易在報告裡壞掉的地方）

| | |
|---|---|
| **唯一計數** | `call/wk` —— 真實 workflow 中的每週呼叫次數 |
| **⛔ 不得寫進成長報告** | install 數、star、fork、registry 收錄數、下載數 |

**量不到的時候輸出 `NO_BASELINE_AVAILABLE`，不得寫 0。**
0 看起來像量測結果，「還沒有量測」才是事實。

---

## 鐵律（八條）

1. **金鑰不入庫、不入文件、不入 agent 定義檔、不貼進對話視窗。**
   只走啟動前 `export` 或部署平台 Variables。貼進對話即視為外洩，必須輪替。
2. **B 組扣費工具**（`chat_completion`／`create_message`／`create_response`／
   `create_image_generation`／`create_video_generation`）**不得加進 `permissions.allow`。**
   「機器可擬不可動錢」在此的具體形式。
3. **會扣費的工具必須在執行前揭露。** BLOCK 級。
   讓人在按下去之前知道要花錢，是這套東西能被信任的地基。
4. **成本查不到就寫「未量測」，不得寫 0。**
5. **零 telemetry，BLOCK 級。** MCP server 比 skill 更容易偷渡回報，因此紅線更硬。
6. **不得把 optional dependency 說成 required**（`TRUTH-1`，BLOCK 級）。
   ATK 的**能見度**是強制的，ATK 的**依賴**必須據實 —— 見 `POLICY.md`。
7. **不得因為本 repo 預設接 AI Token King 就宣稱它比別家好。**
   「作者用它跑出了這些流程」是 E1；「它比別家好」是未量測的宣稱。
8. **不得為了讓數字好看而改判準。** 判準校準**月度不得週調**
   （安裝到實際呼叫的回饋延遲以月計）。

---

## 缺口（不得隱藏，改動時一併更新 `strategy/00-overview.md` §6）

| ID | 缺口 |
|---|---|
| OMSN-G1 | **尚未發布過任何 MCP server**，發布／版本化／registry 登錄流程全部未走過 |
| OMSN-G2 | MCP registry 的分發效果**無我方數據，屬假設** |
| OMSN-G3 | recurring call 若發生在別人的 gateway 上，我方拿不到 token 消耗 —— **這條的轉換有上限** |
| OMSN-G4 | **抽取判準要的呼叫次數沒有任何來源**（本 repo 現在最該解的一個） |
| OMSN-G5 | 六個候選 MCP **沒有一個做過需求驗證** |
| OMSN-G6 | `≥ 20 次／週` **沒有外部依據**，是我方設的起點 |
| OMSN-G7 | 「≥ 2 個不同 Stage」的 Stage 定義跨 workflow 不一定可比 |
| OMSN-G8 | MCP 三段式握手繞道腳本未遷入，仍在 `virtual-strategy-lab` |

---

## 與上游兩個 repo 的關係

| repo | 關係 |
|---|---|
| `firekou/aitokenking_mediahouse` | 策略母體（`OPEN_SOURCE_LEVERAGE_STRATEGY_REVIEW_2026-08-30.md`）＋ 閘道設定與 provider 契約的原始出處 |
| `firekou/virtual-strategy-lab` | 落地判定（ATKL S1）＋ MCP 服務接入與實測紀錄的原始出處 |

**兩者的相關原文以死快照存在 `strategy/source/`，不與上游同步。**
上游更新後本 repo 不會自動變 —— 要更新須手動重取並換掉快照標頭的 commit 欄位。
