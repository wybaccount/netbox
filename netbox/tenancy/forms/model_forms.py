from django import forms

from netbox.forms import NetBoxModelForm
from tenancy.models import *
from utilities.forms import BootstrapMixin
from utilities.forms.fields import CommentField, DynamicModelChoiceField, SlugField

__all__ = (
    'ContactAssignmentForm',
    'ContactForm',
    'ContactGroupForm',
    'ContactRoleForm',
    'TenantForm',
    'TenantGroupForm',
)


#
# Tenants
#

class TenantGroupForm(NetBoxModelForm):
    parent = DynamicModelChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False
    )
    slug = SlugField()

    fieldsets = (
        ('租户组', (
            'parent', 'name', 'slug', 'description', 'tags',
        )),
    )

    class Meta:
        model = TenantGroup
        fields = [
            'parent', 'name', 'slug', 'description', 'tags',
        ]


class TenantForm(NetBoxModelForm):
    slug = SlugField()
    group = DynamicModelChoiceField(
        queryset=TenantGroup.objects.all(),
        required=False
    )
    comments = CommentField()

    fieldsets = (
        ('租户', ('name', 'slug', 'group', 'description', 'tags')),
    )

    class Meta:
        model = Tenant
        fields = (
            'name', 'slug', 'group', 'description', 'comments', 'tags',
        )


#
# Contacts
#

class ContactGroupForm(NetBoxModelForm):
    parent = DynamicModelChoiceField(
        queryset=ContactGroup.objects.all(),
        required=False
    )
    slug = SlugField()

    fieldsets = (
        ('联系人群组', (
            'parent', 'name', 'slug', 'description', 'tags',
        )),
    )

    class Meta:
        model = ContactGroup
        fields = ('parent', 'name', 'slug', 'description', 'tags')


class ContactRoleForm(NetBoxModelForm):
    slug = SlugField()

    fieldsets = (
        ('联系人角色', (
            'name', 'slug', 'description', 'tags',
        )),
    )

    class Meta:
        model = ContactRole
        fields = ('name', 'slug', 'description', 'tags')


class ContactForm(NetBoxModelForm):
    group = DynamicModelChoiceField(
        queryset=ContactGroup.objects.all(),
        required=False
    )
    comments = CommentField()

    fieldsets = (
        ('联系方式', ('group', 'name', 'title', 'phone', 'email', 'address', 'link', 'description', 'tags')),
    )

    class Meta:
        model = Contact
        fields = (
            'group', 'name', 'title', 'phone', 'email', 'address', 'link', 'description', 'comments', 'tags',
        )
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }


class ContactAssignmentForm(BootstrapMixin, forms.ModelForm):
    group = DynamicModelChoiceField(
        queryset=ContactGroup.objects.all(),
        required=False,
        initial_params={
            'contacts': '$contact'
        }
    )
    contact = DynamicModelChoiceField(
        queryset=Contact.objects.all(),
        query_params={
            'group_id': '$group'
        }
    )
    role = DynamicModelChoiceField(
        queryset=ContactRole.objects.all()
    )

    class Meta:
        model = ContactAssignment
        fields = (
            'content_type', 'object_id', 'group', 'contact', 'role', 'priority',
        )
        widgets = {
            'content_type': forms.HiddenInput(),
            'object_id': forms.HiddenInput(),
        }
