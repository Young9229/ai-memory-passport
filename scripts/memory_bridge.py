#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Memory Passport - Universal Cross-Tool Memory & Preference Bridge
Zero-dependency Python 3 CLI for scanning, exporting, validating, and importing
long-term user preferences and memories across AI tools.
"""

import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import sys
from pathlib import Path

# Ensure UTF-8 console output on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROTOCOL_VERSION = "AI-PASSPORT/1.0"
MARKER_START = "<!-- AI-PASSPORT-START -->"
MARKER_END = "<!-- AI-PASSPORT-END -->"
RAW_JSON_START = "<!-- RAW_PASSPORT_START"
RAW_JSON_END = "RAW_PASSPORT_END -->"

REQUIRED_HEADERS = [
    "## [1] 身份与工作背景 (Identity & Work Context)",
    "## [2] 沟通与输出偏好 (Communication & Output Preferences)",
    "## [3] 工作流铁律与红线 (Workflow Guardrails & Hard Constraints)",
    "## [4] 环境路径与工具链 (Environment, Paths & Toolchains)",
    "## [5] 长期关注与周期任务 (Active Focus & Recurring Routines)",
]


def now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).astimezone().isoformat(timespec="seconds")


def get_home() -> Path:
    return Path.home()


def discover_sources(workspace: Path = None) -> list:
    """Scan local machine and optional workspace for known AI tool memory/preference files."""
    home = get_home()
    ws = workspace or Path.cwd()
    sources = []

    def add_if_exists(tool_id: str, tool_name: str, path: Path, kind: str):
        try:
            if path.exists() and path.is_file() and path.stat().st_size > 0:
                sources.append({
                    "tool_id": tool_id,
                    "tool_name": tool_name,
                    "path": str(path.resolve()),
                    "kind": kind,
                    "size": path.stat().st_size,
                    "mtime": datetime.datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds"),
                })
        except Exception:
            pass

    # 1. WorkBuddy / CodeBuddy
    wb_dir = home / ".workbuddy"
    if wb_dir.exists():
        add_if_exists("workbuddy", "WorkBuddy", wb_dir / "USER.md", "user_profile")
        add_if_exists("workbuddy", "WorkBuddy", wb_dir / "SOUL.md", "soul_persona")
        add_if_exists("workbuddy", "WorkBuddy", wb_dir / "IDENTITY.md", "identity")
        mem_dir = wb_dir / "memory"
        if mem_dir.exists():
            for f in sorted(mem_dir.glob("*_memory.md")):
                add_if_exists("workbuddy", "WorkBuddy", f, "memory_block")
            add_if_exists("workbuddy", "WorkBuddy", mem_dir / "MEMORY.md", "memory_md")

    # 2. Google Antigravity / Gemini
    gemini_dir = home / ".gemini"
    if gemini_dir.exists():
        add_if_exists("antigravity", "Antigravity", gemini_dir / "GEMINI.md", "global_rules")
        add_if_exists("antigravity", "Antigravity", gemini_dir / "config" / "GEMINI.md", "global_rules")

    # 3. Universal .agents
    agents_dir = home / ".agents"
    if agents_dir.exists():
        add_if_exists("agents", "Universal Agents", agents_dir / "AGENTS.md", "global_rules")
        rules_dir = agents_dir / "rules"
        if rules_dir.exists():
            for f in sorted(rules_dir.glob("*.md")):
                add_if_exists("agents", "Universal Agents", f, "rule_file")

    # 4. Claude Code
    claude_dir = home / ".claude"
    if claude_dir.exists():
        add_if_exists("claude", "Claude Code", claude_dir / "CLAUDE.md", "global_rules")

    # 5. Cursor
    cursor_dir = home / ".cursor"
    if cursor_dir.exists():
        rules_dir = cursor_dir / "rules"
        if rules_dir.exists():
            for f in sorted(rules_dir.glob("*.mdc")):
                add_if_exists("cursor", "Cursor IDE", f, "cursor_rule")

    # 6. Windsurf
    windsurf_file = home / ".codeium" / "windsurf" / "memories" / "global_rules.md"
    add_if_exists("windsurf", "Windsurf IDE", windsurf_file, "global_rules")

    # 7. OpenClaw
    openclaw_ws = home / ".openclaw" / "workspace"
    if openclaw_ws.exists():
        add_if_exists("openclaw", "OpenClaw", openclaw_ws / "USER.md", "user_profile")
        add_if_exists("openclaw", "OpenClaw", openclaw_ws / "SOUL.md", "soul_persona")
        add_if_exists("openclaw", "OpenClaw", openclaw_ws / "MEMORY.md", "memory_md")

    # 8. Current Workspace Rules
    for rel, tid, tname in [
        ("CLAUDE.md", "claude", "Claude Code (Workspace)"),
        ("AGENTS.md", "agents", "Universal Agents (Workspace)"),
        ("GEMINI.md", "antigravity", "Antigravity (Workspace)"),
        (".cursorrules", "cursor", "Cursor (Workspace)"),
        (".windsurfrules", "windsurf", "Windsurf (Workspace)"),
    ]:
        add_if_exists(tid, tname, ws / rel, "workspace_rules")

    return sources


def redact_secrets(text: str) -> str:
    """Redact potential sensitive tokens, passwords, or keys when --redact is enabled."""
    patterns = [
        (r"(?i)(api[_-]?key|secret|token|password|passwd|pwd)\s*[:=]\s*['\"]?[A-Za-z0-9_\-\.~+/]{8,}['\"]?", r"\1: <REDACTED_SECRET>"),
        (r"sk-[A-Za-z0-9]{20,}", "<REDACTED_API_KEY>"),
        (r"ghp_[A-Za-z0-9]{20,}", "<REDACTED_GITHUB_TOKEN>"),
    ]
    out = text
    for pat, repl in patterns:
        out = re.sub(pat, repl, out)
    return out


def parse_workbuddy_memory(content: str) -> dict:
    """Parse WorkBuddy's *_memory.md format into the 5 universal dimensions."""
    sections = {
        "identity": [],
        "communication": [],
        "guardrails": [],
        "environment": [],
        "routines": [],
    }
    # Strip RAW_JSON comment block first
    clean = re.sub(r"<!--\s*RAW_JSON_START.*?RAW_JSON_END\s*-->", "", content, flags=re.DOTALL).strip()

    # Extract blocks by bold headers (**工作背景**, **个人背景**, **当前关注**, **近期动态**)
    blocks = {}
    current_key = "general"
    blocks[current_key] = []
    for line in clean.splitlines():
        s = line.strip()
        if s in ("**工作背景**", "### 工作背景", "## 工作背景"):
            current_key = "work"
            blocks.setdefault(current_key, [])
        elif s in ("**个人背景**", "### 个人背景", "## 个人背景"):
            current_key = "personal"
            blocks.setdefault(current_key, [])
        elif s in ("**当前关注**", "### 当前关注", "## 当前关注"):
            current_key = "focus"
            blocks.setdefault(current_key, [])
        elif s in ("**近期动态**", "### 近期动态", "## 近期动态"):
            current_key = "recent"
            blocks.setdefault(current_key, [])
        elif s.startswith("# ") or s.startswith("> ") or s == "## Memory Block" or s == "---":
            continue
        else:
            if s:
                blocks.setdefault(current_key, []).append(s)

    # Split work block into identity & environment
    for line in blocks.get("work", []):
        sentences = [p.strip() for p in re.split(r"(?<=[。；])", line) if p.strip()]
        for sent in sentences:
            if any(k in sent for k in ("环境", "数据库", "MySQL", "Python", "工作区", "代理", "Windows", "macOS", "Linux")):
                sections["environment"].append(f"- {sent}")
            else:
                sections["identity"].append(f"- {sent}")

    # Split personal block into communication & guardrails
    for line in blocks.get("personal", []):
        sentences = [p.strip() for p in re.split(r"(?<=[。；])", line) if p.strip()]
        for sent in sentences:
            if any(k in sent for k in ("严禁", "验证", "核验", "禁止截断", "备份", "可追溯", "高风险", "不截断", "合规", "劳动法", "只写已确认")):
                sections["guardrails"].append(f"- {sent}")
            else:
                sections["communication"].append(f"- {sent}")

    # Focus -> routines
    for line in blocks.get("focus", []):
        sentences = [p.strip() for p in re.split(r"(?<=[。；])", line) if p.strip()]
        for sent in sentences:
            sections["routines"].append(f"- {sent}")

    # Recent -> environment or routines
    for line in blocks.get("recent", []):
        item = line if line.startswith("-") else f"- {line}"
        if any(k in item for k in ("路径", "PowerShell", "环境", "MySQL", "web-access", "目录")):
            sections["environment"].append(item)
        else:
            sections["routines"].append(item)

    return sections


def parse_generic_markdown(content: str, source_label: str) -> dict:
    """Fallback parser for generic USER.md / CLAUDE.md / GEMINI.md files."""
    sections = {
        "identity": [],
        "communication": [],
        "guardrails": [],
        "environment": [],
        "routines": [],
    }
    # Strip YAML frontmatter and HTML comments
    clean = re.sub(r"^---\r?\n.*?\r?\n---\r?\n?", "", content, flags=re.DOTALL)
    clean = re.sub(r"<!--.*?-->", "", clean, flags=re.DOTALL).strip()
    if not clean:
        return sections

    # If it's already an AI-PASSPORT.md format, extract directly
    if "AI-PASSPORT/1.0" in content:
        key_map = {
            "[1]": "identity",
            "[2]": "communication",
            "[3]": "guardrails",
            "[4]": "environment",
            "[5]": "routines",
        }
        cur = None
        for line in clean.splitlines():
            if line.startswith("## "):
                cur = None
                for k, v in key_map.items():
                    if k in line:
                        cur = v
                        break
            elif cur and line.strip() and not line.strip().startswith("---"):
                sections[cur].append(line.rstrip())
        return sections

    boilerplate_phrases = (
        "The more you know, the better you can help",
        "You're not a chatbot. You're becoming someone",
        "Each session, you wake up fresh",
        "If you change this file, tell the user",
        "This file is yours to evolve",
        "This isn't just metadata",
        "Save this file at the workspace root",
        "Bootstrapping a workspace manually",
        "*(待补充)*",
        "*(optional)*",
    )

    for line in clean.splitlines():
        s = line.strip()
        if not s or s.startswith("#") or s == "---":
            continue
        if any(bp in s for bp in boilerplate_phrases):
            continue
        # Skip empty markdown field labels like "- **Occupation:**"
        if re.match(r"^-\s*\*\*[^*]+:\*\*\s*$", s):
            continue
        if s in ("Notes:", "- Notes:"):
            continue

        bullet = s if s.startswith("-") else f"- [{source_label}] {s}"
        if any(k in s for k in ("禁止", "严禁", "必须", "不得", "备份", "验证", "Private things stay private", "When in doubt, ask", "Never send half-baked")):
            sections["guardrails"].append(bullet)
        elif any(k in s for k in ("路径", "环境", "代理", "Python", "Windows", "macOS", "CLI", "path", "proxy")):
            sections["environment"].append(bullet)
        elif any(k in s for k in ("语言", "语气", "格式", "排版", "表格", "中文", "Vibe:", "Be genuinely helpful", "Concise when needed")):
            sections["communication"].append(bullet)
        elif any(k in s for k in ("每周", "每日", "每月", "定时", "周报", "公众号", "日常基于")):
            sections["routines"].append(bullet)
        else:
            sections["identity"].append(bullet)
    return sections


def deduplicate_lines(lines: list) -> list:
    seen = set()
    result = []
    for line in lines:
        norm = re.sub(r"\s+", " ", line.strip())
        if norm and norm not in seen:
            seen.add(norm)
            result.append(line.strip())
    return result


def build_passport_markdown(merged: dict, source_tools: list, do_redact: bool = False) -> str:
    ts = now_iso()
    sec_texts = {}
    defaults = {
        "identity": "- 暂未检测到身份与工作背景记录，可在此补充职业角色、负责模块与文档规范。",
        "communication": "- 默认使用中文交流，表达简洁、权威、可执行，关键对比使用表格呈现。",
        "guardrails": "- 先验证可行性再执行；重要修改前必须保留备份；严禁虚构数据或截断输出。",
        "environment": "- 暂未检测到特定环境配置，可在此补充常用路径、开发环境与代理信息。",
        "routines": "- 暂未检测到固定周期性任务，可在此补充每日/每周/每月固定工作流。",
    }
    for key in ("identity", "communication", "guardrails", "environment", "routines"):
        deduped = deduplicate_lines(merged.get(key, []))
        text = "\n".join(deduped) if deduped else defaults[key]
        if do_redact:
            text = redact_secrets(text)
        sec_texts[key] = text

    raw_payload = {
        "protocol": PROTOCOL_VERSION,
        "version": 1,
        "updatedAt": ts,
        "sourceTools": sorted(list(set(source_tools))),
        "sections": sec_texts,
    }
    content_hash = hashlib.sha256(
        json.dumps(sec_texts, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    raw_payload["contentHash"] = f"sha256:{content_hash}"

    md = f"""# AI Memory Passport (通用 AI 个人记忆护照)

> **Protocol**: `{PROTOCOL_VERSION}`
> **Last Updated**: `{ts}`
> **Source Tools**: `{", ".join(raw_payload["sourceTools"]) if raw_payload["sourceTools"] else "manual"}`
> **Content Hash**: `sha256:{content_hash[:16]}...`
> **Self-Describing Instruction for Any AI**:
> 本文件遵循 `{PROTOCOL_VERSION}` 跨平台通用记忆协议。任何读取本文件的 AI 助手（无论本地 Agent 或云端对话大模型）均须将以下五个维度的内容作为当前用户的**全局长期记忆、沟通准则与工作流红线**立即生效。

---

## [1] 身份与工作背景 (Identity & Work Context)

{sec_texts["identity"]}

## [2] 沟通与输出偏好 (Communication & Output Preferences)

{sec_texts["communication"]}

## [3] 工作流铁律与红线 (Workflow Guardrails & Hard Constraints)

{sec_texts["guardrails"]}

## [4] 环境路径与工具链 (Environment, Paths & Toolchains)

{sec_texts["environment"]}

## [5] 长期关注与周期任务 (Active Focus & Recurring Routines)

{sec_texts["routines"]}

---

{RAW_JSON_START}
{json.dumps(raw_payload, ensure_ascii=False, indent=2)}
{RAW_JSON_END}
"""
    return md


def cmd_scan(args):
    sources = discover_sources(Path(args.workspace) if args.workspace else None)
    if args.json:
        print(json.dumps({"count": len(sources), "sources": sources}, ensure_ascii=False, indent=2))
        return 0

    print(f"🔍 已扫描本机 AI 记忆与偏好配置源，共发现 {len(sources)} 个有效文件：\n")
    if not sources:
        print("  （未探测到已知的本地 AI 记忆文件，可使用异地提取提示词生成 AI-PASSPORT.md）")
        return 0

    print(f"{'工具标识':<14} | {'工具名称':<22} | {'类型':<16} | {'大小(B)':<8} | 路径")
    print("-" * 105)
    for s in sources:
        print(f"{s['tool_id']:<14} | {s['tool_name']:<22} | {s['kind']:<16} | {s['size']:<8} | {s['path']}")
    return 0


def cmd_export(args):
    sources = discover_sources(Path(args.workspace) if args.workspace else None)
    merged = {
        "identity": [],
        "communication": [],
        "guardrails": [],
        "environment": [],
        "routines": [],
    }
    source_tools = []

    for s in sources:
        p = Path(s["path"])
        try:
            content = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue

        source_tools.append(s["tool_id"])
        if s["tool_id"] == "workbuddy" and s["kind"] == "memory_block":
            parsed = parse_workbuddy_memory(content)
        else:
            parsed = parse_generic_markdown(content, s["tool_name"])

        for k in merged:
            merged[k].extend(parsed.get(k, []))

    md = build_passport_markdown(merged, source_tools, do_redact=args.redact)
    out_path = Path(args.output).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(md, encoding="utf-8")

    print(f"✅ 已成功导出通用 AI 记忆护照：{out_path}")
    print(f"   - 聚合来源工具：{', '.join(sorted(set(source_tools))) if source_tools else '默认模板'}")
    for idx, (k, label) in enumerate([
        ("identity", "[1] 身份与工作背景"),
        ("communication", "[2] 沟通与输出偏好"),
        ("guardrails", "[3] 工作流铁律与红线"),
        ("environment", "[4] 环境路径与工具链"),
        ("routines", "[5] 长期关注与周期任务"),
    ], 1):
        count = len(deduplicate_lines(merged[k]))
        print(f"   - {label}：{count} 条核心记忆")
    return 0


def cmd_validate(args):
    p = Path(args.passport).resolve()
    if not p.exists():
        print(f"❌ 找不到记忆护照文件：{p}")
        return 1

    content = p.read_text(encoding="utf-8", errors="replace")
    errors = []

    if PROTOCOL_VERSION not in content:
        errors.append(f"缺少协议版本声明 `{PROTOCOL_VERSION}`")

    for h in REQUIRED_HEADERS:
        if h not in content:
            errors.append(f"缺少标准维度章节标题：`{h}`")

    match = re.search(r"<!--\s*RAW_PASSPORT_START\s*(.*?)\s*RAW_PASSPORT_END\s*-->", content, flags=re.DOTALL)
    if not match:
        errors.append("缺少尾部 `RAW_PASSPORT_START ... RAW_PASSPORT_END` 机器校验 JSON 块")
    else:
        try:
            data = json.loads(match.group(1))
            if data.get("protocol") != PROTOCOL_VERSION:
                errors.append("JSON 块中的 protocol 字段不匹配")
        except Exception as e:
            errors.append(f"尾部 JSON 块解析失败：{e}")

    if errors:
        print(f"❌ 记忆护照校验未通过（{p}）：")
        for err in errors:
            print(f"   - {err}")
        return 1

    print(f"✅ 记忆护照校验通过：{p}（符合 {PROTOCOL_VERSION} 标准规范）")
    return 0


def backup_file(path: Path) -> Path:
    if not path.exists():
        return None
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    bak = path.with_name(f"{path.name}.bak-{ts}")
    shutil.copy2(path, bak)
    return bak


def extract_clean_body_from_passport(passport_content: str) -> str:
    """Extract the 5D sections from AI-PASSPORT.md for clean injection into target rule files."""
    body = re.sub(r"<!--\s*RAW_PASSPORT_START.*?RAW_PASSPORT_END\s*-->", "", passport_content, flags=re.DOTALL).strip()
    return f"{MARKER_START}\n{body}\n{MARKER_END}\n"


def upsert_marker_block(target_path: Path, block_text: str) -> tuple:
    """Insert or update the AI-PASSPORT marker block inside a target Markdown file with backup."""
    bak = backup_file(target_path) if target_path.exists() else None
    target_path.parent.mkdir(parents=True, exist_ok=True)

    if target_path.exists():
        existing = target_path.read_text(encoding="utf-8", errors="replace")
        pattern = re.compile(re.escape(MARKER_START) + r".*?" + re.escape(MARKER_END) + r"\n?", flags=re.DOTALL)
        if pattern.search(existing):
            updated = pattern.sub(block_text, existing)
            action = "updated_marker_block"
        else:
            updated = existing.rstrip() + "\n\n" + block_text
            action = "appended_marker_block"
    else:
        updated = block_text
        action = "created_new_file"

    target_path.write_text(updated, encoding="utf-8")
    return action, bak


def cmd_import(args):
    passport_path = Path(args.passport).resolve()
    if not passport_path.exists():
        print(f"❌ 找不到输入的记忆护照文件：{passport_path}")
        return 1

    passport_content = passport_path.read_text(encoding="utf-8", errors="replace")
    block_text = extract_clean_body_from_passport(passport_content)
    home = get_home()

    target_map = {
        "workbuddy": home / ".workbuddy" / "USER.md",
        "antigravity": home / ".agents" / "rules" / "ai-memory-passport.md",
        "agents": home / ".agents" / "AGENTS.md",
        "claude": home / ".claude" / "CLAUDE.md",
        "cursor": home / ".cursor" / "rules" / "ai-memory-passport.mdc",
        "windsurf": home / ".codeium" / "windsurf" / "memories" / "global_rules.md",
        "openclaw": home / ".openclaw" / "workspace" / "USER.md",
    }

    requested = [t.strip().lower() for t in args.target.split(",") if t.strip()]
    if "all" in requested:
        # Only import to tools whose parent root exists, plus workbuddy and agents by default
        selected = []
        for tid, tpath in target_map.items():
            if tid in ("workbuddy", "antigravity", "agents") or tpath.parent.exists() or tpath.parent.parent.exists():
                selected.append(tid)
    else:
        selected = [t for t in requested if t in target_map]

    if not selected:
        print(f"❌ 未匹配到有效目标工具。支持的目标：{', '.join(target_map.keys())} 或 all")
        return 1

    results = []
    for tid in selected:
        tpath = target_map[tid]
        if args.dry_run:
            results.append((tid, str(tpath), "dry_run_ready", None))
            continue

        if tid == "cursor":
            mdc_header = "---\ndescription: Universal AI User Memory & Preferences Passport\nglobs: *\nalwaysApply: true\n---\n\n"
            action, bak = upsert_marker_block(tpath, mdc_header + block_text)
        else:
            action, bak = upsert_marker_block(tpath, block_text)
        results.append((tid, str(tpath), action, str(bak) if bak else "无(新建)"))

    print("📦 记忆护照注入执行结果：\n")
    print(f"{'目标工具':<14} | {'执行动作':<22} | {'目标文件路径':<52} | 备份文件")
    print("-" * 120)
    for tid, tpath, action, bak in results:
        print(f"{tid:<14} | {action:<22} | {tpath:<52} | {bak}")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="AI Memory Passport - 通用 AI 长期记忆与个人偏好跨平台迁移工具"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_scan = sub.add_parser("scan", help="扫描本机已安装的 AI 工具记忆与偏好文件")
    p_scan.add_argument("--workspace", default=None, help="指定额外扫描的工作区目录")
    p_scan.add_argument("--json", action="store_true", help="以 JSON 格式输出")
    p_scan.set_defaults(func=cmd_scan)

    p_export = sub.add_parser("export", help="从本机 AI 工具提取并合成通用 AI-PASSPORT.md")
    p_export.add_argument("--output", "-o", default="./AI-PASSPORT.md", help="输出护照文件路径")
    p_export.add_argument("--workspace", default=None, help="指定工作区目录")
    p_export.add_argument("--redact", action="store_true", help="自动脱敏密码与敏感 Token（适合公开分享）")
    p_export.set_defaults(func=cmd_export)

    p_val = sub.add_parser("validate", help="校验 AI-PASSPORT.md 格式完整性")
    p_val.add_argument("--passport", "-p", default="./AI-PASSPORT.md", help="待校验的护照文件路径")
    p_val.set_defaults(func=cmd_validate)

    p_imp = sub.add_parser("import", help="将 AI-PASSPORT.md 安全注入到目标 AI 工具（自动备份）")
    p_imp.add_argument("--passport", "-p", default="./AI-PASSPORT.md", help="输入的护照文件路径")
    p_imp.add_argument(
        "--target", "-t",
        default="workbuddy,antigravity,agents",
        help="目标工具标识（逗号分隔）：workbuddy,antigravity,claude,cursor,windsurf,openclaw,agents 或 all"
    )
    p_imp.add_argument("--dry-run", action="store_true", help="仅预览将要修改的目标路径，不实际写入")
    p_imp.set_defaults(func=cmd_import)

    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
