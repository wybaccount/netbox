from django.utils.translation import gettext as _

from netbox.registry import registry
from . import *

#
# Nav menus
#

ORGANIZATION_MENU = Menu(
    label=_('组织'),
    icon_class='mdi mdi-domain',
    groups=(
        MenuGroup(
            label=_('站点'),
            items=(
                get_model_item('dcim', 'site', _('站点')),
                get_model_item('dcim', 'region', _('地区')),
                get_model_item('dcim', 'sitegroup', _('站点组')),
                get_model_item('dcim', 'location', _('地点')),
            ),
        ),
        MenuGroup(
            label=_('机架'),
            items=(
                get_model_item('dcim', 'rack', _('机架')),
                get_model_item('dcim', 'rackrole', _('机架角色')),
                get_model_item('dcim', 'rackreservation', _('预订')),
                MenuItem(
                    link='dcim:rack_elevation_list',
                    link_text=_('垂直布局'),
                    permissions=['dcim.view_rack']
                ),
            ),
        ),
        MenuGroup(
            label=_('租赁'),
            items=(
                get_model_item('tenancy', 'tenant', _('租户')),
                get_model_item('tenancy', 'tenantgroup', _('租户组')),
            ),
        ),
        MenuGroup(
            label=_('联系方式'),
            items=(
                get_model_item('tenancy', 'contact', _('联系方式')),
                get_model_item('tenancy', 'contactgroup', _('联系组')),
                get_model_item('tenancy', 'contactrole', _('联系角色')),
                get_model_item('tenancy', 'contactassignment', _('联系分配'), actions=[]),
            ),
        ),
    ),
)

DEVICES_MENU = Menu(
    label=_('设备'),
    icon_class='mdi mdi-server',
    groups=(
        MenuGroup(
            label=_('设备'),
            items=(
                get_model_item('dcim', 'device', _('设备')),
                get_model_item('dcim', 'module', _('模块')),
                get_model_item('dcim', 'devicerole', _('设备角色')),
                get_model_item('dcim', 'platform', _('平台')),
                get_model_item('dcim', 'virtualchassis', _('虚拟机箱')),
                get_model_item('dcim', 'virtualdevicecontext', _('虚拟设备上下文')),
            ),
        ),
        MenuGroup(
            label=_('设备类型'),
            items=(
                get_model_item('dcim', 'devicetype', _('设备类型')),
                get_model_item('dcim', 'moduletype', _('模块类型')),
                get_model_item('dcim', 'manufacturer', _('制造商')),
            ),
        ),
        MenuGroup(
            label=_('设备组件'),
            items=(
                get_model_item('dcim', 'interface', _('接口')),
                get_model_item('dcim', 'frontport', _('前端端口')),
                get_model_item('dcim', 'rearport', _('后端口')),
                get_model_item('dcim', 'consoleport', _('控制台端口')),
                get_model_item('dcim', 'consoleserverport', _('控制台服务器端口')),
                get_model_item('dcim', 'powerport', _('电源端口')),
                get_model_item('dcim', 'poweroutlet', _('电源插座')),
                get_model_item('dcim', 'modulebay', _('模块托架')),
                get_model_item('dcim', 'devicebay', _('设备托架')),
                get_model_item('dcim', 'inventoryitem', _('库存物品')),
                get_model_item('dcim', 'inventoryitemrole', _('库存项目角色')),
            ),
        ),
    ),
)

CONNECTIONS_MENU = Menu(
    label=_('连接'),
    icon_class='mdi mdi-connection',
    groups=(
        MenuGroup(
            label=_('连接'),
            items=(
                get_model_item('dcim', 'cable', _('电缆'), actions=['import']),
                get_model_item('wireless', 'wirelesslink', _('无线连接'), actions=['import']),
                MenuItem(
                    link='dcim:interface_connections_list',
                    link_text=_('接口连接'),
                    permissions=['dcim.view_interface']
                ),
                MenuItem(
                    link='dcim:console_connections_list',
                    link_text=_('控制台连接'),
                    permissions=['dcim.view_consoleport']
                ),
                MenuItem(
                    link='dcim:power_connections_list',
                    link_text=_('电源连接'),
                    permissions=['dcim.view_powerport']
                ),
            ),
        ),
    ),
)

# WIRELESS_MENU = Menu(
#     label=_('Wireless'),
#     icon_class='mdi mdi-wifi',
#     groups=(
#         MenuGroup(
#             label=_('Wireless'),
#             items=(
#                 get_model_item('wireless', 'wirelesslan', _('Wireless LANs')),
#                 get_model_item('wireless', 'wirelesslangroup', _('Wireless LAN Groups')),
#             ),
#         ),
#     ),
# )

IPAM_MENU = Menu(
    label=_('IP地址管理'),
    icon_class='mdi mdi-counter',
    groups=(
        MenuGroup(
            label=_('IP地址'),
            items=(
                get_model_item('ipam', 'ipaddress', _('IP地址')),
                get_model_item('ipam', 'iprange', _('IP范围')),
            ),
        ),
        MenuGroup(
            label=_('前缀'),
            items=(
                get_model_item('ipam', 'prefix', _('前缀')),
                get_model_item('ipam', 'role', _('前缀和VLAN角色')),
            ),
        ),
        MenuGroup(
            label=_('ASNs'),
            items=(
                get_model_item('ipam', 'asnrange', _('ASN范围')),
                get_model_item('ipam', 'asn', _('ASNs')),
            ),
        ),
        MenuGroup(
            label=_('聚合'),
            items=(
                get_model_item('ipam', 'aggregate', _('聚合')),
                get_model_item('ipam', 'rir', _('RIRs')),
            ),
        ),
        MenuGroup(
            label=_('VRFS'),
            items=(
                get_model_item('ipam', 'vrf', _('VRFs')),
                get_model_item('ipam', 'routetarget', _('路由目标')),
            ),
        ),
        MenuGroup(
            label=_('VLANS'),
            items=(
                get_model_item('ipam', 'vlan', _('VLANs')),
                get_model_item('ipam', 'vlangroup', _('VLAN Groups')),
            ),
        ),
        MenuGroup(
            label=_('其他'),
            items=(
                get_model_item('ipam', 'fhrpgroup', _('FHRP组')),
                get_model_item('ipam', 'servicetemplate', _('服务模板')),
                get_model_item('ipam', 'service', _('服务')),
            ),
        ),
    ),
)

OVERLAY_MENU = Menu(
    label=_('覆盖'),
    # label=_('Overlay'),
    icon_class='mdi mdi-graph-outline',
    groups=(
        MenuGroup(
            label='L2VPNs',
            items=(
                get_model_item('ipam', 'l2vpn', _('L2VPNs')),
                get_model_item('ipam', 'l2vpntermination', _('终端')),
                # get_model_item('ipam', 'l2vpntermination', _('Terminations')),
            ),
        ),
    ),
)

# VIRTUALIZATION_MENU = Menu(
#     label=_('Virtualization'),
#     icon_class='mdi mdi-monitor',
#     groups=(
#         MenuGroup(
#             label=_('Virtual Machines'),
#             items=(
#                 get_model_item('virtualization', 'virtualmachine', _('Virtual Machines')),
#                 get_model_item('virtualization', 'vminterface', _('Interfaces')),
#             ),
#         ),
#         MenuGroup(
#             label=_('Clusters'),
#             items=(
#                 get_model_item('virtualization', 'cluster', _('Clusters')),
#                 get_model_item('virtualization', 'clustertype', _('Cluster Types')),
#                 get_model_item('virtualization', 'clustergroup', _('Cluster Groups')),
#             ),
#         ),
#     ),
# )

CIRCUITS_MENU = Menu(
    label=_('电路'),
    icon_class='mdi mdi-transit-connection-variant',
    groups=(
        MenuGroup(
            label=_('电路'),
            items=(
                get_model_item('circuits', 'circuit', _('电路')),
                get_model_item('circuits', 'circuittype', _('电路类型')),
            ),
        ),
        MenuGroup(
            label=_('供应商'),
            items=(
                get_model_item('circuits', 'provider', _('供应商')),
                get_model_item('circuits', 'provideraccount', _('供应商账户')),
                get_model_item('circuits', 'providernetwork', _('供应商网络')),
            ),
        ),
    ),
)

POWER_MENU = Menu(
    label=_('电源'),
    icon_class='mdi mdi-flash',
    groups=(
        MenuGroup(
            label=_('电源'),
            items=(
                get_model_item('dcim', 'powerfeed', _('电源供应线路')),
                get_model_item('dcim', 'powerpanel', _('电源面板')),
            ),
        ),
    ),
)

PROVISIONING_MENU = Menu(
    label=_('配置'),
    icon_class='mdi mdi-file-document-multiple-outline',
    groups=(
        MenuGroup(
            label=_('配置'),
            items=(
                get_model_item('extras', 'configcontext', _('配置上下文'), actions=['add']),
                get_model_item('extras', 'configtemplate', _('配置模板'), actions=['add']),
            ),
        ),  
    ),
)

# CUSTOMIZATION_MENU = Menu(
#     label=_('Customization'),
#     icon_class='mdi mdi-toolbox-outline',
#     groups=(
#         MenuGroup(
#             label=_('Customization'),
#             items=(
#                 get_model_item('extras', 'customfield', _('Custom Fields')),
#                 get_model_item('extras', 'customlink', _('Custom Links')),
#                 get_model_item('extras', 'exporttemplate', _('Export Templates')),
#                 get_model_item('extras', 'savedfilter', _('Saved Filters')),
#                 get_model_item('extras', 'tag', 'Tags'),
#                 get_model_item('extras', 'imageattachment', _('Image Attachments'), actions=()),
#             ),
#         ),
#         MenuGroup(
#             label=_('Reports & Scripts'),
#             items=(
#                 MenuItem(
#                     link='extras:report_list',
#                     link_text=_('Reports'),
#                     permissions=['extras.view_report']
#                 ),
#                 MenuItem(
#                     link='extras:script_list',
#                     link_text=_('Scripts'),
#                     permissions=['extras.view_script']
#                 ),
#             ),
#         ),
#     ),
# )

OPERATIONS_MENU = Menu(
    label=_('Operations'),
    icon_class='mdi mdi-cogs',
    groups=(
        MenuGroup(
            label=_('Integrations'),
            items=(
                get_model_item('core', 'datasource', _('Data Sources')),
                get_model_item('extras', 'webhook', _('Webhooks')),
            ),
        ),
        MenuGroup(
            label=_('Jobs'),
            items=(
                MenuItem(
                    link='core:job_list',
                    link_text=_('Jobs'),
                    permissions=['core.view_job'],
                ),
            ),
        ),
        MenuGroup(
            label=_('Logging'),
            items=(
                get_model_item('extras', 'journalentry', _('Journal Entries'), actions=['import']),
                get_model_item('extras', 'objectchange', _('Change Log'), actions=[]),
            ),
        ),
    ),
)


MENUS = [
    ORGANIZATION_MENU,
    DEVICES_MENU,
    CONNECTIONS_MENU,
    # WIRELESS_MENU,
    IPAM_MENU,
    OVERLAY_MENU,
    # VIRTUALIZATION_MENU,
    CIRCUITS_MENU,
    POWER_MENU,
    PROVISIONING_MENU,
    # CUSTOMIZATION_MENU,
    # OPERATIONS_MENU,
]

#
# Add plugin menus
#

for menu in registry['plugins']['menus']:
    MENUS.append(menu)

if registry['plugins']['menu_items']:

    # Build the default plugins menu
    groups = [
        MenuGroup(label=label, items=items)
        for label, items in registry['plugins']['menu_items'].items()
    ]
    plugins_menu = Menu(
        label=_("Plugins"),
        icon_class="mdi mdi-puzzle",
        groups=groups
    )
    MENUS.append(plugins_menu)
