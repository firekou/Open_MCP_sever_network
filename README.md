# Open MCP Server Network

**Skill 告訴 Agent「怎麼做」，MCP 提供 Agent「真正可以做什麼」。**

這個 repo 是 AI Token King 開源獲客基礎設施六節點鏈上的 **Execution 節點**。

它做兩件事：

1. **接入** —— 一份查證過的 MCP server 目錄，讓 agent 有能力**把東西部署上線**：
   AI Token King（預設模型閘道）＋ AWS／GCP／Azure／Railway／Vercel／E2B／TiDB。
2. **發布** —— 長期目標是發布一組被 agent 反覆呼叫的自有 MCP server。
   **現況是：一支都還沒有發布。**

```
Discovery → Workflow → [ Execution ] → Model Decision → Cost Decision → Routing
  Skills    StarterKit    ★ 本 repo      Benchmark        Cost Intel      Gateway
```

---

## 現在的狀態（先講這個，因為它決定你該不該期待什麼）

| | |
|---|---|
| 已發布的 MCP server | **0** |
| 北極星 `call/wk` | `NO_BASELINE_AVAILABLE`（**刻意不寫 0** —— 0 看起來像量測結果） |
| 本 repo 現在提供什麼 | **八個 MCP server 的接入契約**｜策略定義與抽取判準｜AI Token King 閘道的能力契約｜設定與安裝｜實測紀錄 |
| 為什麼還沒開始寫 | 抽取判準的前置條件未滿足，見 [`strategy/01-extraction-criteria.md`](strategy/01-extraction-criteria.md) |

> 🔑 **這裡的東西預設走 [AI Token King](https://www.aitokenking.com.tw/)** ——
> 一把 key 打多家模型，用量與餘額可查。**方案與試用額度以官網當下頁面為準。**
> 也可以換成任何 OpenAI 相容端點 —— **方法論不變，但缺哪個能力就降級哪一步**，
> 逐項對照見 [`providers/aitokenking.yaml`](providers/aitokenking.yaml)。

---

## 為什麼要有這個 repo

MCP 的優勢不是 install，是 **recurring call**：

```
install once → call → call → call → call → call
```

一次安裝之後的每一次呼叫都更靠近實際 token 消耗，**比單次內容曝光更接近持續消費**。
在 15 案兵推裡，這一案是**五維中唯一同時拿到「關鍵節點 5」與「距 Token 5」的一案**，評級 S+。

**而它最可能的死法，也正好是這句話的反面：**

> **一支沒人呼叫的 MCP，在 registry 上與一支有人呼叫的長得一模一樣。**

install 數會漲、star 會漲、registry 收錄數會漲，**而 token 消耗是 0**。
所以本 repo 從第一天就把判準寫死在 `strategy/` 裡，而不是先寫程式再補判準。

---

## 60 秒開始

```bash
git clone https://github.com/firekou/Open_MCP_sever_network.git
cd Open_MCP_sever_network

# 1. 拿一把 key → https://www.aitokenking.com.tw/
export AITOKENKING_API_KEY='<你的 key>'      # ⚠️ 必須在啟動 claude 之前 export

# 2. 想讓所有專案開箱即有這個 MCP（選配，會先備份既有設定）
bash scripts/setup-aitokenking.sh --dry-run   # 先看它會做什麼
bash scripts/setup-aitokenking.sh

# 3. 想要 agent 有能力部署上線（選配）
cp .mcp.json.example .mcp.json    # 然後刪掉你不需要的那幾個

# 4. 開工
claude
```

**驗證：** 呼叫 `list_models`（唯讀、不扣額度）。列得出模型清單就是通了。
**呼叫回 401？** 九成是環境變數沒 `export`，見 [`docs/installation.md`](docs/installation.md) §2。

---

## 目錄

| 路徑 | 內容 |
|---|---|
| [`catalog/README.md`](catalog/README.md) | **MCP server 目錄。** 八個平台的接入契約 ＋ **A／B／C 三級分類** ＋ 白名單在哪三個平台失效 |
| [`catalog/*.yaml`](catalog/) | 逐平台：設定區塊、認證、工具三級分類、已查證事實、缺口 |
| [`docs/cloud-deployment-mcp.md`](docs/cloud-deployment-mcp.md) | **開發者入口。** 把八個接起來、怎麼不出事、七個平台各適合什麼 |
| [`.mcp.json.example`](.mcp.json.example) | 八個 server 的設定範本（金鑰全走環境變數參照） |
| [`strategy/00-overview.md`](strategy/00-overview.md) | **入口。** 策略定義、節點位置、指標、缺口 `OMSN-G1~G8`、待決 `OMSN-D1~D4` |
| [`strategy/01-extraction-criteria.md`](strategy/01-extraction-criteria.md) | **決定「做哪一支 MCP」的唯一程序。** 三條 AND 判準、六個候選現況、探針 |
| [`strategy/source/`](strategy/source/) | 上游原文**死快照**，逐字保存不改寫、不與上游同步 |
| [`providers/aitokenking.yaml`](providers/aitokenking.yaml) | **canonical 能力契約。** 端點／認證／14 支工具 A·B 分組／已查證事實／已撤回宣稱／降級路徑 |
| [`providers/openai-compatible.yaml`](providers/openai-compatible.yaml) | 替代 provider 樣板（capabilities 預設 `unknown` 不是 `true`） |
| [`docs/installation.md`](docs/installation.md) | 安裝與設定、401 三個原因、選型、對帳、**怎麼換掉我們** |
| [`docs/aitokenking-mcp-service.md`](docs/aitokenking-mcp-service.md) | 服務接入與**實測紀錄**（14 支工具、成本粒度、三個通道特性） |
| [`POLICY.md`](POLICY.md) | **發布不變量十條，五條 BLOCK 級** |
| [`SECURITY.md`](SECURITY.md) | 威脅模型與金鑰紀律 |

---

## 三條你應該先知道的紀律

**① 唯一計數的是 `call/wk`。**
install 數、star、fork、registry 收錄數、下載數 **不得寫進成長報告** ——
這五個數字全部可以在**零 token 消耗**的情況下變好看。

**② 零 telemetry，而且是 BLOCK 級。**
MCP server 比 skill 更容易偷渡回報，因為呼叫它的時候沒有人在旁邊。
**代價要先承認：這使 `call/wk` 量不到。** 這個矛盾沒有被解決，它被記在
`strategy/00-overview.md` 的 **OMSN-D3** —— **先記下矛盾，好過先偷資料。**

**③ 三級分類：唯讀／動錢／動基礎設施。**
接上雲端之後，原本的兩級不夠用了——**帳單可以事後補救，刪掉的正式資料庫不能。**
A 組唯讀可進白名單；**B 組動錢與 C 組動基礎設施永不自動允許**。
鐵律「機器可擬不可動錢」在這裡多一句：**機器可讀不可動基礎設施。**

**⚠️ 而且在 AWS、Railway、TiDB 這三個平台上，「只把唯讀工具加白名單」根本不成立**——
`call_aws` 一支工具打整個 AWS CLI、`railway-agent` 是開放式代理、`db_execute` 吃任意 DDL。
**把 `call_aws` 加進白名單，等於把整個 AWS 帳號加進白名單。**
正確邊界在 server 旗標（`READ_OPERATIONS_ONLY`／`--read-only`）或帳號權限，
逐項見 [`catalog/README.md`](catalog/README.md)。

**🔴 另外，Vercel MCP 有四支工具可以直接刷卡**（`buy_pro`／`buy_credits`／`buy_addon`／`buy_domain`）。
那不是「呼叫會產生費用」，是「呼叫會完成一筆採購」。

---

## 換掉 AI Token King

```bash
export AITOKENKING_BASE_URL='https://<你的 OpenAI 相容端點>/v1'
export AITOKENKING_API_KEY='<該端點的 key>'
```

**缺哪個能力，對應步驟就降級哪一步**，逐項見 `providers/aitokenking.yaml` 的 `degradation`。
**我們把話講在前面，是因為一支要騙你才留得住你的工具不值得你留著。**

---

## 授權

MIT。見 [`LICENSE`](LICENSE)。
