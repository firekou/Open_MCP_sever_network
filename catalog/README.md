# MCP Server 目錄 —— 我方接入的第三方 MCP

**這個目錄是「我們用別人的」，不是「我們發布的」。**
我方自己發布的 MCP server 數量目前是 **0**（缺口 `OMSN-G1`），那件事的家在 `strategy/`。

每個檔案是一份**可查證的接入契約**：怎麼裝、怎麼認證、有哪些工具、
**哪些工具按下去會付錢、哪些會動到正式環境**。

---

## ★ 三級分類（本目錄最重要的東西）

Media House 傳下來的規則是兩級：唯讀進白名單、扣費不進白名單。
**接上雲端之後兩級不夠用了**，因為多了一種完全不同的失敗方式。

| 組 | 定義 | 出事的樣子 | 能不能進 `permissions.allow` |
|---|---|---|---|
| **A · 唯讀** | 查詢、列出、讀 log。不改變任何狀態 | 沒事 | ✅ 可以 |
| **B · 動錢** | 每次呼叫產生費用，或直接購買 | **一張帳單** | ⛔ **永不** |
| **C · 動基礎設施** | 部署、刪除、改設定、DDL、改權限 | **一次線上事故** | ⛔ **永不** |

**B 與 C 不可以合併成一組。**
帳單是可以事後補救的（申訴、退款、認賠）；**刪掉的正式資料庫不是。**
把它們寫成同一組，會讓「這支只是會花一點錢」和「這支會砍掉生產環境」
在設定檔裡長得一模一樣 —— 而它們需要的審核強度差好幾個數量級。

原本的鐵律「**機器可擬不可動錢**」在這裡多一句：
**機器可讀不可動基礎設施。**

---

## ⚠️ 三個平台上，「把唯讀工具加白名單」這個做法根本不成立

這是這次盤點最重要的發現，**它推翻了一個看起來理所當然的做法**。

| 平台 | 問題工具 | 為什麼白名單失效 |
|---|---|---|
| **AWS** | `call_aws` | **一支工具打整個 AWS CLI。** 同一支工具可以 `s3 ls`，也可以 `rds delete-db-instance` —— 工具名稱層級分不出唯讀與否 |
| **Railway** | `railway-agent` | 開放式代理工具，能做什麼由 prompt 決定不由工具名決定 |
| **TiDB** | `db_execute` | 一支工具吃任意 DML／DDL |

**在這三個平台上，安全邊界不在 `permissions.allow`，在 server 自己的旗標或帳號權限：**

```
AWS    → READ_OPERATIONS_ONLY=true      （server 端強制唯讀）
Azure  → azmcp server start --read-only （server 端過濾工具清單）
TiDB   → 給一個只有 SELECT 權限的資料庫帳號（server 沒有唯讀旗標，只能從帳號下手）
Railway→ 沒有唯讀旗標 —— 只能逐次核准
```

**把 `call_aws` 加進白名單，等於把整個 AWS 帳號加進白名單。**

---

## 總表（查證日 2026-08-31，全部來自官方文件＝E2）

| 平台 | 檔案 | 官方？ | 傳輸 | 認證 | 有唯讀旗標？ | 會動錢？ |
|---|---|---|---|---|---|---|
| **AI Token King** | `aitokenking.yaml` | ✅ 廠商 | HTTP | API key | ⬜ 無（靠 A／B 分組） | ✅ 5 支生成工具 |
| AWS | `aws.yaml` | ✅ awslabs | stdio | AWS 憑證鏈 | ✅ `READ_OPERATIONS_ONLY` | ✅ 開資源就計費 |
| Google Cloud | `gcp-cloud-run.yaml` | ✅ GoogleCloudPlatform | stdio | `gcloud` ADC | ⬜ 無 | ✅ `create-project` 綁 billing |
| Azure | `azure.yaml` | ✅ microsoft／Azure | stdio | Azure Identity | ✅ `--read-only` | ✅ 開資源就計費 |
| Railway | `railway.yaml` | ✅ railwayapp | HTTP／stdio | OAuth／CLI | ⬜ 無 | ✅ 部署就計費 |
| Vercel | `vercel.yaml` | ✅ vercel | HTTP | OAuth | ⬜ 無 | 🔴 **有 `buy_*` 直接刷卡** |
| E2B | `e2b.yaml` | ✅ e2b-dev | stdio | `E2B_API_KEY` | ⬜ 無 | ✅ sandbox 按用量計費 |
| TiDB | `tidb.yaml` | ✅ PingCAP | stdio | 資料庫帳密 | ⬜ 無（用帳號權限代替） | ⬜ 依方案 |

---

## 🔴 Vercel 是唯一一個可以直接花你的錢買東西的

其他平台的「動錢」是**間接的**：你開了一台機器，月底收到帳單。
Vercel MCP 有四支工具是**直接的**：

```
buy_pro       買 Pro 方案
buy_credits   買額度
buy_addon     買附加元件
buy_domain    買網域
```

**這不是「呼叫會產生費用」，這是「呼叫會完成一筆採購」。**
它們在本目錄一律歸 **B 組**，且 `vercel.yaml` 額外標記 `purchase: true` ——
**一個 agent 在沒有人看著的時候買了一個網域，事後很難說那是誤會。**

---

## 每個檔案的格式

```yaml
id / label / vendor / official / status
transport            stdio ｜ http
config               ★ 可原樣貼進 .mcp.json 的區塊
auth                 method ／ env ／ notes
safety
  read_only_flag     server 端有沒有唯讀開關；沒有就寫 null 並說明替代做法
  group_a / b / c    三級分類
  allowlist_viable   ★ 逐工具白名單在這個平台成不成立
verified_facts       每條附 verified_at ／ source ／ evidence
gaps                 查不到的東西，寫出來不隱藏
```

**與 `providers/*.yaml` 的分工：** `providers/` 管**模型閘道的能力契約**
（有沒有 vision、能不能查餘額、缺了會降級成什麼）；
`catalog/` 管**MCP server 的接入契約**（怎麼裝、按下去會不會出事）。
`aitokenking` 兩邊都有一份，**但事實的家仍然只有 `providers/aitokenking.yaml`** ——
`catalog/aitokenking.yaml` 只寫接入面，能力面一律指過去。
