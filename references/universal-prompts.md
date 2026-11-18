# 跨平台 / 异地 / 网页端 AI 通用提取与注入提示词库

当源 AI 或目标 AI 位于**异地设备、手机端、网页端（ChatGPT / Claude / DeepSeek / Kimi / Gemini / 豆包等）**或无法直接访问本地文件系统时，使用以下通用识别指令完成跨平台转移。

---

## 一、 源 AI 记忆自提取指令（Extraction Prompt）

> **使用方式**：将以下代码块中的全部内容复制并发送给**你正在使用的源 AI 工具**。源 AI 会自动盘点它所记住的关于你的所有长期记忆、偏好与对话上下文，并输出一份标准的 `AI-PASSPORT.md` 文本。

```markdown
【系统指令：生成 AI-PASSPORT.md 个人长期记忆护照】

请盘点你目前在 Memory（记忆库）、Custom Instructions（自定义指令）、个人画像以及历史对话中积累的关于我的所有**长期有效信息**，过滤掉一次性的临时问答噪音，严格按照以下 Markdown 模板输出一份完整的 `AI-PASSPORT.md`（不要省略任何细节，直接输出可复制的 Markdown 源码块）：

# AI Memory Passport (通用 AI 个人记忆护照)
> Protocol: `AI-PASSPORT/1.0`
> Updated: <当前日期 ISO-8601>

## [1] 身份与工作背景 (Identity & Work Context)
- 详细列出我的职业身份、负责的核心业务模块、日常工作场景、文书/代码/交付物标准格式。

## [2] 沟通与输出偏好 (Communication & Output Preferences)
- 详细列出我偏好的语言、语气风格、结构化排版要求（如表格、序号、公式/数字格式）、以及我明确反感或禁止的回复方式。

## [3] 工作流铁律与红线 (Workflow Guardrails & Hard Constraints)
- 详细列出我在处理任务时的硬性规定（如：先验证后执行、先读后写、禁止截断、严禁虚构、必须备份、合规要求等）。

## [4] 环境路径与工具链 (Environment, Paths & Toolchains)
- 详细列出我常用的操作系统、软件环境、开发语言/数据库版本、网络代理、常用路径约定、以及已知的软件/环境踩坑记录（如有敏感密码请脱敏为 `<REDACTED>`）。

## [5] 长期关注与周期任务 (Active Focus & Recurring Routines)
- 详细列出我按日/周/月推进的固定工作流程、当前持续跟进的重点项目、以及固定的快捷触发口令约定。
```

---

## 二、 目标 AI 记忆冷启动注入指令（Injection Prompt）

> **使用方式**：当你去到一个新的 AI 平台（或异地设备上的 AI）时：
> - **方式 1（直接上传文件）**：直接将生成的 `AI-PASSPORT.md` 作为附件上传（或放入 Claude Projects / ChatGPT 知识库），并发送一句：`请读取附件中的 AI-PASSPORT.md，将其作为我的全局长期记忆与沟通规范永久生效。`
> - **方式 2（纯文本粘贴注入）**：将下方提示词与你的 `AI-PASSPORT.md` 内容一起粘贴发送给目标 AI：

```markdown
【系统指令：加载并激活 AI-PASSPORT.md 个人长期记忆护照】

以下是我从其他 AI 工具迁移过来的《AI 通用个人记忆护照 (AI-PASSPORT/1.0)》。请你执行以下操作：
1. **完整解析并内化**：将下方五个维度的设定（身份背景、沟通偏好、工作流红线、环境工具链、长期周期任务）作为你与我交互的最高优先级全局上下文。
2. **持久化存储**：
   - 如果你具备本地文件读写能力（如 WorkBuddy、Antigravity、Claude Code、Cursor、OpenClaw 等），请将这些记忆无损合并到你的全局记忆文件（如 `USER.md`、`MEMORY.md`、`CLAUDE.md` 或 `.agents/rules/`）中，并在修改前备份原文件。
   - 如果你是网页端/云端对话 AI 且支持 Memory 功能，请将核心条目写入你的长期 Memory 中。
3. **对齐确认**：读取完毕后，请用简短的表格向我汇报你已成功加载的 5 个维度核心要点，无需寒暄，直接进入就绪状态。

---
<在此处粘贴你的 AI-PASSPORT.md 内容>
```

---

## 三、 单次未完成长对话交接指令（Session Handoff Prompt）

> **使用方式**：除了长期记忆外，如果你有一段正在进行中的复杂任务对话需要跨 AI 接力，可将以下指令发给源 AI，生成一份即插即用的任务交接单：

```markdown
请将我们当前正在进行的任务浓缩为一份《跨 AI 任务无缝交接单 (SESSION-HANDOFF.md)》，包含以下 5 项：
1. **最终目标 (Objective)**：一句话说明我们要完成什么。
2. **已确认事实与架构决策 (Confirmed Decisions)**：已经敲定、无需重新讨论的方案细节。
3. **当前进度与最新产物 (Current State & Artifacts)**：已经完成了哪些步骤，涉及哪些文件或关键代码片段。
4. **已排除的死胡同 (Dead Ends - 切勿重试)**：我们已经尝试过但失败或被否决的做法及原因，防止接手的新 AI 重复踩坑。
5. **下一步立即行动 (Immediate Next Step)**：接手的新 AI 收到这份交接单后，第一步应该直接执行什么操作。
```
