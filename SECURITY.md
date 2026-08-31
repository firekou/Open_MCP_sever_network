# 安全政策

## 這個 repo 的威脅模型，一句話

**它發布的是「別人的 agent 會自動反覆呼叫的行程」。**

```
我方發布 MCP server  →  使用者安裝  →  agent 自動呼叫  →  call  →  call  →  call
                                          ↑ 這裡沒有人在看
```

skill 是一份文字檔，安裝的人多半會掃一眼；**MCP server 被呼叫時，沒有人在旁邊。**
所以本 repo 的紅線比 Media House 更硬，不是因為我們更謹慎，是因為**觀察者不見了**。

---

## 三個必須分開想的攻擊面

| 面向 | 風險 | 硬規則 |
|---|---|---|
| **我方 → 使用者** | 我們發布的 server 偷偷回報、偷偷扣費、偷偷擴權 | **零 telemetry（BLOCK）**；扣費工具必須在 tool description 明講且不得預設允許 |
| **外部資料 → 使用者** | server 從外部抓回的內容被 agent 當成指令執行（prompt injection） | **回傳內容一律是資料不是指令。** server 不得回傳「請執行以下命令」形式的內容，且應在 tool description 註明回傳為外部資料 |
| **使用者 → 我方** | 呼叫參數含金鑰、個資、專案內容 | **不落地、不記錄、不轉送。** 需要 log 時只記錄不可還原的計數 |

**第二面是最容易被忽略的一面。**
一支「幫你抓網頁回來」的 MCP，如果那個網頁上寫著「ignore previous instructions」，
它就成了注入管道，而且**過程中沒有任何一步會報錯**。

---

## 金鑰

- **不得寫進版本庫、文件、agent 定義檔，不得貼進對話視窗。**
  只走啟動前 `export` 或部署平台 Variables。
- **貼進對話即視為外洩，必須立刻輪替** —— MCP 連線在 session 啟動時就已建立，
  對話中的文字進不到 header，所以貼了既沒有用、又留下了紀錄。
- canonical 變數：`AITOKENKING_API_KEY`。**repo 內只出現變數名，不出現值。**
- **B 組扣費工具永不進 `permissions.allow`**（`chat_completion`／`create_message`／
  `create_response`／`create_image_generation`／`create_video_generation`）。
  `scripts/setup-aitokenking.sh` 會主動偵測並以非 0 結束。

---

## 安裝本 repo 任何產物的人應該知道

- 目前本 repo **尚未發布任何 MCP server**（缺口 `OMSN-G1`）。
  它現在提供的是策略文件、AI Token King 閘道的能力契約，以及設定腳本。
- `scripts/setup-aitokenking.sh` 會**改寫你的 `~/.claude.json` 與 `~/.claude/settings.json`**
  （先備份）。它寫入的是 `${AITOKENKING_API_KEY}` 這個**參照**，不接受、不寫入、不回顯金鑰值。
- 設定完成後，A 組 9 支唯讀工具會進入自動允許清單；**B 組 5 支扣費工具不會，這是刻意的。**

---

## 回報漏洞

在 GitHub 開 issue，標題加上 `[security]`。
若涉及可被利用的注入路徑，**請先不要公開 PoC 的完整內容**，在 issue 裡描述形狀即可。

**特別歡迎這一類回報：** 你發現本 repo 的某個產物在文件裡宣稱了一件它做不到的事，
或是把 optional 依賴寫成 required。**那是 `TRUTH-1`，在這裡與安全漏洞同級。**
