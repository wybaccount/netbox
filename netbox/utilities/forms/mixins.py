from django import forms

from .widgets import APISelect, APISelectMultiple, ClearableFileInput

__all__ = (
    'BootstrapMixin',
)


class BootstrapMixin:
    """
    Add the base Bootstrap CSS classes to form elements.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        exempt_widgets = [
            forms.FileInput,
            forms.RadioSelect,
            APISelect,
            APISelectMultiple,
            ClearableFileInput,
        ]

        for field_name, field in self.fields.items():
            css = field.widget.attrs.get('class', '')

            if field.widget.__class__ in exempt_widgets:
                continue

            elif isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = f'{css} form-check-input'

            elif isinstance(field.widget, forms.SelectMultiple) and 'size' in field.widget.attrs:
                # Use native Bootstrap class for multi-line <select> widgets
                field.widget.attrs['class'] = f'{css} form-select form-select-sm'

            elif isinstance(field.widget, (forms.Select, forms.SelectMultiple)):
                field.widget.attrs['class'] = f'{css} netbox-static-select'

            else:
                field.widget.attrs['class'] = f'{css} form-control'

            if field.required and not isinstance(field.widget, forms.FileInput):
                field.widget.attrs['required'] = 'required'

            # 表单placeholder
            if 'placeholder' not in field.widget.attrs and field.label is not None:
                fLabel = ''
                labelMap = {
                    'Search': '搜索',
                    'Name': '名称',
                    'Status': '状态',
                    'Facility': '设施',
                    'Description': '描述',
                    'Physical address': '物理地址',
                    'Shipping address': '邮寄地址',
                    'Latitude': '纬度',
                    'Longitude': '经度'
                }
                if field.label in labelMap:
                    fLabel = labelMap[field.label]
                else:
                    fLabel = field.label

                field.widget.attrs['placeholder'] = fLabel

    def is_valid(self):
        is_valid = super().is_valid()

        # Apply is-invalid CSS class to fields with errors
        if not is_valid:
            for field_name in self.errors:
                # Ignore e.g. __all__
                if field := self.fields.get(field_name):
                    css = field.widget.attrs.get('class', '')
                    field.widget.attrs['class'] = f'{css} is-invalid'

        return is_valid
