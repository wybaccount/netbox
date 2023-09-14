import decimal
import yaml

from functools import cached_property

from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import F, ProtectedError
from django.db.models.functions import Lower
from django.db.models.signals import post_save
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from dcim.choices import *
from dcim.constants import *
from extras.models import ConfigContextModel
from extras.querysets import ConfigContextModelQuerySet
from netbox.config import ConfigItem
from netbox.models import OrganizationalModel, PrimaryModel
from utilities.choices import ColorChoices
from utilities.fields import ColorField, NaturalOrderingField
from .device_components import *
from .mixins import WeightMixin


__all__ = (
    'Device',
    'DeviceRole',
    'DeviceType',
    'Manufacturer',
    'Module',
    'ModuleType',
    'Platform',
    'VirtualChassis',
    'VirtualDeviceContext',
)


#
# Device Types
#

class Manufacturer(OrganizationalModel):
    """
    A Manufacturer represents a company which produces hardware devices; for example, Juniper or Dell.
    """
    # Generic relations
    contacts = GenericRelation(
        to='tenancy.ContactAssignment'
    )

    def get_absolute_url(self):
        return reverse('dcim:manufacturer', args=[self.pk])


class DeviceType(PrimaryModel, WeightMixin):
    """
    A DeviceType represents a particular make (Manufacturer) and model of device. It specifies rack height and depth, as
    well as high-level functional role(s).

    Each DeviceType can have an arbitrary number of component templates assigned to it, which define console, power, and
    interface objects. For example, a Juniper EX4300-48T DeviceType would have:

      * 1 ConsolePortTemplate
      * 2 PowerPortTemplates
      * 48 InterfaceTemplates

    When a new Device of this type is created, the appropriate console, power, and interface objects (as defined by the
    DeviceType) are automatically created as well.
    """
    manufacturer = models.ForeignKey(
        to='dcim.Manufacturer',
        on_delete=models.PROTECT,
        related_name='device_types'
    )
    model = models.CharField(
        max_length=100
    )
    slug = models.SlugField(
        max_length=100
    )
    default_platform = models.ForeignKey(
        to='dcim.Platform',
        on_delete=models.SET_NULL,
        related_name='+',
        blank=True,
        null=True,
        verbose_name='Default platform'
    )
    part_number = models.CharField(
        max_length=50,
        blank=True,
        help_text=_('Discrete part number (optional)')
    )
    u_height = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=1.0,
        verbose_name='Height (U)'
    )
    is_full_depth = models.BooleanField(
        default=True,
        verbose_name='全深度',
        help_text=_('Device consumes both front and rear rack faces')
    )
    subdevice_role = models.CharField(
        max_length=50,
        choices=SubdeviceRoleChoices,
        blank=True,
        verbose_name='Parent/child status',
        help_text=_('Parent devices house child devices in device bays. Leave blank '
                    'if this device type is neither a parent nor a child.')
    )
    airflow = models.CharField(
        max_length=50,
        choices=DeviceAirflowChoices,
        blank=True
    )
    front_image = models.ImageField(
        upload_to='devicetype-images',
        blank=True
    )
    rear_image = models.ImageField(
        upload_to='devicetype-images',
        blank=True
    )

    images = GenericRelation(
        to='extras.ImageAttachment'
    )

    clone_fields = (
        'manufacturer', 'default_platform', 'u_height', 'is_full_depth', 'subdevice_role', 'airflow', 'weight', 'weight_unit'
    )
    prerequisite_models = (
        'dcim.Manufacturer',
    )

    class Meta:
        ordering = ['manufacturer', 'model']
        constraints = (
            models.UniqueConstraint(
                fields=('manufacturer', 'model'),
                name='%(app_label)s_%(class)s_unique_manufacturer_model'
            ),
            models.UniqueConstraint(
                fields=('manufacturer', 'slug'),
                name='%(app_label)s_%(class)s_unique_manufacturer_slug'
            ),
        )

    def __str__(self):
        return self.model

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Save a copy of u_height for validation in clean()
        self._original_u_height = self.u_height

        # Save references to the original front/rear images
        self._original_front_image = self.front_image
        self._original_rear_image = self.rear_image

    def get_absolute_url(self):
        return reverse('dcim:devicetype', args=[self.pk])

    @property
    def get_full_name(self):
        return f"{ self.manufacturer } { self.model }"

    def to_yaml(self):
        data = {
            'manufacturer': self.manufacturer.name,
            'model': self.model,
            'slug': self.slug,
            'default_platform': self.default_platform.name if self.default_platform else None,
            'part_number': self.part_number,
            'u_height': float(self.u_height),
            'is_full_depth': self.is_full_depth,
            'subdevice_role': self.subdevice_role,
            'airflow': self.airflow,
            'comments': self.comments,
            'weight': float(self.weight) if self.weight is not None else None,
            'weight_unit': self.weight_unit,
        }

        # Component templates
        if self.consoleporttemplates.exists():
            data['console-ports'] = [
                c.to_yaml() for c in self.consoleporttemplates.all()
            ]
        if self.consoleserverporttemplates.exists():
            data['console-server-ports'] = [
                c.to_yaml() for c in self.consoleserverporttemplates.all()
            ]
        if self.powerporttemplates.exists():
            data['power-ports'] = [
                c.to_yaml() for c in self.powerporttemplates.all()
            ]
        if self.poweroutlettemplates.exists():
            data['power-outlets'] = [
                c.to_yaml() for c in self.poweroutlettemplates.all()
            ]
        if self.interfacetemplates.exists():
            data['interfaces'] = [
                c.to_yaml() for c in self.interfacetemplates.all()
            ]
        if self.frontporttemplates.exists():
            data['front-ports'] = [
                c.to_yaml() for c in self.frontporttemplates.all()
            ]
        if self.rearporttemplates.exists():
            data['rear-ports'] = [
                c.to_yaml() for c in self.rearporttemplates.all()
            ]
        if self.modulebaytemplates.exists():
            data['module-bays'] = [
                c.to_yaml() for c in self.modulebaytemplates.all()
            ]
        if self.devicebaytemplates.exists():
            data['device-bays'] = [
                c.to_yaml() for c in self.devicebaytemplates.all()
            ]

        return yaml.dump(dict(data), sort_keys=False)

    def clean(self):
        super().clean()

        # U height must be divisible by 0.5
        if self.u_height % decimal.Decimal(0.5):
            raise ValidationError({
                'u_height': "U height must be in increments of 0.5 rack units."
            })

        # If editing an existing DeviceType to have a larger u_height, first validate that *all* instances of it have
        # room to expand within their racks. This validation will impose a very high performance penalty when there are
        # many instances to check, but increasing the u_height of a DeviceType should be a very rare occurrence.
        if self.pk and self.u_height > self._original_u_height:
            for d in Device.objects.filter(device_type=self, position__isnull=False):
                face_required = None if self.is_full_depth else d.face
                u_available = d.rack.get_available_units(
                    u_height=self.u_height,
                    rack_face=face_required,
                    exclude=[d.pk]
                )
                if d.position not in u_available:
                    raise ValidationError({
                        'u_height': "Device {} in rack {} does not have sufficient space to accommodate a height of "
                                    "{}U".format(d, d.rack, self.u_height)
                    })

        # If modifying the height of an existing DeviceType to 0U, check for any instances assigned to a rack position.
        elif self.pk and self._original_u_height > 0 and self.u_height == 0:
            racked_instance_count = Device.objects.filter(
                device_type=self,
                position__isnull=False
            ).count()
            if racked_instance_count:
                url = f"{reverse('dcim:device_list')}?manufactuer_id={self.manufacturer_id}&device_type_id={self.pk}"
                raise ValidationError({
                    'u_height': mark_safe(
                        f'Unable to set 0U height: Found <a href="{url}">{racked_instance_count} instances</a> already '
                        f'mounted within racks.'
                    )
                })

        if (
                self.subdevice_role != SubdeviceRoleChoices.ROLE_PARENT
        ) and self.pk and self.devicebaytemplates.count():
            raise ValidationError({
                'subdevice_role': "Must delete all device bay templates associated with this device before "
                                  "declassifying it as a parent device."
            })

        if self.u_height and self.subdevice_role == SubdeviceRoleChoices.ROLE_CHILD:
            raise ValidationError({
                'u_height': "Child device types must be 0U."
            })

    def save(self, *args, **kwargs):
        ret = super().save(*args, **kwargs)

        # Delete any previously uploaded image files that are no longer in use
        if self.front_image != self._original_front_image:
            self._original_front_image.delete(save=False)
        if self.rear_image != self._original_rear_image:
            self._original_rear_image.delete(save=False)

        return ret

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)

        # Delete any uploaded image files
        if self.front_image:
            self.front_image.delete(save=False)
        if self.rear_image:
            self.rear_image.delete(save=False)

    @property
    def is_parent_device(self):
        return self.subdevice_role == SubdeviceRoleChoices.ROLE_PARENT

    @property
    def is_child_device(self):
        return self.subdevice_role == SubdeviceRoleChoices.ROLE_CHILD


class ModuleType(PrimaryModel, WeightMixin):
    """
    A ModuleType represents a hardware element that can be installed within a device and which houses additional
    components; for example, a line card within a chassis-based switch such as the Cisco Catalyst 6500. Like a
    DeviceType, each ModuleType can have console, power, interface, and pass-through port templates assigned to it. It
    cannot, however house device bays or module bays.
    """
    manufacturer = models.ForeignKey(
        to='dcim.Manufacturer',
        on_delete=models.PROTECT,
        related_name='module_types'
    )
    model = models.CharField(
        max_length=100
    )
    part_number = models.CharField(
        max_length=50,
        blank=True,
        help_text=_('Discrete part number (optional)')
    )

    # Generic relations
    images = GenericRelation(
        to='extras.ImageAttachment'
    )

    clone_fields = ('manufacturer', 'weight', 'weight_unit',)
    prerequisite_models = (
        'dcim.Manufacturer',
    )

    class Meta:
        ordering = ('manufacturer', 'model')
        constraints = (
            models.UniqueConstraint(
                fields=('manufacturer', 'model'),
                name='%(app_label)s_%(class)s_unique_manufacturer_model'
            ),
        )

    def __str__(self):
        return self.model

    def get_absolute_url(self):
        return reverse('dcim:moduletype', args=[self.pk])

    def to_yaml(self):
        data = {
            'manufacturer': self.manufacturer.name,
            'model': self.model,
            'part_number': self.part_number,
            'comments': self.comments,
            'weight': float(self.weight) if self.weight is not None else None,
            'weight_unit': self.weight_unit,
        }

        # Component templates
        if self.consoleporttemplates.exists():
            data['console-ports'] = [
                c.to_yaml() for c in self.consoleporttemplates.all()
            ]
        if self.consoleserverporttemplates.exists():
            data['console-server-ports'] = [
                c.to_yaml() for c in self.consoleserverporttemplates.all()
            ]
        if self.powerporttemplates.exists():
            data['power-ports'] = [
                c.to_yaml() for c in self.powerporttemplates.all()
            ]
        if self.poweroutlettemplates.exists():
            data['power-outlets'] = [
                c.to_yaml() for c in self.poweroutlettemplates.all()
            ]
        if self.interfacetemplates.exists():
            data['interfaces'] = [
                c.to_yaml() for c in self.interfacetemplates.all()
            ]
        if self.frontporttemplates.exists():
            data['front-ports'] = [
                c.to_yaml() for c in self.frontporttemplates.all()
            ]
        if self.rearporttemplates.exists():
            data['rear-ports'] = [
                c.to_yaml() for c in self.rearporttemplates.all()
            ]

        return yaml.dump(dict(data), sort_keys=False)


#
# Devices
#

class DeviceRole(OrganizationalModel):
    """
    Devices are organized by functional role; for example, "Core Switch" or "File Server". Each DeviceRole is assigned a
    color to be used when displaying rack elevations. The vm_role field determines whether the role is applicable to
    virtual machines as well.
    """
    color = ColorField(
        default=ColorChoices.COLOR_GREY
    )
    vm_role = models.BooleanField(
        default=True,
        verbose_name='虚拟机角色',
        help_text=_('Virtual machines may be assigned to this role')
    )
    config_template = models.ForeignKey(
        to='extras.ConfigTemplate',
        on_delete=models.PROTECT,
        related_name='device_roles',
        blank=True,
        null=True
    )

    def get_absolute_url(self):
        return reverse('dcim:devicerole', args=[self.pk])


class Platform(OrganizationalModel):
    """
    Platform refers to the software or firmware running on a Device. For example, "Cisco IOS-XR" or "Juniper Junos".
    NetBox uses Platforms to determine how to interact with devices when pulling inventory data or other information by
    specifying a NAPALM driver.
    """
    manufacturer = models.ForeignKey(
        to='dcim.Manufacturer',
        on_delete=models.PROTECT,
        related_name='platforms',
        blank=True,
        null=True,
        help_text=_('Optionally limit this platform to devices of a certain manufacturer')
    )
    config_template = models.ForeignKey(
        to='extras.ConfigTemplate',
        on_delete=models.PROTECT,
        related_name='platforms',
        blank=True,
        null=True
    )
    napalm_driver = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='NAPALM driver',
        help_text=_('The name of the NAPALM driver to use when interacting with devices')
    )
    napalm_args = models.JSONField(
        blank=True,
        null=True,
        verbose_name='NAPALM arguments',
        help_text=_('Additional arguments to pass when initiating the NAPALM driver (JSON format)')
    )

    def get_absolute_url(self):
        return reverse('dcim:platform', args=[self.pk])


def update_interface_bridges(device, interface_templates, module=None):
    """
    Used for device and module instantiation. Iterates all InterfaceTemplates with a bridge assigned
    and applies it to the actual interfaces.
    """
    for interface_template in interface_templates.exclude(bridge=None):
        interface = Interface.objects.get(device=device, name=interface_template.resolve_name(module=module))

        if interface_template.bridge:
            interface.bridge = Interface.objects.get(device=device, name=interface_template.bridge.resolve_name(module=module))
            interface.full_clean()
            interface.save()


class Device(PrimaryModel, ConfigContextModel):
    """
    A Device represents a piece of physical hardware mounted within a Rack. Each Device is assigned a DeviceType,
    DeviceRole, and (optionally) a Platform. Device names are not required, however if one is set it must be unique.

    Each Device must be assigned to a site, and optionally to a rack within that site. Associating a device with a
    particular rack face or unit is optional (for example, vertically mounted PDUs do not consume rack units).

    When a new Device is created, console/power/interface/device bay components are created along with it as dictated
    by the component templates assigned to its DeviceType. Components can also be added, modified, or deleted after the
    creation of a Device.
    """
    device_type = models.ForeignKey(
        to='dcim.DeviceType',
        on_delete=models.PROTECT,
        related_name='instances'
    )
    device_role = models.ForeignKey(
        to='dcim.DeviceRole',
        on_delete=models.PROTECT,
        related_name='devices',
        help_text=_("The function this device serves")
    )
    tenant = models.ForeignKey(
        to='tenancy.Tenant',
        on_delete=models.PROTECT,
        related_name='devices',
        blank=True,
        null=True
    )
    platform = models.ForeignKey(
        to='dcim.Platform',
        on_delete=models.SET_NULL,
        related_name='devices',
        blank=True,
        null=True
    )
    name = models.CharField(
        max_length=64,
        blank=True,
        null=True
    )
    _name = NaturalOrderingField(
        target_field='name',
        max_length=100,
        blank=True,
        null=True
    )
    serial = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Serial number',
        help_text=_("Chassis serial number, assigned by the manufacturer")
    )
    asset_tag = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        unique=True,
        verbose_name='Asset tag',
        help_text=_('A unique tag used to identify this device')
    )
    site = models.ForeignKey(
        to='dcim.Site',
        on_delete=models.PROTECT,
        related_name='devices'
    )
    location = models.ForeignKey(
        to='dcim.Location',
        on_delete=models.PROTECT,
        related_name='devices',
        blank=True,
        null=True
    )
    rack = models.ForeignKey(
        to='dcim.Rack',
        on_delete=models.PROTECT,
        related_name='devices',
        blank=True,
        null=True
    )
    position = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        blank=True,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(RACK_U_HEIGHT_MAX + 0.5)],
        verbose_name='Position (U)',
        help_text=_('The lowest-numbered unit occupied by the device')
    )
    face = models.CharField(
        max_length=50,
        blank=True,
        choices=DeviceFaceChoices,
        verbose_name='Rack face'
    )
    status = models.CharField(
        max_length=50,
        choices=DeviceStatusChoices,
        default=DeviceStatusChoices.STATUS_ACTIVE
    )
    airflow = models.CharField(
        max_length=50,
        choices=DeviceAirflowChoices,
        blank=True
    )
    primary_ip4 = models.OneToOneField(
        to='ipam.IPAddress',
        on_delete=models.SET_NULL,
        related_name='+',
        blank=True,
        null=True,
        verbose_name='Primary IPv4'
    )
    primary_ip6 = models.OneToOneField(
        to='ipam.IPAddress',
        on_delete=models.SET_NULL,
        related_name='+',
        blank=True,
        null=True,
        verbose_name='Primary IPv6'
    )
    cluster = models.ForeignKey(
        to='virtualization.Cluster',
        on_delete=models.SET_NULL,
        related_name='devices',
        blank=True,
        null=True
    )
    virtual_chassis = models.ForeignKey(
        to='VirtualChassis',
        on_delete=models.SET_NULL,
        related_name='members',
        blank=True,
        null=True
    )
    vc_position = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=[MaxValueValidator(255)],
        help_text=_('Virtual chassis position')
    )
    vc_priority = models.PositiveSmallIntegerField(
        blank=True,
        null=True,
        validators=[MaxValueValidator(255)],
        help_text=_('Virtual chassis master election priority')
    )
    config_template = models.ForeignKey(
        to='extras.ConfigTemplate',
        on_delete=models.PROTECT,
        related_name='devices',
        blank=True,
        null=True
    )

    # Generic relations
    contacts = GenericRelation(
        to='tenancy.ContactAssignment'
    )
    images = GenericRelation(
        to='extras.ImageAttachment'
    )

    objects = ConfigContextModelQuerySet.as_manager()

    clone_fields = (
        'device_type', 'device_role', 'tenant', 'platform', 'site', 'location', 'rack', 'face', 'status', 'airflow',
        'cluster', 'virtual_chassis',
    )
    prerequisite_models = (
        'dcim.Site',
        'dcim.DeviceRole',
        'dcim.DeviceType',
    )

    class Meta:
        ordering = ('_name', 'pk')  # Name may be null
        constraints = (
            models.UniqueConstraint(
                Lower('name'), 'site', 'tenant',
                name='%(app_label)s_%(class)s_unique_name_site_tenant'
            ),
            models.UniqueConstraint(
                Lower('name'), 'site',
                name='%(app_label)s_%(class)s_unique_name_site',
                condition=Q(tenant__isnull=True),
                violation_error_message="Device name must be unique per site."
            ),
            models.UniqueConstraint(
                fields=('rack', 'position', 'face'),
                name='%(app_label)s_%(class)s_unique_rack_position_face'
            ),
            models.UniqueConstraint(
                fields=('virtual_chassis', 'vc_position'),
                name='%(app_label)s_%(class)s_unique_virtual_chassis_vc_position'
            ),
        )

    def __str__(self):
        if self.name and self.asset_tag:
            return f'{self.name} ({self.asset_tag})'
        elif self.name:
            return self.name
        elif self.virtual_chassis and self.asset_tag:
            return f'{self.virtual_chassis.name}:{self.vc_position} ({self.asset_tag})'
        elif self.virtual_chassis:
            return f'{self.virtual_chassis.name}:{self.vc_position} ({self.pk})'
        elif self.device_type and self.asset_tag:
            return f'{self.device_type.manufacturer} {self.device_type.model} ({self.asset_tag})'
        elif self.device_type:
            return f'{self.device_type.manufacturer} {self.device_type.model} ({self.pk})'
        return super().__str__()

    def get_absolute_url(self):
        return reverse('dcim:device', args=[self.pk])

    def clean(self):
        super().clean()

        # Validate site/location/rack combination
        if self.rack and self.site != self.rack.site:
            raise ValidationError({
                'rack': f"Rack {self.rack} does not belong to site {self.site}.",
            })
        if self.location and self.site != self.location.site:
            raise ValidationError({
                'location': f"Location {self.location} does not belong to site {self.site}.",
            })
        if self.rack and self.location and self.rack.location != self.location:
            raise ValidationError({
                'rack': f"Rack {self.rack} does not belong to location {self.location}.",
            })

        if self.rack is None:
            if self.face:
                raise ValidationError({
                    'face': "Cannot select a rack face without assigning a rack.",
                })
            if self.position:
                raise ValidationError({
                    'position': "Cannot select a rack position without assigning a rack.",
                })

        # Validate rack position and face
        if self.position and self.position % decimal.Decimal(0.5):
            raise ValidationError({
                'position': "Position must be in increments of 0.5 rack units."
            })
        if self.position and not self.face:
            raise ValidationError({
                'face': "Must specify rack face when defining rack position.",
            })

        # Prevent 0U devices from being assigned to a specific position
        if hasattr(self, 'device_type'):
            if self.position and self.device_type.u_height == 0:
                raise ValidationError({
                    'position': f"A U0 device type ({self.device_type}) cannot be assigned to a rack position."
                })

        if self.rack:

            try:
                # Child devices cannot be assigned to a rack face/unit
                if self.device_type.is_child_device and self.face:
                    raise ValidationError({
                        'face': "Child device types cannot be assigned to a rack face. This is an attribute of the "
                                "parent device."
                    })
                if self.device_type.is_child_device and self.position:
                    raise ValidationError({
                        'position': "Child device types cannot be assigned to a rack position. This is an attribute of "
                                    "the parent device."
                    })

                # Validate rack space
                rack_face = self.face if not self.device_type.is_full_depth else None
                exclude_list = [self.pk] if self.pk else []
                available_units = self.rack.get_available_units(
                    u_height=self.device_type.u_height, rack_face=rack_face, exclude=exclude_list
                )
                if self.position and self.position not in available_units:
                    raise ValidationError({
                        'position': f"U{self.position} is already occupied or does not have sufficient space to "
                                    f"accommodate this device type: {self.device_type} ({self.device_type.u_height}U)"
                    })

            except DeviceType.DoesNotExist:
                pass

        # Validate primary IP addresses
        vc_interfaces = self.vc_interfaces(if_master=False)
        if self.primary_ip4:
            if self.primary_ip4.family != 4:
                raise ValidationError({
                    'primary_ip4': f"{self.primary_ip4} is not an IPv4 address."
                })
            if self.primary_ip4.assigned_object in vc_interfaces:
                pass
            elif self.primary_ip4.nat_inside is not None and self.primary_ip4.nat_inside.assigned_object in vc_interfaces:
                pass
            else:
                raise ValidationError({
                    'primary_ip4': f"The specified IP address ({self.primary_ip4}) is not assigned to this device."
                })
        if self.primary_ip6:
            if self.primary_ip6.family != 6:
                raise ValidationError({
                    'primary_ip6': f"{self.primary_ip6} is not an IPv6 address."
                })
            if self.primary_ip6.assigned_object in vc_interfaces:
                pass
            elif self.primary_ip6.nat_inside is not None and self.primary_ip6.nat_inside.assigned_object in vc_interfaces:
                pass
            else:
                raise ValidationError({
                    'primary_ip6': f"The specified IP address ({self.primary_ip6}) is not assigned to this device."
                })

        # Validate manufacturer/platform
        if hasattr(self, 'device_type') and self.platform:
            if self.platform.manufacturer and self.platform.manufacturer != self.device_type.manufacturer:
                raise ValidationError({
                    'platform': f"The assigned platform is limited to {self.platform.manufacturer} device types, but "
                                f"this device's type belongs to {self.device_type.manufacturer}."
                })

        # A Device can only be assigned to a Cluster in the same Site (or no Site)
        if self.cluster and self.cluster.site is not None and self.cluster.site != self.site:
            raise ValidationError({
                'cluster': "The assigned cluster belongs to a different site ({})".format(self.cluster.site)
            })

        # Validate virtual chassis assignment
        if self.virtual_chassis and self.vc_position is None:
            raise ValidationError({
                'vc_position': "A device assigned to a virtual chassis must have its position defined."
            })

    def _instantiate_components(self, queryset, bulk_create=True):
        """
        Instantiate components for the device from the specified component templates.

        Args:
            bulk_create: If True, bulk_create() will be called to create all components in a single query
                         (default). Otherwise, save() will be called on each instance individually.
        """
        if bulk_create:
            components = [obj.instantiate(device=self) for obj in queryset]
            if not components:
                return
            model = components[0]._meta.model
            model.objects.bulk_create(components)
            # Manually send the post_save signal for each of the newly created components
            for component in components:
                post_save.send(
                    sender=model,
                    instance=component,
                    created=True,
                    raw=False,
                    using='default',
                    update_fields=None
                )
        else:
            for obj in queryset:
                component = obj.instantiate(device=self)
                component.save()

    def save(self, *args, **kwargs):
        is_new = not bool(self.pk)

        # Inherit airflow attribute from DeviceType if not set
        if is_new and not self.airflow:
            self.airflow = self.device_type.airflow

        # Inherit default_platform from DeviceType if not set
        if is_new and not self.platform:
            self.platform = self.device_type.default_platform

        # Inherit location from Rack if not set
        if self.rack and self.rack.location:
            self.location = self.rack.location

        super().save(*args, **kwargs)

        # If this is a new Device, instantiate all the related components per the DeviceType definition
        if is_new:
            self._instantiate_components(self.device_type.consoleporttemplates.all())
            self._instantiate_components(self.device_type.consoleserverporttemplates.all())
            self._instantiate_components(self.device_type.powerporttemplates.all())
            self._instantiate_components(self.device_type.poweroutlettemplates.all())
            self._instantiate_components(self.device_type.interfacetemplates.all())
            self._instantiate_components(self.device_type.rearporttemplates.all())
            self._instantiate_components(self.device_type.frontporttemplates.all())
            self._instantiate_components(self.device_type.modulebaytemplates.all())
            self._instantiate_components(self.device_type.devicebaytemplates.all())
            # Disable bulk_create to accommodate MPTT
            self._instantiate_components(self.device_type.inventoryitemtemplates.all(), bulk_create=False)
            # Interface bridges have to be set after interface instantiation
            update_interface_bridges(self, self.device_type.interfacetemplates.all())

        # Update Site and Rack assignment for any child Devices
        devices = Device.objects.filter(parent_bay__device=self)
        for device in devices:
            device.site = self.site
            device.rack = self.rack
            device.location = self.location
            device.save()

    @property
    def identifier(self):
        """
        Return the device name if set; otherwise return the Device's primary key as {pk}
        """
        if self.name is not None:
            return self.name
        return '{{{}}}'.format(self.pk)

    @property
    def primary_ip(self):
        if ConfigItem('PREFER_IPV4')() and self.primary_ip4:
            return self.primary_ip4
        elif self.primary_ip6:
            return self.primary_ip6
        elif self.primary_ip4:
            return self.primary_ip4
        else:
            return None

    @property
    def interfaces_count(self):
        return self.vc_interfaces().count()

    def get_config_template(self):
        """
        Return the appropriate ConfigTemplate (if any) for this Device.
        """
        if self.config_template:
            return self.config_template
        if self.device_role.config_template:
            return self.device_role.config_template
        if self.platform and self.platform.config_template:
            return self.platform.config_template

    def get_vc_master(self):
        """
        If this Device is a VirtualChassis member, return the VC master. Otherwise, return None.
        """
        return self.virtual_chassis.master if self.virtual_chassis else None

    def vc_interfaces(self, if_master=True):
        """
        Return a QuerySet matching all Interfaces assigned to this Device or, if this Device is a VC master, to another
        Device belonging to the same VirtualChassis.

        :param if_master: If True, return VC member interfaces only if this Device is the VC master.
        """
        filter = Q(device=self)
        if self.virtual_chassis and (self.virtual_chassis.master == self or not if_master):
            filter |= Q(device__virtual_chassis=self.virtual_chassis, mgmt_only=False)
        return Interface.objects.filter(filter)

    def get_cables(self, pk_list=False):
        """
        Return a QuerySet or PK list matching all Cables connected to a component of this Device.
        """
        from .cables import Cable
        cable_pks = []
        for component_model in [
            ConsolePort, ConsoleServerPort, PowerPort, PowerOutlet, Interface, FrontPort, RearPort
        ]:
            cable_pks += component_model.objects.filter(
                device=self, cable__isnull=False
            ).values_list('cable', flat=True)
        if pk_list:
            return cable_pks
        return Cable.objects.filter(pk__in=cable_pks)

    def get_children(self):
        """
        Return the set of child Devices installed in DeviceBays within this Device.
        """
        return Device.objects.filter(parent_bay__device=self.pk)

    def get_status_color(self):
        return DeviceStatusChoices.colors.get(self.status)

    @cached_property
    def total_weight(self):
        total_weight = sum(
            module.module_type._abs_weight
            for module in Module.objects.filter(device=self)
            .exclude(module_type___abs_weight__isnull=True)
            .prefetch_related('module_type')
        )
        if self.device_type._abs_weight:
            total_weight += self.device_type._abs_weight
        return round(total_weight / 1000, 2)


class Module(PrimaryModel, ConfigContextModel):
    """
    A Module represents a field-installable component within a Device which may itself hold multiple device components
    (for example, a line card within a chassis switch). Modules are instantiated from ModuleTypes.
    """
    device = models.ForeignKey(
        to='dcim.Device',
        on_delete=models.CASCADE,
        related_name='modules'
    )
    module_bay = models.OneToOneField(
        to='dcim.ModuleBay',
        on_delete=models.CASCADE,
        related_name='installed_module'
    )
    module_type = models.ForeignKey(
        to='dcim.ModuleType',
        on_delete=models.PROTECT,
        related_name='instances'
    )
    status = models.CharField(
        max_length=50,
        choices=ModuleStatusChoices,
        default=ModuleStatusChoices.STATUS_ACTIVE
    )
    serial = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Serial number'
    )
    asset_tag = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        unique=True,
        verbose_name='Asset tag',
        help_text=_('A unique tag used to identify this device')
    )

    clone_fields = ('device', 'module_type', 'status')

    class Meta:
        ordering = ('module_bay',)

    def __str__(self):
        return f'{self.module_bay.name}: {self.module_type} ({self.pk})'

    def get_absolute_url(self):
        return reverse('dcim:module', args=[self.pk])

    def get_status_color(self):
        return ModuleStatusChoices.colors.get(self.status)

    def clean(self):
        super().clean()

        if hasattr(self, "module_bay") and (self.module_bay.device != self.device):
            raise ValidationError(
                f"Module must be installed within a module bay belonging to the assigned device ({self.device})."
            )

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        super().save(*args, **kwargs)

        adopt_components = getattr(self, '_adopt_components', False)
        disable_replication = getattr(self, '_disable_replication', False)

        # We skip adding components if the module is being edited or
        # both replication and component adoption is disabled
        if not is_new or (disable_replication and not adopt_components):
            return

        # Iterate all component types
        for templates, component_attribute, component_model in [
            ("consoleporttemplates", "consoleports", ConsolePort),
            ("consoleserverporttemplates", "consoleserverports", ConsoleServerPort),
            ("interfacetemplates", "interfaces", Interface),
            ("powerporttemplates", "powerports", PowerPort),
            ("poweroutlettemplates", "poweroutlets", PowerOutlet),
            ("rearporttemplates", "rearports", RearPort),
            ("frontporttemplates", "frontports", FrontPort)
        ]:
            create_instances = []
            update_instances = []

            # Prefetch installed components
            installed_components = {
                component.name: component
                for component in getattr(self.device, component_attribute).filter(module__isnull=True)
            }

            # Get the template for the module type.
            for template in getattr(self.module_type, templates).all():
                template_instance = template.instantiate(device=self.device, module=self)

                if adopt_components:
                    existing_item = installed_components.get(template_instance.name)

                    # Check if there's a component with the same name already
                    if existing_item:
                        # Assign it to the module
                        existing_item.module = self
                        update_instances.append(existing_item)
                        continue

                # Only create new components if replication is enabled
                if not disable_replication:
                    create_instances.append(template_instance)

            component_model.objects.bulk_create(create_instances)
            # Emit the post_save signal for each newly created object
            for component in create_instances:
                post_save.send(
                    sender=component_model,
                    instance=component,
                    created=True,
                    raw=False,
                    using='default',
                    update_fields=None
                )

            update_fields = ['module']
            component_model.objects.bulk_update(update_instances, update_fields)
            # Emit the post_save signal for each updated object
            for component in update_instances:
                post_save.send(
                    sender=component_model,
                    instance=component,
                    created=False,
                    raw=False,
                    using='default',
                    update_fields=update_fields
                )

        # Interface bridges have to be set after interface instantiation
        update_interface_bridges(self.device, self.module_type.interfacetemplates, self)


#
# Virtual chassis
#

class VirtualChassis(PrimaryModel):
    """
    A collection of Devices which operate with a shared control plane (e.g. a switch stack).
    """
    master = models.OneToOneField(
        to='Device',
        on_delete=models.PROTECT,
        related_name='vc_master_for',
        blank=True,
        null=True
    )
    name = models.CharField(
        max_length=64
    )
    domain = models.CharField(
        max_length=30,
        blank=True
    )

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'virtual chassis'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('dcim:virtualchassis', kwargs={'pk': self.pk})

    def clean(self):
        super().clean()

        # Verify that the selected master device has been assigned to this VirtualChassis. (Skip when creating a new
        # VirtualChassis.)
        if self.pk and self.master and self.master not in self.members.all():
            raise ValidationError({
                'master': f"The selected master ({self.master}) is not assigned to this virtual chassis."
            })

    def delete(self, *args, **kwargs):

        # Check for LAG interfaces split across member chassis
        interfaces = Interface.objects.filter(
            device__in=self.members.all(),
            lag__isnull=False
        ).exclude(
            lag__device=F('device')
        )
        if interfaces:
            raise ProtectedError(
                f"Unable to delete virtual chassis {self}. There are member interfaces which form a cross-chassis LAG",
                interfaces
            )

        return super().delete(*args, **kwargs)


class VirtualDeviceContext(PrimaryModel):
    device = models.ForeignKey(
        to='Device',
        on_delete=models.PROTECT,
        related_name='vdcs',
        blank=True,
        null=True
    )
    name = models.CharField(
        max_length=64
    )
    status = models.CharField(
        max_length=50,
        choices=VirtualDeviceContextStatusChoices,
    )
    identifier = models.PositiveSmallIntegerField(
        help_text='Numeric identifier unique to the parent device',
        blank=True,
        null=True,
    )
    primary_ip4 = models.OneToOneField(
        to='ipam.IPAddress',
        on_delete=models.SET_NULL,
        related_name='+',
        blank=True,
        null=True,
        verbose_name='Primary IPv4'
    )
    primary_ip6 = models.OneToOneField(
        to='ipam.IPAddress',
        on_delete=models.SET_NULL,
        related_name='+',
        blank=True,
        null=True,
        verbose_name='Primary IPv6'
    )
    tenant = models.ForeignKey(
        to='tenancy.Tenant',
        on_delete=models.PROTECT,
        related_name='vdcs',
        blank=True,
        null=True
    )
    comments = models.TextField(
        blank=True
    )

    class Meta:
        ordering = ['name']
        constraints = (
            models.UniqueConstraint(
                fields=('device', 'identifier',),
                name='%(app_label)s_%(class)s_device_identifier'
            ),
            models.UniqueConstraint(
                fields=('device', 'name',),
                name='%(app_label)s_%(class)s_device_name'
            ),
        )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('dcim:virtualdevicecontext', kwargs={'pk': self.pk})

    def get_status_color(self):
        return VirtualDeviceContextStatusChoices.colors.get(self.status)

    @property
    def primary_ip(self):
        if ConfigItem('PREFER_IPV4')() and self.primary_ip4:
            return self.primary_ip4
        elif self.primary_ip6:
            return self.primary_ip6
        elif self.primary_ip4:
            return self.primary_ip4
        else:
            return None

    def clean(self):
        super().clean()

        # Validate primary IPv4/v6 assignment
        for primary_ip, family in ((self.primary_ip4, 4), (self.primary_ip6, 6)):
            if not primary_ip:
                continue
            if primary_ip.family != family:
                raise ValidationError({
                    f'primary_ip{family}': f"{primary_ip} is not an IPv{family} address."
                })
            device_interfaces = self.device.vc_interfaces(if_master=False)
            if primary_ip.assigned_object not in device_interfaces:
                raise ValidationError({
                    f'primary_ip{family}': _('Primary IP address must belong to an interface on the assigned device.')
                })
