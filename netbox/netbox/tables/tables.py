import django_tables2 as tables
from django.contrib.auth.models import AnonymousUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import FieldDoesNotExist
from django.db.models.fields.related import RelatedField
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from django_tables2.data import TableQuerysetData

from extras.models import CustomField, CustomLink
from extras.choices import CustomFieldVisibilityChoices
from netbox.tables import columns
from utilities.paginator import EnhancedPaginator, get_paginate_count
from utilities.utils import get_viewname, highlight_string, title

__all__ = (
    'BaseTable',
    'NetBoxTable',
    'SearchTable',
)


class BaseTable(tables.Table):
    """
    Base table class for NetBox objects. Adds support for:

        * User configuration (column preferences)
        * Automatic prefetching of related objects
        * BS5 styling

    :param user: Personalize table display for the given user (optional). Has no effect if AnonymousUser is passed.
    """
    exempt_columns = ()

    class Meta:
        attrs = {
            'class': 'table table-hover object-list',
        }

    def __init__(self, *args, user=None, **kwargs):

        super().__init__(*args, **kwargs)

        # Set default empty_text if none was provided
        if self.empty_text is None:
            self.empty_text = f"No {self._meta.model._meta.verbose_name_plural} found"

        # Determine the table columns to display by checking the following:
        #   1. User's configuration for the table
        #   2. Meta.default_columns
        #   3. Meta.fields
        selected_columns = None
        if user is not None and not isinstance(user, AnonymousUser):
            selected_columns = user.config.get(f"tables.{self.__class__.__name__}.columns")
        if not selected_columns:
            selected_columns = getattr(self.Meta, 'default_columns', self.Meta.fields)

        # Hide non-selected columns which are not exempt
        for column in self.columns:
            if column.name not in [*selected_columns, *self.exempt_columns]:
                self.columns.hide(column.name)

        # Rearrange the sequence to list selected columns first, followed by all remaining columns
        # TODO: There's probably a more clever way to accomplish this
        self.sequence = [
            *[c for c in selected_columns if c in self.columns.names()],
            *[c for c in self.columns.names() if c not in selected_columns]
        ]

        # PK column should always come first
        if 'pk' in self.sequence:
            self.sequence.remove('pk')
            self.sequence.insert(0, 'pk')

        # Actions column should always come last
        if 'actions' in self.sequence:
            self.sequence.remove('actions')
            self.sequence.append('actions')

        # Dynamically update the table's QuerySet to ensure related fields are pre-fetched
        if isinstance(self.data, TableQuerysetData):

            prefetch_fields = []
            for column in self.columns:
                if column.visible:
                    model = getattr(self.Meta, 'model')
                    accessor = column.accessor
                    prefetch_path = []
                    for field_name in accessor.split(accessor.SEPARATOR):
                        try:
                            field = model._meta.get_field(field_name)
                        except FieldDoesNotExist:
                            break
                        if isinstance(field, RelatedField):
                            # Follow ForeignKeys to the related model
                            prefetch_path.append(field_name)
                            model = field.remote_field.model
                        elif isinstance(field, GenericForeignKey):
                            # Can't prefetch beyond a GenericForeignKey
                            prefetch_path.append(field_name)
                            break
                    if prefetch_path:
                        prefetch_fields.append('__'.join(prefetch_path))
            self.data.data = self.data.data.prefetch_related(*prefetch_fields)

    def _get_columns(self, visible=True):
        columns = []
        columnsMap = {
            'Last updated': '最后更新时间',
            'Created': '创建时间',
            'Description': '描述',
            'Comments': '评论',
            'Tags': '标签',
            'Longitude': '经度',
            'Latitude': '纬度',
            'Shipping address': '邮寄地址',
            'Physical address': '物理地址',
            'Time zone': '时区',
            'Facility': '设施',
            'Device': '设备',
            'Devices': '设备',
            'Module bay': '模块托架',
            'Manufacturer': '制造商',
            'Module type': '模块类型',
            'Status': '状态',
            'Serial number': '序列号',
            'Asset tag': '资产标签',
            'Tenant Group': '租户组',
            'Platform': '平台',
            'Platforms': '平台',
            'Region': '地区',
            'Site Group': '站点组',
            'Position (U)': '位置(U)',
            'Rack face': '机柜正面',
            'Airflow': '空气流动',
            'IPv4 Address': 'IPv4地址',
            'IPv6 Address': 'IPv6地址',
            'Cluster': '集群',
            'Virtual chassis': '虚拟机箱',
            'Config template': '配置模板',
            'Contacts': '联系方式',
            'Name': '名称',
            'Tenant': '租户',
            'Site': '站点',
            'Location': '地点',
            'Rack': '机柜',
            'Role': '角色',
            'Type': '类型',
            'IP Address': 'IP地址',
            'Color': '颜色',
            'NAPALM arguments': 'NAPALM参数',
            'NAPALM driver': 'NAPALM驱动',
            'Domain': '域',
            'Master': '主节点',
            'Members': '成员',
            'Interfaces': '接口',
            'Identifier': '标识符',
            'Default platform': '默认平台',
            'Parent/child status': '父/子状态',
            'Weight': '重量',
            'Device Type': '设备类型',
            'Device Types': '设备类型',
            'Part number': '零件号',
            'Height (U)': '高度(U)',
            'Full Depth': '全深度',
            'Instances': '实例',
            'Module Type': '模块类型',
            'Module Types': '模块类型',
            'Inventory Items': '库存物品',
            'Module': '模块',
            'Management only': '仅限管理',
            'Speed (Kbps)': '速度(Kbps)',
            'Duplex': '复式',
            'Mode': '模式',
            'MAC Address': 'MAC地址',
            'PoE mode': 'PoE模式',
            'PoE type': 'PoE类型',
            'Wireless role': '无线角色',
            'Wireless channel': '无线通道',
            'Channel frequency (MHz)': '信道频率(MHz)',
            'Channel width (MHz)': '信道宽度(MHz)',
            'Transmit power (dBm)': '发射功率(dBm)',
            'Mark connected': '标记已连接',
            'Cable': '电缆',
            'Cable Color': '电缆颜色',
            'Wireless link': '无线连接',
            'Link Peers': '链接对等方',
            'Connection': '连接',
            'IP Addresses': 'IP地址',
            'Label': '标签',
            'Enabled': '启用',
            'Rear port': '背面端口',
            'Position': '位置',
            'Positions': '位置',
            'Speed': '速度',
            'Maximum draw': '最大功耗',
            'Allocated draw': '分配功耗',
            'Power port': '电源端口',
            'Feed leg': '电源线路',
            'Installed device': '已安装设备',
            'Module status': '模块状态',
            'Component': '组件',
            'Discovered': '已发现',
            'Items': '项目',
            'Sites': '站点',
            'Racks': '机柜',
            'Width': '宽度',
            'Outer Width': '外宽',
            'Outer Depth': '外深度',
            'Mounting depth': '安装深度',
            'Max weight': '最大重量',
            'Power': '电源',
            'Height': '高度',
            'Space': '空间',
            'Reservation': '预定',
            'Units': '单位',
            'User': '用户',
            'Group': '群',
            'Tenants': '租户',
            'Address': '机柜',
            'Link': '联系',
            'Assignments': '分配',
            'Title': '标题',
            'Phone': '电话',
            'Email': '电子邮件',
            'Object Type': '对象类型',
            'Object': '对象',
            'Contact': '联系方式',
            'Priority': '优先级',
            'Device A': '设备A',
            'Device B': '设备B',
            'Rack A': '机柜A',
            'Rack B': '机柜B',
            'Location A': '地点A',
            'Location B': '地点B',
            'Site A': '站点A',
            'Site B': '站点B',
            'Length': '长度',
            'Termination A': '终端A',
            'Termination B': '终端B',
            'Auth cipher': '身份验证密码',
            'Pre-shared key': '预共享密钥',
            'Interface A': '接口A',
            'Interface B': '接口B',
            'Auth Type': '验证类型',
            'Utilization': '使用率',
            'Start address': '起始地址',
            'End address': '结束地址',
            'Size': '大小',
            'Pool': '分配资源池',
            'Marked Utilized': '标记已使用',
            'Depth': '深度',
            'Prefix': '前缀',
            'Children': '子网掩码',
            'Prefixes': '前缀',
            'IP Ranges': 'IP范围',
            'Start': '开始',
            'End': '结尾',
            'Site Count': '站点数量',
            'Provider Count': '供应商数量',
            'Aggregate': '聚合',
            'Added': '添加',
            'Private': '私有',
            'Unique': '唯一',
            'Import targets': '导入目标',
            'Export targets': '导出目标',
            'Minimum VLAN ID': '最小VLAN ID',
            'Maximum VLAN ID': '最大VLAN ID',
            'Scope type': '范围类型',
            'Scope': '范围',
            'Authentication key': '身份验证密钥',
            'Protocol': '协议',
            'Authentication type': '身份验证类型',
            'Ports': '端口号',
            'IP addresses': 'Ip地址',
            'Parent': '父级',
            'Account': '账户',
            'Installed': '已安装',
            'Terminates': '终止',
            'Commit Rate': '提交率',
            'Circuit ID': '电路ID',
            'Provider': '供应商',
            'Circuits': '电路',
            'Accounts': '账户',
            'Account Count': '账户数量',
            'Account ID': '账户ID',
            'Service ID': '服务ID',
            'Max utilization': '最大利用率',
            'Available power (VA)': '可用功率 (VA)',
            'Power panel': '电力面板',
            'Supply': '供电',
            'Voltage': '电压',
            'Amperage': '电流',
            'Phase': '相',
            'Feeds': '源',
            'Regions': '地区',
            'Locations': '地点',
            'Roles': '角色',
            'Cluster types': '集群类型',
            'Cluster groups': '集群组',
            'Clusters': '集群',
            'Tenant groups': '租户组',
            'Data source': '数据源',
            'Data file': '数据文件',
            'Data synced': '数据已同步',
            'Active': '活跃',
            'Synced': '同步',
            'Object Site': '对象站点',
            'Object Parent': '对象父级',
            'Installed module': '已安装模块',
            'Time': '时间'
        }

        for name, column in self.columns.items():
            if column.visible == visible and name not in self.exempt_columns:
                 if column.verbose_name in columnsMap:
                    columns.append((name, columnsMap[column.verbose_name]))
                 else:
                    columns.append((name, column.verbose_name))
        return columns

    @property
    def available_columns(self):
        return self._get_columns(visible=False)

    @property
    def selected_columns(self):
        return self._get_columns(visible=True)

    @property
    def objects_count(self):
        """
        Return the total number of real objects represented by the Table. This is useful when dealing with
        prefixes/IP addresses/etc., where some table rows may represent available address space.
        """
        if not hasattr(self, '_objects_count'):
            self._objects_count = sum(1 for obj in self.data if hasattr(obj, 'pk'))
        return self._objects_count

    def configure(self, request):
        """
        Configure the table for a specific request context. This performs pagination and records
        the user's preferred ordering logic.
        """
        # Save ordering preference
        if request.user.is_authenticated:
            table_name = self.__class__.__name__
            if self.prefixed_order_by_field in request.GET:
                if request.GET[self.prefixed_order_by_field]:
                    # If an ordering has been specified as a query parameter, save it as the
                    # user's preferred ordering for this table.
                    ordering = request.GET.getlist(self.prefixed_order_by_field)
                    request.user.config.set(f'tables.{table_name}.ordering', ordering, commit=True)
                else:
                    # If the ordering has been set to none (empty), clear any existing preference.
                    request.user.config.clear(f'tables.{table_name}.ordering', commit=True)
            elif ordering := request.user.config.get(f'tables.{table_name}.ordering'):
                # If no ordering has been specified, set the preferred ordering (if any).
                self.order_by = ordering

        # Paginate the table results
        paginate = {
            'paginator_class': EnhancedPaginator,
            'per_page': get_paginate_count(request)
        }
        tables.RequestConfig(request, paginate).configure(self)


class NetBoxTable(BaseTable):
    """
    Table class for most NetBox objects. Adds support for custom field & custom link columns. Includes
    default columns for:

        * PK (row selection)
        * ID
        * Actions
    """
    pk = columns.ToggleColumn(
        visible=False
    )
    id = tables.Column(
        linkify=True,
        verbose_name='ID'
    )
    actions = columns.ActionsColumn()

    exempt_columns = ('pk', 'actions')

    class Meta(BaseTable.Meta):
        pass

    def __init__(self, *args, extra_columns=None, **kwargs):
        if extra_columns is None:
            extra_columns = []

        # Add custom field & custom link columns
        content_type = ContentType.objects.get_for_model(self._meta.model)
        custom_fields = CustomField.objects.filter(
            content_types=content_type
        ).exclude(ui_visibility=CustomFieldVisibilityChoices.VISIBILITY_HIDDEN)

        extra_columns.extend([
            (f'cf_{cf.name}', columns.CustomFieldColumn(cf)) for cf in custom_fields
        ])
        custom_links = CustomLink.objects.filter(content_types=content_type, enabled=True)
        extra_columns.extend([
            (f'cl_{cl.name}', columns.CustomLinkColumn(cl)) for cl in custom_links
        ])

        super().__init__(*args, extra_columns=extra_columns, **kwargs)

    @property
    def htmx_url(self):
        """
        Return the base HTML request URL for embedded tables.
        """
        if getattr(self, 'embedded', False):
            viewname = get_viewname(self._meta.model, action='list')
            try:
                return reverse(viewname)
            except NoReverseMatch:
                pass
        return ''


class SearchTable(tables.Table):
    object_type = columns.ContentTypeColumn(
        verbose_name=_('Type'),
        order_by="object___meta__verbose_name",
    )
    object = tables.Column(
        linkify=True,
        order_by=('name', )
    )
    field = tables.Column()
    value = tables.Column()

    trim_length = 30

    class Meta:
        attrs = {
            'class': 'table table-hover object-list',
        }
        empty_text = _('No results found')

    def __init__(self, data, highlight=None, **kwargs):
        self.highlight = highlight
        super().__init__(data, **kwargs)

    def render_field(self, value, record):
        if hasattr(record.object, value):
            return title(record.object._meta.get_field(value).verbose_name)
        return value

    def render_value(self, value):
        if not self.highlight:
            return value

        value = highlight_string(value, self.highlight, trim_pre=self.trim_length, trim_post=self.trim_length)

        return mark_safe(value)
