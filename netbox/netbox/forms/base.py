from django import forms
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.utils.translation import gettext as _

from extras.choices import CustomFieldFilterLogicChoices, CustomFieldTypeChoices, CustomFieldVisibilityChoices
from extras.forms.mixins import CustomFieldsMixin, SavedFiltersMixin
from extras.models import CustomField, Tag
from utilities.forms import BootstrapMixin, CSVModelForm
from utilities.forms.fields import CSVModelMultipleChoiceField, DynamicModelMultipleChoiceField

__all__ = (
    'NetBoxModelForm',
    'NetBoxModelImportForm',
    'NetBoxModelBulkEditForm',
    'NetBoxModelFilterSetForm',
)


class NetBoxModelForm(BootstrapMixin, CustomFieldsMixin, forms.ModelForm):
    """
    Base form for creating & editing NetBox models. Extends Django's ModelForm to add support for custom fields.

    Attributes:
        fieldsets: An iterable of two-tuples which define a heading and field set to display per section of
            the rendered form (optional). If not defined, the all fields will be rendered as a single section.
    """
    fieldsets = ()
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    def _get_content_type(self):
        return ContentType.objects.get_for_model(self._meta.model)

    def _get_form_field(self, customfield):
        if self.instance.pk:
            form_field = customfield.to_form_field(set_initial=False)
            form_field.initial = self.instance.custom_field_data.get(customfield.name, None)
            return form_field

        return customfield.to_form_field()

    def clean(self):

        # Save custom field data on instance
        for cf_name, customfield in self.custom_fields.items():
            if cf_name not in self.fields:
                # Custom fields may be absent when performing bulk updates via import
                continue
            key = cf_name[3:]  # Strip "cf_" from field name
            value = self.cleaned_data.get(cf_name)

            # Convert "empty" values to null
            if value in self.fields[cf_name].empty_values:
                self.instance.custom_field_data[key] = None
            else:
                self.instance.custom_field_data[key] = customfield.serialize(value)

        return super().clean()


class NetBoxModelImportForm(CSVModelForm, NetBoxModelForm):
    """
    Base form for creating a NetBox objects from CSV data. Used for bulk importing.
    """
    id = forms.IntegerField(
        required=False,
        help_text='要更新的现有对象的数字ID (若不创建新对象)'
    )
    tags = CSVModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        to_field_name='slug',
        help_text='用逗号分隔的标签别名，用双引号括起来 (例如 "标签1,标签2,标签3")'
    )

    def _get_custom_fields(self, content_type):
        return CustomField.objects.filter(content_types=content_type).filter(
            ui_visibility=CustomFieldVisibilityChoices.VISIBILITY_READ_WRITE
        )

    def _get_form_field(self, customfield):
        return customfield.to_form_field(for_csv_import=True)


class NetBoxModelBulkEditForm(BootstrapMixin, CustomFieldsMixin, forms.Form):
    """
    Base form for modifying multiple NetBox objects (of the same type) in bulk via the UI. Adds support for custom
    fields and adding/removing tags.

    Attributes:
        fieldsets: An iterable of two-tuples which define a heading and field set to display per section of
            the rendered form (optional). If not defined, the all fields will be rendered as a single section.
        nullable_fields: A list of field names indicating which fields support being set to null/empty
    """
    nullable_fields = ()

    pk = forms.ModelMultipleChoiceField(
        queryset=None,  # Set from self.model on init
        widget=forms.MultipleHiddenInput
    )
    add_tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )
    remove_tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['pk'].queryset = self.model.objects.all()

        self._extend_nullable_fields()

    def _get_form_field(self, customfield):
        return customfield.to_form_field(set_initial=False, enforce_required=False)

    def _extend_nullable_fields(self):
        nullable_custom_fields = [
            name for name, customfield in self.custom_fields.items() if (not customfield.required and customfield.ui_visibility == CustomFieldVisibilityChoices.VISIBILITY_READ_WRITE)
        ]
        self.nullable_fields = (*self.nullable_fields, *nullable_custom_fields)


class NetBoxModelFilterSetForm(BootstrapMixin, CustomFieldsMixin, SavedFiltersMixin, forms.Form):
    """
    Base form for FilerSet forms. These are used to filter object lists in the NetBox UI. Note that the
    corresponding FilterSet *must* provide a `q` filter.

    Attributes:
        model: The model class associated with the form
        fieldsets: An iterable of two-tuples which define a heading and field set to display per section of
            the rendered form (optional). If not defined, the all fields will be rendered as a single section.
    """
    q = forms.CharField(
        required=False,
        label=_('Search')
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Limit saved filters to those applicable to the form's model
        content_type = ContentType.objects.get_for_model(self.model)
        self.fields['filter_id'].widget.add_query_params({
            'content_type_id': content_type.pk,
        })

    def _get_custom_fields(self, content_type):
        return super()._get_custom_fields(content_type).exclude(
            Q(filter_logic=CustomFieldFilterLogicChoices.FILTER_DISABLED) |
            Q(type=CustomFieldTypeChoices.TYPE_JSON)
        )

    def _get_form_field(self, customfield):
        return customfield.to_form_field(set_initial=False, enforce_required=False, enforce_visibility=False)
