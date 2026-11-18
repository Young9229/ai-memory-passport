# AI-PASSPORT.md 通用记忆护照协议规范 (v1.0)

`AI-PASSPORT.md` 是一种**人类可读、全 AI 原生可解析**的跨平台个人长期记忆与偏好交换文件格式。它采用「自描述协议头 + 五维 Markdown 正文 + 尾部 JSON 镜像块」的三段式结构。

---

## 1. 文件三段式结构

### 第一段：自描述协议头（Self-Describing Protocol Header）
位于文件顶部，使用引用块声明该文件的性质。当用户将 `AI-PASSPORT.md` 直接上传或粘贴给任何没有任何预装插件的 AI（如网页版 ChatGPT、Claude、DeepSeek）时，AI 读到这段声明即可立即明白如何解析并应用其中的个人偏好。

### 第二段：五维记忆正文（5D Memory Body）
严格划分为以下 5 个二级标题章节（H2）：
1. `## [1] 身份与工作背景 (Identity & Work Context)`
2. `## [2] 沟通与输出偏好 (Communication & Output Preferences)`
3. `## [3] 工作流铁律与红线 (Workflow Guardrails & Hard Constraints)`
4. `## [4] 环境路径与工具链 (Environment, Paths & Toolchains)`
5. `## [5] 长期关注与周期任务 (Active Focus & Recurring Routines)`

### 第三段：机器可读 JSON 镜像块（Embedded JSON Block）
位于文件末尾的 HTML 注释块 `<!-- RAW_PASSPORT_START ... RAW_PASSPORT_END -->` 中，便于脚本工具（如 `memory_bridge.py` 或 WorkBuddy 的 `memory.md` 解析器）进行无损结构化读写、版本控制与 SHA-256 校验。

---

## 2. 主流 AI 工具本地存储落点映射表

`scripts/memory_bridge.py` 支持自动探测与双向转换以下主流 AI 工具的本地记忆与全局偏好配置：

| 工具标识 (`target`) | 工具名称 | 本地记忆/偏好文件典型路径（`~` 代表用户主目录） | 注入适配方式 |
| :--- | :--- | :--- | :--- |
| `workbuddy` | **WorkBuddy / CodeBuddy** | `~/.workbuddy/USER.md`<br>`~/.workbuddy/SOUL.md`<br>`~/.workbuddy/memory/*_memory.md` | 更新 `USER.md` 个人画像；增量同步至 `memory/*_memory.md`（保留 `RAW_JSON` 结构） |
| `antigravity` | **Google Antigravity** | `~/.gemini/GEMINI.md`<br>`~/.gemini/config/`<br>`~/.agents/rules/user-memory-passport.md` | 写入全局规则与 `~/.gemini/GEMINI.md` 标记块 |
| `claude` | **Claude Code (CLI/IDE)** | `~/.claude/CLAUDE.md`<br>`{workspace}/CLAUDE.md` | 在 `CLAUDE.md` 的 `<!-- AI-PASSPORT-START/END -->` 标记块中无损更新 |
| `cursor` | **Cursor IDE** | `~/.cursor/rules/ai-memory-passport.mdc`<br>`{workspace}/.cursorrules` | 生成带 `alwaysApply: true` 头部的 `.mdc` 规则文件 |
| `windsurf` | **Windsurf IDE** | `~/.codeium/windsurf/memories/global_rules.md`<br>`{workspace}/.windsurfrules` | 标记块合并注入 `global_rules.md` |
| `openclaw` | **OpenClaw** | `~/.openclaw/workspace/USER.md`<br>`~/.openclaw/workspace/MEMORY.md` | 映射合并至 `USER.md` 与 `MEMORY.md` |
| `agents` | **通用 Agent 标准 (AGENTS.md)** | `~/.agents/AGENTS.md`<br>`{workspace}/AGENTS.md` | 遵循开放 `AGENTS.md` 标准注入标记块 |

---

## 3. 安全与隐私脱敏规范

在生成需要上传到 GitHub 或跨平台传输的 `AI-PASSPORT.md` 时，必须遵守以下脱敏规则：
- **严禁包含明文凭据**：任何 API Key、RefreshToken、数据库密码、内网私有鉴权串必须替换为 `<REDACTED_SECRET>`。
- **保留结构与路径元信息**：本地工作区路径、工具调用方式、代理环境变量配置属于操作上下文，可根据用户需要保留（公开分享到 GitHub 时建议使用模板文件 `AI-PASSPORT.template.md`）。
