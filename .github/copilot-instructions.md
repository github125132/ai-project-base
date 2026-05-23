# Copilot Instructions

本文件由 [AGENTS.md](../AGENTS.md) 驱动。所有 AI 编码助手接手本项目时，以 `AGENTS.md` 为唯一权威入口。

## 摘要

- 项目采用"项目总仓 + 各端独立代码仓"的多仓模式
- 三阶段工作流：初始化 → 需求沟通与计划生成 → 子任务并行执行
- 后端基于 ruoyi-vue-pro (Java 17 + Spring Boot 3)，管理端基于 yudao-ui-admin-vue3 (Vue 3 + Element Plus)，移动端基于 uniapp (Vue 3 + TypeScript)
- 用户可见内容必须中文；状态码、枚举名不得直接展示
- 状态字段遵循双轨规则（字典 / 枚举二选一）
- 凭据不进仓库（使用 `.env` + `project.config.yaml`）

## 必读顺序

见 [docs/README.md](../docs/README.md) 的"唯一权威必读顺序"。

## 工作流

```
理解需求 → 判断涉及仓库 → 查进度总览和相关子文档 → 查现有代码风格 →
设计实现方案 → 更新或创建 progress 子文档 → 修改代码 → 验证 →
更新进度文档 → 分仓提交推送
```

## 提交规范

提交信息使用中文，格式：`{类型}: {模块}: {简述}`

类型：`feat` / `fix` / `docs` / `refactor` / `style` / `test` / `chore`
