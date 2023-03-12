import string
from .models import Articles, Languages, Translations, TranlsationGroups, StaticInformation
import datetime
from django.db.models import Q
import json
from django.apps import apps
from django.core.paginator import Paginator
from django.http import JsonResponse, QueryDict
import re
from django.core.files.storage import default_storage
from main.models import ProductVariants

# get request.data in JSON
def serialize_request(model, request):
    langs = Languages.objects.filter(active=True)

    data_dict = {}

    for field in model._meta.fields:
        if field.name == 'id':
            continue

        field_dict = {}
        if str(field.get_internal_type()) == 'JSONField':
            for key in request.POST:
                key_split = str(key).split('#')
                if key_split[0] == str(field.name):
                    for lang in langs:
                        if key_split[-1] == lang.code:
                            field_dict[lang.code] = request.POST.get(key)
            data_dict[str(field.name)] = field_dict
        else:
            value = request.POST.get(str(field.name))
            if value and field.get_internal_type() != 'BooleanField':
                data_dict[str(field.name)] = value
            elif field.get_internal_type() == 'BooleanField':
                if field.name in request.POST:
                    data_dict[str(field.name)] = True
                elif field.name not in request.POST:
                    data_dict[str(field.name)] = False
            
    return data_dict


# search_paginate
def search_pagination(request):
    url = request.path + '?'

    if 'q=' in request.get_full_path():
        if '&' in request.get_full_path():
            url = request.get_full_path().split('&')[0] + '&'
        else:
            url = request.get_full_path() + '&'

    return url



# list to queryset
def list_to_queryset(model_list):
    if len(model_list) > 0:
        return model_list[0].__class__.objects.filter(
            pk__in=[obj.pk for obj in model_list])
    else:
        return []


# list of dicts to queryset
def list_of_dicts_to_queryset(list, model):
    if len(list) > 0:
        return model.objects.filter(id__in=[int(obj['id']) for obj in list])
    else:
        return []



# search translations
def search_translation(query, queryset, *args, **kwargs):
    langs = Languages.objects.all()
    endlist = []
    if query and query != '':
        query = query.lower()
        for item in queryset:
            for lang in langs:
                if query in str(item.value.get(lang.code, '')).lower() or query in str(item.key).lower() or query in str(item.group.sub_text + '.' + item.key).lower():
                    endlist.append(item)
                continue
    
        queryset = list_to_queryset(endlist)
    
    return queryset



# pagination
def paginate(queryset, request, number):
    paginator = Paginator(queryset, number)

    try:
        page_obj = paginator.get_page(request.GET.get("page"))
    except:
        page_obj = paginator.get_page(request.GET.get(1))

    return page_obj


# get lst data
def get_lst_data(queryset, request, number):
    lst_one = paginate(queryset, request, number)
    page = request.GET.get('page')

    if page is None or int(page) == 1:
        lst_two = range(1, number + 1)
    else:
        start = (int(page) - 1) * number + 1
        end = int(page) * number

        if end > len(queryset):
            end = len(queryset)

        lst_two = range(start, end + 1)


    return dict(pairs=zip(lst_one, lst_two))


# langs save
def lang_save(form, request):
    lang = form.save()
    key = request.POST.get('dropzone-key')
    sess_image = request.session.get(key)

    if sess_image:
        lang.icon = sess_image[0]['name']
        request.session[key].remove(sess_image[0])
        request.session.modified = True
        lang.save()

    if lang.default:
        for lng in Languages.objects.exclude(id=lang.id):
            lng.default = False
            lng.save()

    return lang




# is valid
def is_valid_field(data, field):
    lang = Languages.objects.filter(default=True).first()
    try:
        val = data.get(field, {}).get(lang.code, '')
    except:
        return False

    print(val == '')
    print('!!!!', val != '')

    return val != ''



# clean text
def clean_text(str):
    for char in string.punctuation:
        str = str.replace(char, ' ')

    return str.replace(' ', '')



# requeired field errors
def required_field_validate(fields: list, data):
    error = {}

    for field in fields:
        if field not in data:
            error[field] = 'This field is reuqired'

    return error


# get option from request
def get_option_from_post(i, req):
    print(req)
    langs = Languages.objects.filter(active=True)
    data_dict = {}
    for lang in langs:
        option = req.POST.get(f'option[{lang.code}][{i}]')
        data_dict[lang.code] = option

    return {'name': data_dict}


# collect options
def collect_options(nbm, req):
    end_data = []
    for i in range(1, nbm+1):
        data_dict = get_option_from_post(i, req)
        end_data.append(data_dict)

    return end_data


# get baners
def get_baner(key, id, request, def_data=None):
    langs = Languages.objects.filter(active=True)
    baner_data = {}

    if langs.exists():
        for lang in langs:
            images = [it for it in request.session.get(f'{key}_{lang.code}') if str(it['id']) == str(id)]
            if images:
                image = images[0]
                baner_data[lang.code] = image['name']

                request.session.get(f'{key}_{lang.code}').remove(image)
                request.session.modified = True
            elif def_data:
                baner_data[lang.code] = def_data.get(lang.code, '')

    return baner_data



# request itemto bool
def boolize(item):
    data = {'on': True, 'off': False}

    return data.get(item)



# serialize variant from request
def serialize_variant(i, l, request):
    exclude_list = ['product', 'images']
    fileds = [it for it in ProductVariants._meta.fields if it.name not in exclude_list]
    data_dict = {}

    for field in fileds:
        if field.get_internal_type() == 'BooleanField':
            val = request.POST.get(f'{field.name}[{i}][{l}]', 'off')
            data_dict[field.name] = boolize(val)
        else:
            val = request.POST.get(f'{field.name}[{i}][{l}]')
            data_dict[field.name] = val

    return data_dict
