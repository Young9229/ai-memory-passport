# AI Memory Passport (`ai-memory-passport`)

> **通用 AI 个人长期记忆与偏好跨平台迁移技能 | Universal AI Memory & Preference Portability Skill**

`ai-memory-passport` 是一套**不绑定特定工具、跨平台、跨设备通用**的个人长期记忆与沟通偏好迁移方案。它通过全平台 AI 原生可识别的自描述协议文件 **`AI-PASSPORT.md`**，将你在任意 AI 工具中沉淀的**个人身份背景、沟通排版偏好、工作流红线铁律、环境工具链配置、周期性 SOP** 无损提取并同步到任何其他 AI 工具中使用。

---

## 核心特性

1. **全 AI 通用识别协议（`AI-PASSPORT/1.0`）**：
   - 采用「自描述协议头 + 五维 Markdown 语义块 + 尾部 `RAW_PASSPORT_JSON` 校验块」三段式单文件架构。
   - 无论是本地 Agent（**WorkBuddy、Google Antigravity、Claude Code、Cursor、Windsurf、OpenClaw**）还是网页端大模型（**ChatGPT、Claude、DeepSeek、Kimi、Gemini、豆包**），均可零门槛直接识别并加载。
2. **本地与异地双模流转**：
   - **本地自动扫描与注入**：内置零依赖 Python CLI（`scripts/memory_bridge.py`），一键扫描本机已安装的各类 AI 工具记忆源，自动去重合并并导出/注入。
   - **异地/跨平台无文件流转**：内置通用「源 AI 记忆自提取提示词」与「目标 AI 冷启动注入提示词」，在手机端、网页端或异地电脑上仅靠复制粘贴即可完成记忆迁移。
3. **非破坏性增量融合与自动备份**：
   - 导入目标工具时采用 `<!-- AI-PASSPORT-START/END -->` 标记块增量融合，绝不粗暴覆盖目标工具原有配置。
   - 每次写入前自动生成 `.bak-<timestamp>` 备份文件，并支持 `--redact` 自动脱敏敏感凭据。

---

## 目录结构

```text
ai-memory-passport/
├── SKILL.md                        # 核心技能指令（兼容 WorkBuddy / Antigravity / Claude / OpenClaw）
├── _meta.json                      # WorkBuddy 技能元数据声明
├── README.md                       # 项目说明与快速上手指南
├── LICENSE                         # MIT 开源协议
├── .gitignore                      # Git 忽略规则（默认拦截个人私密 AI-PASSPORT.md 上传）
├── scripts/
│   └── memory_bridge.py            # 零依赖跨平台 CLI（scan / export / validate / import）
├── references/
│   ├── passport-spec.md            # AI-PASSPORT/1.0 协议规范与主流工具落点映射表
│   └── universal-prompts.md        # 网页端/异地 AI 通用记忆提取与冷启动注入提示词库
└── assets/
    └── AI-PASSPORT.template.md     # 空白 AI-PASSPORT.md 标准模板
```

---

## 快速开始

### 1. 作为 Agent Skill 安装使用

将本仓库克隆或复制到对应工具的技能目录即可直接通过自然语言触发（例如：*“帮我导出当前 AI 的个人记忆护照”* 或 *“把我的 AI-PASSPORT.md 同步到本机所有 AI 工具”*）：

- **WorkBuddy / CodeBuddy**：`~/.workbuddy/skills/ai-memory-passport`
- **Google Antigravity / 通用 Agents**：`~/.agents/skills/ai-memory-passport` 或项目内 `.agents/skills/ai-memory-passport`
- **Claude Code / OpenClaw**：`~/.claude/skills/ai-memory-passport` 或 `~/.openclaw/skills/ai-memory-passport`

### 2. 命令行直接运行（`memory_bridge.py`）

无需安装任何第三方 Python 包（仅使用 Python 3 标准库）：

```bash
# 1. 扫描本机已存在的 AI 记忆与规则文件
python scripts/memory_bridge.py scan

# 2. 导出并合成通用记忆护照（添加 --redact 可自动脱敏密码/Token）
python scripts/memory_bridge.py export --output ./AI-PASSPORT.md

# 3. 校验护照格式与 SHA-256 完整性
python scripts/memory_bridge.py validate --passport ./AI-PASSPORT.md

# 4. 预览将要注入的目标工具路径（Dry-Run）
python scripts/memory_bridge.py import --passport ./AI-PASSPORT.md --target all --dry-run

# 5. 执行安全注入（自动备份原文件）
python scripts/memory_bridge.py import --passport ./AI-PASSPORT.md --target workbuddy,antigravity,claude,cursor
```

---

## 五维通用记忆模型（5D Memory Schema）

| 维度 | 标题 | 核心记录内容 |
| :--- | :--- | :--- |
| **[1]** | **身份与工作背景** | 职业角色、负责业务模块、组织规范、公文/代码交付标准 |
| **[2]** | **沟通与输出偏好** | 交互语言、语气风格、排版规范（表格/序号/空格约定）、禁止的回复方式 |
| **[3]** | **工作流铁律与红线** | 先验后行、先读后写、写前备份、禁止截断、严禁虚构、合规边界 |
| **[4]** | **环境路径与工具链** | 操作系统、工作区路径、数据库/Python 环境、代理端口、环境踩坑记录 |
| **[5]** | **长期关注与周期任务** | 每日/每周/每月固定 SOP、长期跟进专项、常用快捷触发指令约定 |

---

## License

MIT License
