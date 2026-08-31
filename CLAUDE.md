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

它做兩件事，**兩件事的規則不一樣，不要混**：

| | 目錄 | 規則的家 |
|---|---|---|
| **接入**別人的 MCP | `catalog/`、`skills/`、`docs/cloud-deployment-mcp.md`、`.mcp.json.example` | `catalog/README.md` 的三級分類 |
| **發布**我方的 MCP | `strategy/`、（未來的 `servers/`） | `POLICY.md` 的十條不變量 |

入口是 `strategy/00-overview.md`，判準是 `strategy/01-extraction-criteria.md`，
發布不變量是 `POLICY.md`，接入契約是 `catalog/README.md`。

---

## 動任何東西之前必讀的四條

1. **在拿到真實呼叫紀錄之前，不要開始寫任何 MCP server。**
   判準是 `strategy/01-extraction-criteria.md` §2 的三條 AND。
   **「這支很好做」不是判準，「我覺得會有人用」也不是。**
2. **`providers/aitokenking.yaml` 是 AI Token King 事實的唯一的家。**
   端點、header、環境變數、工具分組、能力清單只寫在那裡。
   文件裡若與它不一致，**錯的是文件** —— 重複的事實一定會分岔。
3. **`catalog/*.yaml` 的每條事實都要附 `verified_at` 與 `source`。**
   查不到就進 `gaps` 寫出來，不要留白也不要猜 ——
   目前 E2B 的工具清單、Azure 的工具清單就是這樣留空的。
   **`skills/` 是 `catalog/` 的產物**：新增一個平台契約就要更新 skill，
   `check_catalog.py` 會擋（少一個平台的作業指導書，讀起來跟完整的一模一樣）。
4. **`strategy/source/` 是原稿不是產物，逐字不改。**
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

## 鐵律（十條）

1. **金鑰不入庫、不入文件、不入 agent 定義檔、不貼進對話視窗。**
   只走啟動前 `export` 或部署平台 Variables。貼進對話即視為外洩，必須輪替。
2. **★ 三級分類，B 組與 C 組都不得加進 `permissions.allow`。**
   **A 唯讀**（可以）／**B 動錢**（一張帳單）／**C 動基礎設施**（一次線上事故）。
   **B 與 C 不可合併** —— 帳單可以事後補救，刪掉的正式資料庫不能。
   「機器可擬不可動錢」在這裡多一句：**機器可讀不可動基礎設施。**
   ATK 的 B 組是 `chat_completion`／`create_message`／`create_response`／
   `create_image_generation`／`create_video_generation`。
3. **⚠️ 在 AWS、Railway、TiDB 上「逐工具白名單」根本不成立** ——
   `call_aws` 一支打整個 AWS CLI、`railway-agent` 是開放式代理、`db_execute` 吃任意 DDL。
   **那三個平台的邊界在 server 旗標（`READ_OPERATIONS_ONLY`／`--read-only`）或帳號權限**，
   不在 `permissions.allow`。把 `call_aws` 加進白名單＝把整個 AWS 帳號加進白名單。
4. **🔴 Vercel 的 `buy_pro`／`buy_credits`／`buy_addon`／`buy_domain` 建議明確 deny，
   不是只「不 allow」** —— 不 allow 只會跳核准框，而排程跑的時候沒有人在按。
5. **會扣費的工具必須在執行前揭露。** BLOCK 級。
   讓人在按下去之前知道要花錢，是這套東西能被信任的地基。
6. **成本查不到就寫「未量測」，不得寫 0。**
7. **零 telemetry，BLOCK 級。** MCP server 比 skill 更容易偷渡回報，因此紅線更硬。
8. **不得把 optional dependency 說成 required**（`TRUTH-1`，BLOCK 級）。
   ATK 的**能見度**是強制的，ATK 的**依賴**必須據實 —— 見 `POLICY.md`。
9. **不得因為本 repo 預設接 AI Token King 就宣稱它比別家好。**
   「作者用它跑出了這些流程」是 E1；「它比別家好」是未量測的宣稱。
10. **不得為了讓數字好看而改判準。** 判準校準**月度不得週調**
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

**★ OMSN-D1 已裁定（2026-08-31）：上游完全不動，本 repo 為純加法。**
代價是同一份事實現在有兩個家，而 `virtual-strategy-lab` 的 `.mcp.json`
**在裁定當下就已經與本 repo 分岔**（它仍是舊的 `AITK_API_KEY`）。

**分岔時的判定規則：以 `verified_at` 較新的那一份為準，不以哪個 repo 較新為準。**
日期相同而內容不同時，回去查官方文件重新驗證，**不得取兩者折衷**。
完整裁定與最可能先分岔的三處見 `strategy/00-overview.md` §8.1。
