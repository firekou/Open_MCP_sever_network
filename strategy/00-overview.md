# Open MCP Server Network —— 策略總覽（canonical）

**專案代號：** `OMSN`｜**建立日：** 2026-08-31｜**狀態：** 策略已遷入，**尚未發布任何 MCP server**
**節點：** Execution —— 六節點鏈（Discovery → Workflow → **Execution** → Model Decision → Cost Decision → Routing）裡的第三個
**上游評級：** S+（15 案兵推第一，五維中唯一同時拿到「關鍵節點 5」與「距 Token 5」）
**上游 Phase：** 4（**排序正確，不得提前** —— 理由見 §3）

---

## §1 一句話

**Skill 告訴 Agent「怎麼做」，MCP 提供 Agent「真正可以做什麼」。**

MCP 的優勢不是 install，是 **recurring call**：

```
install once → call → call → call → call → call
```

一次安裝之後的每一次呼叫都更靠近實際 token 消耗，**比單次內容曝光更接近持續消費**。
這是它被評 S+ 的唯一理由，也是本 repo 存在的唯一理由。

---

## §2 這個 repo 從哪裡來

| | |
|---|---|
| 策略母體 | `firekou/aitokenking_mediahouse` 的 `OPEN_SOURCE_LEVERAGE_STRATEGY_REVIEW_2026-08-30.md`（600 行／15 案兵推 → Top 5） |
| 落地判定 | `firekou/virtual-strategy-lab` 的 `projects/atk-leverage-infrastructure/01-mcp-network.md`（ATKL S1） |
| 閘道與設定 | 同兩 repo 的 `providers/aitokenking.yaml`、`scripts/setup-aitokenking.sh`、`docs/aitokenking-mcp-service.md` |
| 遷入日 | 2026-08-31 |

**上游兩份原文以死快照保存在 `strategy/source/`，逐字不改。**
本檔案與 `01`／`02` 是**產物**：它們把散在兩個 repo、面向不同讀者的內容
收斂成一份「在這個 repo 裡要怎麼做」。**原稿與產物說的不一樣時，錯的是產物。**

**為什麼要獨立成 repo：**
上游那份策略同時管五條線（Skill 分發／Benchmark／Workflow Factory／Cost Engine／MCP Network），
而 MCP 是五條裡**唯一需要發布可執行伺服器**的一條——它有版本、有 registry 登錄、有
呼叫端相容性、有安全邊界，這些東西放在一個以「skill 產線」為主體的 repo 裡會長不出來。

---

## §3 ★ 為什麼不得提前

上游 Phase 4 的理由：

> **不要一次做大量 MCP。先從 Phase 3 的 workflow 中「最常被重複呼叫、
> 且多個 workflow 都會需要」的能力抽成 MCP。**
> 這可以避免做出**沒有真實使用需求的 MCP**。

**我方補充的理由，是本 repo 最該記住的一句：**

> **一支沒人呼叫的 MCP，在 registry 上與一支有人呼叫的長得一模一樣。**

它會讓我們誤以為 Execution 節點已經佔住了。
**Install 數是虛榮指標，`call/wk` 才是這條的真實指標。**

### 抽取判準（不得憑感覺選要做哪一支）

```
候選 = 在真實 workflow 執行紀錄中被呼叫 ≥ 20 次／週
      且 ≥ 2 個不同 Stage 都會用到
      且 不需要新蓋能力（已在手）
```

**在拿到呼叫次數之前，本 repo 不指定要做哪一支 MCP。**
上游列的六個候選是**候選不是決定**：

```text
video-transcript-mcp
creator-research-mcp
social-content-mcp
model-price-mcp
token-usage-mcp
prompt-cost-mcp
```

**⚠️ 唯一例外：`model-price-mcp` 與 `token-usage-mcp` 的資料我方已經有了**
（平台快照 109 個模型定價 ＋ `list_usage` 明細），若成本引擎自用版做完，這兩支的邊際成本極低——
**但仍須先看呼叫數才決定是否發布。邊際成本低不是需求存在的證據。**

詳細判準與分期見 `strategy/01-extraction-criteria.md`。

---

## §4 指標

| | 指標 | 說明 |
|---|---|---|
| **北極星** | `call/wk` | 真實 workflow 中的每週呼叫次數。**這是唯一計數的東西** |
| 輔助 | 呼叫該 MCP 的**不同 workflow 數** | 一個 workflow 呼叫 100 次 ≠ 100 個 workflow 各呼叫 1 次 |
| ⛔ 虛榮指標 | install 數、star、fork、registry 收錄數、下載數 | **這五個全部可以在零 token 消耗的情況下變好看** |

**現況一律輸出 `NO_BASELINE_AVAILABLE`，刻意不寫 0** —— 0 看起來像量測結果，
「還沒有量測」才是事實。本 repo 至今發布過的 MCP server 數為 **0**（見 §6 缺口 OMSN-G1）。

---

## §5 路徑對映（上游相對路徑 → 本 repo）

上游兩份快照裡的相對路徑指向它們原本的 repo，在這裡不成立。對照如下：

| 上游寫的 | 本 repo |
|---|---|
| `.mcp.json` 的 `aitokenking` | `.mcp.json`（同名，金鑰環境變數已改 canonical 名稱） |
| `docs/aitokenking-mcp-service.md` | `docs/aitokenking-mcp-service.md`（同路徑） |
| `providers/aitokenking.yaml` | `providers/aitokenking.yaml`（同路徑） |
| `scripts/mcp/setup-global-mcp.sh` | `scripts/setup-aitokenking.sh` |
| Media House `skills/aitokenking-setup/` | `docs/installation.md`（同內容，改寫成文件不是 skill） |
| `platform-snapshot-*.json`（109 模型定價） | **未遷入**，仍在 `virtual-strategy-lab/ai-radar/`（見 OMSN-G4） |

---

## §6 缺口（不隱藏；沿用上游編號並新增本 repo 的）

| ID | 缺口 | 來源 |
|---|---|---|
| **OMSN-G1** | **我方尚未發布過任何 MCP server。** 發布、版本化、registry 登錄流程全部未走過 | 上游 ATKL-G9 |
| **OMSN-G2** | MCP registry 的分發效果**無任何我方數據，屬假設** | 上游 ATKL-G10 |
| **OMSN-G3** | recurring call 若發生在**別人的 gateway** 上，我方拿不到任何 token 消耗。`role: optional` 是誠實的，但也意味著這條的轉換**有上限** | 上游 ATKL-G11 |
| **OMSN-G4** | 抽取判準要的「呼叫次數」目前**沒有任何來源**——上游 Phase 3 workflow 尚未跑滿 4 週，我方手上一筆真實呼叫紀錄都沒有 | 本 repo 新增 |
| **OMSN-G5** | 上游 §4.1 的六個候選 MCP **沒有一個做過需求驗證**，它們是提案時想出來的名字 | 本 repo 新增 |
| **OMSN-G6** | 抽取判準的 `≥ 20 次／週` **沒有外部依據**，是我方設的起點（見 `01` §6） | 本 repo 新增 |
| **OMSN-G7** | 「≥ 2 個不同 Stage」的 Stage 定義來自 Media House 產線分層，跨 workflow 不一定可比 | 本 repo 新增 |
| **OMSN-G8** | MCP 三段式握手繞道腳本 `aitk_mcp_call.sh` **未遷入**，仍在 `virtual-strategy-lab` | 本 repo 新增 |

**OMSN-G4 是本 repo 現在最該解的一個，而它的解法不是寫程式。**
在沒有呼叫紀錄之前開始寫 MCP，等於用「我覺得會有人用」取代判準——
**那正是判準存在要防的事。**

---

## §7 紅線

發布任何 MCP server 之前，四條硬規則逐條過（完整版見 `POLICY.md`）：

| # | 規則 |
|---|---|
| 1 | **扣費工具必須在執行前揭露**，且不得預設允許 |
| 2 | **不得把 optional 依賴說成 required**（`TRUTH-1`） |
| 3 | **不得宣稱替代 provider 擁有它沒有的能力** |
| 4 | **零 telemetry** —— MCP server 比 skill 更容易偷渡回報，**因此紅線更硬** |

---

## §8 待決（本 repo 獨立發展的入口）

| ID | 待決事項 | 誰決定 |
|---|---|---|
| **OMSN-D1** | 本 repo 與 Media House／virtual-strategy-lab 的資產歸屬邊界（哪些留原地、哪些只留指標） | Frank |
| **OMSN-D2** | 在沒有 Phase 3 呼叫紀錄的情況下，是否先做一支**已知需求**的 MCP 作為流程探針（目的是走一次發布與 registry 登錄，不是佔節點） | Frank + Edwin |
| **OMSN-D3** | `call/wk` 在零 telemetry 前提下**怎麼量** —— 這是 attribution 命門在本 repo 的具體形式 | Edwin（Jet 覆核） |
| **OMSN-D4** | 是否沿用上游六個候選名稱，或等呼叫紀錄出來後重新命名 | Edwin |

**OMSN-D3 是四個裡唯一會推翻北極星的一個。**
零 telemetry 是不可讓步的紅線，而 `call/wk` 需要知道有人呼叫過——
**在解掉這個矛盾之前，`call/wk` 是一個我們同意採用但量不到的指標。**
