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
                    'Longitude': '经度',
                    'Outer width': '宽度',
                    'Outer depth': '深度',
                    'Weight': '重量',
                    'Max weight': '最大重量',
                    'Facility ID': '设施ID',
                    'Serial number': '序列号',
                    'Asset tag': '资产标签',
                    'Mounting depth': '安装深度',
                    'Descending units': '降序单位',
                    'Weight unit': '重量单位',
                    'Title': '标题',
                    'Phone': '电话',
                    'Email': '电子邮件',
                    'Address': '地址',
                    'Link': '链接',
                    'Position': '位置',
                    'Priority': '优先级',
                    'NAPALM driver': 'NAPALM驱动',
                    'NAPALM arguments': 'NAPALM参数',
                    'Domain': '域',
                    'Identifier': '标识符',
                    'Comments': '评论',
                    'Model': '模型',
                    'Part number': '零件号',
                    'Is full depth': '全深度',
                    'Speed (Kbps)': '速度(Kbps)',
                    'MAC address': 'MAC地址',
                    'Transmit power (dBm)': '发射功率(dBm)',
                    'Channel frequency (MHz)': '信道频率(MHz)',
                    'Channel width (MHz)': '信道宽度(MHz)'
                }
                if field.label in labelMap:
                    fLabel = labelMap[field.label]
                else:
                    fLabel = field.label

                field.widget.attrs['placeholder'] = ''

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
