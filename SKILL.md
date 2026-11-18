---
name: ai-memory-passport
description: "通用 AI 长期记忆与个人偏好跨平台迁移技能（AI Memory Passport）。使用全平台 AI 通用的自描述协议文件（AI-PASSPORT.md），实现个人长期记忆、沟通偏好、工作流红线、环境配置在任意 AI 工具之间的本地自动迁移、异地跨设备迁移及网页端/客户端跨生态无缝流转。当用户提到迁移记忆、导出/导入 AI 偏好、更换 AI 工具、同步个人设定、生成 AI 记忆护照、跨平台转移上下文时触发。"
license: MIT
metadata:
  slug: ai-memory-passport
  displayName: "AI 记忆护照（通用 AI 偏好与长期记忆跨平台迁移）"
  version: "1.0.0"
  author: "Yang Zhixiang"
  description_zh: "使用全平台 AI 通用的 AI-PASSPORT.md 协议文件，实现个人长期偏好与记忆在任意本地或云端 AI 工具间的无损提取、合并与迁移。"
  description_en: "Universal AI long-term memory and preference portability skill using the self-describing AI-PASSPORT.md protocol for local, remote, and cross-platform AI migration."
  compatibility: "Universal (WorkBuddy, Antigravity, Claude Code, Cursor, Windsurf, OpenClaw, ChatGPT, Claude, DeepSeek, Kimi, Gemini, etc.)"
---

# AI 记忆护照（AI Memory Passport）

本技能提供一套**不绑定特定工具、跨平台、跨地域通用**的个人长期记忆与偏好迁移方案。核心载体是全 AI 通用识别的自描述文件 **`AI-PASSPORT.md`（AI 通用记忆护照）**，配合零依赖 Python 工具脚本 `scripts/memory_bridge.py`，支持**本机自动迁移**与**异地/网页端跨平台迁移**。

---

## 核心设计原则（Agent 必读）

1. **工具无关与协议优先**：
   - 所有记忆与偏好统一收敛为单文件标准格式 `AI-PASSPORT.md`（Markdown 语义分块 + 尾部 `RAW_PASSPORT_JSON` 机器可读校验块）。
   - 任何具备文本读取或对话能力的 AI（无论是本地 Agent 还是网页端大模型）均可直接识别、导出、吸收该文件。
2. **融合优先，严禁破坏性覆盖**：
   - 将记忆导入目标工具时，默认采用**增量融合（Merge & Deduplicate）**策略，保留目标工具已有的非冲突设定。
   - **写前必备份**：修改任何本地配置文件前，必须先生成 `.bak-<timestamp>` 备份文件。
3. **只迁长期高价值资产，过滤临时噪音**：
   - 仅提取和迁移**个人长期偏好、身份背景、沟通规范、工作流铁律、环境工具链、周期性关注事项**。
   - 严禁盲目搬运临时会话报错、一次性草稿、或者明文高危密钥（Token/Password 必须脱敏为占位符）。
4. **先预览确认，后执行落盘**：
   - 在向目标位置写入或覆盖前，必须向用户展示结构化变更摘要表格，经用户确认后再执行落盘。

---

## 五维通用记忆模型（Universal 5D Memory Schema）

提炼或合成 `AI-PASSPORT.md` 时，必须将散乱信息归类为以下五个标准维度：

| 维度编号 | 维度名称 | 包含内容说明 |
| :--- | :--- | :--- |
| **[1] Identity & Context** | **身份与工作背景** | 职业角色、负责业务模块、组织架构规范、公文/交付物标准格式 |
| **[2] Communication Style** | **沟通与输出偏好** | 交互语言、语气风格、排版规范（如表格优先、数字空格规则）、严禁出现的 AI 套话 |
| **[3] Workflow Guardrails** | **工作流铁律与红线** | 先读后写、写前验证、备份留痕、严禁虚构数据、安全合规边界 |
| **[4] Tech & Environment** | **环境路径与工具链** | 操作系统、固定工作区路径、数据库/Python 环境、代理配置、常用外部技能与系统避坑记录 |
| **[5] Active Focus & Routines** | **长期关注与周期任务** | 每日/每周/每月固定 SOP、正在推进的长期专项、常用触发指令约定 |

详细格式规范参见 [references/passport-spec.md](./references/passport-spec.md)。

---

## 标准执行工作流

当用户触发本技能时，先判断迁移场景属于以下三种模式中的哪一种，再按步骤执行：

### 模式 A：本机探测与导出（Local Scan & Export）

适用于：将当前电脑上已使用的 AI 工具（WorkBuddy、Antigravity、Claude Code、Cursor、OpenClaw 等）中的长期记忆提取并打包为通用 `AI-PASSPORT.md`，用于备份或带走。

1. **执行本机记忆源扫描**：
   运行内置脚本探测本机已存在的 AI 记忆、人设与规则文件：
   ```bash
   python "<skill_dir>/scripts/memory_bridge.py" scan
   ```
2. **提取并合成通用记忆护照**：
   运行导出命令将本机扫描到的记忆源自动汇总为初版护照文件：
   ```bash
   python "<skill_dir>/scripts/memory_bridge.py" export --output "./AI-PASSPORT.md"
   ```
3. **AI 语义精炼与去重（关键步骤）**：
   - 读取生成的 `./AI-PASSPORT.md` 以及扫描到的源文件。
   - 按照「五维通用记忆模型」进行语义合并、去重、冲突消解和敏感凭证脱敏。
   - 更新 `./AI-PASSPORT.md` 中的五大模块及尾部 `RAW_PASSPORT_JSON` 元数据。
4. **验证与交付**：
   运行校验命令确保格式完整：
   ```bash
   python "<skill_dir>/scripts/memory_bridge.py" validate --passport "./AI-PASSPORT.md"
   ```
   向用户展示提炼后的五维记忆摘要表及生成的 `AI-PASSPORT.md` 文件路径。

---

### 模式 B：异地 / 跨平台 / 网页端 AI 提取（Universal Prompt Transfer）

适用于：源 AI 工具在另一台设备、云端沙盒或网页端（如 ChatGPT、Claude 网页版、DeepSeek、Kimi 等），无法直接扫描本地文件。

1. **发放「自提取指令卡」**：
   读取 [references/universal-prompts.md](./references/universal-prompts.md) 中的 **「源 AI 记忆自提取 Prompt」**，发给用户并请用户复制到源 AI 对话框中执行。
2. **接收并标准化**：
   - 当用户把源 AI 输出的内容粘贴回来（或上传源 AI 导出的 JSON/MD 文件）后，按「五维通用记忆模型」清洗并写入 `./AI-PASSPORT.md`。
   - 若用户要求将当前 `AI-PASSPORT.md` 注入到另一个网页端/异地 AI，读取 [references/universal-prompts.md](./references/universal-prompts.md) 中的 **「目标 AI 记忆注入 Prompt」**，将护照内容封装为一段自包含的冷启动指令交由用户复制发送，或直接让用户将 `AI-PASSPORT.md` 作为附件/知识库文档上传给目标 AI。

---

### 模式 C：将记忆护照导入/同步到本机目标工具（Local Import & Sync）

适用于：用户已有 `AI-PASSPORT.md`（或刚从其他平台提取完毕），希望写入本机的某个或多个 AI 工具（如 WorkBuddy、Antigravity、Claude Code、Cursor、Windsurf、OpenClaw 等）。

1. **预览与冲突检测（Dry-Run）**：
   先读取目标工具现有的记忆或规则文件（路径映射见 `memory_bridge.py`），比对 `AI-PASSPORT.md` 中的五维内容：
   - 列出**新增项**、**保留项**与**潜在冲突项**（以表格呈现）。
   - 询问用户确认要写入的目标工具列表（例如：`workbuddy`、`antigravity`、`claude`、`cursor`、`openclaw`、`agents`）。
2. **执行带备份的安全注入**：
   用户确认后，调用脚本将护照注入目标工具（脚本会自动创建 `.bak` 备份并按目标工具原生格式写入）：
   ```bash
   python "<skill_dir>/scripts/memory_bridge.py" import --passport "./AI-PASSPORT.md" --target all
   ```
   （也可指定单一目标，如 `--target workbuddy` 或 `--target claude`）。
3. **写后回读核验**：
   读取写入后的目标文件与备份文件路径，向用户汇报每个目标工具的真实落盘状态。

---

## 捆绑资源索引

- **核心脚本**：[scripts/memory_bridge.py](./scripts/memory_bridge.py) — 跨平台（Windows/macOS/Linux）零依赖命令行工具，支持 `scan`、`export`、`import`、`validate` 四大子命令。
- **协议规范**：[references/passport-spec.md](./references/passport-spec.md) — `AI-PASSPORT.md` 文件结构规范与各主流 AI 工具存储落点映射表。
- **跨平台提示词**：[references/universal-prompts.md](./references/universal-prompts.md) — 面向无本地文件权限的网页端/异地 AI 的「一键套取记忆 Prompt」与「一键注入记忆 Prompt」。
- **标准模板**：[assets/AI-PASSPORT.template.md](./assets/AI-PASSPORT.template.md) — 空白 `AI-PASSPORT.md` 标准模板。
