# 上游原文死快照 —— Open Source Leverage Strategy Review（MCP 相關段落）

> **這份檔案是原稿不是產物。逐字保存，不改寫、不補充、不與上游同步。**
>
> | | |
> |---|---|
> | 來源 repo | `firekou/aitokenking_mediahouse` |
> | 來源檔案 | `OPEN_SOURCE_LEVERAGE_STRATEGY_REVIEW_2026-08-30.md`（全文 600 行，15 案兵推 → Top 5） |
> | 上游 commit | `cf91493` |
> | 取用日 | 2026-08-31 |
> | 取用範圍 | 只取與 Open MCP Server Network 直接相關的段落：§0 摘要相關句、§4.1 兵推、§6.3 Execution、Phase 4、§10 紅線、§11 最終定義 |
>
> **為什麼只取一部分：** 上游那份文件同時管五條策略（Skill 分發／Benchmark／Workflow
> Factory／Cost Engine／MCP Network），本 repo 只承接其中一條。
> 把不屬於本 repo 的四條也搬過來，等於製造第二個會分岔的事實來源。
>
> **上游若更新，本快照不會自動變。** 要更新須手動重取並換掉上面的 commit 欄位。

---

## §0 Executive Summary —— Top 5 之首

新版 Top 5：

1. **Open MCP Server Network**
2. **Benchmark + Token Cost Intelligence Lab**
3. **Agent Skill Distribution Network**
4. **AI Workflow Starter Kits / Factories**
5. **Token Cost Calculator / Model Decision Engine**

原先 Top 5 中的 Creator Dataset 不應取消，而應重新定位為整個系統的「情報與彈藥中心」，供養 Skills、Workflow、Benchmark、MCP 與 Cost Engine。

---

## §3 15 案兵推評分（本案該列）

| # | 方案 | 借現成勢 | 關鍵節點 | 自動複利 | 事件借勢 | 距 Token | 等級 |
|---|---|---:|---:|---:|---:|---:|---|
| 2 | Open MCP Server Network | 5 | 5 | 5 | 4 | 5 | S+ |

**五維中唯一同時拿到「關鍵節點 5」與「距 Token 5」的一案。**

---

# 4. Top 5 兵推

## 4.1 Open MCP Server Network — Execution 節點

### 借的勢

- Agent 工具化需求
- MCP 生態與 Registry 的既有分發能力
- Agent 對可直接呼叫能力的需求
- 重複工具呼叫所產生的長期使用頻率

### 關鍵資源

Skill 告訴 Agent「怎麼做」，MCP 則提供 Agent「真正可以做什麼」。

候選 MCP：

```text
video-transcript-mcp
creator-research-mcp
social-content-mcp
model-price-mcp
token-usage-mcp
prompt-cost-mcp
```

AI Token King 應作為模型能力需要時的透明預設 gateway，但維持 provider 可替換性與 truthfulness policy。

### 兵推

MCP 最大優勢不是 install，而是 recurring call：

```text
install once
   ↓
call
call
call
call
call
```

如果 MCP 進入真正 production workflow，它比單次內容曝光更接近持續 Token Consumption。

**結論：S+，長期第一級戰略資產。**

---

---

## §6.3 Execution（六種關鍵資源之一）

回答：「Agent 真正可以呼叫什麼？」

主要資產：**MCP**

---

# 9. 執行優先順序 —— Phase 4 · MCP Network

不要一次做大量 MCP。先從 Phase 3 workflow 中「最常被重複呼叫、且多個 workflow 都會需要」的能力抽成 MCP。

這可以避免做出沒有真實使用需求的 MCP。

> **上下文（不在取用範圍內，但影響本案排序）：** 上游把 MCP Network 排在 Phase 4，
> 前面是 Phase 1 Distribution First、Phase 2 Cost Intelligence MVP、Phase 3 Workflow Factory；
> 後面是 Phase 5 Benchmark Automation。**排序理由見上一段：先有呼叫紀錄，才知道該抽哪一支。**

---

# 10. 防止策略失敗的紅線

本策略雖然強調「植入」與 distribution leverage，但必須維持目前 repository 已建立的可信度原則：

1. **不得把 optional AI Token King dependency 偽裝成 required。**
2. **不得為了 attribution 破壞使用者隱私。**
3. **不得製造假 benchmark 或選擇性呈現結果。**
4. **不得讓 Skill / MCP 的實用性低於推廣目的。**
5. **不得把開源專案變成廣告殼。**
6. **AI Token King 的存在應發生在它真正解決 routing、model access、cost visibility 或 usage management 問題的位置。**

核心判斷：

> **Utility 必須先成立，Promotion 才能形成複利。**

如果 Utility 不成立，強植入只會破壞 GitHub reputation、fork rate 與長期 Agent citation。

---

# 11. 最終戰略定義

不應再將策略描述成：

> 做更多開源工具來推廣 AI Token King。

應正式定義為：

> **找出高 Token 使用者必然經過的 Discovery、Workflow、Execution、Decision、Economics 與 Routing 節點，利用 Skill、MCP、Benchmark、Automation 與 Open Source Distribution 逐步佔住這些節點，讓市場需求、模型更新、Agent 搜尋與社群分發本身成為 AI Token King 的增長力量。**

最終目的不是單次導流，而是建立：

> **AI Token King Open-source Acquisition Infrastructure**

當外部 AI 生態越活躍、模型越多、價格越常變、Agent 越普及、Workflow 越複雜，這套 infrastructure 理論上應獲得越多天然需求，而不是需要等比例增加行銷投入。

這才是本次兵推所追求的「以少勝多」與局勢傾斜。
