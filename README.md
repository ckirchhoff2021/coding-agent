# Research Agent

> 基于 [deepagents](https://github.com/langchain-ai/deepagents) 的本地科研 Agent 框架：
> 一键启动、Web UI、多会话持久化、**完整执行过程可视化**、后台自进化 curator。

![stack](https://img.shields.io/badge/python-3.12+-blue) ![framework](https://img.shields.io/badge/deepagents-0.6.12-purple) ![license](https://img.shields.io/badge/license-MIT-green)

---

## ✨ 特性

- 🧠 **OpenAI 协议兼容** — 可接入任何兼容 Chat Completions 的模型（OpenAI / DeepSeek / Qwen / Doubao / vLLM 等）
- 🤝 **SubAgents** — 内置 data-analyst / literature-researcher / code-implementer 三个专职子代理，主 Agent 自动委派
- 🛠️ **完整工具链** — Shell 执行、文件读写、目录搜索、Todo 规划、子代理委派（deepagents 内置）；可选 Tavily 联网搜索
- 💾 **多会话持久化** — SQLite 保存全部会话、消息、工具调用轨迹，可随时切回历史会话
- 📊 **执行过程可视化** — Web UI 实时展示"📋 任务规划（状态实时更新）→ ⚙️ 工具调用时间线（参数+返回值默认展开）→ ✅ 最终回复"
- 🖼️ **多媒体预览** — 图片 / 视频 / 音频 / HTML 自动内嵌预览
- 🧬 **自进化 Curator** — 后台线程周期扫描会话，把稳定经验沉淀到 `data/memory/AGENTS.md` 与 `data/skills/`，自动回注
- 🎯 **零外部依赖** — 本项目自包含，不依赖任何上层仓库

---

## 🚀 快速开始

### 1. 安装

```bash
cd coding-agent
uv venv
source .venv/bin/activate
uv sync
```

### 2. 配置模型

```bash
cp .env.example .env
# 编辑 .env，填入你的模型 API 配置
```

最少需要配置 `BRAIN_API_KEY` / `BRAIN_API_URL` / `BRAIN_MODEL_NAME`（OpenAI 协议兼容即可）。
示例（豆包/火山方舟）：

```env
BRAIN_API_KEY=sk-xxx
BRAIN_API_URL=https://ark.cn-beijing.volces.com/api/v3
BRAIN_MODEL_NAME=doubao-seed-2-1-pro-260628
```

### 3. 启动 Web 服务

```bash
uv run python -m research_agent.server
# 或安装后的命令行入口：research-agent-server --port 8321
```

浏览器打开 **http://127.0.0.1:8321** 即可使用。

---

## 📁 项目结构

```
coding-agent/
├── research_agent/        # Python 包
│   ├── __init__.py
│   ├── config.py          # 配置 + 环境变量加载
│   ├── tools.py           # 内置附加工具（可选 web_search 等）
│   ├── subagents.py       # 3 个内置 SubAgent 定义
│   ├── agent_factory.py   # Agent 工厂（模型+工具+技能+checkpointer）
│   ├── session_store.py   # SQLite 会话/消息持久化
│   ├── curator.py         # 后台自进化子代理
│   ├── server.py          # FastAPI 服务（SSE + 会话 API + 文件预览）
│   ├── cli.py             # 命令行入口
│   └── static/            # 前端静态资源（index.html / favicon.svg）
├── skills/                # 用户/项目技能（每个子目录一个 SKILL.md）
│   └── quick-summary/
├── data/                  # 运行时数据（自动生成）
│   ├── sessions.db        # 会话元数据
│   ├── checkpoints.db     # langgraph 状态快照
│   ├── memory/AGENTS.md   # curator 沉淀的长期记忆
│   └── skills/            # curator 自动生成的新技能
├── outputs/               # Agent 产出的文件（前端自动预览）
├── tests/                 # 单元测试
├── pyproject.toml
├── .env.example
└── README.md
```

---

## 🎛️ 命令行

```bash
# Web 服务
uv run python -m research_agent.server --port 8321 --host 0.0.0.0
uv run python -m research_agent.server --no-curator    # 禁用自进化

# 命令行对话（不开前端）
uv run python -m research_agent.cli "帮我分析 outputs 目录下有什么"
uv run python -m research_agent.cli --list            # 列出历史会话
uv run python -m research_agent.cli --session <id>    # 继续某会话

# 手动跑一轮 curator（调试）
uv run python -m research_agent.curator --once

# 测试
uv run pytest tests -q
```

---

## 🔧 模型配置说明

所有遵循 OpenAI Chat Completions 协议的模型都可用。常用配置：

| 提供商 | BRAIN_API_URL | 备注 |
|---|---|---|
| OpenAI | `https://api.openai.com/v1` | 默认 |
| DeepSeek | `https://api.deepseek.com/v1` | deepseek-chat / deepseek-reasoner |
| 阿里 DashScope/Qwen | `https://dashscope.aliyuncs.com/compatible-mode/v1` | qwen-plus / qwen-max |
| 火山方舟/豆包 | `https://ark.cn-beijing.volces.com/api/v3` | doubao-* endpoint |
| vLLM 本地 | `http://localhost:8000/v1` | 自部署开源模型 |
| Ollama | `http://localhost:11434/v1` | 需设置 model 名 |

> 注意：不输出 reasoning 的模型（如豆包 seed-pro、gpt-4o-mini）在 Web UI 中不会显示"💭 思考过程"块，只会展示规划卡片 + 工具时间线。若需要显式思考过程，使用 deepseek-reasoner / qwen3 等推理模型。

---

## 🧩 添加自定义技能

在 `skills/` 下创建子目录，放入 `SKILL.md`：

```markdown
---
name: my-skill
description: 一句话说明何时触发该技能
---

# 技能名

## 适用场景
...

## 步骤
1. ...
2. ...
```

重启服务后自动加载。curator 也会自动往 `data/skills/` 沉淀新技能。

---

## 🔌 添加自定义 SubAgent

在 `research_agent/subagents.py` 的 `build_subagents()` 中追加一个 `SubAgent(...)` 即可，可指定专属 model/tools/system_prompt。

---

## 🔒 安全说明

- 文件预览接口严格限制在 `outputs/` 目录下，防路径穿越
- Shell 后端默认在项目根目录下执行命令（非 virtual 模式），请在信任环境下使用
- `.env` 已在 `.gitignore` 中，请勿提交密钥

---

## 📜 License

MIT
