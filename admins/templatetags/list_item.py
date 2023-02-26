from django.template.defaulttags import register


@register.filter
def list_item(list, i):
    print(list)
    return list[int(i)]
