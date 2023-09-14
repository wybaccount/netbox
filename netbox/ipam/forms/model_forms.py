from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from dcim.models import Device, Interface, Location, Rack, Region, Site, SiteGroup
from ipam.choices import *
from ipam.constants import *
from ipam.formfields import IPNetworkFormField
from ipam.models import *
from netbox.forms import NetBoxModelForm
from tenancy.forms import TenancyForm
from utilities.exceptions import PermissionsViolation
from utilities.forms import BootstrapMixin, add_blank_choice
from utilities.forms.fields import (
    CommentField, ContentTypeChoiceField, DynamicModelChoiceField, DynamicModelMultipleChoiceField, NumericArrayField,
    SlugField,
)
from utilities.forms.widgets import DatePicker
from virtualization.models import Cluster, ClusterGroup, VirtualMachine, VMInterface

__all__ = (
    'AggregateForm',
    'ASNForm',
    'ASNRangeForm',
    'FHRPGroupForm',
    'FHRPGroupAssignmentForm',
    'IPAddressAssignForm',
    'IPAddressBulkAddForm',
    'IPAddressForm',
    'IPRangeForm',
    'L2VPNForm',
    'L2VPNTerminationForm',
    'PrefixForm',
    'RIRForm',
    'RoleForm',
    'RouteTargetForm',
    'ServiceForm',
    'ServiceCreateForm',
    'ServiceTemplateForm',
    'VLANForm',
    'VLANGroupForm',
    'VRFForm',
)


class VRFForm(TenancyForm, NetBoxModelForm):
    import_targets = DynamicModelMultipleChoiceField(
        queryset=RouteTarget.objects.all(),
        required=False
    )
    export_targets = DynamicModelMultipleChoiceField(
        queryset=RouteTarget.objects.all(),
        required=False
    )
    comments = CommentField()

    fieldsets = (
        ('VRF', ('name', 'rd', 'enforce_unique', 'description', 'tags')),
        ('路由目标', ('import_targets', 'export_targets')),
        ('租用', ('tenant_group', 'tenant')),
    )

    class Meta:
        model = VRF
        fields = [
            'name', 'rd', 'enforce_unique', 'import_targets', 'export_targets', 'tenant_group', 'tenant', 'description',
            'comments', 'tags',
        ]
        labels = {
            'rd': "RD",
        }


class RouteTargetForm(TenancyForm, NetBoxModelForm):
    fieldsets = (
        ('路由目标', ('name', 'description', 'tags')),
        ('租用', ('tenant_group', 'tenant')),
    )
    comments = CommentField()

    class Meta:
        model = RouteTarget
        fields = [
            'name', 'tenant_group', 'tenant', 'description', 'comments', 'tags',
        ]


class RIRForm(NetBoxModelForm):
    slug = SlugField()

    fieldsets = (
        ('RIR', (
            'name', 'slug', 'is_private', 'description', 'tags',
        )),
    )

    class Meta:
        model = RIR
        fields = [
            'name', 'slug', 'is_private', 'description', 'tags',
        ]


class AggregateForm(TenancyForm, NetBoxModelForm):
    rir = DynamicModelChoiceField(
        queryset=RIR.objects.all(),
        label=_('RIR')
    )
    comments = CommentField()

    fieldsets = (
        ('聚合', ('prefix', 'rir', 'date_added', 'description', 'tags')),
        ('租用', ('tenant_group', 'tenant')),
    )

    class Meta:
        model = Aggregate
        fields = [
            'prefix', 'rir', 'date_added', 'tenant_group', 'tenant', 'description', 'comments', 'tags',
        ]
        widgets = {
            'date_added': DatePicker(),
        }


class ASNRangeForm(TenancyForm, NetBoxModelForm):
    rir = DynamicModelChoiceField(
        queryset=RIR.objects.all(),
        label=_('RIR'),
    )
    slug = SlugField()
    fieldsets = (
        ('ASN范围', ('name', 'slug', 'rir', 'start', 'end', 'description', 'tags')),
        ('租用', ('tenant_group', 'tenant')),
    )

    class Meta:
        model = ASNRange
        fields = [
            'name', 'slug', 'rir', 'start', 'end', 'tenant_group', 'tenant', 'description', 'tags'
        ]


class ASNForm(TenancyForm, NetBoxModelForm):
    rir = DynamicModelChoiceField(
        queryset=RIR.objects.all(),
        label=_('RIR'),
    )
    sites = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        label=_('Sites'),
        required=False
    )
    comments = CommentField()

    fieldsets = (
        ('ASN', ('asn', 'rir', 'sites', 'description', 'tags')),
        ('租用', ('tenant_group', 'tenant')),
    )

    class Meta:
        model = ASN
        fields = [
            'asn', 'rir', 'sites', 'tenant_group', 'tenant', 'description', 'comments', 'tags'
        ]
        widgets = {
            'date_added': DatePicker(),
        }

    def __init__(self, data=None, instance=None, *args, **kwargs):
        super().__init__(data=data, instance=instance, *args, **kwargs)

        if self.instance and self.instance.pk is not None:
            self.fields['sites'].initial = self.instance.sites.all().values_list('id', flat=True)

    def save(self, *args, **kwargs):
        instance = super().save(*args, **kwargs)
        instance.sites.set(self.cleaned_data['sites'])
        return instance


class RoleForm(NetBoxModelForm):
    slug = SlugField()

    fieldsets = (
        ('角色', (
            'name', 'slug', 'weight', 'description', 'tags',
        )),
    )

    class Meta:
        model = Role
        fields = [
            'name', 'slug', 'weight', 'description', 'tags',
        ]


class PrefixForm(TenancyForm, NetBoxModelForm):
    vrf = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label=_('VRF')
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        selector=True,
        null_option='None'
    )
    vlan = DynamicModelChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        selector=True,
        label=_('VLAN'),
    )
    role = DynamicModelChoiceField(
        queryset=Role.objects.all(),
        required=False
    )
    comments = CommentField()

    fieldsets = (
        ('前缀', ('prefix', 'status', 'vrf', 'role', 'is_pool', 'mark_utilized', 'description', 'tags')),
        ('站点/VLAN 分配', ('site', 'vlan')),
        ('租用', ('tenant_group', 'tenant')),
    )

    class Meta:
        model = Prefix
        fields = [
            'prefix', 'vrf', 'site', 'vlan', 'status', 'role', 'is_pool', 'mark_utilized', 'tenant_group', 'tenant',
            'description', 'comments', 'tags',
        ]


class IPRangeForm(TenancyForm, NetBoxModelForm):
    vrf = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label=_('VRF')
    )
    role = DynamicModelChoiceField(
        queryset=Role.objects.all(),
        required=False
    )
    comments = CommentField()

    fieldsets = (
        ('IP范围', ('vrf', 'start_address', 'end_address', 'role', 'status', 'mark_utilized', 'description', 'tags')),
        ('租用', ('tenant_group', 'tenant')),
    )

    class Meta:
        model = IPRange
        fields = [
            'vrf', 'start_address', 'end_address', 'status', 'role', 'tenant_group', 'tenant', 'mark_utilized',
            'description', 'comments', 'tags',
        ]


class IPAddressForm(TenancyForm, NetBoxModelForm):
    interface = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        selector=True,
    )
    vminterface = DynamicModelChoiceField(
        queryset=VMInterface.objects.all(),
        required=False,
        selector=True,
        label=_('Interface'),
    )
    fhrpgroup = DynamicModelChoiceField(
        queryset=FHRPGroup.objects.all(),
        required=False,
        selector=True,
        label=_('FHRP Group')
    )
    vrf = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label=_('VRF')
    )
    nat_inside = DynamicModelChoiceField(
        queryset=IPAddress.objects.all(),
        required=False,
        selector=True,
        label=_('IP Address'),
    )
    primary_for_parent = forms.BooleanField(
        required=False,
        label=_('将此设置为 设备/虚拟机 的主要 IP')
    )
    comments = CommentField()

    class Meta:
        model = IPAddress
        fields = [
            'address', 'vrf', 'status', 'role', 'dns_name', 'primary_for_parent', 'nat_inside', 'tenant_group',
            'tenant', 'description', 'comments', 'tags',
        ]

    def __init__(self, *args, **kwargs):

        # Initialize helper selectors
        instance = kwargs.get('instance')
        initial = kwargs.get('initial', {}).copy()
        if instance:
            if type(instance.assigned_object) is Interface:
                initial['interface'] = instance.assigned_object
            elif type(instance.assigned_object) is VMInterface:
                initial['vminterface'] = instance.assigned_object
            elif type(instance.assigned_object) is FHRPGroup:
                initial['fhrpgroup'] = instance.assigned_object
        kwargs['initial'] = initial

        super().__init__(*args, **kwargs)

        # Initialize primary_for_parent if IP address is already assigned
        if self.instance.pk and self.instance.assigned_object:
            parent = getattr(self.instance.assigned_object, 'parent_object', None)
            if parent and (
                self.instance.address.version == 4 and parent.primary_ip4_id == self.instance.pk or
                self.instance.address.version == 6 and parent.primary_ip6_id == self.instance.pk
            ):
                self.initial['primary_for_parent'] = True

        # Disable object assignment fields if the IP address is designated as primary
        if self.initial.get('primary_for_parent'):
            self.fields['interface'].disabled = True
            self.fields['vminterface'].disabled = True
            self.fields['fhrpgroup'].disabled = True

    def clean(self):
        super().clean()

        # Handle object assignment
        selected_objects = [
            field for field in ('interface', 'vminterface', 'fhrpgroup') if self.cleaned_data[field]
        ]
        if len(selected_objects) > 1:
            raise forms.ValidationError({
                selected_objects[1]: "An IP address can only be assigned to a single object."
            })
        elif selected_objects:
            assigned_object = self.cleaned_data[selected_objects[0]]
            if self.instance.pk and self.cleaned_data['primary_for_parent'] and assigned_object != self.instance.assigned_object:
                raise ValidationError(
                    "Cannot reassign IP address while it is designated as the primary IP for the parent object"
                )
            self.instance.assigned_object = assigned_object
        else:
            self.instance.assigned_object = None

        # Primary IP assignment is only available if an interface has been assigned.
        interface = self.cleaned_data.get('interface') or self.cleaned_data.get('vminterface')
        if self.cleaned_data.get('primary_for_parent') and not interface:
            self.add_error(
                'primary_for_parent', "Only IP addresses assigned to an interface can be designated as primary IPs."
            )

        # Do not allow assigning a network ID or broadcast address to an interface.
        if interface and (address := self.cleaned_data.get('address')):
            if address.ip == address.network:
                msg = f"{address} is a network ID, which may not be assigned to an interface."
                if address.version == 4 and address.prefixlen not in (31, 32):
                    raise ValidationError(msg)
                if address.version == 6 and address.prefixlen not in (127, 128):
                    raise ValidationError(msg)
            if address.version == 4 and address.ip == address.broadcast and address.prefixlen not in (31, 32):
                msg = f"{address} is a broadcast address, which may not be assigned to an interface."
                raise ValidationError(msg)

    def save(self, *args, **kwargs):
        ipaddress = super().save(*args, **kwargs)

        # Assign/clear this IPAddress as the primary for the associated Device/VirtualMachine.
        interface = self.instance.assigned_object
        if type(interface) in (Interface, VMInterface):
            parent = interface.parent_object
            if self.cleaned_data['primary_for_parent']:
                if ipaddress.address.version == 4:
                    parent.primary_ip4 = ipaddress
                else:
                    parent.primary_ip6 = ipaddress
                parent.save()
            elif ipaddress.address.version == 4 and parent.primary_ip4 == ipaddress:
                parent.primary_ip4 = None
                parent.save()
            elif ipaddress.address.version == 6 and parent.primary_ip6 == ipaddress:
                parent.primary_ip6 = None
                parent.save()

        return ipaddress


class IPAddressBulkAddForm(TenancyForm, NetBoxModelForm):
    vrf = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label=_('VRF')
    )

    class Meta:
        model = IPAddress
        fields = [
            'address', 'vrf', 'status', 'role', 'dns_name', 'description', 'tenant_group', 'tenant', 'tags',
        ]


class IPAddressAssignForm(BootstrapMixin, forms.Form):
    vrf_id = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label=_('VRF')
    )
    q = forms.CharField(
        required=False,
        label=_('Search'),
    )


class FHRPGroupForm(NetBoxModelForm):

    # Optionally create a new IPAddress along with the FHRPGroup
    ip_vrf = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label=_('VRF')
    )
    ip_address = IPNetworkFormField(
        required=False,
        label=_('Address')
    )
    ip_status = forms.ChoiceField(
        choices=add_blank_choice(IPAddressStatusChoices),
        required=False,
        label=_('Status')
    )
    comments = CommentField()

    fieldsets = (
        ('FHRP组', ('protocol', 'group_id', 'name', 'description', 'tags')),
        ('身份验证', ('auth_type', 'auth_key')),
        ('虚拟IP地址', ('ip_vrf', 'ip_address', 'ip_status'))
    )

    class Meta:
        model = FHRPGroup
        fields = (
            'protocol', 'group_id', 'auth_type', 'auth_key', 'name', 'ip_vrf', 'ip_address', 'ip_status', 'description',
            'comments', 'tags',
        )

    def save(self, *args, **kwargs):
        instance = super().save(*args, **kwargs)
        user = getattr(instance, '_user', None)  # Set under FHRPGroupEditView.alter_object()

        # Check if we need to create a new IPAddress for the group
        if self.cleaned_data.get('ip_address'):
            ipaddress = IPAddress(
                vrf=self.cleaned_data['ip_vrf'],
                address=self.cleaned_data['ip_address'],
                status=self.cleaned_data['ip_status'],
                role=FHRP_PROTOCOL_ROLE_MAPPINGS.get(self.cleaned_data['protocol'], IPAddressRoleChoices.ROLE_VIP),
                assigned_object=instance
            )
            ipaddress.populate_custom_field_defaults()
            ipaddress.save()

            # Check that the new IPAddress conforms with any assigned object-level permissions
            if not IPAddress.objects.restrict(user, 'add').filter(pk=ipaddress.pk).first():
                raise PermissionsViolation()

        return instance

    def clean(self):
        super().clean()

        ip_vrf = self.cleaned_data.get('ip_vrf')
        ip_address = self.cleaned_data.get('ip_address')
        ip_status = self.cleaned_data.get('ip_status')

        if ip_address:
            ip_form = IPAddressForm({
                'address': ip_address,
                'vrf': ip_vrf,
                'status': ip_status,
            })
            if not ip_form.is_valid():
                self.errors.update({
                    f'ip_{field}': error for field, error in ip_form.errors.items()
                })


class FHRPGroupAssignmentForm(BootstrapMixin, forms.ModelForm):
    group = DynamicModelChoiceField(
        queryset=FHRPGroup.objects.all()
    )

    class Meta:
        model = FHRPGroupAssignment
        fields = ('group', 'priority')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        ipaddresses = self.instance.interface.ip_addresses.all()
        for ipaddress in ipaddresses:
            self.fields['group'].widget.add_query_param('related_ip', ipaddress.pk)


class VLANGroupForm(NetBoxModelForm):
    scope_type = ContentTypeChoiceField(
        queryset=ContentType.objects.filter(model__in=VLANGROUP_SCOPE_TYPES),
        required=False
    )
    region = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        required=False,
        initial_params={
            'sites': '$site'
        }
    )
    sitegroup = DynamicModelChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        initial_params={
            'sites': '$site'
        },
        label=_('Site group')
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        initial_params={
            'locations': '$location'
        },
        query_params={
            'region_id': '$region',
            'group_id': '$sitegroup',
        }
    )
    location = DynamicModelChoiceField(
        queryset=Location.objects.all(),
        required=False,
        initial_params={
            'racks': '$rack'
        },
        query_params={
            'site_id': '$site',
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
    clustergroup = DynamicModelChoiceField(
        queryset=ClusterGroup.objects.all(),
        required=False,
        initial_params={
            'clusters': '$cluster'
        },
        label=_('Cluster group')
    )
    cluster = DynamicModelChoiceField(
        queryset=Cluster.objects.all(),
        required=False,
        query_params={
            'group_id': '$clustergroup',
        }
    )
    slug = SlugField()

    fieldsets = (
        ('VLAN组', ('name', 'slug', 'description', 'tags')),
        ('子虚拟局域网', ('min_vid', 'max_vid')),
        ('范围', ('scope_type', 'region', 'sitegroup', 'site', 'location', 'rack', 'clustergroup', 'cluster')),
    )

    class Meta:
        model = VLANGroup
        fields = [
            'name', 'slug', 'description', 'scope_type', 'region', 'sitegroup', 'site', 'location', 'rack',
            'clustergroup', 'cluster', 'min_vid', 'max_vid', 'tags',
        ]

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        initial = kwargs.get('initial', {})

        if instance is not None and instance.scope:
            initial[instance.scope_type.model] = instance.scope

            kwargs['initial'] = initial

        super().__init__(*args, **kwargs)

    def clean(self):
        super().clean()

        # Assign scope based on scope_type
        if self.cleaned_data.get('scope_type'):
            scope_field = self.cleaned_data['scope_type'].model
            self.instance.scope = self.cleaned_data.get(scope_field)
        else:
            self.instance.scope_id = None


class VLANForm(TenancyForm, NetBoxModelForm):
    group = DynamicModelChoiceField(
        queryset=VLANGroup.objects.all(),
        required=False,
        selector=True,
        label=_('VLAN Group')
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        null_option='None',
        selector=True
    )
    role = DynamicModelChoiceField(
        queryset=Role.objects.all(),
        required=False
    )
    comments = CommentField()

    class Meta:
        model = VLAN
        fields = [
            'site', 'group', 'vid', 'name', 'status', 'role', 'tenant_group', 'tenant', 'description', 'comments',
            'tags',
        ]


class ServiceTemplateForm(NetBoxModelForm):
    ports = NumericArrayField(
        base_field=forms.IntegerField(
            min_value=SERVICE_PORT_MIN,
            max_value=SERVICE_PORT_MAX
        ),
        help_text=_("Comma-separated list of one or more port numbers. A range may be specified using a hyphen.")
    )
    comments = CommentField()

    fieldsets = (
        ('服务模板', (
            'name', 'protocol', 'ports', 'description', 'tags',
        )),
    )

    class Meta:
        model = ServiceTemplate
        fields = ('name', 'protocol', 'ports', 'description', 'comments', 'tags')


class ServiceForm(NetBoxModelForm):
    device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        selector=True
    )
    virtual_machine = DynamicModelChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        selector=True
    )
    ports = NumericArrayField(
        base_field=forms.IntegerField(
            min_value=SERVICE_PORT_MIN,
            max_value=SERVICE_PORT_MAX
        ),
        help_text=_("Comma-separated list of one or more port numbers. A range may be specified using a hyphen.")
    )
    ipaddresses = DynamicModelMultipleChoiceField(
        queryset=IPAddress.objects.all(),
        required=False,
        label=_('IP Addresses'),
        query_params={
            'device_id': '$device',
            'virtual_machine_id': '$virtual_machine',
        }
    )
    comments = CommentField()

    class Meta:
        model = Service
        fields = [
            'device', 'virtual_machine', 'name', 'protocol', 'ports', 'ipaddresses', 'description', 'comments', 'tags',
        ]


class ServiceCreateForm(ServiceForm):
    service_template = DynamicModelChoiceField(
        queryset=ServiceTemplate.objects.all(),
        required=False
    )

    class Meta(ServiceForm.Meta):
        fields = [
            'device', 'virtual_machine', 'service_template', 'name', 'protocol', 'ports', 'ipaddresses', 'description',
            'tags',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Fields which may be populated from a ServiceTemplate are not required
        for field in ('name', 'protocol', 'ports'):
            self.fields[field].required = False
            del self.fields[field].widget.attrs['required']

    def clean(self):
        super().clean()
        if self.cleaned_data['service_template']:
            # Create a new Service from the specified template
            service_template = self.cleaned_data['service_template']
            self.cleaned_data['name'] = service_template.name
            self.cleaned_data['protocol'] = service_template.protocol
            self.cleaned_data['ports'] = service_template.ports
            if not self.cleaned_data['description']:
                self.cleaned_data['description'] = service_template.description
        elif not all(self.cleaned_data[f] for f in ('name', 'protocol', 'ports')):
            raise forms.ValidationError("Must specify name, protocol, and port(s) if not using a service template.")


#
# L2VPN
#


class L2VPNForm(TenancyForm, NetBoxModelForm):
    slug = SlugField()
    import_targets = DynamicModelMultipleChoiceField(
        queryset=RouteTarget.objects.all(),
        required=False
    )
    export_targets = DynamicModelMultipleChoiceField(
        queryset=RouteTarget.objects.all(),
        required=False
    )
    comments = CommentField()

    fieldsets = (
        ('L2VPN', ('name', 'slug', 'type', 'identifier', 'description', 'tags')),
        ('路由目标', ('import_targets', 'export_targets')),
        ('租用', ('tenant_group', 'tenant')),
    )

    class Meta:
        model = L2VPN
        fields = (
            'name', 'slug', 'type', 'identifier', 'import_targets', 'export_targets', 'tenant', 'description',
            'comments', 'tags'
        )


class L2VPNTerminationForm(NetBoxModelForm):
    l2vpn = DynamicModelChoiceField(
        queryset=L2VPN.objects.all(),
        required=True,
        query_params={},
        label=_('L2VPN'),
        fetch_trigger='open'
    )
    vlan = DynamicModelChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        selector=True,
        label=_('VLAN')
    )
    interface = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        selector=True
    )
    vminterface = DynamicModelChoiceField(
        queryset=VMInterface.objects.all(),
        required=False,
        selector=True,
        label=_('Interface')
    )

    class Meta:
        model = L2VPNTermination
        fields = ('l2vpn', )

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        initial = kwargs.get('initial', {}).copy()

        if instance:
            if type(instance.assigned_object) is Interface:
                initial['interface'] = instance.assigned_object
            elif type(instance.assigned_object) is VLAN:
                initial['vlan'] = instance.assigned_object
            elif type(instance.assigned_object) is VMInterface:
                initial['vminterface'] = instance.assigned_object
            kwargs['initial'] = initial

        super().__init__(*args, **kwargs)

    def clean(self):
        super().clean()

        interface = self.cleaned_data.get('interface')
        vminterface = self.cleaned_data.get('vminterface')
        vlan = self.cleaned_data.get('vlan')

        if not (interface or vminterface or vlan):
            raise ValidationError('A termination must specify an interface or VLAN.')
        if len([x for x in (interface, vminterface, vlan) if x]) > 1:
            raise ValidationError('A termination can only have one terminating object (an interface or VLAN).')

        self.instance.assigned_object = interface or vminterface or vlan
