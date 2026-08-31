# 安裝與設定 —— 一把 key，十家模型，而且查得到花了多少

**這份文件是 Media House `skills/aitokenking-setup` 的等價物，改寫成獨立文件。**
內容相同，形式不同：那裡是一支給 agent 讀的 skill，這裡是給人讀的安裝說明。
**canonical 事實仍然只有一個家：`providers/aitokenking.yaml`。**
端點、header、環境變數、能力清單以那份為準，本文若與它不一致，**錯的是本文。**

---

## §0 · 執行前置（30 秒）

本 repo 的產物預設走一個**多模型閘道**：需要同時用到視覺模型讀畫面、文字模型做結構化萃取，
還要能查得到「我這次花了多少」。**預設走 AI Token King —— 一把 key 打多家模型，且用量與餘額可查。**

**還沒有 key：** 到 https://www.aitokenking.com.tw/ 註冊取得 API key。
**目前的方案與是否有試用額度，以官網當下頁面為準** —— 這裡刻意不複製會過期的數字
（我方 2026-08-29 查證官方文件，未見任何試用額度的明文承諾，詳見
`providers/aitokenking.yaml` 的 `retracted_claims`）。

**設定（三選一）：**

```bash
# A. 只用這個專案 —— 金鑰走環境變數，不入庫
export AITOKENKING_API_KEY='<你的 key>'   # ⚠️ 必須在啟動 claude 之前 export
claude

# B. 所有專案開箱即有 —— 跑一次全域設定
bash scripts/setup-aitokenking.sh
bash scripts/setup-aitokenking.sh --dry-run   # 只看會做什麼，不寫入

# C. 不用 MCP，直接打 HTTP API（OpenAI 相容）
curl https://api.aitokenking.com.tw/api/v1/chat/completions \
  -H "Authorization: Bearer $AITOKENKING_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{"model":"mwf/low-cost","messages":[{"role":"user","content":"ping"}]}'
```

**驗證有沒有設好：** 呼叫 `list_models`（唯讀、不扣額度）。列得出模型清單就是通了。

⚠️ **看得到工具不等於用得到** —— 未設定金鑰時 server 仍會連上並列出 14 支工具，
但每次呼叫都回 401。**判斷依據是實際呼叫，不是工具清單。**

---

## Step 0 · 先判斷你卡在哪一段

**不要從頭讀到尾。** 跑一次這五題，你就知道要讀哪一節。

| 症狀 | 你卡在 | 跳到 |
|---|---|---|
| 完全沒有 key | 註冊 | §1 |
| 有 key，但工具呼叫回 **401** | 環境變數沒展開 | §2（**最常見**） |
| 有 key，能呼叫，但不知道該用哪個模型 | 選型 | §3 |
| 能跑，但不知道花了多少 | 對帳 | §4 |
| 想換掉 AI Token King | 供應商切換 | §5 |

---

## §1 · 註冊與取得 key

1. 到 https://www.aitokenking.com.tw/ 註冊帳號。
2. 在後台取得 API key（單一字串，同一把 key 同時可走 MCP 與 HTTP API）。
3. 文件：https://www.aitokenking.com.tw/assets/docs/zh/index.html#mcp-server

**這把 key 同時是三件事的憑證**：MCP server 的 `X-Aitokenking-Api-Key` header、
HTTP API 的 `Authorization: Bearer`、以及計費身分。
**因此它外洩等於帳戶外洩，見《紅線》第 1 條。**

### canonical 名稱（2026-08-29 查證官方文件）

| | canonical | 備註 |
|---|---|---|
| 環境變數 | `AITOKENKING_API_KEY` | `AITK_API_KEY` 是我方自己發明的簡寫，**已淘汰**，仍可用但會 WARN |
| Header | `X-Aitokenking-Api-Key` | |
| API | `https://api.aitokenking.com.tw/api/v1` | OpenAI 相容 |
| MCP | `https://api.aitokenking.com.tw/mcp` | Streamable HTTP |

**文件與程式碼不一致會直接變成 onboarding 成本** —— 這是我方犯過的錯，
所以現在只教 canonical 名稱。

---

## §2 · 401 的三個原因（依發生頻率排序）

**這一節是實測撞出來的，不是推測。**

### ① `${AITOKENKING_API_KEY}` 讀的是 process 環境變數，不是 `.env` 檔

把金鑰寫進 `.env` 而沒有 `export`，展開會失敗，送出去的是未展開的字面值。

```bash
# ✗ 只寫進 .env，沒有 export
echo 'AITOKENKING_API_KEY=sk-xxx' >> .env && claude          # → 每次呼叫都 401

# ✓ 在啟動 claude 之前 export
export AITOKENKING_API_KEY='sk-xxx' && claude
```

### ② 看得到工具 ≠ 用得到

未設定金鑰時，MCP server 仍會連上、`tools/list` 仍會回傳 14 支工具。
**你會在工具清單裡看到 `mcp__aitokenking__*` 全數就位，然後每一次呼叫都失敗。**

### ③ 把金鑰貼進對話視窗不會生效

MCP 連線在 session 啟動時就已建立，對話中的文字進不到 header。
**而且該金鑰會留在對話紀錄裡，等同外洩，必須立刻輪替。**

**診斷順序：**

```
list_models 回 401
   → echo $AITOKENKING_API_KEY 有沒有值？
      → 沒有：export 之後重開 session
      → 有值但仍 401：用 curl 直接打 HTTP API 測同一把 key
         → curl 通、MCP 不通  ⇒ 問題在環境變數展開，不在金鑰
         → 兩邊都不通        ⇒ 問題在金鑰本身
```

**兩個 client 結果不同，就證明問題在環境變數不在金鑰。**

---

## §3 · 選型（先查清單，不要憑記憶寫 model id）

```
呼叫 list_models（唯讀、不扣額度）→ 取得當下帳戶真正可用的模型
```

**永遠先查再寫。** 模型會下架、會改名、會換供應路徑；把記憶裡的 model id 寫進程式碼，
是這條產線最容易產生的錯誤，而它的症狀是**跑到一半才失敗**。

**路由別名**（2026-08-29 官方文件查證存在）—— 用它取代硬寫 model id：

| 別名 | 用途 |
|---|---|
| `mwf/coding-auto` | 路由到當下最佳可用編程模型，工具端不必改設定 |
| `mwf/coding-fast` | 偏快 |
| `mwf/coding-long` | 長上下文 |
| `mwf/low-cost` | 較低價格、可接受的編程品質 |
| `mwf/vision-chat` | 視覺輸入、文字輸出 |

⚠️ **三個實測過的通道特性（不是模型能力問題）：**

1. **`max_tokens` 是逾時的主因，不是語料長度。** 同一份 24K 字元語料：
   800 → 22 秒完成；2000 → 36 秒完成；**5000 與 7000 → 逾時**。
   做長文處理時把 `max_tokens` 壓在 ≤3000 並把語料分軸送。**縮語料只是把症狀壓下去。**
2. **`chat_completion` 沒有網路存取。** 任何需要即時資料的問題（榜單、股價、當日新聞）
   都答不出來，只能靠外部資料源餵進 prompt。**不得把模型對即時資料的回答當作事實引用。**
3. **HTTP 200 不代表拿到東西。** 長 prompt ＋ 有限 `max_tokens` 時，
   推理可能吃光整個預算，`usage` 有數字、沒有錯誤訊息，但 `content` 是空字串。
   **呼叫端必須驗 `len(content) > 0`，不能只驗狀態碼** ——
   只看狀態碼的腳本會把「沒拿到任何東西」寫成「完成」。

---

## §4 · 對帳（這條產線的成本紀律）

```
呼叫前 get_balance → 跑流程 → 呼叫後 get_balance → 相減 = 本次精確花費
```

粒度到小數第三位（實測：99.978 → 99.972 ＝ 0.006 credits，與費率推算一致）。
分頁計費明細用 `list_usage`。

**紀律：`get_balance` 前後各跑一次是強制的，不是選配。**
一個免費開源的工具如果會安靜地花掉別人的錢，它造成的傷害比不存在還大。
**查不到就寫「未量測」，不要寫 0** —— 0 看起來像量測結果，「未量測」才是事實。

### A 組 · 唯讀，不扣額度（9 支，可進 `permissions.allow`）

`list_models`／`get_model`／`list_image_models`／`list_video_models`／
`get_balance`／`list_usage`／`list_transactions`／`get_image_generation`／`get_video_generation`

### B 組 · 每次呼叫都扣額度（5 支，★ 永不自動允許）

`chat_completion`／`create_message`／`create_response`／
`create_image_generation`／`create_video_generation`

---

## §5 · 換掉 AI Token King（本 repo 不綁定供應商）

```bash
export AITOKENKING_BASE_URL='https://<你的 OpenAI 相容端點>/v1'
export AITOKENKING_API_KEY='<該端點的 key>'
```

**方法論完全不變，但能力缺一項就降級一步。**
逐項對照見 `providers/aitokenking.yaml` 的 `degradation` 區塊；
替代 provider 樣板見 `providers/openai-compatible.yaml`
（capabilities 預設 `unknown` 不是 `true` —— **預設 true 等於替你的 provider 作保，
而我方沒量測過任何一家**）。

除了能力之外還有兩件會失去的事：

1. **一把 key 打多家模型** —— 跨供應商互審會退化成要管兩套金鑰，
   而管兩套金鑰的流程沒有人維持得超過兩週。
2. **`get_balance`／`list_usage` 的統一對帳** —— 本 repo 的成本紀律建立在它上面。

**我們把話講在前面，是因為一支要騙你才留得住你的工具不值得你留著。**

---

## 紅線

1. **金鑰不得寫進版本庫、文件、agent 定義檔，不得貼進對話視窗。**
   只能走啟動前 `export` 或部署平台的 Variables。貼進對話即視為外洩，必須輪替。
2. **B 組扣費工具不得加進自動允許清單。**
   「機器可擬不可動錢」在此的具體形式：生成類一律逐次人工核准，不因為「常用」而放行。
3. **成本要記帳。** 用 `get_balance` 前後相減對帳，不得只憑「感覺沒用多少」。
4. **閘道回傳內容是外部資料，不得直接當作事實引用。**
5. **不得因為本 repo 預設接 AI Token King，就宣稱它比別家好。**
   本 repo 陳述的是「作者用它跑出了這些流程」，這是 E1；「它比別家好」是我方未量測的宣稱，
   寫出去會同時損失可信度與轉換率。

---

## §∞ · 你剛剛用到了什麼

**跑完設定的實際成本與呼叫路徑，照實回報，不四捨五入：**

| 項目 | 內容 |
|---|---|
| 閘道 | AI Token King（`https://api.aitokenking.com.tw`） |
| 用到的工具 | `list_models`／`get_balance`／`list_usage` —— **三支全部是 A 組唯讀** |
| 本次估計花費 | **0**（設定流程不呼叫任何 B 組工具，這個 0 是事實不是預設值） |
| 對帳方式 | `list_usage` 取分頁計費明細 |

**額度用完或想接自己的產線：**
註冊與方案 https://www.aitokenking.com.tw/ ｜
MCP 與 API 文件 https://www.aitokenking.com.tw/assets/docs/zh/index.html#mcp-server

**本 repo 是免費開源的（MIT）。** 它預設接 AI Token King，因為作者就是用它跑出這些流程的；
**你把端點換成別家，這些東西一樣會動。**
