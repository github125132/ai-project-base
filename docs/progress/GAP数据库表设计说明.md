# GAP 数据库表设计说明

> 基于《中药材GAP检查指南》(2023年6月) 的完整业务表结构
> 文件位置: `ai-project-server/sql/mysql/gap-tables.sql`

---

## 一、设计原则

### 1.1 yudao 模块复用

| yudao 已有模块 | 复用内容 | 说明 |
|--------------|---------|------|
| `system_user` / `system_dept` / `system_post` / `system_role` | 人员、部门、岗位、角色 | 人员档案、组织架构、权限管理 |
| `system_dict_data` / `system_dict_type` | 数据字典 | 禁用农药清单、农事类型、投入品类别等枚举值 |
| `infra_file` | 文件附件 | 鉴定报告、检测报告、现场照片等附件存储 |
| `infra_api_access_log` / `infra_api_error_log` | API 日志 | 系统级访问日志和错误日志 |
| `bpm_process_instance` / `bpm_task` | 审批流程 | 变更审批、文件审批、放行审批等工作流 |
| `wms_warehouse` / `wms_receipt_order` / `wms_shipment_order` | 仓储管理 | 仓库基础信息、出入库单据 |
| `mes_dv_machinery` / `mes_dv_check_record` | 设备台账 | 农机设备登记、点检保养记录 |

### 1.2 审计字段规范

所有 GAP 业务表统一包含以下审计字段，符合 yudao 规范：

```sql
creator        varchar(64)   -- 创建者
create_time    datetime      -- 创建时间
updater        varchar(64)   -- 更新者
update_time    datetime      -- 更新时间 (ON UPDATE CURRENT_TIMESTAMP)
deleted        bit(1)        -- 逻辑删除标志
tenant_id      bigint(20)    -- 租户编号 (多租户隔离)
```

### 1.3 数据变更审计追踪

除基础审计字段外，专设三张日志表实现 GAP 要求的电子数据可追溯性：

- **`gap_operation_log`** — 业务操作日志：记录谁在什么时间对哪条记录做了什么操作
- **`gap_data_change_log`** — 数据变更日志：字段级变更追踪，记录旧值/新值/变更原因
- **`gap_data_review`** — 关键数据复核记录：定期复核制度，满足"记录复核"检查要求

---

## 二、模块与表清单 (66 张表)

### Module 1: 基地档案管理 (8 张表)

| 表名 | 说明 | 覆盖检查要点 |
|------|------|------------|
| `gap_base_info` | 基地信息主表 | 3.1 基地选址、3.2 种植设施 |
| `gap_base_environment` | 环境评估 | 3.1 环境评估 |
| `gap_base_soil` | 土壤检测 (含重金属) | 3.1 土壤条件 |
| `gap_base_water` | 水源检测 | 3.1 水源条件、3.3 水质要求 |
| `gap_base_weather` | 气象数据 | 3.1 气象条件 |
| `gap_base_facility` | 基地设施设备 | 3.2 田间设施、3.3 加工设施 |
| `gap_plot` | 地块管理 (含 GIS) | 5.1 种植规划 |
| `gap_plot_planting` | 地块种植历史 | 5.1 种植档案、轮作记录 |

### Module 2: 品种种子管理 (4 张表)

| 表名 | 说明 | 覆盖检查要点 |
|------|------|------------|
| `gap_variety` | 品种档案 | 4.1 基源鉴定 |
| `gap_seed_batch` | 种子种苗批次 | 4.2 种子批次管理 |
| `gap_origin_identify` | 基源鉴定 | 4.1 物种鉴定 |
| `gap_seed_treatment` | 种子处理记录 | 4.2 种子处理 |

### Module 3: 投入品管理 (6 张表)

| 表名 | 说明 | 覆盖检查要点 |
|------|------|------------|
| `gap_input_category` | 投入品分类 | 投入品分类管理 |
| `gap_input_product` | 投入品产品 (含禁用/限用标识) | 5.4 农药使用清单 |
| `gap_input_supplier` | 供应商档案 (含审计) | 4.2 供应商审计 |
| `gap_input_inventory` | 投入品库存 | 3.2 投入品存放 |
| `gap_input_use_record` | 投入品使用记录 (含禁用拦截) | 5.4 农药使用记录、禁用拦截 |
| `gap_waste_disposal` | 废弃物处理 | 3.2 废弃物处理 |

### Module 4: 农事活动管理 (7 张表)

| 表名 | 说明 | 覆盖检查要点 |
|------|------|------------|
| `gap_planting_plan` | 种植计划 | 5.1 种植计划 |
| `gap_farming_record` | 农事记录主表 | 5.2 整地播种、5.3 田间管理 |
| `gap_farming_detail` | 农事记录明细 | 农事记录详情 |
| `gap_pest_control` | 病虫害防治方案 | 5.4 防治原则 |
| `gap_irrigation_record` | 灌溉记录 | 5.3 灌溉排水 |
| `gap_fertilization_record` | 施肥记录 | 5.3 施肥管理 |
| `gap_fertilization_detail` | 施肥明细 | 肥料种类用量 |

### Module 5: 采收加工管理 (5 张表)

| 表名 | 说明 | 覆盖检查要点 |
|------|------|------------|
| `gap_harvest_plan` | 采收计划 | 6.1 采收期确定 |
| `gap_harvest_record` | 采收记录 (含批次号) | 6.1 采收方法、天气条件 |
| `gap_process_record` | 加工记录 | 6.2 加工SOP |
| `gap_process_detail` | 加工工序明细 | 6.2 清洗、干燥、特殊加工 |
| `gap_drying_record` | 干燥记录 (温度监控) | 6.2 干燥温度、干燥终点 |
| `gap_package_record` | 包装记录 | 6.3 包装标识 |

### Module 6: 仓储物流管理 (6 张表)

| 表名 | 说明 | 覆盖检查要点 |
|------|------|------------|
| `gap_storage_area` | 仓库分区 (待验/合格/不合格/发货区) | 3.4/7.3 货位管理 |
| `gap_storage_in_record` | 药材入库记录 | 7.3 入库验收 |
| `gap_storage_out_record` | 药材出库记录 | 7.3 出库管理 |
| `gap_storage_check` | 养护检查 (温湿度、虫害、霉变) | 3.4/7.3 养护管理 |
| `gap_transport_record` | 运输记录 | 7.4 运输管理 |
| `gap_unqualified_handle` | 不合格品处理 | 7.3 不合格品 |

### Module 7: 质量检测管理 (7 张表)

| 表名 | 说明 | 覆盖检查要点 |
|------|------|------------|
| `gap_quality_standard` | 质量标准 (企业内控>国标) | 9.1 质量标准 |
| `gap_inspect_task` | 检验任务 | 9.2 检验管理 |
| `gap_inspect_record` | 检验记录 (原始记录) | 9.2 原始记录 |
| `gap_inspect_report` | 检验报告 | 9.2 检验报告 |
| `gap_pesticide_residue` | 农残检测明细 (33种禁用清单) | 5.4/9.2 农残检测 |
| `gap_heavy_metal` | 重金属检测明细 | 9.2 重金属检测 |
| `gap_sample_record` | 留样管理 | 9.3 留样管理 |
| `gap_release_record` | 放行审核 (质量负责人签字) | 7.2 放行审核 |

### Module 8: 文件体系管理 (4 张表)

| 表名 | 说明 | 覆盖检查要点 |
|------|------|------------|
| `gap_document_category` | 文件分类 | 8.1 文件体系 |
| `gap_document` | 文件档案 (版本控制/审批/废止) | 8.2 文件控制 |
| `gap_sop` | SOP库 | 8.1 SOP |
| `gap_record_template` | 记录模板 | 8.1 记录表单 |

### Module 9: 培训管理 (5 张表)

| 表名 | 说明 | 覆盖检查要点 |
|------|------|------------|
| `gap_training_course` | 培训课程库 | 2.2 培训内容 |
| `gap_training_plan` | 培训计划 | 2.2 培训计划 |
| `gap_training_record` | 培训记录 | 2.2 培训记录 |
| `gap_training_participant` | 培训参与明细 (签到/考核) | 2.2 培训记录、考核 |
| `gap_person_health` | 人员健康档案 (到期预警) | 2.2 健康档案、2.3 疾病控制 |

### Module 10: 内部审核管理 (4 张表)

| 表名 | 说明 | 覆盖检查要点 |
|------|------|------------|
| `gap_audit_plan` | 审核计划 | 1.5 自检计划 |
| `gap_audit_checklist` | 检查表 | 1.5 检查表 |
| `gap_audit_checklist_item` | 检查表项目 | 1.5 检查表 |
| `gap_nc_item` | 不符合项 (整改闭环) | 1.5 不符合项、整改跟踪 |

### Module 11: 变更/投诉/召回 (3 张表)

| 表名 | 说明 | 覆盖检查要点 |
|------|------|------------|
| `gap_change_record` | 变更记录 (关联 bpm 审批流) | 1.3 变更控制 |
| `gap_complaint` | 投诉记录 | 1.4 投诉处理 |
| `gap_recall_record` | 召回记录 | 1.4 产品召回 |

### Module 12: 溯源管理 (2 张表)

| 表名 | 说明 | 覆盖检查要点 |
|------|------|------------|
| `gap_trace_batch` | 溯源批次 (全链条快照) | 全章节追溯 |
| `gap_trace_node` | 溯源节点 (种植→农事→采收→加工→仓储→检验→放行) | 全章节追溯 |

### Module 13: 审计日志 (3 张表)

| 表名 | 说明 | 覆盖检查要点 |
|------|------|------------|
| `gap_operation_log` | 业务操作日志 | 8.3 电子记录 |
| `gap_data_change_log` | 数据变更日志 (字段级审计追踪) | 8.3 电子数据可追溯性 |
| `gap_data_review` | 关键数据复核记录 | 8.3 记录复核 |

---

## 三、核心数据流

```
基地选址(gap_base_info)
    ↓
地块管理(gap_plot) ←→ 土壤/水源/气象检测(gap_base_soil/water/weather)
    ↓
品种档案(gap_variety) ←→ 基源鉴定(gap_origin_identify)
    ↓
种子种苗批次(gap_seed_batch) ←→ 种子处理(gap_seed_treatment)
    ↓
种植计划(gap_planting_plan)
    ↓
地块种植记录(gap_plot_planting) ←→ 地块(gap_plot)
    ↓
农事活动记录(gap_farming_record) ←→ 明细(gap_farming_detail)
    │   ├── 整地/播种/移栽
    │   ├── 灌溉(gap_irrigation_record)
    │   ├── 施肥(gap_fertilization_record + detail)
    │   ├── 病虫害防治(gap_pest_control) + 农药使用(gap_input_use_record)
    │   └── 除草/整枝/覆盖
    ↓
采收计划(gap_harvest_plan) ←→ 采收记录(gap_harvest_record) [生成批次号]
    ↓
加工记录(gap_process_record) ←→ 工序明细(gap_process_detail)
    │   ├── 清洗/去皮/切制
    │   ├── 干燥(gap_drying_record) [温度监控]
    │   └── 特殊处理
    ↓
包装记录(gap_package_record) [标签内容]
    ↓
入库(gap_storage_in_record) ←→ 仓库分区(gap_storage_area)
    ↓
检验任务(gap_inspect_task)
    ├── 检验记录(gap_inspect_record)
    ├── 农残检测(gap_pesticide_residue)
    ├── 重金属检测(gap_heavy_metal)
    └── 检验报告(gap_inspect_report)
    ↓
留样(gap_sample_record)
    ↓
放行审核(gap_release_record) [质量负责人签字]
    ↓
出库(gap_storage_out_record)
    ↓
运输(gap_transport_record)
    ↓
追溯(gap_trace_batch + gap_trace_node) [全链条节点]
```

### 关键追溯路径

| 检查要点 | 追溯路径 |
|---------|---------|
| 追溯具体地块 | trace_batch.plot_id → gap_plot → gap_base_info |
| 追溯具体批次 | trace_batch.batch_no → 采收记录/加工记录/检验报告 |
| 追溯农药使用 | trace_node(农事) → farming_record → input_use_record |
| 追溯检验结果 | trace_node(检验) → inspect_report → pesticide_residue/heavy_metal |
| 追溯人员 | 所有记录.operator_id / supervisor_id → system_user |

---

## 四、GAP 检查要点覆盖对照

| 检查章节 | 检查要点 | 覆盖表 |
|---------|---------|--------|
| **1.1 质量管理体系** | 质量方针目标、组织机构 | gap_base_info(负责人) |
| **1.2 文件管理** | 文件体系、文件控制 | gap_document、gap_sop、gap_record_template |
| **1.3 变更管理** | 变更控制、变更评估 | gap_change_record(关联 bpm) |
| **1.4 投诉与召回** | 投诉处理、产品召回 | gap_complaint、gap_recall_record |
| **1.5 自检** | 自检计划、不符合项、整改 | gap_audit_plan、gap_nc_item |
| **2.1 关键人员** | 人员任命、职责 | 复用 system_user + gap_base_info(负责人字段) |
| **2.2 人员培训** | 培训计划、培训记录、考核 | gap_training_plan/record/participant |
| **2.3 人员卫生** | 健康档案、疾病控制 | gap_person_health(到期预警) |
| **3.1 基地选址** | 环境评估、土壤、水源、气象 | gap_base_environment/soil/water/weather |
| **3.2 种植设施** | 田间设施、投入品存放 | gap_base_facility、gap_input_inventory |
| **3.3 加工设施** | 加工场所、设备要求 | gap_process_record、复用 mes_dv_machinery |
| **3.4 仓储设施** | 仓库条件、功能分区 | gap_storage_area、复用 wms_warehouse |
| **4.1 基源鉴定** | 物种鉴定、鉴定档案 | gap_origin_identify、gap_variety |
| **4.2 种子种苗** | 种源来源、种子质量、检疫 | gap_seed_batch、gap_seed_treatment |
| **5.1 种植规划** | 种植计划、轮作、档案 | gap_planting_plan、gap_plot_planting |
| **5.2 整地播种** | 整地要求、播种时间 | gap_farming_record(整地/播种) |
| **5.3 田间管理** | 中耕除草、灌溉、施肥 | gap_farming_record、gap_irrigation_record、gap_fertilization_record |
| **5.4 病虫害防治** | 防治原则、农药使用、禁用拦截 | gap_pest_control、gap_input_use_record(禁用检查) |
| **6.1 采收管理** | 采收期、天气、分批 | gap_harvest_plan、gap_harvest_record |
| **6.2 产地加工** | 加工SOP、干燥温度 | gap_process_record + detail、gap_drying_record |
| **6.3 包装暂存** | 包装材料、标识 | gap_package_record |
| **7.1 包装管理** | 包材标准、检验 | gap_package_record(包材验收) |
| **7.2 质量检验与放行** | 质量标准、放行审核 | gap_quality_standard、gap_release_record |
| **7.3 仓储管理** | 入库验收、分区、养护 | gap_storage_in_record、gap_storage_area、gap_storage_check |
| **7.4 运输管理** | 运输工具、条件、防护 | gap_transport_record |
| **8.1 文件体系** | 质量手册、SOP、记录 | gap_document_category、gap_document、gap_sop、gap_record_template |
| **8.2 文件控制** | 编号、审批、修订、废止 | gap_document(版本/审批流程) |
| **8.3 记录管理** | 填写规范、修改规定、保存期限 | gap_record_template、gap_data_change_log、gap_data_review |
| **9.1 质量标准** | 标准制定、内容 | gap_quality_standard |
| **9.2 检验管理** | 取样、检验方法、原始记录 | gap_inspect_task/record/report、gap_pesticide_residue、gap_heavy_metal |
| **9.3 留样管理** | 留样数量、条件、期限 | gap_sample_record |

---

## 五、关键业务规则 (基于表结构)

### 5.1 禁用农药拦截

`gap_input_product.is_banned = 1` 的农药，在 `gap_input_use_record` 插入时必须拦截。该字段与 GAP 检查要点 5.4 的 33 种禁用农药清单对应，可通过 `system_dict_data` 字典维护。

### 5.2 安全间隔期校验

`gap_input_use_record` 中的 `earliest_harvest_date` = `use_date` + `safety_interval`(来自 `gap_input_product`)。采收日期不得早于该日期。

### 5.3 数据变更审计

所有业务记录的修改，通过触发器或 AOP 切面写入 `gap_data_change_log`，记录字段级旧值/新值。修改原因由业务层在修改时传入，满足 GAP 第 8.3 条"记录修改需划改签名"的电子等效要求。

### 5.4 质量负责人放行否决权

`gap_release_record` 中 `approver_id` 必须关联 `gap_base_info.quality_user_id`（质量负责人），且只有 `status = 2`(已批准) 的批次才能出库。

### 5.5 留样到期预警

`gap_sample_record` 中 `expiry_date` 到期前 30 天自动预警，`destroy_date` 记录销毁日期，`destroyer_id` + `witness_id` 双人确认。

---

## 六、索引设计说明

每张表均按以下原则建立索引：

1. **业务编码字段** (`code`, `no`, `batch_no`)：唯一索引 (uk_) 或普通索引 (idx_)
2. **外键关联字段** (`*_id`)：普通索引，加速 JOIN 查询
3. **时间字段** (`*_date`, `*_time`)：普通索引，加速时间范围查询
4. **状态字段** (`status`)：普通索引，加速状态筛选
5. **复合索引**：高频组合查询场景（如 `idx_base_date` 基地+日期）

---

*文档版本: v1.0*
*创建日期: 2026-05-24*
