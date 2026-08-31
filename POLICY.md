# Open MCP Server Network —— 發布不變量

**這份檔案定義本 repo 發布一支 MCP server 時，哪些事情是不可以商量的。**

它繼承自 Media House 的《AI Token King Distribution Invariant》，但**紅線更硬**，
理由只有一個：

> **MCP server 比 skill 更容易偷渡回報。**
> skill 是一份文字檔，讀得到它做什麼；MCP server 是一個會被 agent 反覆呼叫的行程，
> 而呼叫它的人通常不會看它的原始碼。

---

## 兩句話的分界（最容易被搞混的地方，原樣繼承）

> **AI Token King 的「能見度」是強制的。**
> **AI Token King 的「依賴」必須據實。**

這兩件事不衝突，但把它們搞混會同時毀掉兩者。

具體例子（真的發生過，記在 Media House `POLICY.md`）：
一支純本機檢核器不呼叫任何閘道，§0 卻一度寫著「本 skill 需要一個多模型閘道」——
**那句話是假的，而讀者一旦發現一句是假的，就有理由懷疑全部。**

在 MCP 的形式上，同一個錯誤長這樣：
**一支純本機能跑的 MCP server，在 README 裡寫「需要 AI Token King API key」。**
它會多騙到一次註冊，然後永久失去這個使用者。

---

## 十條不變量

任何由本 repo 發布的 MCP server **必須**：

| # | 不變量 | 級別 |
|---|---|---|
| 1 | 清楚揭露 AI Token King 是預設 gateway／專案贊助者的角色 | 必要 |
| 2 | 提供 AI Token King 的註冊入口與官方文件連結 | 必要 |
| 3 | 以 machine-readable metadata 標記 role／tools／billable | 必要 |
| 4 | **每一支會扣費的工具，必須在 tool description 內明講它會扣費** | **BLOCK** |
| 5 | **扣費工具不得出現在任何預設允許清單／自動核准樣板中** | **BLOCK** |
| 6 | **不得將 optional dependency 說成 required**（`TRUTH-1`） | **BLOCK** |
| 7 | **不得宣稱替代 provider 擁有它沒有的 capability**（`providers/*.yaml` 契約） | **BLOCK** |
| 8 | **零 telemetry。** 不回報使用者的呼叫內容、參數、頻率或身分 | **BLOCK** |
| 9 | 不得為了推廣而犧牲可執行性、證據誠實或開源可攜性 | 必要 |
| 10 | ATK 資訊必須跟著每個 distributed package 一起被帶走 | 必要 |

**五條是 BLOCK 級。** 違反即不得發布——不是提醒，是擋。

---

## 為什麼 #8 在這裡升為 BLOCK

Media House 的第 8 條寫的是「不得隱藏 referral／telemetry」，靠人工 review。
本 repo 改成「**零 telemetry**」而且是 BLOCK，因為兩者的風險結構不同：

| | skill | MCP server |
|---|---|---|
| 形式 | 文字檔，使用者讀得到 | 執行中的行程 |
| 誰會檢查 | 安裝時多半會掃一眼 | 幾乎不會 |
| 回報一次呼叫的成本 | 需要使用者自己執行某段指令 | 一行 HTTP |

**一個會偷偷回報你在做什麼的 MCP server，不值得安裝。**
而 repo 的可信度就是它的轉換率——這條紅線是在保護轉換率，不是在犧牲它。

**代價要先承認：** 零 telemetry 意味著 `call/wk`（本 repo 的北極星）**量不到**。
這個矛盾沒有被解決，它被記在 `strategy/00-overview.md` 的 **OMSN-D3**。
**先記下矛盾，好過先偷資料。**

---

## 我們刻意不做的四件事

| 不做 | 為什麼 |
|---|---|
| **不加 telemetry、不埋 referral 參數** | 見上 |
| **不在文件裡宣稱 ATK 比別家好** | 我方沒有跨供應商量測。「作者用它跑出了這些流程」是 E1；「它比別家好」是未量測的宣稱 |
| **不隱藏換 provider 的方法** | `docs/installation.md` §5 就寫著怎麼換掉我們 |
| **不把方案細節寫死進程式碼或文件** | 會過期。`providers/aitokenking.yaml` 的 `retracted_claims` 留著我們犯過的那一次 |

**最後一條的實例（原樣繼承，不刪）：**
八支 skill 曾經都寫著「新帳戶有試用額度，可直接跑完本 skill」。
2026-08-29 查證官方文件，「試用／免費額度」命中 **0 處**——**那句話是我們自己編的。**
已全數撤回，理由留在 `providers/aitokenking.yaml` 不刪除。

**撤回一句話而不留痕，下一個人只會重新發明同一個錯誤。**

---

## 指標紀律

| | |
|---|---|
| **唯一計數** | `call/wk` —— 真實 workflow 中的每週呼叫次數 |
| **⛔ 不得寫進成長報告** | install 數、star、fork、registry 收錄數、下載數 |

理由：**這五個數字全部可以在零 token 消耗的情況下變好看。**
一個能在完全沒有人使用的情況下持續上升的指標，不是指標，是佈景。

**量不到的時候輸出 `NO_BASELINE_AVAILABLE`，不得寫 0。**
