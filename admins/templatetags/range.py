from django.template.defaulttags import register



@register.filter(name='range')
def filter_range(number):
    return range(1, int(number) + 1)
