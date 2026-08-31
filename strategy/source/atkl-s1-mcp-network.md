# 上游原文死快照 —— ATKL S1 · Open MCP Server Network

> **這份檔案是原稿不是產物。逐字保存，不改寫、不補充、不與上游同步。**
>
> | | |
> |---|---|
> | 來源 repo | `firekou/virtual-strategy-lab` |
> | 來源檔案 | `projects/atk-leverage-infrastructure/01-mcp-network.md` |
> | 上游 commit | `f3eb7fd` |
> | 取用日 | 2026-08-31 |
> | 性質 | 兌心科技對上游 §4.1 的落地判定（ATKL 專案 S1 條） |
>
> **原文中的相對路徑指向 `virtual-strategy-lab`，在本 repo 內不成立。**
> 對應關係見 `strategy/00-overview.md` §5。

---

# S1 · Open MCP Server Network — Execution 節點

**上游評級：** S+（長期第一級戰略資產）｜**上游 Phase：** 4
**我方判定：** 排序正確，**不得提前**——理由見 §3｜**Owner：** Edwin（R）／Alice（A）／Jet（C，扣費工具）

---

## §1 借的勢

**Skill 告訴 Agent「怎麼做」，MCP 提供 Agent「真正可以做什麼」。**

MCP 的優勢不是 install，是 **recurring call**：

```
install once → call → call → call → call → call
```

一次安裝之後的每一次呼叫都更靠近實際 token 消耗，
**比單次內容曝光更接近持續消費**。這是它被評 S+ 的唯一理由。

---

## §2 兌心現有零件

| 零件 | 實際位置 | 說明 |
|---|---|---|
| **已接入的 MCP** | `.mcp.json` 的 `aitokenking`（`https://api.aitokenking.com.tw/mcp`） | 14 支工具，金鑰走 `${AITK_API_KEY}` **不入庫** |
| A 組唯讀 9 支 | 已列入 `permissions.allow` | `list_models`／`get_model`／`get_balance`／`list_usage`／任務輪詢 |
| B 組扣費 5 支 | **刻意不自動允許** | `chat_completion`／`create_message`／`create_response`／圖片與影片生成 |
| 實測紀錄 | `docs/aitokenking-mcp-service.md` §5 | curl 作為 MCP client 全通；`get_balance` 前後相減粒度到小數第三位 |

**★ 我方已經是 MCP 的使用者，不是零起點。** 要做的是從「用別人的」變成「發布自己的」。

---

## §3 ★ 為什麼不得提前到 Phase 1–3

上游 Phase 4 的理由寫得很清楚，我方完全同意並加一條：

> **不要一次做大量 MCP。先從 Phase 3 的 workflow 中「最常被重複呼叫、
> 且多個 workflow 都會需要」的能力抽成 MCP。**
> 這可以避免做出**沒有真實使用需求的 MCP**。

**我方補充的理由：一支沒人呼叫的 MCP，在 registry 上與一支有人呼叫的長得一模一樣。**
它會讓我們誤以為 Execution 節點已經佔住了。
**Install 數是虛榮指標，`call/wk` 才是這條的真實指標。**

→ **抽取判準（Phase 3 跑滿 4 週後才計算）：**

```
候選 = 在 workflow 執行紀錄中被呼叫 ≥ 20 次／週
      且 ≥ 2 個不同 Stage 都會用到
      且 不需要新蓋能力（已在手）
```

**在拿到 Phase 3 的呼叫次數之前，本條不指定要做哪一支 MCP。**
上游列的六個候選（`video-transcript-mcp`／`creator-research-mcp`／`social-content-mcp`／
`model-price-mcp`／`token-usage-mcp`／`prompt-cost-mcp`）**是候選不是決定**。

**⚠️ 唯一例外：`model-price-mcp` 與 `token-usage-mcp` 的資料我方已經有了**
（`platform-snapshot` 109 個模型定價 ＋ `list_usage` 明細），
**若 S5 自用版做完，這兩支的邊際成本極低**——但仍須先看 Phase 3 呼叫數才決定是否發布。

---

## §4 發布 MCP 的四條硬規則

| # | 規則 | 為什麼 |
|---|---|---|
| 1 | **扣費工具必須在執行前揭露**，且不得預設允許 | 上游不變量④（`AITK-BILL`，BLOCK 級）＋ 兌心鐵律「機器可擬不可動錢」 |
| 2 | **不得把 optional 依賴說成 required** | `TRUTH-1`（BLOCK 級）。純本機能跑的工具就寫純本機能跑 |
| 3 | **不得宣稱替代 provider 擁有它沒有的能力** | `providers/*.yaml` 契約 |
| 4 | **零 telemetry** | MCP server 比 skill 更容易偷渡回報，**因此紅線更硬** |

---

## §5 探針與缺口

```
探針（Phase 3 之後，1 週）：
  只做「呼叫次數盤點」——不寫任何 MCP。
  從 Phase 3 的 4 週執行紀錄算出上面那個候選公式的結果。
判準：能不能指出一支 call/wk ≥ 20 的能力。指不出來 → 本條延後，不是硬做。
成本：0
```

| 缺口 | 說明 |
|---|---|
| **ATKL-G9** | **我方尚未發布過任何 MCP server**，發布、版本化、registry 登錄流程全部未走過 |
| **ATKL-G10** | MCP registry 的分發效果無任何我方數據，屬**假設** |
| **ATKL-G11** | recurring call 若發生在**別人的 gateway** 上，我方拿不到任何 token 消耗——`role: optional` 是誠實的，但也意味著這條的轉換是有上限的 |
