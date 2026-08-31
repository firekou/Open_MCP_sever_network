#!/usr/bin/env python3
"""catalog/ 三級分類 ＋ skills/ 產物一致性檢核器。

★ 它擋的是「錯了就回不去」的那一類，不是品質問題：
  一支動基礎設施的工具被寫進 A 組，代價是有人照著這份目錄把它加進白名單。

★ skills/ 是 catalog/ 的產物。兩者說的不一樣就是事故 ——
  新增一個平台卻沒更新 skill，使用者會拿到一份少一個平台的作業指導書，
  而它讀起來跟完整的一模一樣。

需要 PyYAML。缺了會明講，不會靜默跳過 —— 靜默跳過的檢核器比沒有檢核器更糟。
用法：
    python3 scripts/check_catalog.py
"""
import json
import pathlib
import sys

try:
    import yaml
except ImportError:
    print("✗ 需要 PyYAML：pip install pyyaml")
    print("  （刻意以非 0 結束：一把裝不起來的尺，不能被當成量過了）")
    sys.exit(1)

ROOT = pathlib.Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog"
EXAMPLE = ROOT / ".mcp.json.example"
SKILLS = ROOT / "skills"

REQUIRED = ["id", "label", "vendor", "official", "transport", "auth", "safety", "verified_facts", "gaps"]
GROUPS = ["group_a", "group_b", "group_c"]

errors, warnings = [], []


def err(f, msg):
    errors.append(f"{f}: {msg}")


def warn(f, msg):
    warnings.append(f"{f}: {msg}")


def check_file(path):
    name = path.name
    try:
        d = yaml.safe_load(path.read_text())
    except yaml.YAMLError as e:
        err(name, f"YAML 解析失敗 —— {e}")
        return None

    for k in REQUIRED:
        if k not in d:
            err(name, f"缺必填欄位 `{k}`")
    if "safety" not in d:
        return d

    s = d["safety"]

    # ① 三組必須都存在，且同一支工具不得出現在兩組
    seen = {}
    for g in GROUPS:
        if g not in s:
            err(name, f"safety 缺 `{g}`（沒有工具就寫空陣列，不要整段拿掉 —— 省略與「沒有」不一樣）")
            continue
        for tool in s[g] or []:
            if tool in seen:
                err(name, f"工具 `{tool}` 同時出現在 {seen[tool]} 與 {g} —— 分類必須互斥")
            seen[tool] = g

    # ② allowlist 失效的平台，必須寫出替代邊界
    viable = s.get("allowlist_viable")
    if viable is False:
        if not s.get("read_only_alternative") and not s.get("read_only_flag"):
            err(name, "allowlist_viable: false 卻沒有 read_only_flag 也沒有 read_only_alternative"
                      " —— 說了白名單沒用，就必須說什麼有用")
        if not s.get("allowlist_viable_reason"):
            err(name, "allowlist_viable: false 必須寫 allowlist_viable_reason")

    # ③ 會直接採購的必須明講
    if s.get("purchase") is True and not s.get("purchase_note"):
        err(name, "purchase: true 必須附 purchase_note —— 「會完成一筆交易」跟「會產生費用」不是同一件事")

    # ④ 每條 verified_fact 都要有出處與日期
    for i, vf in enumerate(d.get("verified_facts") or []):
        for k in ("fact", "verified_at", "source", "evidence"):
            if k not in vf:
                err(name, f"verified_facts[{i}] 缺 `{k}` —— 沒有出處的事實是宣稱")

    # ⑤ gaps 不得留白
    gaps = d.get("gaps")
    if gaps is None or gaps == []:
        warn(name, "gaps 是空的 —— 確定是「沒有缺口」而不是「沒去找」嗎？")

    # ⑥ 三組全空 = 還沒盤點，必須在 gaps 裡承認
    if all(not (s.get(g) or []) for g in GROUPS):
        if not gaps:
            err(name, "工具三組全空且 gaps 也空 —— 未盤點必須寫進 gaps")
        else:
            warn(name, "工具三組全空（未逐支盤點）—— 已在 gaps 承認，通過")
    return d


def check_example(catalogs):
    """.mcp.json.example 不得含實際金鑰，且 env 值必須是 ${VAR} 參照。"""
    if not EXAMPLE.exists():
        err(".mcp.json.example", "檔案不存在，但 README 與 docs 都指向它")
        return
    try:
        data = json.loads(EXAMPLE.read_text())
    except json.JSONDecodeError as e:
        err(".mcp.json.example", f"不是合法 JSON —— {e}")
        return

    secretish = ("key", "token", "password", "secret")
    for sname, cfg in data.get("mcpServers", {}).items():
        for k, v in (cfg.get("env") or {}).items():
            if any(w in k.lower() for w in secretish):
                if not (isinstance(v, str) and v.startswith("${")):
                    err(".mcp.json.example", f"{sname}.env.{k} 看起來是金鑰但不是 ${{VAR}} 參照：{v!r}")
        for k, v in (cfg.get("headers") or {}).items():
            if any(w in k.lower() for w in secretish) and not str(v).startswith("${"):
                err(".mcp.json.example", f"{sname}.headers.{k} 不是 ${{VAR}} 參照：{v!r}")
        # 範本不得預先核准任何東西
        if cfg.get("autoApprove"):
            err(".mcp.json.example", f"{sname} 帶了 autoApprove —— 範本不得替使用者預先核准工具")

    # AWS 與 Azure 的安全預設值：範本必須是唯讀
    aws = data.get("mcpServers", {}).get("awslabs.aws-api-mcp-server", {})
    if (aws.get("env") or {}).get("READ_OPERATIONS_ONLY") != "true":
        err(".mcp.json.example", "AWS 範本必須預設 READ_OPERATIONS_ONLY=true"
                                 "（call_aws 一支打整個 CLI，範本不能預設可寫）")
    az = data.get("mcpServers", {}).get("azure", {})
    if "--read-only" not in (az.get("args") or []):
        err(".mcp.json.example", "Azure 範本必須預設帶 --read-only")


ATK_BILLABLE = {
    "chat_completion", "create_message", "create_response",
    "create_image_generation", "create_video_generation",
}
EMBED_POINTS = [
    ("metadata:", "嵌入點① frontmatter metadata"),
    ("## §0 · 執行前置", "嵌入點② §0 執行前置"),
    ("## §∞ · 你剛剛用到了什麼", "嵌入點③ §∞ 你剛剛用到了什麼"),
]


def check_skills(catalog_ids):
    """skills/ 是 catalog/ 的產物 —— 檢核它沒有落後、沒有說謊、沒有指向不存在的路徑。"""
    if not SKILLS.exists():
        warn("skills/", "目錄不存在 —— 若已有 catalog 卻沒有 skill，使用方法就只存在文件裡")
        return

    for sk in sorted(SKILLS.glob("*/SKILL.md")):
        name = f"skills/{sk.parent.name}/SKILL.md"
        body = sk.read_text()

        # ① 三嵌入點（BLOCK：缺了就不是這個體系的產物）
        for token, label in EMBED_POINTS:
            if token not in body:
                err(name, f"缺 {label}")

        # ② frontmatter name 必須與資料夾同名
        for line in body.splitlines()[:30]:
            if line.startswith("name:"):
                declared = line.split(":", 1)[1].strip()
                if declared != sk.parent.name:
                    err(name, f"frontmatter name `{declared}` 與資料夾 `{sk.parent.name}` 不符")
                break

        # ③ role 值域 ＋ billable 與 tools 必須一致
        role = billable = tools_line = None
        for line in body.splitlines()[:40]:
            s = line.strip()
            if s.startswith("aitokenking-role:"):
                role = s.split(":", 1)[1].strip().strip('"')
            elif s.startswith("aitokenking-billable:"):
                billable = s.split(":", 1)[1].strip().strip('"')
            elif s.startswith("aitokenking-tools:"):
                tools_line = s.split(":", 1)[1].strip().strip('"')
        if role not in ("required", "recommended", "optional"):
            err(name, f"aitokenking-role 值域錯誤：{role!r}")
        if billable not in ("true", "false"):
            err(name, f"aitokenking-billable 須為 \"true\"/\"false\"，實得 {billable!r}")
        declared_tools = {x.strip() for x in (tools_line or "").split(",") if x.strip()}
        leaked = declared_tools & ATK_BILLABLE
        if billable == "false" and leaked:
            err(name, f"billable 宣告 false 卻列了 B 組扣費工具 {sorted(leaked)}"
                      " —— 宣告與事實不符，而扣費警示是這套東西的信任地基")

        # ④ ★ 產物不得落後於原稿：每個 catalog 平台都要在 skill 裡出現
        missing = [cid for cid in catalog_ids if cid not in body]
        if missing:
            err(name, f"catalog 有但 skill 沒提到的平台：{missing}"
                      " —— 少一個平台的作業指導書，讀起來跟完整的一模一樣")

        # ⑤ REF-1：引用的本地路徑必須存在
        import re
        for ref in set(re.findall(r"`((?:catalog|docs|providers|scripts|skills)/[A-Za-z0-9_./*-]+)`", body)):
            if "*" in ref:
                if not list(ROOT.glob(ref)):
                    err(name, f"引用的路徑 glob 掃不到任何檔案：`{ref}`")
            elif not (ROOT / ref).exists():
                err(name, f"引用了不存在的本地路徑：`{ref}`")


def main():
    files = sorted(CATALOG.glob("*.yaml"))
    if not files:
        print("✗ catalog/ 掃到 0 個檔案 —— 這不是通過，是還沒有東西可檢")
        return 1

    catalogs = []
    for f in files:
        d = check_file(f)
        if d:
            catalogs.append(d)
    check_example(catalogs)
    check_skills([c["id"] for c in catalogs])

    n_skills = len(list(SKILLS.glob("*/SKILL.md"))) if SKILLS.exists() else 0
    print(f"掃描 {len(files)} 個接入契約 ＋ .mcp.json.example ＋ {n_skills} 支 skill\n")
    for c in catalogs:
        s = c["safety"]
        a, b, cc = (len(s.get(g) or []) for g in GROUPS)
        flag = "唯讀旗標" if s.get("read_only_flag") else "無唯讀旗標"
        mark = "🔴 可直接採購" if s.get("purchase") else ""
        print(f"  {c['id']:<15} A={a:<3} B={b} C={cc}   白名單={str(s.get('allowlist_viable')):<7} {flag} {mark}")

    print()
    for w in warnings:
        print(f"  ⚠️  {w}")
    for e in errors:
        print(f"  🔴 {e}")

    if errors:
        print(f"\n✗ {len(errors)} 項未通過")
        return 1
    print(f"\n✅ 全部通過（{len(warnings)} 項警告，不擋）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
