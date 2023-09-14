from django import forms
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext as _
from timezone_field import TimeZoneFormField

from dcim.choices import *
from dcim.constants import *
from dcim.models import *
from extras.models import ConfigTemplate
from ipam.models import ASN, IPAddress, VLAN, VLANGroup, VRF
from netbox.forms import NetBoxModelForm
from tenancy.forms import TenancyForm
from utilities.forms import BootstrapMixin, add_blank_choice
from utilities.forms.fields import (
    CommentField, ContentTypeChoiceField, DynamicModelChoiceField, DynamicModelMultipleChoiceField, JSONField,
    NumericArrayField, SlugField,
)
from utilities.forms.widgets import APISelect, ClearableFileInput, HTMXSelect, NumberWithOptions, SelectWithPK
from virtualization.models import Cluster
from wireless.models import WirelessLAN, WirelessLANGroup
from .common import InterfaceCommonForm, ModuleCommonForm

__all__ = (
    'CableForm',
    'ConsolePortForm',
    'ConsolePortTemplateForm',
    'ConsoleServerPortForm',
    'ConsoleServerPortTemplateForm',
    'DeviceBayForm',
    'DeviceBayTemplateForm',
    'DeviceForm',
    'DeviceRoleForm',
    'DeviceTypeForm',
    'DeviceVCMembershipForm',
    'FrontPortForm',
    'FrontPortTemplateForm',
    'InterfaceForm',
    'InterfaceTemplateForm',
    'InventoryItemForm',
    'InventoryItemRoleForm',
    'InventoryItemTemplateForm',
    'LocationForm',
    'ManufacturerForm',
    'ModuleForm',
    'ModuleBayForm',
    'ModuleBayTemplateForm',
    'ModuleTypeForm',
    'PlatformForm',
    'PopulateDeviceBayForm',
    'PowerFeedForm',
    'PowerOutletForm',
    'PowerOutletTemplateForm',
    'PowerPanelForm',
    'PowerPortForm',
    'PowerPortTemplateForm',
    'RackForm',
    'RackReservationForm',
    'RackRoleForm',
    'RearPortForm',
    'RearPortTemplateForm',
    'RegionForm',
    'SiteForm',
    'SiteGroupForm',
    'VCMemberSelectForm',
    'VirtualChassisForm',
    'VirtualDeviceContextForm'
)


class RegionForm(NetBoxModelForm):
    parent = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        required=False
    )
    slug = SlugField()

    fieldsets = (
        ('地区', (
            'parent', 'name', 'slug', 'description', 'tags',
        )),
    )

    class Meta:
        model = Region
        fields = (
            'parent', 'name', 'slug', 'description', 'tags',
        )


class SiteGroupForm(NetBoxModelForm):
    parent = DynamicModelChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False
    )
    slug = SlugField()

    fieldsets = (
        ('站点组', (
            'parent', 'name', 'slug', 'description', 'tags',
        )),
    )

    class Meta:
        model = SiteGroup
        fields = (
            'parent', 'name', 'slug', 'description', 'tags',
        )


class SiteForm(TenancyForm, NetBoxModelForm):
    region = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        required=False
    )
    group = DynamicModelChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False
    )
    asns = DynamicModelMultipleChoiceField(
        queryset=ASN.objects.all(),
        label=_('ASNs'),
        required=False
    )
    slug = SlugField()
    time_zone = TimeZoneFormField(
        choices=add_blank_choice(TimeZoneFormField().choices),
        required=False
    )
    comments = CommentField()

    fieldsets = (
        ('站点', (
            'name', 'slug', 'status', 'region', 'group', 'facility', 'asns', 'time_zone', 'description', 'tags',
        )),
        ('租赁', ('tenant_group', 'tenant')),
        ('联系方式', ('physical_address', 'shipping_address', 'latitude', 'longitude')),
    )

    class Meta:
        model = Site
        fields = (
            'name', 'slug', 'status', 'region', 'group', 'tenant_group', 'tenant', 'facility', 'asns', 'time_zone',
            'description', 'physical_address', 'shipping_address', 'latitude', 'longitude', 'comments', 'tags',
        )
        widgets = {
            'physical_address': forms.Textarea(
                attrs={
                    'rows': 3,
                }
            ),
            'shipping_address': forms.Textarea(
                attrs={
                    'rows': 3,
                }
            ),
        }


class LocationForm(TenancyForm, NetBoxModelForm):
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        selector=True
    )
    parent = DynamicModelChoiceField(
        queryset=Location.objects.all(),
        required=False,
        query_params={
            'site_id': '$site'
        }
    )
    slug = SlugField()

    fieldsets = (
        ('位置', ('site', 'parent', 'name', 'slug', 'status', 'description', 'tags')),
        ('租户', ('tenant_group', 'tenant')),
    )

    class Meta:
        model = Location
        fields = (
            'site', 'parent', 'name', 'slug', 'status', 'description', 'tenant_group', 'tenant', 'tags',
        )


class RackRoleForm(NetBoxModelForm):
    slug = SlugField()

    fieldsets = (
        ('机柜角色', (
            'name', 'slug', 'color', 'description', 'tags',
        )),
    )

    class Meta:
        model = RackRole
        fields = [
            'name', 'slug', 'color', 'description', 'tags',
        ]


class RackForm(TenancyForm, NetBoxModelForm):
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        selector=True
    )
    location = DynamicModelChoiceField(
        queryset=Location.objects.all(),
        required=False,
        query_params={
            'site_id': '$site'
        }
    )
    role = DynamicModelChoiceField(
        queryset=RackRole.objects.all(),
        required=False
    )
    comments = CommentField()

    class Meta:
        model = Rack
        fields = [
            'site', 'location', 'name', 'facility_id', 'tenant_group', 'tenant', 'status', 'role', 'serial',
            'asset_tag', 'type', 'width', 'u_height', 'desc_units', 'outer_width', 'outer_depth', 'outer_unit',
            'mounting_depth', 'weight', 'max_weight', 'weight_unit', 'description', 'comments', 'tags',
        ]


class RackReservationForm(TenancyForm, NetBoxModelForm):
    rack = DynamicModelChoiceField(
        queryset=Rack.objects.all(),
        selector=True
    )
    units = NumericArrayField(
        base_field=forms.IntegerField(),
        help_text=_("Comma-separated list of numeric unit IDs. A range may be specified using a hyphen.")
    )
    user = forms.ModelChoiceField(
        queryset=User.objects.order_by(
            'username'
        )
    )
    comments = CommentField()

    fieldsets = (
        ('预定', ('rack', 'units', 'user', 'description', 'tags')),
        ('租户', ('tenant_group', 'tenant')),
    )

    class Meta:
        model = RackReservation
        fields = [
            'rack', 'units', 'user', 'tenant_group', 'tenant', 'description', 'comments', 'tags',
        ]


class ManufacturerForm(NetBoxModelForm):
    slug = SlugField()

    fieldsets = (
        ('制造商', (
            'name', 'slug', 'description', 'tags',
        )),
    )

    class Meta:
        model = Manufacturer
        fields = [
            'name', 'slug', 'description', 'tags',
        ]


class DeviceTypeForm(NetBoxModelForm):
    manufacturer = DynamicModelChoiceField(
        queryset=Manufacturer.objects.all()
    )
    default_platform = DynamicModelChoiceField(
        queryset=Platform.objects.all(),
        required=False
    )
    slug = SlugField(
        slug_source='model'
    )
    comments = CommentField()

    fieldsets = (
        ('设备类型', ('manufacturer', 'model', 'slug', 'default_platform', 'description', 'tags')),
        ('机箱', (
            'u_height', 'is_full_depth', 'part_number', 'subdevice_role', 'airflow', 'weight', 'weight_unit',
        )),
        ('图片', ('front_image', 'rear_image')),
    )

    class Meta:
        model = DeviceType
        fields = [
            'manufacturer', 'model', 'slug', 'default_platform', 'part_number', 'u_height', 'is_full_depth',
            'subdevice_role', 'airflow', 'weight', 'weight_unit', 'front_image', 'rear_image', 'description',
            'comments', 'tags',
        ]
        widgets = {
            'front_image': ClearableFileInput(attrs={
                'accept': DEVICETYPE_IMAGE_FORMATS
            }),
            'rear_image': ClearableFileInput(attrs={
                'accept': DEVICETYPE_IMAGE_FORMATS
            }),
        }


class ModuleTypeForm(NetBoxModelForm):
    manufacturer = DynamicModelChoiceField(
        queryset=Manufacturer.objects.all()
    )
    comments = CommentField()

    fieldsets = (
        ('模块类型', ('manufacturer', 'model', 'part_number', 'description', 'tags')),
        ('重量', ('weight', 'weight_unit'))
    )

    class Meta:
        model = ModuleType
        fields = [
            'manufacturer', 'model', 'part_number', 'weight', 'weight_unit', 'description', 'comments', 'tags',
        ]


class DeviceRoleForm(NetBoxModelForm):
    config_template = DynamicModelChoiceField(
        queryset=ConfigTemplate.objects.all(),
        required=False
    )
    slug = SlugField()

    fieldsets = (
        ('设备角色', (
            'name', 'slug', 'color', 'vm_role', 'config_template', 'description', 'tags',
        )),
    )

    class Meta:
        model = DeviceRole
        fields = [
            'name', 'slug', 'color', 'vm_role', 'config_template', 'description', 'tags',
        ]


class PlatformForm(NetBoxModelForm):
    manufacturer = DynamicModelChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False
    )
    config_template = DynamicModelChoiceField(
        queryset=ConfigTemplate.objects.all(),
        required=False
    )
    slug = SlugField(
        max_length=64
    )

    fieldsets = (
        ('平台', (
            'name', 'slug', 'manufacturer', 'config_template', 'napalm_driver', 'napalm_args', 'description', 'tags',
        )),
    )

    class Meta:
        model = Platform
        fields = [
            'name', 'slug', 'manufacturer', 'config_template', 'napalm_driver', 'napalm_args', 'description', 'tags',
        ]
        widgets = {
            'napalm_args': forms.Textarea(),
        }


class DeviceForm(TenancyForm, NetBoxModelForm):
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        selector=True
    )
    location = DynamicModelChoiceField(
        queryset=Location.objects.all(),
        required=False,
        query_params={
            'site_id': '$site'
        },
        initial_params={
            'racks': '$rack'
        }
    )
    rack = DynamicModelChoiceField(
        queryset=Rack.objects.all(),
        required=False,
        query_params={
            'site_id': '$site',
            'location_id': '$location',
        }
    )
    position = forms.DecimalField(
        required=False,
        help_text=_("The lowest-numbered unit occupied by the device"),
        widget=APISelect(
            api_url='/api/dcim/racks/{{rack}}/elevation/',
            attrs={
                'disabled-indicator': 'device',
                'data-dynamic-params': '[{"fieldName":"face","queryParam":"face"}]'
            }
        )
    )
    device_type = DynamicModelChoiceField(
        queryset=DeviceType.objects.all(),
        selector=True
    )
    device_role = DynamicModelChoiceField(
        queryset=DeviceRole.objects.all()
    )
    platform = DynamicModelChoiceField(
        queryset=Platform.objects.all(),
        required=False
    )
    cluster = DynamicModelChoiceField(
        queryset=Cluster.objects.all(),
        required=False,
        selector=True
    )
    comments = CommentField()
    local_context_data = JSONField(
        required=False,
        label=''
    )
    virtual_chassis = DynamicModelChoiceField(
        queryset=VirtualChassis.objects.all(),
        required=False,
        selector=True
    )
    vc_position = forms.IntegerField(
        required=False,
        label=_('Position'),
        help_text=_("The position in the virtual chassis this device is identified by")
    )
    vc_priority = forms.IntegerField(
        required=False,
        label=_('Priority'),
        help_text=_("The priority of the device in the virtual chassis")
    )
    config_template = DynamicModelChoiceField(
        queryset=ConfigTemplate.objects.all(),
        required=False
    )

    class Meta:
        model = Device
        fields = [
            'name', 'device_role', 'device_type', 'serial', 'asset_tag', 'site', 'rack', 'location', 'position', 'face',
            'status', 'airflow', 'platform', 'primary_ip4', 'primary_ip6', 'cluster', 'tenant_group', 'tenant',
            'virtual_chassis', 'vc_position', 'vc_priority', 'description', 'config_template', 'comments', 'tags',
            'local_context_data'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:

            # Compile list of choices for primary IPv4 and IPv6 addresses
            for family in [4, 6]:
                ip_choices = [(None, '---------')]

                # Gather PKs of all interfaces belonging to this Device or a peer VirtualChassis member
                interface_ids = self.instance.vc_interfaces(if_master=False).values_list('pk', flat=True)

                # Collect interface IPs
                interface_ips = IPAddress.objects.filter(
                    address__family=family,
                    assigned_object_type=ContentType.objects.get_for_model(Interface),
                    assigned_object_id__in=interface_ids
                ).prefetch_related('assigned_object')
                if interface_ips:
                    ip_list = [(ip.id, f'{ip.address} ({ip.assigned_object})') for ip in interface_ips]
                    ip_choices.append(('Interface IPs', ip_list))
                # Collect NAT IPs
                nat_ips = IPAddress.objects.prefetch_related('nat_inside').filter(
                    address__family=family,
                    nat_inside__assigned_object_type=ContentType.objects.get_for_model(Interface),
                    nat_inside__assigned_object_id__in=interface_ids
                ).prefetch_related('assigned_object')
                if nat_ips:
                    ip_list = [(ip.id, f'{ip.address} (NAT)') for ip in nat_ips]
                    ip_choices.append(('NAT IPs', ip_list))
                self.fields['primary_ip{}'.format(family)].choices = ip_choices

            # If editing an existing device, exclude it from the list of occupied rack units. This ensures that a device
            # can be flipped from one face to another.
            self.fields['position'].widget.add_query_param('exclude', self.instance.pk)

            # Disable rack assignment if this is a child device installed in a parent device
            if self.instance.device_type.is_child_device and hasattr(self.instance, 'parent_bay'):
                self.fields['site'].disabled = True
                self.fields['rack'].disabled = True
                self.initial['site'] = self.instance.parent_bay.device.site_id
                self.initial['rack'] = self.instance.parent_bay.device.rack_id

        else:

            # An object that doesn't exist yet can't have any IPs assigned to it
            self.fields['primary_ip4'].choices = []
            self.fields['primary_ip4'].widget.attrs['readonly'] = True
            self.fields['primary_ip6'].choices = []
            self.fields['primary_ip6'].widget.attrs['readonly'] = True

        # Rack position
        position = self.data.get('position') or self.initial.get('position')
        if position:
            self.fields['position'].widget.choices = [(position, f'U{position}')]


class ModuleForm(ModuleCommonForm, NetBoxModelForm):
    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        initial_params={
            'modulebays': '$module_bay'
        }
    )
    module_bay = DynamicModelChoiceField(
        queryset=ModuleBay.objects.all(),
        query_params={
            'device_id': '$device'
        }
    )
    module_type = DynamicModelChoiceField(
        queryset=ModuleType.objects.all(),
        selector=True
    )
    comments = CommentField()
    replicate_components = forms.BooleanField(
        required=False,
        initial=True,
        help_text=_("Automatically populate components associated with this module type")
    )
    adopt_components = forms.BooleanField(
        required=False,
        initial=False,
        help_text=_("Adopt already existing components")
    )

    fieldsets = (
        ('模块', ('device', 'module_bay', 'module_type', 'status', 'description', 'tags')),
        ('硬件', (
            'serial', 'asset_tag', 'replicate_components', 'adopt_components',
        )),
    )

    class Meta:
        model = Module
        fields = [
            'device', 'module_bay', 'module_type', 'status', 'serial', 'asset_tag', 'tags', 'replicate_components',
            'adopt_components', 'description', 'comments',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            self.fields['device'].disabled = True
            self.fields['replicate_components'].initial = False
            self.fields['replicate_components'].disabled = True
            self.fields['adopt_components'].initial = False
            self.fields['adopt_components'].disabled = True


class CableForm(TenancyForm, NetBoxModelForm):
    comments = CommentField()

    class Meta:
        model = Cable
        fields = [
            'type', 'status', 'tenant_group', 'tenant', 'label', 'color', 'length', 'length_unit', 'description',
            'comments', 'tags',
        ]
        error_messages = {
            'length': {
                'max_value': 'Maximum length is 32767 (any unit)'
            }
        }


class PowerPanelForm(NetBoxModelForm):
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        selector=True
    )
    location = DynamicModelChoiceField(
        queryset=Location.objects.all(),
        required=False,
        query_params={
            'site_id': '$site'
        }
    )
    comments = CommentField()

    fieldsets = (
        ('电源面板', ('site', 'location', 'name', 'description', 'tags')),
    )

    class Meta:
        model = PowerPanel
        fields = [
            'site', 'location', 'name', 'description', 'comments', 'tags',
        ]


class PowerFeedForm(NetBoxModelForm):
    power_panel = DynamicModelChoiceField(
        queryset=PowerPanel.objects.all(),
        selector=True
    )
    rack = DynamicModelChoiceField(
        queryset=Rack.objects.all(),
        required=False,
        selector=True
    )
    comments = CommentField()

    fieldsets = (
        ('电源馈线', ('power_panel', 'rack', 'name', 'status', 'type', 'description', 'mark_connected', 'tags')),
        ('特征', ('supply', 'voltage', 'amperage', 'phase', 'max_utilization')),
    )

    class Meta:
        model = PowerFeed
        fields = [
            'power_panel', 'rack', 'name', 'status', 'type', 'mark_connected', 'supply', 'phase', 'voltage', 'amperage',
            'max_utilization', 'description', 'comments', 'tags',
        ]


#
# Virtual chassis
#

class VirtualChassisForm(NetBoxModelForm):
    master = forms.ModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
    )
    comments = CommentField()

    class Meta:
        model = VirtualChassis
        fields = [
            'name', 'domain', 'master', 'description', 'comments', 'tags',
        ]
        widgets = {
            'master': SelectWithPK(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['master'].queryset = Device.objects.filter(virtual_chassis=self.instance)


class DeviceVCMembershipForm(forms.ModelForm):
    class Meta:
        model = Device
        fields = [
            'vc_position', 'vc_priority',
        ]
        labels = {
            'vc_position': 'Position',
            'vc_priority': 'Priority',
        }

    def __init__(self, validate_vc_position=False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Require VC position (only required when the Device is a VirtualChassis member)
        self.fields['vc_position'].required = True

        # Add bootstrap classes to form elements.
        self.fields['vc_position'].widget.attrs = {'class': 'form-control'}
        self.fields['vc_priority'].widget.attrs = {'class': 'form-control'}

        # Validation of vc_position is optional. This is only required when adding a new member to an existing
        # VirtualChassis. Otherwise, vc_position validation is handled by BaseVCMemberFormSet.
        self.validate_vc_position = validate_vc_position

    def clean_vc_position(self):
        vc_position = self.cleaned_data['vc_position']

        if self.validate_vc_position:
            conflicting_members = Device.objects.filter(
                virtual_chassis=self.instance.virtual_chassis,
                vc_position=vc_position
            )
            if conflicting_members.exists():
                raise forms.ValidationError(
                    'A virtual chassis member already exists in position {}.'.format(vc_position)
                )

        return vc_position


class VCMemberSelectForm(BootstrapMixin, forms.Form):
    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        query_params={
            'virtual_chassis_id': 'null',
        },
        selector=True
    )

    def clean_device(self):
        device = self.cleaned_data['device']
        if device.virtual_chassis is not None:
            raise forms.ValidationError(
                f"Device {device} is already assigned to a virtual chassis."
            )
        return device


#
# Device component templates
#

class ComponentTemplateForm(BootstrapMixin, forms.ModelForm):
    device_type = DynamicModelChoiceField(
        queryset=DeviceType.objects.all()
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Disable reassignment of DeviceType when editing an existing instance
        if self.instance.pk:
            self.fields['device_type'].disabled = True


class ModularComponentTemplateForm(ComponentTemplateForm):
    device_type = DynamicModelChoiceField(
        queryset=DeviceType.objects.all().all(),
        required=False
    )
    module_type = DynamicModelChoiceField(
        queryset=ModuleType.objects.all(),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Disable reassignment of ModuleType when editing an existing instance
        if self.instance.pk:
            self.fields['module_type'].disabled = True


class ConsolePortTemplateForm(ModularComponentTemplateForm):
    fieldsets = (
        (None, ('device_type', 'module_type', 'name', 'label', 'type', 'description')),
    )

    class Meta:
        model = ConsolePortTemplate
        fields = [
            'device_type', 'module_type', 'name', 'label', 'type', 'description',
        ]


class ConsoleServerPortTemplateForm(ModularComponentTemplateForm):
    fieldsets = (
        (None, ('device_type', 'module_type', 'name', 'label', 'type', 'description')),
    )

    class Meta:
        model = ConsoleServerPortTemplate
        fields = [
            'device_type', 'module_type', 'name', 'label', 'type', 'description',
        ]


class PowerPortTemplateForm(ModularComponentTemplateForm):
    fieldsets = (
        (None, (
            'device_type', 'module_type', 'name', 'label', 'type', 'maximum_draw', 'allocated_draw', 'description',
        )),
    )

    class Meta:
        model = PowerPortTemplate
        fields = [
            'device_type', 'module_type', 'name', 'label', 'type', 'maximum_draw', 'allocated_draw', 'description',
        ]


class PowerOutletTemplateForm(ModularComponentTemplateForm):
    power_port = DynamicModelChoiceField(
        queryset=PowerPortTemplate.objects.all(),
        required=False,
        query_params={
            'devicetype_id': '$device_type',
        }
    )

    fieldsets = (
        (None, ('device_type', 'module_type', 'name', 'label', 'type', 'power_port', 'feed_leg', 'description')),
    )

    class Meta:
        model = PowerOutletTemplate
        fields = [
            'device_type', 'module_type', 'name', 'label', 'type', 'power_port', 'feed_leg', 'description',
        ]


class InterfaceTemplateForm(ModularComponentTemplateForm):
    bridge = DynamicModelChoiceField(
        queryset=InterfaceTemplate.objects.all(),
        required=False,
        query_params={
            'devicetype_id': '$device_type',
            'moduletype_id': '$module_type',
        }
    )

    fieldsets = (
        (None, ('device_type', 'module_type', 'name', 'label', 'type', 'enabled', 'mgmt_only', 'description', 'bridge')),
        ('PoE', ('poe_mode', 'poe_type'))
    )

    class Meta:
        model = InterfaceTemplate
        fields = [
            'device_type', 'module_type', 'name', 'label', 'type', 'mgmt_only', 'enabled', 'description', 'poe_mode', 'poe_type', 'bridge',
        ]


class FrontPortTemplateForm(ModularComponentTemplateForm):
    rear_port = DynamicModelChoiceField(
        queryset=RearPortTemplate.objects.all(),
        required=False,
        query_params={
            'devicetype_id': '$device_type',
            'moduletype_id': '$module_type',
        }
    )

    fieldsets = (
        (None, (
            'device_type', 'module_type', 'name', 'label', 'type', 'color', 'rear_port', 'rear_port_position',
            'description',
        )),
    )

    class Meta:
        model = FrontPortTemplate
        fields = [
            'device_type', 'module_type', 'name', 'label', 'type', 'color', 'rear_port', 'rear_port_position',
            'description',
        ]


class RearPortTemplateForm(ModularComponentTemplateForm):
    fieldsets = (
        (None, ('device_type', 'module_type', 'name', 'label', 'type', 'color', 'positions', 'description')),
    )

    class Meta:
        model = RearPortTemplate
        fields = [
            'device_type', 'module_type', 'name', 'label', 'type', 'color', 'positions', 'description',
        ]


class ModuleBayTemplateForm(ComponentTemplateForm):
    fieldsets = (
        (None, ('device_type', 'name', 'label', 'position', 'description')),
    )

    class Meta:
        model = ModuleBayTemplate
        fields = [
            'device_type', 'name', 'label', 'position', 'description',
        ]


class DeviceBayTemplateForm(ComponentTemplateForm):
    fieldsets = (
        (None, ('device_type', 'name', 'label', 'description')),
    )

    class Meta:
        model = DeviceBayTemplate
        fields = [
            'device_type', 'name', 'label', 'description',
        ]


class InventoryItemTemplateForm(ComponentTemplateForm):
    parent = DynamicModelChoiceField(
        queryset=InventoryItemTemplate.objects.all(),
        required=False,
        query_params={
            'devicetype_id': '$device_type'
        }
    )
    role = DynamicModelChoiceField(
        queryset=InventoryItemRole.objects.all(),
        required=False
    )
    manufacturer = DynamicModelChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False
    )
    component_type = ContentTypeChoiceField(
        queryset=ContentType.objects.all(),
        limit_choices_to=MODULAR_COMPONENT_TEMPLATE_MODELS,
        required=False,
        widget=forms.HiddenInput
    )
    component_id = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput
    )

    fieldsets = (
        (None, (
            'device_type', 'parent', 'name', 'label', 'role', 'manufacturer', 'part_id', 'description',
            'component_type', 'component_id',
        )),
    )

    class Meta:
        model = InventoryItemTemplate
        fields = [
            'device_type', 'parent', 'name', 'label', 'role', 'manufacturer', 'part_id', 'description',
            'component_type', 'component_id',
        ]


#
# Device components
#

class DeviceComponentForm(NetBoxModelForm):
    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        selector=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Disable reassignment of Device when editing an existing instance
        if self.instance.pk:
            self.fields['device'].disabled = True


class ModularDeviceComponentForm(DeviceComponentForm):
    module = DynamicModelChoiceField(
        queryset=Module.objects.all(),
        required=False,
        query_params={
            'device_id': '$device',
        }
    )


class ConsolePortForm(ModularDeviceComponentForm):
    fieldsets = (
        (None, (
            'device', 'module', 'name', 'label', 'type', 'speed', 'mark_connected', 'description', 'tags',
        )),
    )

    class Meta:
        model = ConsolePort
        fields = [
            'device', 'module', 'name', 'label', 'type', 'speed', 'mark_connected', 'description', 'tags',
        ]


class ConsoleServerPortForm(ModularDeviceComponentForm):

    fieldsets = (
        (None, (
            'device', 'module', 'name', 'label', 'type', 'speed', 'mark_connected', 'description', 'tags',
        )),
    )

    class Meta:
        model = ConsoleServerPort
        fields = [
            'device', 'module', 'name', 'label', 'type', 'speed', 'mark_connected', 'description', 'tags',
        ]


class PowerPortForm(ModularDeviceComponentForm):

    fieldsets = (
        (None, (
            'device', 'module', 'name', 'label', 'type', 'maximum_draw', 'allocated_draw', 'mark_connected',
            'description', 'tags',
        )),
    )

    class Meta:
        model = PowerPort
        fields = [
            'device', 'module', 'name', 'label', 'type', 'maximum_draw', 'allocated_draw', 'mark_connected',
            'description', 'tags',
        ]


class PowerOutletForm(ModularDeviceComponentForm):
    power_port = DynamicModelChoiceField(
        queryset=PowerPort.objects.all(),
        required=False,
        query_params={
            'device_id': '$device',
        }
    )

    fieldsets = (
        (None, (
            'device', 'module', 'name', 'label', 'type', 'power_port', 'feed_leg', 'mark_connected', 'description',
            'tags',
        )),
    )

    class Meta:
        model = PowerOutlet
        fields = [
            'device', 'module', 'name', 'label', 'type', 'power_port', 'feed_leg', 'mark_connected', 'description',
            'tags',
        ]


class InterfaceForm(InterfaceCommonForm, ModularDeviceComponentForm):
    vdcs = DynamicModelMultipleChoiceField(
        queryset=VirtualDeviceContext.objects.all(),
        required=False,
        label='Virtual Device Contexts',
        query_params={
            'device_id': '$device',
        }
    )
    parent = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        label=_('上级接口'),
        query_params={
            'device_id': '$device',
        }
    )
    bridge = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        label=_('Bridged interface'),
        query_params={
            'device_id': '$device',
        }
    )
    lag = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        label=_('LAG interface'),
        query_params={
            'device_id': '$device',
            'type': 'lag',
        }
    )
    wireless_lan_group = DynamicModelChoiceField(
        queryset=WirelessLANGroup.objects.all(),
        required=False,
        label=_('Wireless LAN group')
    )
    wireless_lans = DynamicModelMultipleChoiceField(
        queryset=WirelessLAN.objects.all(),
        required=False,
        label=_('Wireless LANs'),
        query_params={
            'group_id': '$wireless_lan_group',
        }
    )
    vlan_group = DynamicModelChoiceField(
        queryset=VLANGroup.objects.all(),
        required=False,
        label=_('VLAN group')
    )
    untagged_vlan = DynamicModelChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        label=_('Untagged VLAN'),
        query_params={
            'group_id': '$vlan_group',
            'available_on_device': '$device',
        }
    )
    tagged_vlans = DynamicModelMultipleChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        label=_('Tagged VLANs'),
        query_params={
            'group_id': '$vlan_group',
            'available_on_device': '$device',
        }
    )
    vrf = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label=_('VRF')
    )
    wwn = forms.CharField(
        empty_value=None,
        required=False,
        label=_('WWN')
    )

    fieldsets = (
        ('接口', ('device', 'module', 'name', 'label', 'type', 'speed', 'duplex', 'description', 'tags')),
        ('地址', ('vrf', 'mac_address', 'wwn')),
        ('操作', ('vdcs', 'mtu', 'tx_power', 'enabled', 'mgmt_only', 'mark_connected')),
        ('相关接口', ('parent', 'bridge', 'lag')),
        ('PoE', ('poe_mode', 'poe_type')),
        ('802.1Q 交换', ('mode', 'vlan_group', 'untagged_vlan', 'tagged_vlans')),
        ('无线', (
            'rf_role', 'rf_channel', 'rf_channel_frequency', 'rf_channel_width', 'wireless_lan_group', 'wireless_lans',
        )),
    )

    class Meta:
        model = Interface
        fields = [
            'device', 'module', 'vdcs', 'name', 'label', 'type', 'speed', 'duplex', 'enabled', 'parent', 'bridge', 'lag',
            'mac_address', 'wwn', 'mtu', 'mgmt_only', 'mark_connected', 'description', 'poe_mode', 'poe_type', 'mode',
            'rf_role', 'rf_channel', 'rf_channel_frequency', 'rf_channel_width', 'tx_power', 'wireless_lans',
            'untagged_vlan', 'tagged_vlans', 'vrf', 'tags',
        ]
        widgets = {
            'speed': NumberWithOptions(
                options=InterfaceSpeedChoices
            ),
            'mode': HTMXSelect(),
        }
        labels = {
            'mode': '802.1Q Mode',
        }


class FrontPortForm(ModularDeviceComponentForm):
    rear_port = DynamicModelChoiceField(
        queryset=RearPort.objects.all(),
        query_params={
            'device_id': '$device',
        }
    )

    fieldsets = (
        (None, (
            'device', 'module', 'name', 'label', 'type', 'color', 'rear_port', 'rear_port_position', 'mark_connected',
            'description', 'tags',
        )),
    )

    class Meta:
        model = FrontPort
        fields = [
            'device', 'module', 'name', 'label', 'type', 'color', 'rear_port', 'rear_port_position', 'mark_connected',
            'description', 'tags',
        ]


class RearPortForm(ModularDeviceComponentForm):
    fieldsets = (
        (None, (
            'device', 'module', 'name', 'label', 'type', 'color', 'positions', 'mark_connected', 'description', 'tags',
        )),
    )

    class Meta:
        model = RearPort
        fields = [
            'device', 'module', 'name', 'label', 'type', 'color', 'positions', 'mark_connected', 'description', 'tags',
        ]


class ModuleBayForm(DeviceComponentForm):
    fieldsets = (
        (None, ('device', 'name', 'label', 'position', 'description', 'tags',)),
    )

    class Meta:
        model = ModuleBay
        fields = [
            'device', 'name', 'label', 'position', 'description', 'tags',
        ]


class DeviceBayForm(DeviceComponentForm):
    fieldsets = (
        (None, ('device', 'name', 'label', 'description', 'tags',)),
    )

    class Meta:
        model = DeviceBay
        fields = [
            'device', 'name', 'label', 'description', 'tags',
        ]


class PopulateDeviceBayForm(BootstrapMixin, forms.Form):
    installed_device = forms.ModelChoiceField(
        queryset=Device.objects.all(),
        label=_('Child Device'),
        help_text=_("Child devices must first be created and assigned to the site and rack of the parent device.")
    )

    def __init__(self, device_bay, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['installed_device'].queryset = Device.objects.filter(
            site=device_bay.device.site,
            rack=device_bay.device.rack,
            parent_bay__isnull=True,
            device_type__u_height=0,
            device_type__subdevice_role=SubdeviceRoleChoices.ROLE_CHILD
        ).exclude(pk=device_bay.device.pk)


class InventoryItemForm(DeviceComponentForm):
    parent = DynamicModelChoiceField(
        queryset=InventoryItem.objects.all(),
        required=False,
        query_params={
            'device_id': '$device'
        }
    )
    role = DynamicModelChoiceField(
        queryset=InventoryItemRole.objects.all(),
        required=False
    )
    manufacturer = DynamicModelChoiceField(
        queryset=Manufacturer.objects.all(),
        required=False
    )

    # Assigned component selectors
    consoleport = DynamicModelChoiceField(
        queryset=ConsolePort.objects.all(),
        required=False,
        query_params={
            'device_id': '$device'
        },
        label=_('Console port')
    )
    consoleserverport = DynamicModelChoiceField(
        queryset=ConsoleServerPort.objects.all(),
        required=False,
        query_params={
            'device_id': '$device'
        },
        label=_('Console server port')
    )
    frontport = DynamicModelChoiceField(
        queryset=FrontPort.objects.all(),
        required=False,
        query_params={
            'device_id': '$device'
        },
        label=_('Front port')
    )
    interface = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        query_params={
            'device_id': '$device'
        },
        label=_('Interface')
    )
    poweroutlet = DynamicModelChoiceField(
        queryset=PowerOutlet.objects.all(),
        required=False,
        query_params={
            'device_id': '$device'
        },
        label=_('Power outlet')
    )
    powerport = DynamicModelChoiceField(
        queryset=PowerPort.objects.all(),
        required=False,
        query_params={
            'device_id': '$device'
        },
        label=_('Power port')
    )
    rearport = DynamicModelChoiceField(
        queryset=RearPort.objects.all(),
        required=False,
        query_params={
            'device_id': '$device'
        },
        label=_('Rear port')
    )

    fieldsets = (
        ('Inventory Item', ('device', 'parent', 'name', 'label', 'role', 'description', 'tags')),
        ('Hardware', ('manufacturer', 'part_id', 'serial', 'asset_tag')),
    )

    class Meta:
        model = InventoryItem
        fields = [
            'device', 'parent', 'name', 'label', 'role', 'manufacturer', 'part_id', 'serial', 'asset_tag',
            'description', 'tags',
        ]

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        initial = kwargs.get('initial', {}).copy()
        component_type = initial.get('component_type')
        component_id = initial.get('component_id')

        # Used for picking the default active tab for component selection
        self.no_component = True

        if instance:
            # When editing set the initial value for component selectin
            for component_model in ContentType.objects.filter(MODULAR_COMPONENT_MODELS):
                if type(instance.component) is component_model.model_class():
                    initial[component_model.model] = instance.component
                    self.no_component = False
                    break
        elif component_type and component_id:
            # When adding the InventoryItem from a component page
            if content_type := ContentType.objects.filter(MODULAR_COMPONENT_MODELS).filter(pk=component_type).first():
                if component := content_type.model_class().objects.filter(pk=component_id).first():
                    initial[content_type.model] = component
                    self.no_component = False

        kwargs['initial'] = initial

        super().__init__(*args, **kwargs)

        # Specifically allow editing the device of IntentoryItems
        if self.instance.pk:
            self.fields['device'].disabled = False

    def clean(self):
        super().clean()

        # Handle object assignment
        selected_objects = [
            field for field in (
                'consoleport', 'consoleserverport', 'frontport', 'interface', 'poweroutlet', 'powerport', 'rearport'
            ) if self.cleaned_data[field]
        ]
        if len(selected_objects) > 1:
            raise forms.ValidationError("An InventoryItem can only be assigned to a single component.")
        elif selected_objects:
            self.instance.component = self.cleaned_data[selected_objects[0]]
        else:
            self.instance.component = None


# Device component roles
#

class InventoryItemRoleForm(NetBoxModelForm):
    slug = SlugField()

    fieldsets = (
        ('库存项角色', (
            'name', 'slug', 'color', 'description', 'tags',
        )),
    )

    class Meta:
        model = InventoryItemRole
        fields = [
            'name', 'slug', 'color', 'description', 'tags',
        ]


class VirtualDeviceContextForm(TenancyForm, NetBoxModelForm):
    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        selector=True
    )
    primary_ip4 = DynamicModelChoiceField(
        queryset=IPAddress.objects.all(),
        label='Primary IPv4',
        required=False,
        query_params={
            'device_id': '$device',
            'family': '4',
        }
    )
    primary_ip6 = DynamicModelChoiceField(
        queryset=IPAddress.objects.all(),
        label='Primary IPv6',
        required=False,
        query_params={
            'device_id': '$device',
            'family': '6',
        }
    )

    fieldsets = (
        ('虚拟设备上下文', ('device', 'name', 'status', 'identifier', 'primary_ip4', 'primary_ip6', 'tags')),
        ('租户', ('tenant_group', 'tenant'))
    )

    class Meta:
        model = VirtualDeviceContext
        fields = [
            'device', 'name', 'status', 'identifier', 'primary_ip4', 'primary_ip6', 'tenant_group', 'tenant',
            'comments', 'tags'
        ]
