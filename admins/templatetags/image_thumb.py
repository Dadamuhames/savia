from django.template.defaulttags import register
from django.core.files.storage import default_storage
import os
from django.conf import settings
import json
from easy_thumbnails.templatetags.thumbnail import thumbnail_url, get_thumbnailer

@register.simple_tag
def image_thumb(image, **kwargs):
    alias_key = kwargs.get('alias')
    request = kwargs.get('request')

    alias = settings.THUMBNAIL_ALIASES.get('').get(alias_key)
    if alias is None:
        return None

    size = alias.get('size')
    url = None

    if image and default_storage.exists(image.path):
        orig_url = image.path.split('.')
        thb_url = '.'.join(orig_url) + f'.{size[0]}x{size[1]}_q85.{orig_url[-1]}'
        if default_storage.exists(thb_url):
            last_url = image.url.split('.')
            url = '.'.join(last_url) + f'.{size[0]}x{size[1]}_q85.{last_url[-1]}'
        else:
            url = get_thumbnailer(image)[alias_key].url
    else:
        return '/static/src/img/default.png'

    if url == '' or url is None:
        return None

    if request is not None:
        return request.build_absolute_uri(url)

    return url
