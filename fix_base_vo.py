import os
import re

BASE = 'yudao-module-gap/src/main/java/cn/iocoder/yudao/module/gap/controller/admin/base/vo'

def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

items = [
    ('environment', 'GapBaseEnvironment', '基地环境评估'),
    ('facility', 'GapBaseFacility', '基地设施设备'),
    ('plot', 'GapPlot', '地块管理'),
    ('planting', 'GapPlotPlanting', '地块种植历史'),
    ('soil', 'GapBaseSoil', '土壤检测'),
    ('water', 'GapBaseWater', '水源检测'),
    ('weather', 'GapBaseWeather', '气象数据'),
]

for subpkg, cls, label in items:
    dofile = f'yudao-module-gap/src/main/java/cn/iocoder/yudao/module/gap/dal/dataobject/base/{subpkg}/{cls}DO.java'
    with open(dofile, 'r', encoding='utf-8') as f:
        text = f.read()
    fields = []
    for m in re.finditer(r'/\*\*\s*\n\s*\*\s*([^*\n]+)\n\s*\*/\s*\n\s*private\s+(\w+)\s+(\w+);', text):
        fields.append((m.group(3), m.group(2), m.group(1).strip()))
    if not fields:
        for m in re.finditer(r'/\*\*\s+([^*]+?)\s+\*/\s+private\s+(\w+)\s+(\w+);', text):
            fields.append((m.group(3), m.group(2), m.group(1).strip()))

    save_body = ''
    for name, typ, comment in fields:
        if name == 'id':
            save_body += '    @Schema(description = "%s", example = "1024")\n    private Long id;\n\n' % comment
        else:
            save_body += '    @Schema(description = "%s")\n    private %s %s;\n\n' % (comment, typ, name)

    save = '''package cn.iocoder.yudao.module.gap.controller.admin.base.vo.%s;

import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

@Schema(description = "管理后台 - GAP %s新增/修改 Request VO")
@Data
public class %sSaveReqVO {

%s}
''' % (subpkg, label, cls, save_body)
    write('%s/%s/%sSaveReqVO.java' % (BASE, subpkg, cls), save)

    page_body = ''
    for name, typ, comment in fields:
        if name in ('id','creator','createTime','updater','updateTime','deleted','tenantId','remark'):
            continue
        page_body += '    @Schema(description = "%s")\n    private %s %s;\n\n' % (comment, typ, name)

    page = '''package cn.iocoder.yudao.module.gap.controller.admin.base.vo.%s;

import cn.iocoder.yudao.framework.common.pojo.PageParam;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.ToString;

@Schema(description = "管理后台 - GAP %s分页 Request VO")
@Data
@EqualsAndHashCode(callSuper = true)
@ToString(callSuper = true)
public class %sPageReqVO extends PageParam {

%s}
''' % (subpkg, label, cls, page_body)
    write('%s/%s/%sPageReqVO.java' % (BASE, subpkg, cls), page)

    resp_body = ''
    for name, typ, comment in fields:
        resp_body += '    @Schema(description = "%s")\n    @ExcelProperty("%s")\n    private %s %s;\n\n' % (comment, comment, typ, name)
    resp_body += '    @Schema(description = "创建时间")\n    @ExcelProperty("创建时间")\n    private LocalDateTime createTime;\n'

    resp = '''package cn.iocoder.yudao.module.gap.controller.admin.base.vo.%s;

import cn.idev.excel.annotation.ExcelIgnoreUnannotated;
import cn.idev.excel.annotation.ExcelProperty;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;

import java.time.LocalDateTime;

@Schema(description = "管理后台 - GAP %s Response VO")
@Data
@ExcelIgnoreUnannotated
public class %sRespVO {

%s}
''' % (subpkg, label, cls, resp_body)
    write('%s/%s/%sRespVO.java' % (BASE, subpkg, cls), resp)
    print('Generated %s VO files' % cls)
