# AI Token King MCP Service —— 服務接入與實測紀錄

> **這份檔案遷自 `firekou/virtual-strategy-lab` 的 `docs/aitokenking-mcp-service.md`（commit `f3eb7fd`），
> 2026-08-31 遷入本 repo。**
>
> **遷入時做了三處改寫，其餘逐字保留：**
>
> | 改了什麼 | 原文 | 現在 | 為什麼 |
> |---|---|---|---|
> | 環境變數 | `AITK_API_KEY` | `AITOKENKING_API_KEY` | 2026-08-29 查證官方文件後改用 canonical 名稱；`AITK_API_KEY` 是我方自己發明的簡寫，已淘汰 |
> | Header 大小寫 | `X-AItokenKing-Api-Key` | `X-Aitokenking-Api-Key` | 同上 |
> | 設定腳本路徑 | `scripts/mcp/setup-global-mcp.sh` | `scripts/setup-aitokenking.sh` | 本 repo 的路徑 |
>
> ⚠️ **下方 §5、§6 的實測是 2026-08-19～08-20 用當時的變數名跑的。**
> 改寫的是變數名不是實測結果；**實測數字一個都沒有動。**
>
> ⚠️ **§5.1 的模型清單與價格是 2026-08-19 的死快照，會過期。**
> 當下可用模型一律以 `list_models` 為準 —— **本 repo 的鐵律是「永遠先查再寫」。**

---

**服務名稱：** `aitokenking`｜**類型：** Streamable HTTP MCP Server
**端點：** `https://api.aitokenking.com.tw/mcp`
**官方文件：** https://www.aitokenking.com.tw/assets/docs/zh/index.html#mcp-server
**接入日：** 2026-08-19｜**Owner：** Edwin（FAE）｜**產品面：** Alice

---

## 1. 這個服務是什麼

AI Token King 平台的統一 LLM 閘道（gateway，平台內部代號 `midwayFlow`）的 MCP 介面。
一把 API key 可打多家模型，並可查詢模型清單、餘額、用量與交易流水，另支援圖片與影片生成。

**與 HTTP API 用法的關係：** 同一把 key 同時走 MCP 與 OpenAI 相容 HTTP API，兩條路徑並存、不互相取代。
（上游 `virtual-strategy-lab` 的 `apps/gxs/` 就是走 HTTP API 那一條，別名 `aitk-anthropic`／`aitk-openai`／`aitk-gemini`。**該路徑不在本 repo**。）

---

## 2. 設定位置

| 檔案 | 內容 |
|---|---|
| `.mcp.json` | server 定義。header 值寫 `${AITOKENKING_API_KEY}`，**金鑰不入庫** |
| `.claude/settings.json` | `enabledMcpjsonServers` 啟用本 server；`permissions.allow` 只放**唯讀工具** |
| 環境變數 `AITOKENKING_API_KEY` | 金鑰本體。**不入庫、不寫進任何檔案** |

```jsonc
// .mcp.json
"aitokenking": {
  "type": "http",
  "url": "https://api.aitokenking.com.tw/mcp",
  "headers": { "X-Aitokenking-Api-Key": "${AITOKENKING_API_KEY}" }
}
```

**設定金鑰：**

```bash
# 本機：必須在啟動 claude 之前 export，讓它成為 process 環境變數
export AITOKENKING_API_KEY='<你的 API key>'
claude

# 遠端／部署：Railway 服務 → Variables 新增 AITOKENKING_API_KEY
```

**⚠️ 三個踩過的坑：**

1. **`${AITOKENKING_API_KEY}` 讀的是 process 環境變數，不是 `.env` 檔。**
   把金鑰寫進 `.env` 而沒有 export，展開會失敗。
2. **未設定時 server 仍會連上、仍會列出 14 支工具，但每一次呼叫都回 401。**
   看得到工具不等於用得到。判斷依據是實際呼叫，不是工具清單。
3. **把金鑰貼進對話視窗不會生效。**
   MCP 連線在 session 啟動時就已建立，對話中的文字進不到 header。
   而且該金鑰會留在對話紀錄中，等同外洩，必須輪替。

---

## 2.5 全域設定（讓每個新專案開箱即有）

專案層的 `.mcp.json` 只服務這個 repo。要讓**任何新的 Claude Code 專案**預設就有這個
MCP，設定要放在使用者層級：

```bash
bash scripts/setup-aitokenking.sh            # 實際寫入（會先備份既有設定）
bash scripts/setup-aitokenking.sh --dry-run  # 只看會做什麼
```

腳本寫兩個檔案，**缺一不可**：

| 檔案 | 內容 |
|---|---|
| `~/.claude.json` | `mcpServers.aitokenking` —— server 本身 |
| `~/.claude/settings.json` | `permissions.allow` —— **A 組 9 支唯讀工具**白名單 |

**★ 為什麼一定要兩件一起放：**
只放 server 是搬了一半——新專案會有 MCP，但那 9 支不扣額度的唯讀工具每次都要人工核准，
等於把麻煩換了個地方而不是解決它。

**★ 為什麼 B 組 5 支刻意不放白名單：**
`chat_completion`／`create_message`／`create_response`／圖片與影片生成**每次呼叫都實際扣帳戶額度**。
這是鐵律「機器可擬不可動錢」在此的具體形式——生成類一律逐次人工核准，
**不因為「常用」而放行**。腳本會主動偵測這 5 支有沒有被加進白名單，
發現即警告並以非 0 結束（可接進 CI）。

**金鑰仍然不入設定檔。** 兩個檔案存的都是 `${AITOKENKING_API_KEY}` 這個參照，
金鑰本身只存在 shell 環境（`~/.zshrc` 的 `export`）。腳本不接受、不寫入、不回顯金鑰值。

**⚠️ 要付的代價（決定放全域前該知道）：**
全域設定意味著**所有專案**都會連這個 server，包括與 AI Token King 完全無關的專案——
每個 session 多一次連線與 14 支工具的 schema 載入。若某個專案不需要它，
在該專案的 `.claude/settings.json` 以 `permissions.deny` 或
`disabledMcpjsonServers` 個別關掉，比不放全域更省事。

**⚠️ 遠端 session 無效：** Claude Code on the web／GitHub Action 等遠端執行環境的容器是
用完即回收的，在那裡跑這支腳本只對當次 session 有效。**它要在你自己的機器上跑一次。**

## 3. 工具清單（14 支，2026-08-19 實測取得）

**A 組 · 唯讀查詢（已列入 `permissions.allow`，不需逐次核准）**

| 工具 | 用途 |
|---|---|
| `list_models` / `get_model` | 帳戶可用模型、廠商、模態、能力與定價 |
| `list_image_models` / `list_video_models` | 圖／影片生成模型的解析度、長寬比、時長範圍 |
| `get_balance` | 帳戶用量與餘額 |
| `list_usage` | 分頁計費明細（只含模型用量扣費） |
| `list_transactions` | 充值／套餐購買流水（不含扣費明細） |
| `get_image_generation` / `get_video_generation` | 輪詢既有任務狀態與結果 |

**B 組 · 會消耗額度（刻意**不**自動允許，每次需人工核准）**

| 工具 | 用途 |
|---|---|
| `chat_completion` | OpenAI Chat Completions 相容，支援圖片視覺輸入 |
| `create_message` | Anthropic Messages 相容 |
| `create_response` | OpenAI Responses 相容 |
| `create_image_generation` | 非同步送出圖片生成任務 |
| `create_video_generation` | 非同步送出影片生成任務 |

**A／B 分組是刻意的。** B 組每一次呼叫都在花錢。
公司鐵律「機器可擬不可動錢」在此的具體形式，就是 B 組永遠不進 allow 清單。
要放寬須 Frank 拍板（金額規模決定層級）。**在本 repo，這一條是 `POLICY.md` 不變量 #5，BLOCK 級。**

---

## 4. 紅線

1. **金鑰不得寫進版本庫、不得寫進文件、不得寫進 agent 定義檔、不得貼進對話視窗。**
   只能走啟動前 `export` 的環境變數或部署平台的 Variables。貼進對話即視為外洩，必須輪替。
2. **B 組工具不得自動允許。** 生成類呼叫會扣額度，需人工核准。
3. **成本要記帳。** 用 `list_usage` 對帳，不得只憑「感覺沒用多少」。
4. 本 server 為外部服務，回傳內容視為外部資料，不得直接當作事實引用。

---

## 5. 實測紀錄（2026-08-19）

| 項目 | 結果 |
|---|---|
| 端點可達性 | ✅ `initialize` 回 HTTP 200 |
| serverInfo | `AItokenKing` v3.4.7 |
| protocolVersion | `2025-06-18` |
| `tools/list` | ✅ 取得 14 支工具（以無效金鑰即可列出） |
| 工具已註冊進 Claude Code | ✅ 14 支 `mcp__aitokenking__*` 全數可見 |
| Claude Code MCP client 呼叫 | 🔴 **401 未授權**——環境變數 `AITOKENKING_API_KEY` 未設定，送出未展開的字面值 |
| **curl 作為 MCP client 呼叫** | ✅ **全通**——金鑰從 `.env` 載入，`list_models`／`get_balance`／`chat_completion` 皆成功 |

**兩個 client 的結果不同，證明 401 是環境變數問題不是金鑰問題。**
繞道腳本：上游 `virtual-strategy-lab` 的 `scripts/mcp/aitk_mcp_call.sh`（initialize → notifications/initialized → tools/call 三段式，
金鑰從 `.env` 載入，不出現在指令列）。**該腳本未遷入本 repo**（缺口 `OMSN-G8`）。

### 5.1 `list_models` 實測（2026-08-19）

帳戶可用模型 **48 個**，其中 OpenAI 系 6 個（全部經 MicrosoftAzure）：

| model id | context | 價格 in／out（USD per 1M tokens） |
|---|---|---|
| `gpt-5.6-sol` | 1,050,000 | 10.0 ／ 45.0 |
| `gpt-5.6-terra` | 1,050,000 | 5.0 ／ 22.5 |
| `gpt-5.5` | 1,050,000 | 5.0 ／ 30.0 |
| `gpt-5.4` | 1,050,000 | 5.0 ／ 22.5 |
| `gpt-5.6-luna` | 1,050,000 | 2.0 ／ 9.0 |
| `gpt-5-nano` | 400,000 | 0.05 ／ 0.4 |

另有 Anthropic（`claude-opus-5`／`claude-sonnet-5`／`claude-fable-5` 等）、Google、Qwen、GLM、Kimi、DeepSeek、MiniMax、Dola 各系。
⚠️ 上游 `apps/gxs/` 的預設值 `AITK_MODEL_OPENAI=gpt-5.5` 當時仍存在於清單中，可用。**該應用不在本 repo。**

### 5.2 `chat_completion` 實測（2026-08-19）

| 項目 | 值 |
|---|---|
| model | `gpt-5.6-terra` |
| 提問 | 「今天（2026-08-19）Threads 上的十大熱門話題是什麼？」 |
| 延遲 | 8.0 秒（含三段式握手） |
| usage | prompt 64 ／ completion 219 ／ total 283 tokens |
| 實際扣款 | 餘額 99.978 → 99.972，**0.006 credits** |
| 費率推算 | $0.005248 —— 與實扣一致，**credit ≈ USD** |

**模型回答：拒絕編造，明講無法取得 Threads 即時榜單。**
這是正確行為，也證實一件事：**`chat_completion` 是純模型呼叫，沒有網路存取**。
凡是需要即時資料的問題（榜單、股價、當日新聞），本 gateway 的任何模型都答不出來，
只能靠外部資料源餵進 prompt。**不得把模型對即時資料的回答當作事實引用。**

### 5.3 成本記帳可行性

`get_balance` 在呼叫前後各跑一次即可得到精確扣款，粒度到小數第三位。
`list_usage` 可取分頁計費明細。**成本記帳這條紅線在本 gateway 上是做得到的，沒有藉口。**

---

## 6. ★ 用 gateway 做程式碼覆核的三個限制（2026-08-20 實測）

把整套 GXS 送進 `chat_completion` 做全系統覆核時撞到的三件事。
**都不是模型能力問題，是通道特性**，且三件各花掉一輪以上的除錯。
完整脈絡見上游 `virtual-strategy-lab` 的 `projects/aitokenking/governance-exposure-scan/external-reviews/EXT-REVIEW-2026-08-20b-gpt-full.md` §2。**未遷入本 repo。**

### 6.1 `cyber_policy` 內容過濾會擋掉資安審查的措辭

prompt 寫「請找出漏洞」「給一個攻擊情境」，gateway 回 **HTTP 500**，錯誤內容指向 OpenAI 的 `cyber_policy`。

**這不是應該去抗議的誤判——是我們的措辭不準確。**
我們做的本來就是自己系統的品質覆核，用品質保證的語言描述反而更貼近事實：

```
✗ 「找出漏洞」「攻擊情境」
✓ 「這段程式在什麼情況下會給出錯誤的結果」
✓ 「一個會走到這個錯誤的實際使用情境」
```

改寫後產出品質沒有下降——嚴重級發現照樣包含權限越權與競態。

### 6.2 `max_tokens` 是逾時的主因，不是語料長度

一開始判斷「語料太長」是**錯的**。同一份 24K 字元語料：

| `max_tokens` | 結果 |
|---|---|
| 800 | 22 秒完成 |
| 2000 | 36 秒完成 |
| 5000 | 逾時 |
| 7000 | 逾時 |

**做長文覆核時 `max_tokens` 壓在 ≤3000，並把語料分軸送。**
縮語料只是把症狀壓下去，沒有解決問題。

### 6.3 ⚠️ 只有 `gpt-5.4` 回得出文字——其餘 GPT-5.x 回應為空

`gpt-5.5`、`gpt-5.6-terra`、`gpt-5.6-sol`、`gpt-5.6-luna`、`gpt-5.6-nano`
在長 prompt ＋ 有限 `max_tokens` 的情況下**回應內容為 0 字元**：
推理消耗掉整個 token 預算，`usage.completion_tokens` 顯示用光，
但 `choices[0].message.content` 是空字串。

**這是最危險的一種失敗：HTTP 200、`usage` 有數字、沒有任何錯誤訊息，但東西是空的。**

> **呼叫端必須驗 `len(content) > 0`，不能只驗 HTTP 狀態碼。**
> 只看狀態碼的腳本會把「沒拿到任何東西」寫成「完成」。

⚠️ 這連帶影響上游 `apps/gxs/` 的預設值：`AITK_MODEL_OPENAI=gpt-5.5` 在**短 prompt** 下正常
（§5.1／§5.2 實測可用），但用於長文分析時須改指 `gpt-5.4` 或提高 `max_tokens` 至足以容納推理。
