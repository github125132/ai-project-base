# 中药材GAP基地全流程服务平台

> 本仓基于**通用基线项目模板**生成。任何 AI 会话接手时,**必须按三阶段顺序工作**:
>
> 1. **初始化** —— 见 [docs/00-项目初始化引导.md](docs/00-项目初始化引导.md):占位符替换、子仓改名、配置生成
> 2. **需求沟通与项目计划生成** —— 见 [docs/06-需求沟通与项目计划生成.md](docs/06-需求沟通与项目计划生成.md):向用户问询业务,产出项目计划总览与可并行的子任务文档
> 3. **子任务并行执行与 Git 自动化** —— 见 [docs/07-子任务并行执行与Git自动化.md](docs/07-子任务并行执行与Git自动化.md):按子任务文档落地代码,自动提交、推送、合并
>
> 当前所在阶段由仓库状态判断(详见各阶段文档的"判定方法")。

## 项目身份

- 项目代码:`gap`
- 一句话描述:面向中药材规范化种植基地的 GAP 合规与全流程服务平台
- 风格定位:专业合规、政务级、药企认可、科技清爽、绿色中药材主题
- 支持端:PC 管理后台、手机 APP、(可选)大屏驾驶舱、(可选)外部展示 H5、(可选)线下物料

业务模块、多端范围、UI 原则的完整说明见 [docs/01-项目要求.md](docs/01-项目要求.md)。

## 技术栈与仓库边界

| 层 | 技术 | 子目录 | 远端仓 |
|----|------|--------|--------|
| 后端 | Java 17 + Spring Boot 3 + ruoyi-vue-pro | `ai-project-server/` | `github125132/ai-project-server.git` |
| 管理端 | Vue 3 + Element Plus + yudao-ui-admin-vue3 | `ai-project-admin-web/` | `github125132/ai-project-admin-web.git` |
| 移动端 | uniapp + Vue 3 + TypeScript | `ai-project-uniapp/` | `github125132/ai-project-uniapp.git` |
| 大屏端 | Web 可视化 | 待定 | 后续规划 |
| 外部 H5 | 移动端 H5 | 待定 | 后续规划 |

- 项目总仓负责文档与协作规范,**不收纳**子仓源码
- 子仓为独立 Git 仓库,独立分支、独立 CI、独立发布
- 详细仓库地址模板、初始化步骤、`.gitignore` 规则见 [docs/02-Git仓库初始化引导.md](docs/02-Git仓库初始化引导.md)

## 必读入口

唯一权威必读顺序见 [docs/README.md](docs/README.md)。AI 接手前务必先读该索引,再进入具体子文档。

## Quick start

```bash
# 0. 初始化(首次接入新项目)
# AI 阅读 docs/00-项目初始化引导.md,交互式采集 4 个字段,自动生成 project.config.yaml + .env
# 用户无需手动编辑配置

# 1. 拉取三个子仓(若尚未存在)
git clone "http://${GIT_INTERNAL_USER}@${GIT_INTERNAL_HOST}/github125132/ai-project-server.git" ai-project-server
git clone "http://${GIT_INTERNAL_USER}@${GIT_INTERNAL_HOST}/github125132/ai-project-admin-web.git"   ai-project-admin-web
git clone "http://${GIT_INTERNAL_USER}@${GIT_INTERNAL_HOST}/github125132/ai-project-uniapp.git"     ai-project-uniapp

# 2. 数据库与 Redis
#    见 docs/03-数据库初始化引导.md

# 3. 启动后端
cd ai-project-server && mvn spring-boot:run -pl yudao-server

# 4. 启动管理端
cd ai-project-admin-web && pnpm install && pnpm dev

# 5. 启动移动端
cd ai-project-uniapp && pnpm install && pnpm dev:h5
```

## 不可变基础 vs 项目专属内容

AI 在任何阶段都必须区分以下两类内容,**不可变基础不得随项目需求修改**。

### 不可变(模板级,跨项目稳定)

- 三阶段工作流与 `docs/00`、`docs/06`、`docs/07` 三份协议文档
- `docs/04-AI接手开发规范.md` 的分层结构(Controller/Service/Mapper/DO/VO)、状态字段双轨规则、禁止事项
- `docs/02` 第 2 节"仓库边界(单一权威说明)"
- `.env` / `project.config.yaml` / `application-local.yaml` 凭据机制
- ruoyi-vue-pro、yudao-ui-admin-vue3、uniapp 框架自身代码与目录约定
- 子仓边界:根仓不收纳子仓源码;子仓独立 Git 仓库、独立分支、独立 CI
- `docs/examples/`:历史示例,只读,不参与令牌替换、不被项目计划引用

> 若发现以上内容确有缺陷,**单独提 issue 改进模板本身**,不要混入业务 PR。

### 项目专属(每个项目自行填写)

- `project.config.yaml`(已 gitignored)
- `docs/01-项目要求.md` 的业务模块、多端范围、UI 原则三个 `TODO` 区段
- `docs/05-项目开发进度总览.md` 的"业务模块进度"、"最近变更"、"风险"、"排期"四张表
- `docs/progress/` 下所有子任务设计与开发记录
- 子仓内业务代码:后端 `yudao-module-gap`、前端 `gap` 与 `gap`、移动端业务页面

## 强约束(所有端必须遵守)

### 中文展示

- 代码中类名、变量名、接口字段使用英文
- 用户可见内容必须中文(Web、uniapp、H5、大屏、导出文件)
- 不得把状态码、枚举名、`true/false`、`DRAFT/APPROVED` 等直接展示给用户

### 状态字段约定(唯一规则)

| 场景 | 来源 | 前端展示方式 |
|------|------|--------------|
| 业务字段是**系统字典**(`dict_type` 存在) | 后端只返回 `status`(字典值) | 前端用 `<dict-tag :type="..." :value="status"/>` |
| 业务字段是**枚举或规则计算结果**(无字典) | 后端同时返回 `status` + `statusName` | 前端直接显示 `statusName` |

- 不得两套机制混用。同一字段二选一并在 progress 子文档说明
- 后端禁止用魔法数或裸字符串判断/更新状态,必须经枚举或字典常量
- 状态更新统一走 Service 层业务方法,保留审计留痕

### 安全

- 密码、令牌、内网地址、个人邮箱**不进文档、不进代码**,统一走 `.env` / `application-local.yaml`(已被忽略)
- `project.config.yaml`、`.env*` 已在 `.gitignore`;模板见 `project.config.example.yaml`、`.env.example`

### 开发工作流

```text
理解需求 → 判断涉及仓库 → 查进度总览和相关子文档 → 查现有代码风格 →
设计实现方案 → 更新或创建 progress 子文档 → 修改代码 → 验证 →
更新进度文档 → 分仓提交推送
```

- 一项功能完成后立即提交推送,提交信息中文,格式 `{类型}: {模块}: {简述}`
- 类型:`feat`(新功能) / `fix`(修复) / `docs`(文档) / `refactor`(重构) / `style`(格式) / `test`(测试) / `chore`(构建/工具)
- 功能设计、接口、表结构、页面、验证写入 `docs/progress/` 子文档,不写零散流水账
- 同步更新 [docs/05-项目开发进度总览.md](docs/05-项目开发进度总览.md)

## 关键链接

- 后端框架:<https://gitee.com/zhijiantianya/ruoyi-vue-pro>
- 后端框架文档:<https://doc.iocoder.cn>
- 后端开发规范:[ai-project-server/AGENTS.md](ai-project-server/AGENTS.md)
- 管理端开发规范:[ai-project-admin-web/AGENTS.md](ai-project-admin-web/AGENTS.md)
- 移动端开发规范:[ai-project-uniapp/AGENTS.md](ai-project-uniapp/AGENTS.md)
