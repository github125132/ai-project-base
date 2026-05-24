# Git 仓库初始化引导

## 1. 仓库策略

本项目采用"项目总仓 + 各端独立代码仓"的多仓模式。所有内网主机、账号、邮箱通过 `.env` 维护;项目代码、分组、子仓目录名通过 `project.config.yaml` 维护。**文档与代码仓中不出现真实凭据。**

| 仓库 | 远端 URL 模板 | 本地子目录 | 职责 |
|------|---------------|------------|------|
| 项目总仓 | `http://${GIT_INTERNAL_USER}@${GIT_INTERNAL_HOST}/github125132/gap.git` | `<PROJECT_ROOT>/` | 项目文档、总体方案、协作规范、仓库关系 |
| 后端仓库 | `http://${GIT_INTERNAL_USER}@${GIT_INTERNAL_HOST}/github125132/ai-project-server.git` | `ai-project-server/` | Java 后端 |
| 管理端仓库 | `http://${GIT_INTERNAL_USER}@${GIT_INTERNAL_HOST}/github125132/ai-project-admin-web.git` | `ai-project-admin-web/` | Vue3 管理后台 |
| 移动端仓库 | `http://${GIT_INTERNAL_USER}@${GIT_INTERNAL_HOST}/github125132/ai-project-uniapp.git` | `ai-project-uniapp/` | uniapp 移动端 |

`<PROJECT_ROOT>` 为本机项目根目录,按实际情况替换。

## 2. 仓库边界(单一权威说明)

根仓 `.gitignore` 必须忽略:

```gitignore
/ai-project-server/
/ai-project-admin-web/
/ai-project-uniapp/

project.config.yaml
.env
.env.*
!.env.example
```

理由:三个子目录是独立 Git 仓库,直接提交到总仓会形成嵌套仓,无法独立分支、独立 CI、独立发布。其他文档不再重述这条规则,引用本节即可。

## 3. Git 账号

推送到内网 Git 服务时,统一使用本项目约定的账号与邮箱,**具体值放在 `.env` 中**:

```bash
git config user.name  "$GIT_USER_NAME"
git config user.email "$GIT_USER_EMAIL"
```

建议在每个子仓使用 `local` 配置,避免污染本机其他项目。

## 4. 初始化总仓

```bash
cd <PROJECT_ROOT>
git init
git remote add origin "http://${GIT_INTERNAL_USER}@${GIT_INTERNAL_HOST}/github125132/gap.git"
git config user.name  "$GIT_USER_NAME"
git config user.email "$GIT_USER_EMAIL"
```

总仓只提交:

- `AGENTS.md`
- `docs/`(不含本机生成的临时文件)
- `.gitignore`
- `.env.example`
- `project.config.example.yaml`

## 5. 初始化后端仓

```bash
git clone "http://${GIT_INTERNAL_USER}@${GIT_INTERNAL_HOST}/github125132/ai-project-server.git" ai-project-server
cd ai-project-server
git config user.name  "$GIT_USER_NAME"
git config user.email "$GIT_USER_EMAIL"
```

保留 ruoyi-vue-pro 上游用于同步框架更新:

```bash
git remote add upstream https://gitee.com/zhijiantianya/ruoyi-vue-pro.git
git remote -v
```

推荐分支:`master-jdk17`

## 6. 初始化管理端仓

```bash
git clone "http://${GIT_INTERNAL_USER}@${GIT_INTERNAL_HOST}/github125132/ai-project-admin-web.git" ai-project-admin-web
cd ai-project-admin-web
git config user.name  "$GIT_USER_NAME"
git config user.email "$GIT_USER_EMAIL"
git remote add upstream https://gitee.com/yudaocode/yudao-ui-admin-vue3.git
```

推荐分支:`master`

## 7. 初始化移动端仓

```bash
git clone "http://${GIT_INTERNAL_USER}@${GIT_INTERNAL_HOST}/github125132/ai-project-uniapp.git" ai-project-uniapp
cd ai-project-uniapp
git config user.name  "$GIT_USER_NAME"
git config user.email "$GIT_USER_EMAIL"
```

推荐分支:`master`

## 8. 提交和推送规范

提交信息使用中文,格式 `{类型}: {模块}: {简述}`。

类型:

| 类型 | 说明 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat: 基地管理: 添加基地详情接口` |
| `fix` | 修复缺陷 | `fix: 溯源管理: 修复批次号重复生成` |
| `docs` | 文档变更 | `docs: 初始化项目计划与子任务文档` |
| `refactor` | 重构(不改变功能) | `refactor: 检测管理: 提取报告导出公共方法` |
| `style` | 格式调整 | `style: 管理端: 统一表格列宽` |
| `test` | 测试 | `test: 基地管理: 补充 Service 层单元测试` |
| `chore` | 构建/工具/依赖 | `chore: 升级 ruoyi-vue-pro 上游依赖` |

示例:

- `feat: 基地管理: 添加基地 CRUD 接口`
- `feat: 管理端: 添加基地管理列表与表单页面`
- `feat: 移动端: 添加农事记录录入`
- `docs: 更新项目要求与模块清单`
- `fix: 检测管理: 修复报告导出日期格式错误`

根仓(纯文档)可省略模块:

```text
docs: 生成项目计划与子任务设计
进度: 完成 p0-01-base-基地管理
```

一项功能涉及多个仓库时,分别在对应仓库提交和推送,不混在根仓。

## 9. AI 接手检查清单

```bash
git status -sb
git remote -v
git config user.name
git config user.email

git -C ai-project-server  status -sb
git -C ai-project-admin-web    status -sb
git -C ai-project-uniapp      status -sb
```

若发现用户已有未提交改动,**不得回滚**;只在本次任务范围内追加或提交用户明确要求提交的内容。
