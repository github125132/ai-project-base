import os
import re

BASE = 'yudao-module-gap/src/main/java/cn/iocoder/yudao/module/gap'

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

def gen_do(table, entity, pkg, fields):
    cn = 'Gap' + pascal(entity) + 'DO'
    imps = set()
    for _, typ, _ in fields:
        if typ == 'BigDecimal': imps.add('java.math.BigDecimal')
        if typ == 'LocalDate': imps.add('java.time.LocalDate')
        if typ == 'LocalDateTime': imps.add('java.time.LocalDateTime')
    imp_lines = '\n'.join(f'import {i};' for i in sorted(imps))
    if imp_lines:
        imp_lines = '\n' + imp_lines + '\n'
    body = ''
    for col, typ, comment in fields:
        body += f"""
    /**
     * {comment}
     */
    private {typ} {camel(col)};"""
    content = f"""package cn.iocoder.yudao.module.gap.dal.dataobject.{pkg};

import cn.iocoder.yudao.framework.mybatis.core.dataobject.BaseDO;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.*;{imp_lines}
/**
 * GAP {entity} DO
 *
 * @author 芋道源码
 */
@TableName("{table}")
@Data
@EqualsAndHashCode(callSuper = true)
@ToString(callSuper = true)
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class {cn} extends BaseDO {{{body}
}}
"""
    write(f'{BASE}/dal/dataobject/{pkg}/{cn}.java', content)

def gen_mapper(table, entity, pkg, fields):
    cn = 'Gap' + pascal(entity)
    mname = f'{cn}Mapper'
    query = ''
    for col, typ, comment in fields:
        if col in ('id','creator','create_time','updater','update_time','deleted','tenant_id','remark'):
            continue
        gn = getter_name(col)
        if typ == 'String':
            query += f'\n                .likeIfPresent({cn}DO::get{gn}, reqVO.get{gn}())'
        else:
            query += f'\n                .eqIfPresent({cn}DO::get{gn}, reqVO.get{gn}())'
    fk = ''
    for col, typ, comment in fields:
        if col.endswith('_id') and col != 'id' and typ == 'Long':
            cc = camel(col)
            pc = pascal(col)
            gn = getter_name(col)
            fk += f"""
    default List<{cn}DO> selectListBy{pc}(Long {cc}) {{
        return selectList({cn}DO::get{gn}, {cc});
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
    write(f'{BASE}/dal/mysql/{pkg}/{mname}.java', content)

def gen_service(entity, pkg):
    cn = 'Gap' + pascal(entity)
    sname = f'{cn}Service'
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
    write(f'{BASE}/service/{pkg}/{sname}.java', content)

def gen_service_impl(entity, pkg, err_const):
    cn = 'Gap' + pascal(entity)
    iname = f'{cn}ServiceImpl'
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
    private {cn}Mapper {camel(entity)}Mapper;

    @Override
    public Long create{cn}({cn}SaveReqVO createReqVO) {{
        {cn}DO entity = BeanUtils.toBean(createReqVO, {cn}DO.class);
        {camel(entity)}Mapper.insert(entity);
        return entity.getId();
    }}

    @Override
    public void update{cn}({cn}SaveReqVO updateReqVO) {{
        validate{cn}Exists(updateReqVO.getId());
        {cn}DO updateObj = BeanUtils.toBean(updateReqVO, {cn}DO.class);
        {camel(entity)}Mapper.updateById(updateObj);
    }}

    @Override
    public void delete{cn}(Long id) {{
        validate{cn}Exists(id);
        {camel(entity)}Mapper.deleteById(id);
    }}

    @Override
    public {cn}DO get{cn}(Long id) {{
        return {camel(entity)}Mapper.selectById(id);
    }}

    @Override
    public PageResult<{cn}DO> get{cn}Page({cn}PageReqVO pageReqVO) {{
        return {camel(entity)}Mapper.selectPage(pageReqVO);
    }}

    @Override
    public {cn}DO validate{cn}Exists(Long id) {{
        {cn}DO entity = {camel(entity)}Mapper.selectById(id);
        if (entity == null) {{
            throw exception({err_const});
        }}
        return entity;
    }}
}}
"""
    write(f'{BASE}/service/{pkg}/{iname}.java', content)

def gen_controller(entity, pkg, perm, path):
    cn = 'Gap' + pascal(entity)
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
    private {cn}Service {camel(entity)}Service;

    @PostMapping("/create")
    @Operation(summary = "创建{entity}")
    @PreAuthorize("@ss.hasPermission('{perm}:create')")
    public CommonResult<Long> create{cn}(@Valid @RequestBody {cn}SaveReqVO createReqVO) {{
        return success({camel(entity)}Service.create{cn}(createReqVO));
    }}

    @PutMapping("/update")
    @Operation(summary = "更新{entity}")
    @PreAuthorize("@ss.hasPermission('{perm}:update')")
    public CommonResult<Boolean> update{cn}(@Valid @RequestBody {cn}SaveReqVO updateReqVO) {{
        {camel(entity)}Service.update{cn}(updateReqVO);
        return success(true);
    }}

    @DeleteMapping("/delete")
    @Operation(summary = "删除{entity}")
    @Parameter(name = "id", description = "编号", required = true)
    @PreAuthorize("@ss.hasPermission('{perm}:delete')")
    public CommonResult<Boolean> delete{cn}(@RequestParam("id") Long id) {{
        {camel(entity)}Service.delete{cn}(id);
        return success(true);
    }}

    @GetMapping("/get")
    @Operation(summary = "获得{entity}")
    @Parameter(name = "id", description = "编号", required = true, example = "1024")
    @PreAuthorize("@ss.hasPermission('{perm}:query')")
    public CommonResult<{cn}RespVO> get{cn}(@RequestParam("id") Long id) {{
        {cn}DO entity = {camel(entity)}Service.get{cn}(id);
        return success(BeanUtils.toBean(entity, {cn}RespVO.class));
    }}

    @GetMapping("/page")
    @Operation(summary = "获得{entity}分页")
    @PreAuthorize("@ss.hasPermission('{perm}:query')")
    public CommonResult<PageResult<{cn}RespVO>> get{cn}Page(@Valid {cn}PageReqVO pageReqVO) {{
        PageResult<{cn}DO> pageResult = {camel(entity)}Service.get{cn}Page(pageReqVO);
        return success(BeanUtils.toBean(pageResult, {cn}RespVO.class));
    }}
}}
"""
    write(f'{BASE}/controller/admin/{pkg}/{cn}Controller.java', content)

def gen_vos(entity, pkg, fields):
    cn = 'Gap' + pascal(entity)
    # SaveReqVO
    save_body = ''
    for col, typ, comment in fields:
        if col == 'id':
            save_body += f'    @Schema(description = "{comment}\", example = "1024")\n    private Long id;\n\n'
            continue
        if typ == 'String':
            save_body += f'    @Schema(description = "{comment}")\n    private {typ} {camel(col)};\n\n'
        else:
            save_body += f'    @Schema(description = "{comment}")\n    private {typ} {camel(col)};\n\n'
    save = f"""package cn.iocoder.yudao.module.gap.controller.admin.{pkg}.vo;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

@Schema(description = "管理后台 - GAP {entity}新增/修改 Request VO")
@Data
public class {cn}SaveReqVO {{

{save_body}}}
"""
    write(f'{BASE}/controller/admin/{pkg}/vo/{cn}SaveReqVO.java', save)

    # PageReqVO
    page_body = ''
    for col, typ, comment in fields:
        if col in ('id','creator','create_time','updater','update_time','deleted','tenant_id','remark'):
            continue
        if typ == 'String':
            page_body += f'    @Schema(description = "{comment}")\n    private {typ} {camel(col)};\n\n'
        else:
            page_body += f'    @Schema(description = "{comment}")\n    private {typ} {camel(col)};\n\n'
    page = f"""package cn.iocoder.yudao.module.gap.controller.admin.{pkg}.vo;

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
    write(f'{BASE}/controller/admin/{pkg}/vo/{cn}PageReqVO.java', page)

    # RespVO
    resp_body = ''
    for col, typ, comment in fields:
        resp_body += f'    @Schema(description = "{comment}")\n    @ExcelProperty("{comment}")\n    private {typ} {camel(col)};\n\n'
    resp_body += '    @Schema(description = "创建时间")\n    @ExcelProperty("创建时间")\n    private LocalDateTime createTime;\n'
    resp = f"""package cn.iocoder.yudao.module.gap.controller.admin.{pkg}.vo;

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
    write(f'{BASE}/controller/admin/{pkg}/vo/{cn}RespVO.java', resp)

def gen_all(table, entity, pkg, perm, path, err, fields):
    gen_do(table, entity, pkg, fields)
    gen_mapper(table, entity, pkg, fields)
    gen_service(entity, pkg)
    gen_service_impl(entity, pkg, err)
    gen_controller(entity, pkg, perm, path)
    gen_vos(entity, pkg, fields)

# Table definitions
TABLES = [
    ('gap_waste_disposal', 'waste_disposal', 'input', 'gap:waste-disposal', '/gap/waste-disposal', 'BASE_NOT_EXISTS', [
        ('id','Long','编号'),
        ('record_no','String','处理单号'),
        ('waste_type','Integer','废弃物类型(0农药包装 1农药残液 2肥料袋 3其他)'),
        ('base_id','Long','基地编号'),
        ('source_record_id','Long','来源记录编号'),
        ('quantity','BigDecimal','数量'),
        ('unit','String','单位'),
        ('disposal_date','LocalDate','处理日期'),
        ('disposal_method','String','处理方式'),
        ('disposal_location','String','处理地点'),
        ('handler_id','Long','处理人'),
        ('witness_id','Long','见证人'),
        ('photo_url','String','处理照片'),
        ('status','Integer','状态'),
        ('remark','String','备注'),
    ]),
    ('gap_training_course', 'training_course', 'training', 'gap:training-course', '/gap/training-course', 'TRAINING_COURSE_NOT_EXISTS', [
        ('id','Long','课程编号'),
        ('code','String','课程编码'),
        ('name','String','课程名称'),
        ('category','Integer','类别(0GAP法规 1SOP 2安全生产 3职业道德 4专业技术 5质量管理)'),
        ('content','String','课程内容'),
        ('duration','Integer','课时(小时)'),
        ('instructor','String','讲师'),
        ('instructor_org','String','讲师单位'),
        ('material_url','String','培训资料附件'),
        ('status','Integer','状态'),
        ('remark','String','备注'),
    ]),
    ('gap_training_plan', 'training_plan', 'training', 'gap:training-plan', '/gap/training-plan', 'TRAINING_COURSE_NOT_EXISTS', [
        ('id','Long','计划编号'),
        ('plan_no','String','计划编号'),
        ('year','Integer','年度'),
        ('plan_name','String','计划名称'),
        ('course_id','Long','课程编号'),
        ('training_type','Integer','培训类型(0新员工 1在岗 2转岗 3晋升 4继续教育)'),
        ('target_dept_id','Long','目标部门'),
        ('target_post_ids','String','目标岗位'),
        ('planned_start_date','LocalDate','计划开始日期'),
        ('planned_end_date','LocalDate','计划结束日期'),
        ('planned_participants','Integer','计划人数'),
        ('training_location','String','培训地点'),
        ('training_method','String','培训方式'),
        ('approver_id','Long','审批人'),
        ('approve_time','LocalDateTime','审批时间'),
        ('status','Integer','状态(0草稿 1待审批 2已批准 3执行中 4已完成)'),
        ('remark','String','备注'),
    ]),
    ('gap_training_record', 'training_record', 'training', 'gap:training-record', '/gap/training-record', 'TRAINING_COURSE_NOT_EXISTS', [
        ('id','Long','记录编号'),
        ('record_no','String','记录单号'),
        ('plan_id','Long','培训计划编号'),
        ('course_id','Long','课程编号'),
        ('training_date','LocalDate','培训日期'),
        ('training_start_time','LocalDateTime','开始时间'),
        ('training_end_time','LocalDateTime','结束时间'),
        ('training_location','String','培训地点'),
        ('instructor','String','讲师'),
        ('participant_count','Integer','参加人数'),
        ('content_snapshot','String','培训内容快照'),
        ('attendance_url','String','签到表附件'),
        ('photo_url','String','培训照片'),
        ('status','Integer','状态(0已计划 1已完成 2已考核)'),
        ('remark','String','备注'),
    ]),
    ('gap_training_participant', 'training_participant', 'training', 'gap:training-participant', '/gap/training-participant', 'TRAINING_COURSE_NOT_EXISTS', [
        ('id','Long','编号'),
        ('record_id','Long','培训记录编号'),
        ('user_id','Long','参训人员'),
        ('dept_id','Long','部门'),
        ('post_id','Long','岗位'),
        ('is_attended','Boolean','是否出席'),
        ('attendance_time','LocalDateTime','签到时间'),
        ('exam_score','BigDecimal','考核成绩'),
        ('exam_result','Integer','考核结果(0合格 1不合格 2未考核)'),
        ('cert_no','String','证书编号'),
        ('cert_url','String','证书附件'),
        ('status','Integer','状态'),
        ('remark','String','备注'),
    ]),
    ('gap_person_health', 'person_health', 'training', 'gap:person-health', '/gap/person-health', 'TRAINING_COURSE_NOT_EXISTS', [
        ('id','Long','编号'),
        ('user_id','Long','人员编号'),
        ('check_date','LocalDate','体检日期'),
        ('check_org','String','体检机构'),
        ('check_item','String','检查项目'),
        ('check_result','String','检查结果'),
        ('is_contagious','Boolean','是否传染病'),
        ('is_skin_disease','Boolean','是否皮肤病'),
        ('is_qualified','Boolean','是否合格'),
        ('health_cert_no','String','健康证号'),
        ('health_cert_url','String','健康证附件'),
        ('validity_date','LocalDate','有效期至'),
        ('next_check_date','LocalDate','下次体检日期'),
        ('warning_sent','Boolean','是否已发送到期预警'),
        ('status','Integer','状态(0有效 1即将过期 2已过期)'),
        ('remark','String','备注'),
    ]),
    ('gap_audit_plan', 'audit_plan', 'audit', 'gap:audit-plan', '/gap/audit-plan', 'AUDIT_PLAN_NOT_EXISTS', [
        ('id','Long','计划编号'),
        ('plan_no','String','计划编号'),
        ('year','Integer','年度'),
        ('plan_name','String','计划名称'),
        ('audit_type','Integer','审核类型(0内部审核 1管理评审 2专项检查)'),
        ('audit_scope','String','审核范围'),
        ('planned_start_date','LocalDate','计划开始日期'),
        ('planned_end_date','LocalDate','计划结束日期'),
        ('auditor_leader_id','Long','审核组长'),
        ('auditor_ids','String','审核组员'),
        ('audited_dept_ids','String','被审核部门'),
        ('approver_id','Long','审批人'),
        ('approve_time','LocalDateTime','审批时间'),
        ('status','Integer','状态(0草稿 1待审批 2已批准 3执行中 4已完成)'),
        ('remark','String','备注'),
    ]),
    ('gap_audit_checklist', 'audit_checklist', 'audit', 'gap:audit-checklist', '/gap/audit-checklist', 'AUDIT_PLAN_NOT_EXISTS', [
        ('id','Long','检查表编号'),
        ('checklist_no','String','检查表编号'),
        ('plan_id','Long','审核计划编号'),
        ('name','String','检查表名称'),
        ('check_chapter','String','检查章节'),
        ('applicable_clauses','String','适用条款'),
        ('status','Integer','状态'),
        ('remark','String','备注'),
    ]),
    ('gap_audit_checklist_item', 'audit_checklist_item', 'audit', 'gap:audit-checklist-item', '/gap/audit-checklist-item', 'AUDIT_PLAN_NOT_EXISTS', [
        ('id','Long','编号'),
        ('checklist_id','Long','检查表编号'),
        ('item_no','String','项目编号'),
        ('chapter','String','章节'),
        ('clause','String','条款'),
        ('check_content','String','检查内容'),
        ('check_method','String','检查方法'),
        ('check_standard','String','检查标准'),
        ('sort','Integer','排序'),
        ('status','Integer','状态'),
        ('remark','String','备注'),
    ]),
    ('gap_nc_item', 'nc_item', 'audit', 'gap:nc-item', '/gap/nc-item', 'NC_ITEM_NOT_EXISTS', [
        ('id','Long','编号'),
        ('nc_no','String','不符合项编号'),
        ('plan_id','Long','审核计划编号'),
        ('checklist_id','Long','检查表编号'),
        ('checklist_item_id','Long','检查项目编号'),
        ('nc_type','Integer','不符合类型(0一般 1严重)'),
        ('nc_desc','String','不符合描述'),
        ('clause_reference','String','引用条款'),
        ('evidence','String','证据'),
        ('audited_dept_id','Long','责任部门'),
        ('responsible_user_id','Long','责任人'),
        ('root_cause','String','根本原因分析'),
        ('corrective_action','String','纠正措施'),
        ('corrective_deadline','LocalDate','纠正期限'),
        ('corrective_completion_date','LocalDate','纠正完成日期'),
        ('preventive_action','String','预防措施'),
        ('preventive_deadline','LocalDate','预防期限'),
        ('preventive_completion_date','LocalDate','预防完成日期'),
        ('verifier_id','Long','验证人'),
        ('verify_date','LocalDate','验证日期'),
        ('verify_result','Integer','验证结果(0待验证 1有效 2无效)'),
        ('verify_opinion','String','验证意见'),
        ('status','Integer','状态(0待整改 1整改中 2待验证 3已关闭)'),
        ('remark','String','备注'),
    ]),
]

for t in TABLES:
    gen_all(*t)

# Count files
import subprocess
result = subprocess.run(['find', BASE, '-type', 'f', '-name', '*.java'], capture_output=True, text=True)
count = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
print(f'Generated {len(TABLES)} tables. Total Java files: {count}')
