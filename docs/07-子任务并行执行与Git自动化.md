# 子任务并行执行与 Git 自动化(三阶段工作流之三)

> 前置:已完成 [`06-需求沟通与项目计划生成.md`](./06-需求沟通与项目计划生成.md);`docs/progress/` 下已有子任务文档。
> 本阶段是项目主开发期,会**循环执行**直到所有子任务收尾。

## 1. 工作循环总览

默认采用**全自动并行模式**:AI 持续扫描可执行的子任务,多个子任务同时推进,编译通过即自动合并推送,无需用户介入。

```text
读 progress 列表 → 选可执行子任务(依赖已就绪,多个并行)
  ↓
在每个涉及子仓创建 feature 分支
  ↓
按子任务文档落地代码(后端 → 管理端 → 移动端)
   ↓
 本地验证(编译)
  ↓
更新子任务文档进度 + 更新 docs/05 状态
  ↓
分仓提交 → 推送 feature 分支 → 合并到 main → 推送 main → 删除 feature
  ↓
回到第一步,继续下一个子任务
```

## 2. 选择可执行子任务

可执行 = **依赖全部为"已完成"** + 自身状态为"未开始"或"设计中"。

并行规则(默认全并行):

- 同一子仓内,**不同模块目录**互不冲突的子任务始终并行(分别开 feature 分支)
- 跨子仓的子任务始终可并行(子仓独立)
- 同一文件被多个子任务共享时,串行处理,避免合并冲突
- AI 自动持续扫描所有就绪子任务,按 `p0` > `p1` > `p2` > `p3` 优先级启动并行批次
- 同优先级按依赖图就绪顺序启动,就绪一个启动一个,不等待整批就绪

## 3. 分支策略

### 3.1 根仓(文档)

- 默认分支:`main`
- 文档更新直接在 `main` 提交并 push(子任务的设计文档随计划阶段产出,执行期只更新进度/验收结果)
- 不在根仓开 feature 分支

### 3.2 子仓(代码)

每个子任务对应**每个涉及子仓**建一条 feature 分支:

```text
feature/{progress-file-stem}

示例:
feature/p0-01-base-基地管理     # 后端子仓
feature/p0-01-base-基地管理     # 管理端子仓(同名,独立仓)
```

子仓默认分支:

- `ai-project-server`: `master-jdk17`
- `ai-project-admin-web`: `master`
- `ai-project-uniapp`: `master`

## 4. 单子任务的标准执行序列

### 4.1 起手

```bash
# 子仓内:从默认分支切出 feature
cd ai-project-server
git fetch origin
git checkout -b feature/{stem} origin/master-jdk17
```

### 4.2 开发期间(允许多次小提交)

```bash
git add <具体文件>
git commit -m "{类型}: {模块}: {简述}"
```

类型:`feat` / `fix` / `docs` / `refactor` / `style` / `test` / `chore`(详见 `02-Git仓库初始化引导.md` 第 8 节)。

提交粒度:数据模型 / 接口 / 页面 / 字典 / 权限 / 验证,**每完成一类做一次提交**,不堆成 1000 行的大提交。

### 4.3 收尾(单子仓)

```bash
# 1. 编译通过后,推送 feature
git push -u origin feature/{stem}

# 2. 合并到默认分支(快进或合并提交均可,按子仓约定)
git checkout master-jdk17
git pull --ff-only origin master-jdk17
git merge --no-ff feature/{stem} -m "合并: {模块} {主题} ({stem})"

# 3. 推 main
git push origin master-jdk17

# 4. 删除 feature(本地 + 远端)
git branch -d feature/{stem}
git push origin --delete feature/{stem}
```

### 4.4 收尾(根仓文档)

子任务的代码全部并入子仓默认分支后,**回到根仓**更新文档:

```bash
cd <PROJECT_ROOT>
# 编辑:
#  - docs/progress/{stem}.md 的"开发记录"、"验证记录"、"提交记录"
#  - docs/05-项目开发进度总览.md 的"业务模块进度"、"最近变更"

git add docs/
git commit -m "进度: 完成 {stem}"
git push origin main
```

## 5. 自动化触发点

AI 在以下时机**自动执行**对应 Git 动作,无需用户确认:

| 触发时机 | 仓库 | 动作 |
|----------|------|------|
| 项目计划生成完毕(阶段二结束) | 根仓 | `commit + push origin main` |
| 子任务起手 | 涉及子仓 | `checkout -b feature/{stem}` |
| 单类改动完成(模型/接口/页面/字典/权限/验证) | 当前子仓 | `commit`(暂不 push) |
| 单子仓内子任务代码完成且编译通过 | 当前子仓 | `push feature` → `merge to main` → `push main` → `delete feature` |
| 子任务跨子仓全部并入 | 根仓 | 更新 progress + 05 → `commit + push origin main` |
| 用户在对话中明确说"提交"或"推送" | 当前上下文涉及的仓库 | 按上述对应动作执行 |

> 自动合并前提:编译通过、无冲突。任一不满足则自动回滚(见第 6 节)并记录错误。

## 6. 合并冲突与失败处理

- **不强推**(`--force`)、不跳过 hook(`--no-verify`)
- 出现冲突:自动放弃本次合并,保留 feature 分支现场,在 progress 文档记录冲突文件清单,继续下一个子任务
- 编译失败:不回滚代码,在 progress 文档记录错误信息,标记该子任务为"编译失败"并跳过
- 合并到 main 失败:回滚到 feature 分支保留现场,不删 feature,记录错误后继续
- push 失败(权限、网络、保护规则):记录错误,继续下一个子任务

## 7. 子任务文档进度字段约定

在 `docs/progress/{stem}.md` 中,"开发记录"与"提交记录"两表实时维护:

```markdown
## 开发记录

| 日期 | 仓库 | 变更内容 | 说明 |
|------|------|----------|------|
| 2026-05-18 | ai-project-server | 新建 base 表 + DO + Mapper | DDL 已写入 sql/mysql/gap-tables.sql |
| 2026-05-19 | ai-project-admin-web | 列表 + 表单弹窗 + 字典 | 字典走 dict-tag 分支 |

## 提交记录

| 仓库 | 分支 | 提交信息 | 提交哈希 |
|------|------|----------|----------|
| ai-project-server | feature/p0-01-base-基地管理 → master-jdk17 | 后端: 基地管理 CRUD | abc1234 |
| ai-project-admin-web | feature/p0-01-base-基地管理 → master | 管理端: 基地管理列表与表单 | def5678 |
```

## 8. 完成判定

一个子任务标记为"已完成"必须同时满足:

- [ ] 验收标准(子任务文档第 6 节)全部勾选
- [ ] 涉及子仓的 feature 全部合并入默认分支并已推送
- [ ] 子任务文档的开发记录、验证记录、提交记录已填写
- [ ] `docs/05` 中本模块进度行已更新
- [ ] 无 `.env`、`project.config.yaml`、`application-local.yaml` 误提交

## 9. 禁止事项

- 不要修改"不可变基础"
- 不要在 main 分支上直接做业务代码改动(根仓文档除外)
- 不要把多个子任务的代码挤进一条 feature 分支
- 不要跨子仓做单一原子提交(每个子仓单独提)
- 不要在子任务文档未更新的情况下声明"完成"
- 不要因单个子任务失败阻塞其他子任务的并行执行
