# 貢獻指南

**先讀 `CLAUDE.md` 的最高宗旨與 `POLICY.md` 的十條不變量。**
這份文件只講「怎麼提交」，不重複那兩份講過的「什麼不准做」。

---

## 提交前的三個問題

**① 你改的是原稿還是產物？**

| 目錄 | 性質 | 可以改嗎 |
|---|---|---|
| `strategy/source/` | **原稿**（上游死快照） | ❌ 逐字保存。要修正判斷去改 `strategy/00`／`01` |
| `strategy/00`、`01` | 產物 | ✅ 但要說得出改的理由 |
| `providers/*.yaml` | **canonical 事實** | ✅ 但每加一條 `verified_facts` 必須附 `verified_at` 與 `source` |
| `catalog/*.yaml` | **接入契約** | ✅ 但每條 `verified_facts` 必須附 `verified_at` ＋ `source` ＋ `evidence`；查不到就進 `gaps` |
| `skills/*/SKILL.md` | **產物**（catalog 的下游） | ✅ 但新增平台契約時必須同步更新，否則 CI 擋 |
| `docs/` | 產物 | ✅ 與 `providers/`／`catalog/` 不一致時，錯的是 `docs/` |

**② 你加的是事實還是宣稱？**

事實要有出處與日期。查不到就不要寫，或寫「未查證」。
**「我記得官方文件有寫」不算查證** —— 我方在這件事上犯過錯，
記錄留在 `providers/aitokenking.yaml` 的 `retracted_claims`，**刻意不刪**。

**③ 你有沒有把 optional 說成 required？**

`TRUTH-1` 是 BLOCK 級。一支純本機能跑的東西，文件裡不得寫「需要 API key」。
**多騙到一次註冊，永久失去一個使用者。**

---

## 改 `providers/aitokenking.yaml` 的規矩

這份檔案是全 repo 的事實來源，所以它的修改比別處嚴：

- 新增 `verified_facts` → 必附 `verified_at`（日期）＋ `source`（怎麼查的）＋ `evidence`（E1–E6）
- 移除一條宣稱 → **不要直接刪，移到 `retracted_claims` 並寫 `reason`**
- 改 `capabilities` 的值 → 必須是實測結果，不得是「應該有吧」
- **不得寫入任何具體 model id** —— 鐵律是「永遠先 `list_models` 再寫」，
  在契約裡放一個短生命週期的 model id 等於自己違反自己的規則

---

## 提交前

```bash
python3 scripts/check_catalog.py                  # ★ 三級分類 ＋ 範本安全預設值（需 PyYAML）
bash -n scripts/setup-aitokenking.sh              # shell 語法
bash scripts/setup-aitokenking.sh --dry-run       # 乾跑，不寫入任何檔案
python3 -c "import json;json.load(open('.mcp.json'))"
python3 -c "import yaml,sys;[yaml.safe_load(open(f)) for f in ['providers/aitokenking.yaml','providers/openai-compatible.yaml']]"
grep -rn 'sk-[A-Za-z0-9]\{16,\}' --exclude-dir=.git . && echo '🔴 疑似金鑰' || echo '✅ 無疑似金鑰'
```

**最後一項不是形式。** 金鑰進了 git 歷史，刪檔案沒有用 —— 必須輪替。

### `check_catalog.py` 會擋下什麼（已反向測試確認會響）

同一支工具跨兩組｜`allowlist_viable: false` 卻沒寫替代邊界｜
`purchase: true` 沒寫 `purchase_note`｜`verified_facts` 缺出處或日期｜
範本把 AWS 的 `READ_OPERATIONS_ONLY` 或 Azure 的 `--read-only` 關掉｜
範本裡出現真的金鑰而不是 `${VAR}` 參照｜範本帶 `autoApprove`｜
skill 缺三嵌入點任一｜skill 的 `name` 與資料夾不符｜
skill 宣告 `billable: false` 卻列了 B 組扣費工具｜
**skill 沒提到某個已存在的 catalog 平台**｜skill 引用了不存在的本地路徑（`REF-1`）｜
**宣告支援某語言卻沒把該語言寫進 `description`**（＝該語系叫不動這支 skill）｜
宣告支援某語言卻沒有對應的內文描述區塊。

**它不擋的：** 工具三組全空（未盤點）只 WARN，因為那是誠實的空白 ——
**能擋 PR 的檢核要留給「錯了就回不去」的那一類。**

---

## 送 PR 時請說明

1. **這個改動屬於哪一層**（策略／契約／文件／腳本）。
2. **如果它新增了一個宣稱，出處是什麼、什麼時候查的。**
3. **如果它動到判準或指標定義，為什麼** ——
   判準校準**月度不得週調**，一個 PR 裡「順手把門檻調低」會被退回。
