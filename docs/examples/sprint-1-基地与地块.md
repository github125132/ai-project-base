# Sprint 1：基地管理 + 地块管理设计与开发记录

## 基本信息

| 项目 | 内容 |
|------|------|
| 日期 | 2026-05-18 |
| 模块 | GAP 基地管理、GAP 地块管理 |
| 状态 | 设计中 |
| 涉及仓库 | gap-server、gap-admin-web |
| 涉及端 | 后端、PC 管理端（移动端 Sprint 2 起追加） |
| 优先级 | P0 |

## 需求背景

GAP 平台所有业务（文件、溯源、检测、培训、迎检、申报、基源鉴定）都依赖**基地**与**地块**两个核心实体。Sprint 1 先把这两个实体、基础字典、菜单与权限闭环跑通，后续模块在此基础上挂接。

## 本次范围

- 基地：基础信息、负责人、质量负责人、面积、建设年限、主营品种、GIS 中心点
- 地块：基地下挂、编号、品种、面积、播种日期、状态、负责人
- 字典：基地状态、地块状态、品种、面积单位
- 菜单与权限码：`gap:base:*`、`gap:plot:*`
- PC 管理端：基地/地块的列表、查询、新增、编辑、删除、导出

## 不在本次范围

- GIS 地块多边形绘制（仅留中心点字段，地图组件在 Sprint 4 与溯源/大屏一并处理）
- 农事记录、检测报告联动（Sprint 2 起）
- 移动端基地/地块查看（Sprint 2 起）

## 业务流程

```text
新建基地 → 维护负责人/面积/品种 → 在基地下创建地块 → 设置地块状态 → 列表查询与导出
```

## 数据模型

| 表 | 说明 | 关键字段 |
|----|------|----------|
| `gap_base` | 基地 | `id`、`name`、`code`、`area`、`area_unit`、`leader_user_id`、`quality_user_id`、`build_year`、`main_species`、`center_lng`、`center_lat`、`status` |
| `gap_plot` | 地块 | `id`、`base_id`、`code`、`name`、`species`、`area`、`area_unit`、`sowing_date`、`leader_user_id`、`status` |

> 表结构最终 DDL 写入 `gap-server/sql/mysql/gap.sql`，落地时同步更新本文档与 `docs/05-项目开发进度总览.md`。

## 字典与状态

| 类型 | 编码 | 中文名称 | 说明 |
|------|------|----------|------|
| `gap_base_status` | `0/1/2` | 筹建中 / 运行中 / 停用 | 字典型，前端 `<dict-tag>` |
| `gap_plot_status` | `0/1/2/3` | 待播种 / 在田 / 采收 / 休耕 | 字典型，前端 `<dict-tag>` |
| `gap_area_unit` | `mu/ha/m2` | 亩 / 公顷 / 平方米 | 字典型 |

按根 AGENTS.md "状态字段双轨规则"，本 Sprint 全部字段走**字典**分支，后端不返回 `statusName`。

## 接口设计

| 端 | 方法 | 路径 | 权限码 | 说明 |
|----|------|------|--------|------|
| 管理端 | POST | `/admin-api/gap/base/create` | `gap:base:create` | 新建基地 |
| 管理端 | PUT | `/admin-api/gap/base/update` | `gap:base:update` | 修改基地 |
| 管理端 | DELETE | `/admin-api/gap/base/delete` | `gap:base:delete` | 删除基地 |
| 管理端 | GET | `/admin-api/gap/base/get` | `gap:base:query` | 详情 |
| 管理端 | GET | `/admin-api/gap/base/page` | `gap:base:query` | 分页 |
| 管理端 | GET | `/admin-api/gap/base/export-excel` | `gap:base:export` | 导出 |
| 管理端 | POST | `/admin-api/gap/plot/create` | `gap:plot:create` | 新建地块 |
| 管理端 | PUT | `/admin-api/gap/plot/update` | `gap:plot:update` | 修改地块 |
| 管理端 | DELETE | `/admin-api/gap/plot/delete` | `gap:plot:delete` | 删除地块 |
| 管理端 | GET | `/admin-api/gap/plot/page` | `gap:plot:query` | 分页 |
| 管理端 | GET | `/admin-api/gap/plot/export-excel` | `gap:plot:export` | 导出 |

## 页面与交互

| 页面 | 路径 | 主要能力 |
|------|------|----------|
| 基地列表 | `gap-admin-web/src/views/gap/base/index.vue` | 列表 + 查询 + 新增/编辑/删除/导出 |
| 基地表单弹窗 | `gap-admin-web/src/views/gap/base/GapBaseForm.vue` | 表单 + 校验 |
| 地块列表 | `gap-admin-web/src/views/gap/plot/index.vue` | 列表（带基地筛选）+ 操作 |
| 地块表单弹窗 | `gap-admin-web/src/views/gap/plot/GapPlotForm.vue` | 表单 + 校验 |

## 权限与菜单

| 菜单 | 父级 | 权限码 |
|------|------|--------|
| GAP 管理 | 顶级 | — |
| 基地管理 | GAP 管理 | `gap:base:query` |
| 地块管理 | GAP 管理 | `gap:plot:query` |

## 附件、导出与留痕

- 附件策略：Sprint 1 不涉及附件
- 导出策略：Excel（使用 ruoyi 自带 `ExcelUtils`）
- 审计留痕：`create_time` / `update_time` / `creator` / `updater` 由 `BaseDO` 自动维护

## 验收标准

- [ ] `gap.sql` 包含 `gap_base`、`gap_plot` 建表语句与字典初始化
- [ ] 三套接口（基地、地块、字典）全部跑通，Swagger 可用
- [ ] PC 端两个列表 + 两个表单可完成 CRUD 与导出
- [ ] 权限按角色可生效（默认管理员/质量负责人/基地运营人员三种）
- [ ] 状态展示符合双轨规则的字典分支
- [ ] 无明文密码/IP/邮箱写入任何文档与代码

## 开发记录

| 日期 | 仓库 | 变更内容 | 说明 |
|------|------|----------|------|
| 2026-05-18 | 根仓 | 建立 Sprint 1 子文档 | 设计开工 |

## 遗留事项

- GIS 多边形与地图组件在 Sprint 4 统一规划
- 移动端基地查询在 Sprint 2 起追加
