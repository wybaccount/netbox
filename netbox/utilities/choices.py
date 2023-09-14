from django.conf import settings


class ChoiceSetMeta(type):
    """
    Metaclass for ChoiceSet
    """
    def __new__(mcs, name, bases, attrs):

        # Extend static choices with any configured choices
        if key := attrs.get('key'):
            assert type(attrs['CHOICES']) is list, f"{name} has a key defined but CHOICES is not a list"
            app = attrs['__module__'].split('.', 1)[0]
            replace_key = f'{app}.{key}'
            extend_key = f'{replace_key}+' if replace_key else None
            if replace_key and replace_key in settings.FIELD_CHOICES:
                # Replace the stock choices
                attrs['CHOICES'] = settings.FIELD_CHOICES[replace_key]
            elif extend_key and extend_key in settings.FIELD_CHOICES:
                # Extend the stock choices
                attrs['CHOICES'].extend(settings.FIELD_CHOICES[extend_key])

        # Define choice tuples and color maps
        attrs['_choices'] = []
        attrs['colors'] = {}
        for choice in attrs['CHOICES']:
            if isinstance(choice[1], (list, tuple)):
                grouped_choices = []
                for c in choice[1]:
                    grouped_choices.append((c[0], c[1]))
                    if len(c) == 3:
                        attrs['colors'][c[0]] = c[2]
                attrs['_choices'].append((choice[0], grouped_choices))
            else:
                attrs['_choices'].append((choice[0], choice[1]))
                if len(choice) == 3:
                    attrs['colors'][choice[0]] = choice[2]

        return super().__new__(mcs, name, bases, attrs)

    def __call__(cls, *args, **kwargs):
        # django-filters will check if a 'choices' value is callable, and if so assume that it returns an iterable
        return getattr(cls, '_choices', ())

    def __iter__(cls):
        return iter(getattr(cls, '_choices', ()))


class ChoiceSet(metaclass=ChoiceSetMeta):
    """
    Holds an iterable of choice tuples suitable for passing to a Django model or form field. Choices can be defined
    statically within the class as CHOICES and/or gleaned from the FIELD_CHOICES configuration parameter.
    """
    CHOICES = list()

    @classmethod
    def values(cls):
        return [c[0] for c in unpack_grouped_choices(cls._choices)]


def unpack_grouped_choices(choices):
    """
    Unpack a grouped choices hierarchy into a flat list of two-tuples. For example:

    choices = (
        ('Foo', (
            (1, 'A'),
            (2, 'B')
        )),
        ('Bar', (
            (3, 'C'),
            (4, 'D')
        ))
    )

    becomes:

    choices = (
        (1, 'A'),
        (2, 'B'),
        (3, 'C'),
        (4, 'D')
    )
    """
    unpacked_choices = []
    for key, value in choices:
        if isinstance(value, (list, tuple)):
            # Entered an optgroup
            for optgroup_key, optgroup_value in value:
                unpacked_choices.append((optgroup_key, optgroup_value))
        else:
            unpacked_choices.append((key, value))
    return unpacked_choices


#
# Generic color choices
#

class ColorChoices(ChoiceSet):
    COLOR_DARK_RED = 'aa1409'
    COLOR_RED = 'f44336'
    COLOR_PINK = 'e91e63'
    COLOR_ROSE = 'ffe4e1'
    COLOR_FUCHSIA = 'ff66ff'
    COLOR_PURPLE = '9c27b0'
    COLOR_DARK_PURPLE = '673ab7'
    COLOR_INDIGO = '3f51b5'
    COLOR_BLUE = '2196f3'
    COLOR_LIGHT_BLUE = '03a9f4'
    COLOR_CYAN = '00bcd4'
    COLOR_TEAL = '009688'
    COLOR_AQUA = '00ffff'
    COLOR_DARK_GREEN = '2f6a31'
    COLOR_GREEN = '4caf50'
    COLOR_LIGHT_GREEN = '8bc34a'
    COLOR_LIME = 'cddc39'
    COLOR_YELLOW = 'ffeb3b'
    COLOR_AMBER = 'ffc107'
    COLOR_ORANGE = 'ff9800'
    COLOR_DARK_ORANGE = 'ff5722'
    COLOR_BROWN = '795548'
    COLOR_LIGHT_GREY = 'c0c0c0'
    COLOR_GREY = '9e9e9e'
    COLOR_DARK_GREY = '607d8b'
    COLOR_BLACK = '111111'
    COLOR_WHITE = 'ffffff'

    CHOICES = (
        (COLOR_DARK_RED, '深红色'),
        (COLOR_RED, '红色'),
        (COLOR_PINK, '粉红色'),
        (COLOR_ROSE, '玫瑰色'),
        (COLOR_FUCHSIA, '紫红色'),
        (COLOR_PURPLE, '紫色'),
        (COLOR_DARK_PURPLE, '深紫色'),
        (COLOR_INDIGO, '蓝紫色'),
        (COLOR_BLUE, '蓝色'),
        (COLOR_LIGHT_BLUE, '浅蓝色'),
        (COLOR_CYAN, '蓝绿色'),
        (COLOR_TEAL, '蓝绿色'),
        (COLOR_AQUA, '水绿色'),
        (COLOR_DARK_GREEN, '深绿色'),
        (COLOR_GREEN, '绿色'),
        (COLOR_LIGHT_GREEN, '浅绿色'),
        (COLOR_LIME, '青柠色'),
        (COLOR_YELLOW, '黄色'),
        (COLOR_AMBER, '琥珀色'),
        (COLOR_ORANGE, '橙色'),
        (COLOR_DARK_ORANGE, '深橙色'),
        (COLOR_BROWN, '棕色'),
        (COLOR_LIGHT_GREY, '浅灰色'),
        (COLOR_GREY, '灰色'),
        (COLOR_DARK_GREY, '深灰色'),
        (COLOR_BLACK, '黑色'),
        (COLOR_WHITE, '白色'),
    )


#
# Button color choices
#

class ButtonColorChoices(ChoiceSet):
    """
    Map standard button color choices to Bootstrap 3 button classes
    """
    DEFAULT = 'outline-dark'
    BLUE = 'blue'
    INDIGO = 'indigo'
    PURPLE = 'purple'
    PINK = 'pink'
    RED = 'red'
    ORANGE = 'orange'
    YELLOW = 'yellow'
    GREEN = 'green'
    TEAL = 'teal'
    CYAN = 'cyan'
    GRAY = 'gray'
    GREY = 'gray'  # Backward compatability for <3.2
    BLACK = 'black'
    WHITE = 'white'

    CHOICES = (
        (DEFAULT, 'Default'),
        (BLUE, 'Blue'),
        (INDIGO, 'Indigo'),
        (PURPLE, 'Purple'),
        (PINK, 'Pink'),
        (RED, 'Red'),
        (ORANGE, 'Orange'),
        (YELLOW, 'Yellow'),
        (GREEN, 'Green'),
        (TEAL, 'Teal'),
        (CYAN, 'Cyan'),
        (GRAY, 'Gray'),
        (BLACK, 'Black'),
        (WHITE, 'White'),
    )


#
# Import Choices
#

class ImportMethodChoices(ChoiceSet):
    DIRECT = 'direct'
    UPLOAD = 'upload'
    DATA_FILE = 'datafile'

    CHOICES = [
        (DIRECT, 'Direct'),
        (UPLOAD, 'Upload'),
        (DATA_FILE, 'Data file'),
    ]


class ImportFormatChoices(ChoiceSet):
    AUTO = 'auto'
    CSV = 'csv'
    JSON = 'json'
    YAML = 'yaml'

    CHOICES = [
        (AUTO, '自动检测'),
        (CSV, 'CSV'),
        (JSON, 'JSON'),
        (YAML, 'YAML'),
    ]
