from django import template

__all__ = (
    'getfield',
    'render_custom_fields',
    'render_errors',
    'render_field',
    'render_form',
    'widget_type',
)


register = template.Library()


#
# Filters
#

@register.filter()
def getfield(form, fieldname):
    """
    Return the specified bound field of a Form.
    """
    try:
        return form[fieldname]
    except KeyError:
        return None


@register.filter(name='widget_type')
def widget_type(field):
    """
    Return the widget type
    """
    if hasattr(field, 'widget'):
        return field.widget.__class__.__name__.lower()
    elif hasattr(field, 'field'):
        return field.field.widget.__class__.__name__.lower()
    else:
        return None


#
# Inclusion tags
#

@register.inclusion_tag('form_helpers/render_field.html')
def render_field(field, bulk_nullable=False, label=None):
    """
    Render a single form field from template
    """
    # 详情页表单label
    flabel = ''
    labelMap = {
        'VLAN group': 'VLAN组',
        'Group ID': '组ID',
        'Description': '描述',
        'Tags': '标签',
        'Name': '名称',
        'Search': '搜索',
        'Saved Filter': '已保存的过滤器',
        'Tags field': '标签字段',
        'Parent region': '上级地区',
        'Contact': '联系人',
        'Contact Role': '联系人角色',
        'Contact Group': '联系人组',
        'Parent group': '上级组织',
        'Status': '状态',
        'Region': '地区',
        'Site group': '站点组',
        'Tenant': '租户',
        'Tenant group': '租户组',
        'Facility': '设施',
        'Group': '群',
        'Time zone': '时区',
        'Comments': '评论',
        'Longitude': '经度',
        'Latitude': '纬度',
        'Shipping address': '邮寄地址',
        'Physical address': '物理地址',
        'Parent': '父级',
        'Site': '站点',
        'Sites': '站点',
        'Role': '角色',
        'Type': '类型',
        'Weight': '重量',
        'Max weight': '最大重量',
        'Weight unit': '重量单位',
        'Location': '地点',
        'Serial': '序列',
        'Serial number': '序列号',
        'Width': '宽度',
        'Asset tag': '资产标签',
        'Facility ID': '设施ID',
        'Mounting depth': '安装深度',
        'Height (U)': '高度(U)',
        'Color': '颜色',
        'User': '用户',
        'Rack': '机柜',
        'Units': '单位',
        'Address': '地址',
        'Link': '联系',
        'Title': '标题',
        'Phone': '电话',
        'Email': '电子邮件',
        'Object type': '对象类型',
        'Priority': '优先级',
        'Device role': '设备角色',
        'Device type': '设备类型',
        'Airflow': '空气流动',
        'Position': '位置',
        'Positions': '位置',
        'Platform': '平台',
        'Rack face': '机柜正面',
        'Cluster': '集群',
        'Virtual chassis': '虚拟机箱',
        'Virtual Chassis': '虚拟机箱',
        'Config template': '配置模板',
        'Manufacturer': '制造商',
        'Device': '设备',
        'Module': '模块',
        'Module bay': '模块托架',
        'Module type': '模块类型',
        'NAPALM arguments': 'NAPALM参数',
        'NAPALM driver': 'NAPALM驱动',
        'Domain': '域',
        'Members': '成员',
        'Initial position': '初始位置',
        'Has a primary IP': '拥有主IP',
        'Identifier': '标识符',
        'Primary IPv4': '主IPv4',
        'Primary IPv6': '主IPv6',
        'Default platform': '默认平台',
        'Part number': '零件号',
        'Subdevice role': '子设备角色',
        'Has a front image': '有正面图',
        'Has a rear image': '有背面图',
        'Has console ports': '有控制台端口',
        'Has console server ports': '具有控制台服务器端口',
        'Has power ports': '有电源端口',
        'Has power outlets': '有电源插座',
        'Has interfaces': '有接口',
        'Has pass-through ports': '有直通端口',
        'Has device bays': '有设备托架',
        'Has module bays': '有模块托架',
        'Has inventory items': '有库存物品',
        'Model': '模型',
        'Parent/child status': '父/子状态',
        'Front image': '正面图',
        'Rear image': '背面图',
        'Label': '标签',
        'Enabled': '启用',
        'Speed': '速度',
        'Duplex': '复式',
        'Mode': '模式',
        'MAC address': 'MAC地址',
        'PoE mode': 'PoE模式',
        'PoE type': 'PoE类型',
        'Kind': '种类',
        'Wireless role': '无线角色',
        'Wireless channel': '无线通道',
        'Channel width (MHz)': '信道宽度(MHz)',
        'Transmit power (dBm)': '发射功率(dBm)',
        'Virtual Device Context': '虚拟设备上下文',
        'Virtual Device Contexts': '虚拟设备上下文',
        'Mgmt only': '仅管理',
        'Cabled': '有线',
        'Connected': '连接',
        'Occupied': '占用',
        'Speed (Kbps)': '速度(Kbps)',
        'Parent interface': '上级接口',
        'Bridged interface': '桥接接口',
        'LAG interface': 'LAG接口',
        'Channel frequency (MHz)': '信道频率(MHz)',
        'Wireless LAN group': '无线局域网组',
        'Rear ports': '背面端口',
        'Maximum draw': '最大功耗',
        'Allocated draw': '分配功耗',
        'Feed leg': '电源线路',
        'Discovered': '已发现',
        'Console port': '控制台端口',
        'Part ID': '零件ID',
        'Console server port': '控制台服务器端口',
        'Front port': '前端口',
        'Interface': '接口',
        'Power outlet': '电源插座',
        'Power port': '电源端口',
        'Rear port': '背面端口',
        'Length': '长度',
        'Length unit': '长度单位',
        'Auth cipher': '验证密码',
        'Auth type': '认证类型',
        'Auth psk': '授权密码',
        'Cipher': '密码',
        'Pre-shared key': '预共享密钥',
        'Parent Prefix': '父前缀',
        'Address family': '地址族',
        'Mask length': '掩码长度',
        'Assigned to an interface': '分配接口',
        'Assigned VRF': '分配VRF',
        'Present in VRF': '存在于VRF中',
        'Assigned Device': '分配设备',
        'Assigned VM': '分配VM',
        'IP Address': 'IP地址',
        'Marked as 100% utilized': '标记为 100% 使用',
        'Start address': '起始地址',
        'End address': '结束地址',
        'Search within': '搜索范围内',
        'Is a pool': '是一个地址池',
        'Prefix': '前缀',
        'Start': '首',
        'End': '尾',
        'Date added': '添加日期',
        'Private': '私有',
        'Import targets': '导入目标',
        'Export targets': '导出目标',
        'Imported by VRF': '由 VRF 导入',
        'Exported by VRF': '由 VRF 导出',
        'Minimum VID': '最小VID',
        'Maximum VID': '最大VID',
        'Minimum VLAN ID': '最小VLAN ID',
        'Maximum VLAN ID': '最大VLAN ID',
        'Authentication key': '身份验证密钥',
        'Protocol': '协议',
        'Authentication type': '身份验证类型',
        'Scope type': '范围类型',
        'Port': '端口',
        'Ports': '端口',
        'Service template': '服务模板',
        'IP Addresses': 'IP地址',
        'Assigned Object Type': '分配对象类型',
        'Virtual Machine': '虚拟机',
        'Provider': '供应商',
        'Provider account': '供应商账户',
        'Provider network': '供应商网络',
        'Install date': '安装日期',
        'Termination date': '终止日期',
        'Commit rate (Kbps)': '提交速率 (Kbps)',
        'Circuit ID': '电路ID',
        'Installed': '安装日期',
        'Terminates': '终止日期',
        'ASN (legacy)': 'ASN (传统版本)',
        'Account': '账户',
        'Account ID': '账户ID',
        'Service id': '服务id',
        'Service ID': '服务ID',
        'Power panel': '电力面板',
        'Supply': '供电',
        'Voltage': '电压',
        'Amperage': '电流',
        'Phase': '相',
        'Max utilization': '最大利用率',
        'Data source': '数据源',
        'Data file': '数据文件',
        'Regions': '地区',
        'Locations': '地点',
        'Device Types': '设备类型',
        'Site groups': '站点组',
        'Device types': '设备类型',
        'Platforms': '平台',
        'Roles': '角色',
        'Cluster types': '集群类型',
        'Cluster groups': '集群组',
        'Clusters': '集群',
        'Tenant groups': '租户组',
        'File': '文件',
        'Data': '数据',
        'Format': '格式',
        'Tenants': '租户',
        'Environment params': '环境参数',
        'Template code': '模板代码',
        'Circuit': '电路',
        'Termination': '终端',
        'Port speed (Kbps)': '端口速度(Kbps)',
        'Upstream speed (Kbps)': '上行速度(Kbps)',
        'Cross-connect ID': '交叉连接ID',
        'Patch panel/port(s)': '配线面板/端口'
    }
    if field.label in labelMap:
        flabel = labelMap[field.label]
    else:
        flabel = field.label
    return {
        'field': field,
        'label': label or flabel,
        'bulk_nullable': bulk_nullable,
    }


@register.inclusion_tag('form_helpers/render_custom_fields.html')
def render_custom_fields(form):
    """
    Render all custom fields in a form
    """
    return {
        'form': form,
    }


@register.inclusion_tag('form_helpers/render_form.html')
def render_form(form):
    """
    Render an entire form from template
    """
    return {
        'form': form,
    }


@register.inclusion_tag('form_helpers/render_errors.html')
def render_errors(form):
    """
    Render form errors, if they exist.
    """
    return {
        "form": form
    }
