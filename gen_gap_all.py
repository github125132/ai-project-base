import os
import re
import glob

BASE_DIR = 'yudao-module-gap/src/main/java/cn/iocoder/yudao/module/gap'

def camel(s):
    return re.sub(r'_([a-z])', lambda m: m.group(1).upper(), s)

def pascal(s):
    c = camel(s)
    return c[0].upper() + c[1:] if c else c

def getter_name(s):
    c = camel(s)
    return c[0].upper() + c[1:] if c else c

def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

def parse_do(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    pkg_match = re.search(r'package\s+([\w.]+);', text)
    pkg = pkg_match.group(1).split('.')[-1] if pkg_match else ''
    table_match = re.search(r'@TableName\("([^"]+)"\)', text)
    table = table_match.group(1) if table_match else ''
    class_match = re.search(r'public\s+class\s+(\w+)DO\s', text)
    cls = class_match.group(1) if class_match else ''
    entity = cls[3:] if cls.startswith('Gap') else cls
    entity_lower = re.sub(r'(?<!^)(?=[A-Z])', '_', entity).lower()

    fields = []
    # Match /** comment */ followed by private Type name;
    pattern = r'/\*\*\s*\n\s*\*\s*([^*\n]+)\n\s*\*/\s*\n\s*private\s+(\w+)\s+(\w+);'
    for m in re.finditer(pattern, text):
        comment = m.group(1).strip()
        typ = m.group(2)
        name = m.group(3)
        fields.append((name, typ, comment))

    # Also match single-line /** comment */ patterns
    pattern2 = r'/\*\*\s+([^*]+?)\s+\*/\s+private\s+(\w+)\s+(\w+);'
    if not fields:
        for m in re.finditer(pattern2, text):
            comment = m.group(1).strip()
            typ = m.group(2)
            name = m.group(3)
            fields.append((name, typ, comment))

    # Fallback: just match private declarations
    if not fields:
        for m in re.finditer(r'private\s+(\w+)\s+(\w+);', text):
            typ = m.group(1)
            name = m.group(2)
            fields.append((name, typ, ''))

    return pkg, table, entity, entity_lower, cls, fields

def gen_mapper(pkg, entity, cls, fields):
    cn = cls
    mname = f'{cn}Mapper'
    base = f'{BASE_DIR}/dal/mysql/{pkg}/{mname}.java'
    if os.path.exists(base):
        return
    query = ''
    for name, typ, comment in fields:
        if name in ('id','creator','createTime','updater','updateTime','deleted','tenantId','remark'):
            continue
        gn = getter_name(name)
        if typ == 'String':
            query += f'\n                .likeIfPresent({cn}DO::get{gn}, reqVO.get{gn}())'
        else:
            query += f'\n                .eqIfPresent({cn}DO::get{gn}, reqVO.get{gn}())'
    fk = ''
    for name, typ, comment in fields:
        if name.endswith('Id') and name != 'id' and typ == 'Long':
            gn = getter_name(name)
            pc = pascal(camel(name))
            fk += f"""
    default List<{cn}DO> selectListBy{pc}(Long {name}) {{
        return selectList({cn}DO::get{gn}, {name});
    }}
"""
    content = f"""package cn.iocoder.yudao.module.gap.dal.mysql.{pkg};

import cn.iocoder.yudao.framework.common.pojo.PageResult;
import cn.iocoder.yudao.framework.mybatis.core.mapper.BaseMapperX;
import cn.iocoder.yudao.framework.mybatis.core.query.LambdaQueryWrapperX;
import cn.iocoder.yudao.module.gap.controller.admin.{pkg}.vo.{cn}PageReqVO;
import cn.iocoder.yudao.module.gap.dal.dataobject.{pkg}.{cn}DO;
import org.apache.ibatis.annotations.Mapper;

import java.util.List;

@Mapper
public interface {mname} extends BaseMapperX<{cn}DO> {{

    default PageResult<{cn}DO> selectPage({cn}PageReqVO reqVO) {{
        return selectPage(reqVO, new LambdaQueryWrapperX<{cn}DO>()
                .eqIfPresent({cn}DO::getId, reqVO.getId()){query}
                .orderByDesc({cn}DO::getId));
    }}{fk}}}
"""
    write(base, content)
    print(f'  Generated {mname}')

def gen_service(pkg, entity, cls):
    cn = cls
    sname = f'{cn}Service'
    base = f'{BASE_DIR}/service/{pkg}/{sname}.java'
    if os.path.exists(base):
        return
    content = f"""package cn.iocoder.yudao.module.gap.service.{pkg};

import cn.iocoder.yudao.framework.common.pojo.PageResult;
import cn.iocoder.yudao.module.gap.controller.admin.{pkg}.vo.{cn}PageReqVO;
import cn.iocoder.yudao.module.gap.controller.admin.{pkg}.vo.{cn}SaveReqVO;
import cn.iocoder.yudao.module.gap.dal.dataobject.{pkg}.{cn}DO;
import jakarta.validation.Valid;

import java.util.List;

public interface {sname} {{

    Long create{cn}(@Valid {cn}SaveReqVO createReqVO);

    void update{cn}(@Valid {cn}SaveReqVO updateReqVO);

    void delete{cn}(Long id);

    {cn}DO get{cn}(Long id);

    PageResult<{cn}DO> get{cn}Page({cn}PageReqVO pageReqVO);

    {cn}DO validate{cn}Exists(Long id);
}}
"""
    write(base, content)
    print(f'  Generated {sname}')

def gen_service_impl(pkg, entity, cls, fields, err_const):
    cn = cls
    iname = f'{cn}ServiceImpl'
    base = f'{BASE_DIR}/service/{pkg}/{iname}.java'
    if os.path.exists(base):
        return
    var_name = camel(entity) + 'Mapper'
    content = f"""package cn.iocoder.yudao.module.gap.service.{pkg};

import cn.iocoder.yudao.framework.common.pojo.PageResult;
import cn.iocoder.yudao.framework.common.util.object.BeanUtils;
import cn.iocoder.yudao.module.gap.controller.admin.{pkg}.vo.{cn}PageReqVO;
import cn.iocoder.yudao.module.gap.controller.admin.{pkg}.vo.{cn}SaveReqVO;
import cn.iocoder.yudao.module.gap.dal.dataobject.{pkg}.{cn}DO;
import cn.iocoder.yudao.module.gap.dal.mysql.{pkg}.{cn}Mapper;
import jakarta.annotation.Resource;
import org.springframework.stereotype.Service;
import org.springframework.validation.annotation.Validated;

import static cn.iocoder.yudao.framework.common.exception.util.ServiceExceptionUtil.exception;
import static cn.iocoder.yudao.module.gap.enums.ErrorCodeConstants.{err_const};

@Service
@Validated
public class {iname} implements {cn}Service {{

    @Resource
    private {cn}Mapper {var_name};

    @Override
    public Long create{cn}({cn}SaveReqVO createReqVO) {{
        {cn}DO entity = BeanUtils.toBean(createReqVO, {cn}DO.class);
        {var_name}.insert(entity);
        return entity.getId();
    }}

    @Override
    public void update{cn}({cn}SaveReqVO updateReqVO) {{
        validate{cn}Exists(updateReqVO.getId());
        {cn}DO updateObj = BeanUtils.toBean(updateReqVO, {cn}DO.class);
        {var_name}.updateById(updateObj);
    }}

    @Override
    public void delete{cn}(Long id) {{
        validate{cn}Exists(id);
        {var_name}.deleteById(id);
    }}

    @Override
    public {cn}DO get{cn}(Long id) {{
        return {var_name}.selectById(id);
    }}

    @Override
    public PageResult<{cn}DO> get{cn}Page({cn}PageReqVO pageReqVO) {{
        return {var_name}.selectPage(pageReqVO);
    }}

    @Override
    public {cn}DO validate{cn}Exists(Long id) {{
        {cn}DO entity = {var_name}.selectById(id);
        if (entity == null) {{
            throw exception({err_const});
        }}
        return entity;
    }}
}}
"""
    write(base, content)
    print(f'  Generated {iname}')

def gen_controller(pkg, entity, cls, perm, path):
    cn = cls
    base = f'{BASE_DIR}/controller/admin/{pkg}/{cn}Controller.java'
    if os.path.exists(base):
        return
    var = camel(entity) + 'Service'
    content = f"""package cn.iocoder.yudao.module.gap.controller.admin.{pkg};

import cn.iocoder.yudao.framework.common.pojo.CommonResult;
import cn.iocoder.yudao.framework.common.pojo.PageResult;
import cn.iocoder.yudao.framework.common.util.object.BeanUtils;
import cn.iocoder.yudao.module.gap.controller.admin.{pkg}.vo.{cn}PageReqVO;
import cn.iocoder.yudao.module.gap.controller.admin.{pkg}.vo.{cn}RespVO;
import cn.iocoder.yudao.module.gap.controller.admin.{pkg}.vo.{cn}SaveReqVO;
import cn.iocoder.yudao.module.gap.dal.dataobject.{pkg}.{cn}DO;
import cn.iocoder.yudao.module.gap.service.{pkg}.{cn}Service;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import jakarta.annotation.Resource;
import jakarta.validation.Valid;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.*;

import static cn.iocoder.yudao.framework.common.pojo.CommonResult.success;

@Tag(name = "管理后台 - GAP {entity}")
@RestController
@RequestMapping("{path}")
@Validated
public class {cn}Controller {{

    @Resource
    private {cn}Service {var};

    @PostMapping("/create")
    @Operation(summary = "创建{entity}")
    @PreAuthorize("@ss.hasPermission('{perm}:create')")
    public CommonResult<Long> create{cn}(@Valid @RequestBody {cn}SaveReqVO createReqVO) {{
        return success({var}.create{cn}(createReqVO));
    }}

    @PutMapping("/update")
    @Operation(summary = "更新{entity}")
    @PreAuthorize("@ss.hasPermission('{perm}:update')")
    public CommonResult<Boolean> update{cn}(@Valid @RequestBody {cn}SaveReqVO updateReqVO) {{
        {var}.update{cn}(updateReqVO);
        return success(true);
    }}

    @DeleteMapping("/delete")
    @Operation(summary = "删除{entity}")
    @Parameter(name = "id", description = "编号", required = true)
    @PreAuthorize("@ss.hasPermission('{perm}:delete')")
    public CommonResult<Boolean> delete{cn}(@RequestParam("id") Long id) {{
        {var}.delete{cn}(id);
        return success(true);
    }}

    @GetMapping("/get")
    @Operation(summary = "获得{entity}")
    @Parameter(name = "id", description = "编号", required = true, example = "1024")
    @PreAuthorize("@ss.hasPermission('{perm}:query')")
    public CommonResult<{cn}RespVO> get{cn}(@RequestParam("id") Long id) {{
        {cn}DO entity = {var}.get{cn}(id);
        return success(BeanUtils.toBean(entity, {cn}RespVO.class));
    }}

    @GetMapping("/page")
    @Operation(summary = "获得{entity}分页")
    @PreAuthorize("@ss.hasPermission('{perm}:query')")
    public CommonResult<PageResult<{cn}RespVO>> get{cn}Page(@Valid {cn}PageReqVO pageReqVO) {{
        PageResult<{cn}DO> pageResult = {var}.get{cn}Page(pageReqVO);
        return success(BeanUtils.toBean(pageResult, {cn}RespVO.class));
    }}
}}
"""
    write(base, content)
    print(f'  Generated {cn}Controller')

def gen_vos(pkg, entity, cls, fields):
    cn = cls
    # SaveReqVO
    base = f'{BASE_DIR}/controller/admin/{pkg}/vo/{cn}SaveReqVO.java'
    if not os.path.exists(base):
        save_body = ''
        for name, typ, comment in fields:
            if name == 'id':
                save_body += f'    @Schema(description = "{comment}", example = "1024")\n    private Long id;\n\n'
                continue
            save_body += f'    @Schema(description = "{comment}")\n    private {typ} {name};\n\n'
        content = f"""package cn.iocoder.yudao.module.gap.controller.admin.{pkg}.vo;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

@Schema(description = "管理后台 - GAP {entity}新增/修改 Request VO")
@Data
public class {cn}SaveReqVO {{

{save_body}}}
"""
        write(base, content)
        print(f'  Generated {cn}SaveReqVO')

    # PageReqVO
    base = f'{BASE_DIR}/controller/admin/{pkg}/vo/{cn}PageReqVO.java'
    if not os.path.exists(base):
        page_body = ''
        for name, typ, comment in fields:
            if name in ('id','creator','createTime','updater','updateTime','deleted','tenantId','remark'):
                continue
            page_body += f'    @Schema(description = "{comment}")\n    private {typ} {name};\n\n'
        content = f"""package cn.iocoder.yudao.module.gap.controller.admin.{pkg}.vo;

import cn.iocoder.yudao.framework.common.pojo.PageParam;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.ToString;

@Schema(description = "管理后台 - GAP {entity}分页 Request VO")
@Data
@EqualsAndHashCode(callSuper = true)
@ToString(callSuper = true)
public class {cn}PageReqVO extends PageParam {{

{page_body}}}
"""
        write(base, content)
        print(f'  Generated {cn}PageReqVO')

    # RespVO
    base = f'{BASE_DIR}/controller/admin/{pkg}/vo/{cn}RespVO.java'
    if not os.path.exists(base):
        resp_body = ''
        for name, typ, comment in fields:
            resp_body += f'    @Schema(description = "{comment}")\n    @ExcelProperty("{comment}")\n    private {typ} {name};\n\n'
        resp_body += '    @Schema(description = "创建时间")\n    @ExcelProperty("创建时间")\n    private LocalDateTime createTime;\n'
        content = f"""package cn.iocoder.yudao.module.gap.controller.admin.{pkg}.vo;

import cn.idev.excel.annotation.ExcelIgnoreUnannotated;
import cn.idev.excel.annotation.ExcelProperty;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

import java.time.LocalDateTime;

@Schema(description = "管理后台 - GAP {entity} Response VO")
@Data
@ExcelIgnoreUnannotated
public class {cn}RespVO {{

{resp_body}}}
"""
        write(base, content)
        print(f'  Generated {cn}RespVO')

# Error code mapping
ERR_MAP = {
    'base_info': 'BASE_NOT_EXISTS',
    'base_environment': 'BASE_NOT_EXISTS',
    'base_facility': 'BASE_NOT_EXISTS',
    'base_soil': 'BASE_NOT_EXISTS',
    'base_water': 'BASE_NOT_EXISTS',
    'base_weather': 'BASE_NOT_EXISTS',
    'plot': 'PLOT_NOT_EXISTS',
    'plot_planting': 'BASE_NOT_EXISTS',
    'variety': 'VARIETY_NOT_EXISTS',
    'seed_batch': 'SEED_BATCH_NOT_EXISTS',
    'origin_identify': 'BASE_NOT_EXISTS',
    'seed_treatment': 'BASE_NOT_EXISTS',
    'input_category': 'INPUT_CATEGORY_NOT_EXISTS',
    'input_product': 'INPUT_PRODUCT_NOT_EXISTS',
    'input_supplier': 'INPUT_SUPPLIER_NOT_EXISTS',
    'input_inventory': 'BASE_NOT_EXISTS',
    'input_use_record': 'BASE_NOT_EXISTS',
    'waste_disposal': 'BASE_NOT_EXISTS',
    'planting_plan': 'PLANTING_PLAN_NOT_EXISTS',
    'farming_record': 'FARMING_RECORD_NOT_EXISTS',
    'farming_detail': 'FARMING_RECORD_NOT_EXISTS',
    'pest_control': 'BASE_NOT_EXISTS',
    'irrigation_record': 'BASE_NOT_EXISTS',
    'fertilization_record': 'BASE_NOT_EXISTS',
    'fertilization_detail': 'BASE_NOT_EXISTS',
    'harvest_plan': 'BASE_NOT_EXISTS',
    'harvest_record': 'HARVEST_RECORD_NOT_EXISTS',
    'process_record': 'PROCESS_RECORD_NOT_EXISTS',
    'process_detail': 'PROCESS_RECORD_NOT_EXISTS',
    'drying_record': 'BASE_NOT_EXISTS',
    'package_record': 'BASE_NOT_EXISTS',
    'storage_area': 'STORAGE_AREA_NOT_EXISTS',
    'storage_in_record': 'STORAGE_IN_NOT_EXISTS',
    'storage_out_record': 'STORAGE_OUT_NOT_EXISTS',
    'storage_check': 'BASE_NOT_EXISTS',
    'transport_record': 'BASE_NOT_EXISTS',
    'unqualified_handle': 'BASE_NOT_EXISTS',
    'quality_standard': 'BASE_NOT_EXISTS',
    'inspect_task': 'INSPECT_TASK_NOT_EXISTS',
    'inspect_record': 'BASE_NOT_EXISTS',
    'inspect_report': 'INSPECT_REPORT_NOT_EXISTS',
    'pesticide_residue': 'BASE_NOT_EXISTS',
    'heavy_metal': 'BASE_NOT_EXISTS',
    'sample_record': 'SAMPLE_RECORD_NOT_EXISTS',
    'release_record': 'RELEASE_NOT_EXISTS',
    'document_category': 'BASE_NOT_EXISTS',
    'document': 'DOCUMENT_NOT_EXISTS',
    'sop': 'BASE_NOT_EXISTS',
    'record_template': 'BASE_NOT_EXISTS',
    'training_course': 'TRAINING_COURSE_NOT_EXISTS',
    'training_plan': 'TRAINING_COURSE_NOT_EXISTS',
    'training_record': 'TRAINING_COURSE_NOT_EXISTS',
    'training_participant': 'TRAINING_COURSE_NOT_EXISTS',
    'person_health': 'TRAINING_COURSE_NOT_EXISTS',
    'audit_plan': 'AUDIT_PLAN_NOT_EXISTS',
    'audit_checklist': 'AUDIT_PLAN_NOT_EXISTS',
    'audit_checklist_item': 'AUDIT_PLAN_NOT_EXISTS',
    'nc_item': 'NC_ITEM_NOT_EXISTS',
    'change_record': 'CHANGE_RECORD_NOT_EXISTS',
    'complaint': 'COMPLAINT_NOT_EXISTS',
    'recall_record': 'RECALL_RECORD_NOT_EXISTS',
    'trace_batch': 'TRACE_BATCH_NOT_EXISTS',
    'trace_node': 'TRACE_BATCH_NOT_EXISTS',
    'operation_log': 'BASE_NOT_EXISTS',
    'data_change_log': 'BASE_NOT_EXISTS',
    'data_review': 'BASE_NOT_EXISTS',
}

# Permission and path mapping
PERM_PATH = {
    'base_info': ('gap:base-info', '/gap/base-info'),
    'base_environment': ('gap:base-environment', '/gap/base-environment'),
    'base_facility': ('gap:base-facility', '/gap/base-facility'),
    'base_soil': ('gap:base-soil', '/gap/base-soil'),
    'base_water': ('gap:base-water', '/gap/base-water'),
    'base_weather': ('gap:base-weather', '/gap/base-weather'),
    'plot': ('gap:plot', '/gap/plot'),
    'plot_planting': ('gap:plot-planting', '/gap/plot-planting'),
    'variety': ('gap:variety', '/gap/variety'),
    'seed_batch': ('gap:seed-batch', '/gap/seed-batch'),
    'origin_identify': ('gap:origin-identify', '/gap/origin-identify'),
    'seed_treatment': ('gap:seed-treatment', '/gap/seed-treatment'),
    'input_category': ('gap:input-category', '/gap/input-category'),
    'input_product': ('gap:input-product', '/gap/input-product'),
    'input_supplier': ('gap:input-supplier', '/gap/input-supplier'),
    'input_inventory': ('gap:input-inventory', '/gap/input-inventory'),
    'input_use_record': ('gap:input-use-record', '/gap/input-use-record'),
    'waste_disposal': ('gap:waste-disposal', '/gap/waste-disposal'),
    'planting_plan': ('gap:planting-plan', '/gap/planting-plan'),
    'farming_record': ('gap:farming-record', '/gap/farming-record'),
    'farming_detail': ('gap:farming-detail', '/gap/farming-detail'),
    'pest_control': ('gap:pest-control', '/gap/pest-control'),
    'irrigation_record': ('gap:irrigation-record', '/gap/irrigation-record'),
    'fertilization_record': ('gap:fertilization-record', '/gap/fertilization-record'),
    'fertilization_detail': ('gap:fertilization-detail', '/gap/fertilization-detail'),
    'harvest_plan': ('gap:harvest-plan', '/gap/harvest-plan'),
    'harvest_record': ('gap:harvest-record', '/gap/harvest-record'),
    'process_record': ('gap:process-record', '/gap/process-record'),
    'process_detail': ('gap:process-detail', '/gap/process-detail'),
    'drying_record': ('gap:drying-record', '/gap/drying-record'),
    'package_record': ('gap:package-record', '/gap/package-record'),
    'storage_area': ('gap:storage-area', '/gap/storage-area'),
    'storage_in_record': ('gap:storage-in-record', '/gap/storage-in-record'),
    'storage_out_record': ('gap:storage-out-record', '/gap/storage-out-record'),
    'storage_check': ('gap:storage-check', '/gap/storage-check'),
    'transport_record': ('gap:transport-record', '/gap/transport-record'),
    'unqualified_handle': ('gap:unqualified-handle', '/gap/unqualified-handle'),
    'quality_standard': ('gap:quality-standard', '/gap/quality-standard'),
    'inspect_task': ('gap:inspect-task', '/gap/inspect-task'),
    'inspect_record': ('gap:inspect-record', '/gap/inspect-record'),
    'inspect_report': ('gap:inspect-report', '/gap/inspect-report'),
    'pesticide_residue': ('gap:pesticide-residue', '/gap/pesticide-residue'),
    'heavy_metal': ('gap:heavy-metal', '/gap/heavy-metal'),
    'sample_record': ('gap:sample-record', '/gap/sample-record'),
    'release_record': ('gap:release-record', '/gap/release-record'),
    'document_category': ('gap:document-category', '/gap/document-category'),
    'document': ('gap:document', '/gap/document'),
    'sop': ('gap:sop', '/gap/sop'),
    'record_template': ('gap:record-template', '/gap/record-template'),
    'training_course': ('gap:training-course', '/gap/training-course'),
    'training_plan': ('gap:training-plan', '/gap/training-plan'),
    'training_record': ('gap:training-record', '/gap/training-record'),
    'training_participant': ('gap:training-participant', '/gap/training-participant'),
    'person_health': ('gap:person-health', '/gap/person-health'),
    'audit_plan': ('gap:audit-plan', '/gap/audit-plan'),
    'audit_checklist': ('gap:audit-checklist', '/gap/audit-checklist'),
    'audit_checklist_item': ('gap:audit-checklist-item', '/gap/audit-checklist-item'),
    'nc_item': ('gap:nc-item', '/gap/nc-item'),
    'change_record': ('gap:change-record', '/gap/change-record'),
    'complaint': ('gap:complaint', '/gap/complaint'),
    'recall_record': ('gap:recall-record', '/gap/recall-record'),
    'trace_batch': ('gap:trace-batch', '/gap/trace-batch'),
    'trace_node': ('gap:trace-node', '/gap/trace-node'),
    'operation_log': ('gap:operation-log', '/gap/operation-log'),
    'data_change_log': ('gap:data-change-log', '/gap/data-change-log'),
    'data_review': ('gap:data-review', '/gap/data-review'),
}

# Process all DO files
dofiles = glob.glob(f'{BASE_DIR}/dal/dataobject/*/*DO.java') + glob.glob(f'{BASE_DIR}/dal/dataobject/*/*/*DO.java')
dofiles.sort()

generated = 0
for dofile in dofiles:
    pkg, table, entity, entity_lower, cls, fields = parse_do(dofile)
    if not cls or not fields:
        print(f'SKIP {dofile} (no class/fields)')
        continue
    err = ERR_MAP.get(entity_lower, 'BASE_NOT_EXISTS')
    perm, path = PERM_PATH.get(entity_lower, (f'gap:{entity_lower}', f'/gap/{entity_lower}'))
    print(f'{cls} ({pkg}):')
    gen_mapper(pkg, entity, cls, fields)
    gen_service(pkg, entity, cls)
    gen_service_impl(pkg, entity, cls, fields, err)
    gen_controller(pkg, entity, cls, perm, path)
    gen_vos(pkg, entity, cls, fields)
    generated += 1

print(f'\nProcessed {generated} tables.')
