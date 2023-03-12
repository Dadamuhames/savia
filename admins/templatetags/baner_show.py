from django.template.defaulttags import register
from django.core.files.storage import default_storage
import os
from django.conf import settings
import json
from easy_thumbnails.templatetags.thumbnail import thumbnail_url, get_thumbnailer


@register.simple_tag
def baner_thumb(image, **kwargs):
    alias_key = kwargs.get('alias')
    request = kwargs.get('request')

    alias = settings.THUMBNAIL_ALIASES.get('').get(alias_key)
    if alias is None:
        return None

    size = alias.get('size')
    url = None
    
    if image and default_storage.exists(image):
        open_url = default_storage.open(image).name
        orig_url = open_url.split('.')
        thb_url = '.'.join(orig_url) + f'.{size[0]}x{size[1]}_q85.{orig_url[-1]}'
        if default_storage.exists(thb_url):
            url = thb_url
        else:
            url = get_thumbnailer(open_url)[alias_key]
    else:
        return '/static/src/img/default.png'

    if url == '' or url is None:
        return None

    if request is not None:
        final_url = '/media/' + str(url).split('\media\\')[-1].replace('\\', "/") 
        return request.build_absolute_uri(final_url)

    return url
