# 通用基线项目模板

一套面向 AI 驱动开发的多端项目基础框架。克隆即用，AI 接手后按三阶段工作流进入业务开发。

## 为什么用这套模板

- **AI 优先设计** — 所有规范、文档、仓库结构都面向 AI 编码助手优化，无论 Claude、Codex、Copilot 都遵循同一套规范
- **多仓协作** — 项目总仓管文档和规范，后端/管理端/移动端为独立 Git 仓库，独立分支、独立 CI、独立发布
- **上游同步** — 后端基于 ruoyi-vue-pro，管理端基于 yudao-ui-admin-vue3，保留 `upstream` 远端随时拉取框架更新
- **凭据安全** — 密码、令牌、内网地址不进仓库，统一走 `.env` + `project.config.yaml`（gitignored）
- **进度可追溯** — 总览 + 子文档两层进度体系，每一项功能都有设计、实现和验证记录

## 技术栈

| 层 | 技术 | 子目录 |
|----|------|--------|
| 后端 | Java 17 + Spring Boot 3 + ruoyi-vue-pro | `{PROJECT_CODE}-server/` |
| 管理端 | Vue 3 + Element Plus + yudao-ui-admin-vue3 | `{PROJECT_CODE}-admin-web/` |
| 移动端 | uniapp + Vue 3 + TypeScript | `{PROJECT_CODE}-uniapp/` |

## 快速开始

### 如果你是 AI

阅读 [AGENTS.md](AGENTS.md) → 按 [docs/README.md](docs/README.md) 的必读顺序进入具体文档 → 执行三阶段工作流。

### 如果你是人类开发者

1. 用 AI 编码助手打开本仓库（Claude Code / Copilot / Codex 等）
2. AI 会自动读取 `AGENTS.md`，按 `docs/00-项目初始化引导.md` 引导你完成初始化
3. 回答 4 个问题（项目短代码、中文名称、描述、风格），AI 自动完成剩余配置
4. 提供数据库连接信息和 Git 仓库地址
5. 开始描述你的业务需求

也可以手动按 [docs/README.md](docs/README.md) 的指引操作。

## 项目结构

```text
<PROJECT_ROOT>/
├── AGENTS.md                        # AI 接手唯一权威入口（所有工具共用）
├── CLAUDE.md                        # Claude Code 重定向到 AGENTS.md
├── README.md                        # 本文件
├── .github/
│   └── copilot-instructions.md      # GitHub Copilot 重定向到 AGENTS.md
├── project.config.example.yaml      # 项目身份令牌模板
├── project.config.yaml              # 项目身份（本机，不进仓库）
├── .env.example                     # 凭据模板
├── .env                             # 凭据（本机，不进仓库）
├── .gitignore
├── docs/
│   ├── README.md                    # 文档索引与必读顺序
│   ├── 00-项目初始化引导.md          # 阶段一：初始化
│   ├── 01-项目要求.md               # 业务模块、多端范围、UI 原则
│   ├── 02-Git仓库初始化引导.md       # 仓库策略、双远端、提交规范
│   ├── 03-数据库初始化引导.md        # 数据库与 Redis 配置
│   ├── 04-AI接手开发规范.md         # 后端/管理端/移动端分层规范
│   ├── 05-项目开发进度总览.md        # 整体进度、风险、排期
│   ├── 06-需求沟通与项目计划生成.md   # 阶段二：需求沟通
│   ├── 07-子任务并行执行与Git自动化.md # 阶段三：并行执行
│   ├── progress/                    # 功能级设计、开发和验证记录
│   └── examples/                    # 历史项目示例（只读参考）
├── {PROJECT_CODE}-server/           # 后端（独立 Git 仓库）
├── {PROJECT_CODE}-admin-web/        # 管理端（独立 Git 仓库）
└── {PROJECT_CODE}-uniapp/           # 移动端（独立 Git 仓库）
```

## 许可证

本模板基础结构开放使用。子项目（后端/管理端/移动端）分别遵循各自上游的许可证。
