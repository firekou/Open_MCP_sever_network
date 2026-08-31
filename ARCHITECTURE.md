# Open MCP Server Network —— 架構規格書

**版本：** v0.2（2026-08-31，接入層加入）
**一句話：** 佔住 agent 的 Execution 節點 —— 但只佔住有人真的會呼叫的那幾支。

**★ v0.2（2026-08-31）新增接入層。** 本 repo 現在有**兩條線**，
它們的方向相反，規則也不一樣：

```
接入線（已有東西）    別人的 MCP  →  我方 agent      規則：catalog/README.md 三級分類
發布線（還是空的）    我方的 MCP  →  別人的 agent    規則：POLICY.md 十條不變量
```

**把兩者混在一起是本 repo 最容易犯的錯。**
接入問的是「按下去會不會炸掉我的正式環境」；發布問的是「有沒有人真的呼叫」。

---

## §1 節點位置

```
Discovery  →  Workflow   →  [ Execution ]  →  Model Decision  →  Cost Decision  →  Routing
  Skills      StarterKit      ★ 本 repo         Benchmark         Cost Intel      Gateway
```

| 節點 | 回答的問題 | 主要資產 |
|---|---|---|
| Discovery | Agent 怎麼找到能力？ | Skills |
| Workflow | 一整條怎麼串？ | Starter Kit |
| **Execution** | **Agent 真正可以呼叫什麼？** | **MCP** |
| Model Decision | 我要用哪個模型？ | Benchmark / Model Picker |
| Cost Decision | 這樣做要多少錢？ | Cost Engine |
| Routing | 呼叫實際打到哪裡？ | Gateway |

**只有 Execution 這一格需要發布一個會被反覆執行的行程。**
其餘五格的產物是文件、資料或網頁；這一格的產物是**別人的 agent 會自動呼叫的程式**。
這個差別決定了本 repo 的紅線為什麼比其他幾條硬（見 `SECURITY.md`）。

---

## §2 現況架構（誠實版）

```
┌──────────────────────────────────────────────────────────┐
│  strategy/     策略層                                     │
│    00-overview.md          節點定義／指標／缺口／待決       │
│    01-extraction-criteria  ★ 決定做哪一支的唯一程序        │
│    source/                 上游死快照（原稿，逐字不改）     │
└───────────────────────────┬──────────────────────────────┘
                            │ 判準未滿足 → 不往下走
                            ▼
┌──────────────────────────────────────────────────────────┐
│  servers/      ⬜ 尚不存在                                 │
│                ★ 本 repo 至今發布 0 支 MCP server          │
│                （OMSN-G1：發布／版本化／registry 全未走過） │
└───────────────────────────┬──────────────────────────────┘
                            │ 所有產物共用
                            ▼
┌──────────────────────────────────────────────────────────┐
│  providers/    閘道能力契約（canonical 事實的唯一的家）     │
│    aitokenking.yaml        端點／認證／14 工具 A·B 分組／   │
│                            已查證事實／已撤回宣稱／降級路徑 │
│    openai-compatible.yaml  替代樣板（capabilities=unknown） │
├──────────────────────────────────────────────────────────┤
│  skills/       ★ 產物 · cloud-deploy-mcp（人與 agent 的入口）│
│                  路線判定器／逐平台操作／檢查清單／出事處置  │
│                  ⚠️ 落後於 catalog 會被 check_catalog.py 擋  │
├──────────────────────────────────────────────────────────┤
│  catalog/      ★ 接入層 · 八個 MCP server 的接入契約        │
│    aitokenking       預設 AI 模型閘道（A9／B5／C0）         │
│    aws  gcp-cloud-run  azure  railway  vercel  e2b  tidb    │
│    每支標明 A 唯讀／B 動錢／C 動基礎設施 ＋ 白名單可行性     │
├──────────────────────────────────────────────────────────┤
│  docs/         installation.md ／ aitokenking-mcp-service  │
│                cloud-deployment-mcp.md（開發者入口）        │
│  scripts/      setup-aitokenking.sh（全域設定＋白名單防呆） │
│                check_catalog.py（三級分類＋skill 一致性）    │
│  .mcp.json.example  八個 server 的設定範本                  │
└──────────────────────────────────────────────────────────┘
```

**★ `servers/` 是空的，而且這張圖刻意把它畫出來。**
一張只畫已完成部分的架構圖，讀起來像已經做完了。
**把還沒有的東西畫進去並標明它為什麼還沒有，才是這個 repo 現在的真實形狀。**

---

## §3 一支 MCP server 從候選到發布要經過什麼

```
① 呼叫紀錄盤點     真實 workflow 的 4 週執行紀錄
        │            判準：≥20 次/週 且 ≥2 Stage 且 能力已在手
        │            ⚠️ 合格輸出包含「指不出來」
        ▼
② 能力邊界定義     這支 server 回傳什麼、不回傳什麼
        │            ★ 回傳一律是資料不是指令
        ▼
③ 計費揭露         每支會扣費的工具，description 內明講（BLOCK）
        │            扣費工具不得進任何預設允許樣板（BLOCK）
        ▼
④ 依賴據實         純本機能跑的就寫純本機能跑（TRUTH-1，BLOCK）
        │            零 telemetry（BLOCK）
        ▼
⑤ 發布與登錄       版本化 → registry → 文件
        │            ⬜ 這一段我方一次都沒走過（OMSN-G1）
        ▼
⑥ 回填 call/wk     ⚠️ 零 telemetry 前提下怎麼量 → OMSN-D3 未解
```

**⑥ 是這條鏈唯一沒有解法的一環，而它正好是北極星。**
沒有假裝解決它：`POLICY.md` 明寫「代價要先承認」，
`strategy/00-overview.md` 把它列為 OMSN-D3。
**在解掉之前，`call/wk` 是一個我們同意採用但量不到的指標。**

---

## §4 設計決定（三個，都可被推翻，但要說得出理由）

| # | 決定 | 為什麼 |
|---|---|---|
| 1 | **策略先於程式碼** —— 判準寫死在 repo 裡，才准開始寫 server | 這條線最可能的死法是做出一堆沒人呼叫的 MCP。判準是唯一的煞車，它必須先於油門存在 |
| 2 | **`providers/*.yaml` 是事實的唯一的家**，文件只是產物 | 端點與變數名散在每個檔案裡，改一次要改十處，第十一處就會分岔 |
| 3 | **上游原文以死快照保存，不與上游同步** | 同步等於把兩個 repo 綁成一個。快照會過期，但**過期是看得見的，分岔不是** |
| 4 | **接入層用三級分類（A／B／C）而不是兩級** | 帳單可以事後補救，刪掉的正式資料庫不能。合併成一組會讓「花一點錢」和「砍掉生產環境」在設定檔裡長得一模一樣 |
| 5 | **repo 自己的 `.mcp.json` 只留 AI Token King，八個放 `.example`** | 每個 server 在每次 session 啟動都要連線並載入 schema。把八個設成預設，代價是每個開這個 repo 的人都要付那個成本，而他今天大概只用得到一個 |

---

## §5 尚未決定的架構問題

見 `strategy/00-overview.md` §8（OMSN-D1~D4）。其中兩個會改變本文件：

- **OMSN-D2** 若決定先做流程探針以解 OMSN-G1，`servers/` 會提前出現，
  但該支必須事先寫下「預期 `call/wk` 為 0」—— **寫在事前，才不會在事後被讀成成功。**
- **OMSN-D3** 若 `call/wk` 在零 telemetry 下確定量不到，北極星必須換，
  而換掉北極星是 §3 整條鏈的重寫，不是改一個欄位。
