from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, FormView, TemplateView
from .models import Articles, Languages, Translations, TranlsationGroups, StaticInformation, ArticleCategories, FAQ
from .models import MetaTags, telephone_validator
from main.models import Products, Category, AtributOptions, Atributs, Colors, Baners, ProducVariantImages, CustomDesigns
from order.models import ShortApplication
from .forms import LngForm, UserForm  # , ApplicationForm
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.apps import apps
from django.http import JsonResponse, QueryDict, HttpResponseRedirect
from django.core.files.storage import default_storage
from .utils import *
from .serializers import TranslationSerializer
from django.contrib.auth.models import User
from django.contrib.auth import logout
import os
from django.conf import settings
from django.db import transaction
from main.serializers import CategorySimpleSerializer, AtributSerializer
# Create your views here.



# based list view
class BasedListView(ListView):
    search_fields = list()

    def search(self, queryset, fields: list, *args, **kwargs):
        query = self.request.GET.get("q", '')

        if query == '':
            return queryset

        end_set = set()
        for field in fields:
            qs = queryset.extra(where=[f'LOWER({field}) LIKE %s'], params=[f'%{query.lower()}%'])
            for item in qs:
                end_set.add(item)
    
        queryset = list_to_queryset(list(end_set))

        return queryset

    def get_queryset(self):
        queryset = self.model.objects.order_by('-id')
        queryset = self.search(queryset, self.search_fields)

        return queryset

    def get_context_data(self, **kwargs):
        context = super(BasedListView, self).get_context_data(**kwargs)

        context['objects'] = get_lst_data(
            self.get_queryset(), self.request, 20)
        context['lang'] = Languages.objects.filter(
            active=True).filter(default=True).first()
        context['page_obj'] = paginate(self.get_queryset(), self.request, 20)
        context['url'] = search_pagination(self.request)

        return context


# based create view
class BasedCreateView(CreateView):
    related_model = None
    fields = '__all__'
    image_field = None
    meta = False


    def get(self, request, *args, **kwargs):
        key = self.model._meta.verbose_name
        predelete_image([key], request, '')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(BasedCreateView, self).get_context_data(**kwargs)
        context['langs'] = Languages.objects.filter(active=True).order_by('-default')
        context['lang'] = Languages.objects.filter(default=True).first()

        if self.related_model is not None:
            context['relateds'] = self.related_model.objects.order_by('-id')

        context['dropzone_key'] = self.model._meta.verbose_name

        return context

    
    def get_request_data(self):
        data_dict = serialize_request(self.model, self.request)

        key = self.model._meta.verbose_name
        sess_images = self.request.session.get(key)

        if self.image_field:
            if sess_images and len([it for it in self.request.session.get(key) if it['id'] == '']) > 0:
                image = [it for it in self.request.session.get(key) if it['id'] == ''][0]

                data_dict[self.image_field]= image['name']
                self.request.session.get(key).remove(image)
                self.request.session.modified = True

        return data_dict

    
    def post(self, request, *args, **kwargs):
        context = super().post(request, *args, **kwargs)
        data_dict = self.get_request_data()
        data = self.get_context_data()

        try:
            article = self.model(**data_dict)
            article.full_clean()
            article = self.form_isvalid(article)
        except ValidationError as e:
            data['request_post'] = data_dict
            print(data)
            print(e.message_dict)
            return self.form_error(data, e.message_dict)

        return redirect(self.success_url)
    
    def form_valid(self, form):
        return None
    
    def form_invalid(self, form):
        return None

    def form_isvalid(self, form):
        form.save()
        if self.meta:
            meta_dict = serialize_request(MetaTags, self.request)
            try:
                meta = MetaTags(**meta_dict)
                meta.full_clean()
                meta.save()
                form.meta = meta
                form.save()
            except:
                pass

        return form


    def form_error(self, data, error):
        print(data)

        data['errors'] = error
        return render(self.request, self.template_name, context=data)

        #return super().form_invalid(form)


# based update view
class BasedUpdateView(UpdateView):
    related_model = None
    fields = '__all__'
    image_field = None
    meta = False

    def get(self, request, *args, **kwargs):
        key = self.model._meta.verbose_name
        obj = self.get_object()
        id = obj.id
        predelete_image([key], request, id)
        return super().get(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        context = super(BasedUpdateView, self).get_context_data(**kwargs)
        context['langs'] = Languages.objects.filter(
            active=True).order_by('-default')
        context['lang'] = Languages.objects.filter(default=True).first()
        if self.related_model is not None:
            context['relateds'] = self.related_model.objects.order_by('-id')
        context['dropzone_key'] = self.model._meta.verbose_name

        return context


    def get_request_data(self):
        data_dict = serialize_request(self.model, self.request)
        
        if self.image_field:
            key = self.model._meta.verbose_name
            try:
                file = [it for it in self.request.session.get(key, []) if it['id'] == str(self.get_object().id)][0]
            except:
                file = None

            if file:
                data_dict[self.image_field] = file['name']
                for it in self.request.session.get(key):
                    if it['id'] == str(self.get_object().pk):
                        self.request.session.get(key).remove(it)
                        self.request.session.modified = True

        print(data_dict)

        return data_dict

    def post(self, request, *args, **kwargs):
        context = super().post(request, *args, **kwargs)
        data_dict = self.get_request_data()
        data = self.get_context_data()
        instance = self.get_object()

        try:
            for attr, value in data_dict.items():
                setattr(instance, attr, value)
            instance.full_clean()
            instance = self.form_isvalid(instance)
        except ValidationError as e:
            data['request_post'] = data_dict
            print(data)
            print(e.message_dict)
            return self.form_error(data, e.message_dict)

        return redirect(self.success_url)


    def form_valid(self, form):
        return None

    def form_invalid(self, form):
        return None


    def form_isvalid(self, form):
        form.save()

        if self.meta:
            meta_dict = serialize_request(MetaTags, self.request)
            meta = form.meta
            if meta is None:
                meta = MetaTags.objects.create()
                form.meta = meta
                form.save()

            try:
                for attr, value in meta_dict.items():
                    setattr(form.meta, attr, value)
                form.meta.save()
            except:
                pass


        return form

    def form_error(self, data, error):
        data['errors'] = error
        return render(self.request, self.template_name, context=data)



# home admin
def home(request):
    return render(request, 'admin/base_template.html')


# delete model item
def delete_item(request):
    model_name = request.POST.get("model_name_del")
    app_name = request.POST.get('app_name_del')
    id = request.POST.get('item_id')
    url = request.POST.get("url")

    try:
        model = apps.get_model(model_name=model_name, app_label=app_name)
        model.objects.get(id=int(id)).delete()
    except:
        pass

    return redirect(url)


# save images
def save_images(request):
    if request.method == 'POST':
        key = request.POST.get("key")
        file = request.FILES.get('file')
        id = request.POST.get("id", '')

        
        for it in request.session.get(key, []):
            if it['id'] == str(id) and id != '':
                request.session.get(key).remove(it)
                request.session.modified = True


        request.session[key] = request.session.get(key, [])
        file_name = default_storage.save('dropzone/' + file.name, file)

        data = {
            'id': id,
            'name': file_name
        }

        request.session[key].append(data)
        request.session.modified = True

    return JsonResponse(file_name, safe=False)


# del lang icond
def del_lang_icon(request):
    id = request.POST.get("item_id")
    url = request.POST.get('url')
    try:
        Languages.objects.get(id=int(id)).icon.delete()
    except:
        pass

    return redirect(url)


# delete article group image
def delete_article_group_img(request):
    id = request.POST.get('item_id')

    try:
        ArticleCategories.objects.get(id=int(id)).image.delete()
    except:
        return JsonResponse("error", safe=False)

    return JsonResponse('success', safe=False)


# add static image
def add_static_image(request):
    url = request.POST.get('url')
    key = request.POST.get("key")
    file = request.FILES.get('file')


    try:
        model = StaticInformation.objects.get(id=1)

        if key == 'logo1':
            model.logo_first = file
        elif key == 'logo2':
            model.logo_second = file

        model.save()
    except:
        pass

    return redirect(url)


# delete article images
def del_statics_image(request):
    url = request.POST.get('url')
    key = request.POST.get("key")

    try:
        model = StaticInformation.objects.get(id=1)

        if key == 'logo1':
            model.logo_first.delete()
        elif key == 'logo2':
            model.logo_second.delete()
        elif key == 'cotalog':
            model.cotalog.delete()

        model.save()
    except:
        pass

    return redirect(url)


# delete image
def delete_image(request):
    if request.method == 'POST':
        key = request.POST.get('key')
        file = request.POST.get("file")

        if request.session.get(key):
            for it in list(request.session[key]):
                if it['name'] == file:
                    if default_storage.exists(it['name']):
                        default_storage.delete(it['name'])
                    request.session[key].remove(it)
                    request.session.modified = True

    return redirect(request.META.get("HTTP_REFERER"))

# langs list
class LangsList(ListView):
    model = Languages
    context_object_name = 'langs'
    template_name = 'admin/lang_list.html'

    def get_queryset(self):
        queryset = Languages.objects.all().order_by('-default')
        query = self.request.GET.get("q")
        if query == '':
            query = None

        if query:
            queryset = queryset.filter(
                Q(name__iregex=query) | Q(code__iregex=query))
        return queryset

    def get_context_data(self, **kwargs):
        context = super(LangsList, self).get_context_data(**kwargs)
        context['q'] = self.request.GET.get("q")
        context['langs'] = get_lst_data(self.get_queryset(), self.request, 20)
        context['page_obj'] = paginate(self.get_queryset(), self.request, 20)
        context['url'] = search_pagination(self.request)

        return context


# langs create
class LngCreateView(CreateView):
    model = Languages
    form_class = LngForm
    success_url = '/admin/langs'
    template_name = "admin/lng_create.html"

    def form_valid(self, form):
        lang_save(form, self.request)

        return redirect('langs_list')

    def get_context_data(self, **kwargs):
        context = super(LngCreateView, self).get_context_data(**kwargs)
        context['dropzone_key'] = self.model._meta.verbose_name
        context['images'] = []

        if self.request.session.get(context['dropzone_key']):
            context['images'] = list({'name': it['name'], 'id': clean_text(str(
                it['name']))} for it in self.request.session[context['dropzone_key']] if it['id'] == '')

        return context


# langs update
class LangsUpdate(UpdateView):
    model = Languages
    form_class = LngForm
    success_url = '/admin/langs'
    template_name = "admin/lng_create.html"

    def get_context_data(self, **kwargs):
        context = super(LangsUpdate, self).get_context_data(**kwargs)
        context['dropzone_key'] = self.model._meta.verbose_name

        return context

    def form_valid(self, form):
        lang_save(form, self.request)

        return redirect('langs_list')


# langs delete
def delete_langs(request):
    if request.method == 'POST':
        lng_id = request.POST.get("id")
        try:
            Languages.objects.get(id=int(lng_id)).delete()
        except:
            pass

        url = request.POST.get("url", request.META.get('HTTP_REFERER'))

        return redirect(url)


# static update
class StaticUpdate(BasedUpdateView):
    model = StaticInformation
    fields = "__all__"
    template_name = 'admin/static_add.html'
    success_url = 'static_info'

    def get(self, request, *args, **kwargs):
        k = self.model._meta.verbose_name
        keys = [f'{k}_image', f'{k}_icon']
        predelete_image(keys, self.request, self.get_object().id)
        return super().get(request, *args, **kwargs)

    def get_object(self):
        try:
            object = StaticInformation.objects.get(id=1)
        except:
            object = StaticInformation.objects.create()

        return object

    
    def get_request_data(self):
        data_dict = super().get_request_data()
        cotalog = self.request.FILES.get("cotalog")

        if cotalog:
            data_dict['cotalog'] = cotalog

        return data_dict


# translations list
class TranslationList(ListView):
    model = Translations
    template_name = 'admin/translation_list.html'

    def get_queryset(self):
        queryset = Translations.objects.order_by("-id")
        query = self.request.GET.get("q")
        queryset = search_translation(query, queryset)

        return queryset

    def get_context_data(self, **kwargs):
        context = super(TranslationList, self).get_context_data(**kwargs)
        context['groups'] = TranlsationGroups.objects.all()
        context['langs'] = Languages.objects.filter(
            active=True).order_by('-default')
        context['url'] = search_pagination(self.request)

        # pagination
        context['translations'] = get_lst_data(
            self.get_queryset(), self.request, 20)
        context['page_obj'] = paginate(self.get_queryset(), self.request, 20)

        return context


# translation group
class TranslationGroupDetail(DetailView):
    model = TranlsationGroups
    template_name = 'admin/translation_list.html'

    def get_context_data(self, **kwargs):
        context = super(TranslationGroupDetail,
                        self).get_context_data(**kwargs)
        context['groups'] = TranlsationGroups.objects.all()
        context['langs'] = Languages.objects.filter(
            active=True).order_by('-default')
        lst_one = self.get_object().translations.order_by('-id')

        # search
        query = self.request.GET.get("q")
        lst_one = search_translation(query, lst_one)

        # range
        lst_two = range(1, len(lst_one) + 1)

        # zip 2 lst
        context['translations'] = dict(pairs=zip(lst_one, lst_two))

        return context


# transtion update
def translation_update(request):
    if request.method == 'GET':
        id = request.GET.get('id')

        try:
            translation = Translations.objects.get(id=int(id))
            serializer = TranslationSerializer(translation)

            return JsonResponse(serializer.data)
        except:
            return JsonResponse({'error': 'error'}, safe=False)

    elif request.method == 'POST':
        data = serialize_request(Translations, request)
        id = request.POST.get("id")
        lang = Languages.objects.filter(
            active=True).filter(default=True).first()

        if data.get('value').get(lang.code, '') == '':
            return JsonResponse({'lng_error': 'This language is required'})

        try:
            translation = Translations.objects.get(id=int(id))
            key = data.get('key', '')

            if key == '':
                return JsonResponse({'key_error': 'Key is required'})

            if str(key) in [str(it.key) for it in Translations.objects.filter(group=translation.group).exclude(id=translation.pk)]:
                return JsonResponse({'key_error': 'Key is already in use'})

            translation.key = key
            translation.value = data['value']
            translation.full_clean()
            translation.save()
        except:
            return JsonResponse('some error', safe=False)

        serializer = TranslationSerializer(translation)

        return JsonResponse(serializer.data)


# add translation group
def add_trans_group(request):
    if request.method == 'POST':
        data_dict = serialize_request(TranlsationGroups, request)

        if data_dict.get('sub_text', '') == '':
            return JsonResponse({'key_error': 'Sub text is required'})
        elif (data_dict.get('sub_text'), ) in TranlsationGroups.objects.values_list('sub_text'):
            return JsonResponse({'key_error': 'This key is already in use'})

        try:
            transl_group = TranlsationGroups(**data_dict)
            transl_group.full_clean()
            transl_group.save()
        except ValidationError:
            return JsonResponse({'title_error': 'This title is empty or already in use'})

        data = {
            'id': transl_group.id,
            'name': transl_group.title,
            'key': transl_group.sub_text
        }
        return JsonResponse(data)


# translation group udate
class TranslationGroupUdpate(UpdateView):
    model = TranlsationGroups
    template_name = 'admin/translation_edit.html'
    fields = '__all__'
    success_url = '/admin/translations'

    def get_context_data(self, **kwargs):
        context = super(TranslationGroupUdpate,
                        self).get_context_data(**kwargs)
        context['groups'] = TranlsationGroups.objects.all()
        context['langs'] = Languages.objects.filter(
            active=True).order_by('-default')
        context['lng'] = Languages.objects.filter(
            active=True).filter(default=True).first()
        lst_one = self.get_object().translations.all()

        # range
        lst_two = range(1, len(lst_one) + 1)

        # zip 2 lst
        context['translations'] = dict(pairs=zip(lst_one, lst_two))

        return context

    def post(self, request, *args, **kwargs):
        transls = list(self.get_object().translations.all())
        langs = Languages.objects.filter(active=True).order_by('-default')
        lang = Languages.objects.filter(
            active=True).filter(default=True).first()
        items_count = request.POST.get("item_count")

        data = []
        for l in range(1, int(items_count) + 1):
            new_data = {}
            new_data['id'] = l
            new_data['key'] = request.POST[f'key[{l}]']
            new_data['values'] = []
            for lng in langs:
                new_data['values'].append(
                    {'key': f'value[{l}][{lng.code}]', 'value': request.POST[f'value[{l}][{lng.code}]'], 'def_lang': lang.code, 'lng': lng.code})

            data.append(new_data)

        objects = dict(pairs=zip(data, list(range(1, int(items_count) + 1))))

        for i in range(len(transls)):
            transls[i].key = request.POST.get(f'key[{i + 1}]', '')

            if transls[i].key == '':
                return render(request, template_name=self.template_name, context={'key_errors': {str(i+1): 'Key is required'},  'new_objects': objects, 'langs': langs, 'len': int(items_count) + 1})

            in_default_lng = request.POST.get(f'value[{i+1}][{lang.code}]', '')

            if in_default_lng == '':
                return render(request, template_name=self.template_name, context={'lng_errors': {str(i+1): 'This language is required'}, 'new_objects': objects, 'langs': langs, 'len': int(items_count) + 1})

            value_dict = {}
            for lang in langs:
                value_dict[str(lang.code)
                           ] = request.POST[f'value[{i + 1}][{lang.code}]']

            transls[i].value = value_dict
            try:
                transls[i].full_clean()
                transls[i].save()
            except:
                return render(request, template_name=self.template_name, context={'key_errors': {str(i): 'Key is alredy in use'},  'new_objects': objects, 'langs': langs, 'len': items_count})

        for i in range(len(transls) + 1, int(items_count) + 1):
            new_trans = Translations()
            data = {}
            new_trans.key = request.POST.get(f'key[{i}]', '')

            if new_trans.key == '':
                return render(request, template_name=self.template_name, context={'key_errors': {str(i): 'Key is required'},  'new_objects': objects, 'langs': langs, 'len': items_count})

            value_dict = {}
            in_default_lng = request.POST.get(f'value[{i}][{lang.code}]', '')

            if in_default_lng == '':
                return render(request, template_name=self.template_name, context={'lng_errors': {str(i): 'This language is required'}, 'new_objects': objects, 'langs': langs, 'len': items_count})

            for lang in langs:
                value_dict[str(lang.code)
                           ] = request.POST[f'value[{i}][{lang.code}]']

            new_trans.value = value_dict
            new_trans.group = self.get_object()

            try:
                new_trans.full_clean()
                new_trans.save()
            except:
                return render(request, template_name=self.template_name, context={'key_errors': {str(i): 'Key is alredy in use'}, 'new_objects': objects, 'langs': langs, 'len': items_count})

        return redirect('transl_group_detail', pk=self.get_object().id)

# super users list
class AdminsList(BasedListView):
    model = User
    template_name = 'admin/moterators_list.html'

    def get_queryset(self):
        queryset = User.objects.filter(is_superuser=True)
        query = self.request.GET.get("q", '')

        if query != '':
            queryset = queryset.filter(Q(username__iregex=query) | Q(
                first_name__iregex=query) | Q(last_name__iregex=query))

        return queryset


# super user create
class AdminCreate(CreateView):
    model = User
    form_class = UserForm
    success_url = '/'
    template_name = 'admin/moder_form.html'

    def form_valid(self, form):
        new_user = form.save()
        new_user.is_superuser = True
        full_name = self.request.POST.get("name")

        if full_name:
            if len(full_name.split(' ')) == 1:
                new_user.first_name = full_name.split(' ')[0]

            if len(full_name.split(' ')) == 2:
                new_user.last_name = full_name.split(' ')[1]

        new_user.save()

        return redirect('admin_list')


# admin udate
class AdminUpdate(UpdateView):
    model = User
    form_class = UserForm
    success_url = '/'
    template_name = 'admin/moder_form.html'

    def get_context_data(self, **kwargs):
        context = super(AdminUpdate, self).get_context_data(**kwargs)
        context['full_name'] = None

        if self.get_object().first_name:
            context['full_name'] = self.get_object().first_name

        if self.get_object().last_name:
            context['full_name'] += self.get_object().last_name

        return context

    def form_valid(self, form):
        user = form.save()
        user.is_superuser = True
        full_name = self.request.POST.get("name")

        if full_name:
            if len(full_name.split(' ')) == 1:
                user.first_name = full_name.split(' ')[0]

            if len(full_name.split(' ')) == 2:
                user.last_name = full_name.split(' ')[1]

        user.save()

        return redirect('admin_list')


# del article image
def delete_article_image(request):
    id = request.POST.get("item_id")

    try:
        Articles.objects.get(id=int(id)).image.delete()
    except:
        return JsonResponse({'detail': 'error'})

    return JsonResponse('success', safe=False)


# quic applications
class ShortApplicationList(BasedListView):
    model = ShortApplication
    template_name = 'admin/short_apls.html'


# short application update
class ShortApplicationUpdate(UpdateView):
    model = ShortApplication
    fields = ['nbm', 'status', 'first_name', 'last_name']
    template_name = 'admin/short_apl_edit.html'
    success_url = '/admin/quick_applications'

    def get_context_data(self, **kwargs):
        context = super(ShortApplicationUpdate, self).get_context_data(**kwargs)
        context['statuses'] = ["???? ????????????????????????", "??????????????????????", "??????????????????"]
        context['lang'] = Languages.objects.filter(default=True).first()

        return context



# logout
def logout_view(request):
    logout(request)

    return redirect('login_admin')


# category list
class CategoryList(BasedListView):
    model = Category
    search_fields = ['name']
    template_name = 'admin/category_list.html'


# category create
class CategoryCreate(BasedCreateView):
    model = Category
    fields = '__all__'
    template_name = 'admin/category_form.html'
    success_url = 'category_list'
    related_model = Atributs

    def get(self, request, *args, **kwargs):
        k = self.model._meta.verbose_name
        keys = [f'{k}_image', f'{k}_icon']
        predelete_image(keys, self.request, '')


        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.session.get(f"{context['dropzone_key']}_image"):
            context['images'] = list({'name': it['name'], 'id': clean_text(str(
                it['name']))} for it in self.request.session[f"{context['dropzone_key']}_image"] if it['id'] == '')

        if self.request.session.get(f"{context['dropzone_key']}_icon"):
            context['icons'] = list({'name': it['name'], 'id': clean_text(str(
                it['name']))} for it in self.request.session[f"{context['dropzone_key']}_icon"] if it['id'] == '')

        context['categories'] = Category.objects.filter(parent=None)

        return context

    def get_request_data(self):
        data_dict = super().get_request_data()
        cotalog = self.request.FILES.get("cotalog")
        
        parent_id = self.request.POST.get('parent')
        try:
            parent = Category.objects.get(id=int(parent_id))
            data_dict['parent'] = parent
        except:
            pass
    
        if cotalog:
            data_dict['cotalog'] = cotalog

        key = self.model._meta.verbose_name
        sess_images = self.request.session.get(f'{key}_image')
        if sess_images:
            images = [it for it in sess_images if it['id'] == '']

        if sess_images and len(images) > 0:
            image = images[0]

            data_dict['image'] = image['name']
            self.request.session.get(f'{key}_image').remove(image)
            self.request.session.modified = True

        sess_icons = self.request.session.get(f'{key}_icon')

        if sess_icons:
            icons = [it for it in sess_icons if it['id'] == '']

        if sess_icons and len(icons) > 0:
            icon = icons[0]

            data_dict['icon'] = icon['name']
            self.request.session.get(f'{key}_icon').remove(icon)
            self.request.session.modified = True

        return data_dict


    def form_isvalid(self, form):
        instance = super().form_isvalid(form)

        atributs_ids = self.request.POST.getlist('atributs[]') 
        if atributs_ids:
            atributs = []
            for id in atributs_ids:
                try:
                    atributs.append(Atributs.objects.get(id=int(id)))
                except:
                    pass

            instance.atributs.set(atributs)
            instance.save()

        return instance
        


# category edit
class CategoryEdit(BasedUpdateView):
    model = Category
    fields = '__all__'
    template_name = 'admin/category_form.html'
    success_url = 'category_list'
    related_model = Atributs


    def get(self, request, *args, **kwargs):
        k = self.model._meta.verbose_name
        keys = [f'{k}_image', f'{k}_icon']
        predelete_image(keys, self.request, self.get_object().id)

        return super().get(request, *args, **kwargs)

    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(parent=None).exclude(id=self.get_object().id)

        return context

    def get_request_data(self):
        data_dict = super().get_request_data()
        cotalog = self.request.FILES.get("cotalog")

        parent_id = self.request.POST.get('parent')
        try:
            parent = Category.objects.get(id=int(parent_id))
            data_dict['parent'] = parent
        except:
            pass

        if cotalog:
            data_dict['cotalog'] = cotalog

        key = self.model._meta.verbose_name
        try:
            images = [it for it in self.request.session.get(
                f'{key}_image', []) if it['id'] == str(self.get_object().id)][0]
        except:
            images = None

        try:
            icons = [it for it in self.request.session.get(
                f'{key}_icon', []) if it['id'] == str(self.get_object().id)][0]
        except:
            icons = None

        if images:
            data_dict['image'] = images['name']
            for it in self.request.session.get(f'{key}_image'):
                if it['id'] == str(self.get_object().id):
                    try:
                        self.request.session.get(f'{key}_image').remove(it)
                        self.request.session.modified = True
                    except:
                        pass

        if icons:
            data_dict['icon'] = icons['name']
            for it in self.request.session.get(f'{key}_icon'):
                if it['id'] == str(self.get_object().id):
                    try:
                        self.request.session.get(f'{key}_icon').remove(it)
                        self.request.session.modified = True
                    except:
                        pass

        
        return data_dict


    def form_isvalid(self, form):
        instance = super().form_isvalid(form)

        atributs_ids = self.request.POST.getlist('atributs[]')
        if atributs_ids:
            atributs = []
            for id in atributs_ids:
                try:
                    atributs.append(Atributs.objects.get(id=int(id)))
                except:
                    pass

            instance.atributs.set(atributs)
            instance.save()
        
        return instance


def del_category_file(request):
    pk = request.POST.get('obj_id')
    key = request.POST.get('key')

    try:
        ctg = Category.objects.get(pk=int(pk))
        if key == 'image':
            ctg.image.delete()
        elif key == 'icon':
            ctg.icon.delete()
        elif key == 'cotalog':
            ctg.cotalog.delete()

        ctg.save()

    except:
        return JsonResponse("error", safe=False)

    return JsonResponse('success', safe=False)



# products list
class ProductsList(BasedListView):
    model = Products
    search_fields = ['name']
    template_name = 'admin/products.html'


# faq list
class FAQlist(BasedListView):
    model = FAQ
    search_fields = ['question', 'answer']
    template_name = 'admin/faq.html'


# faq create
class FAQcreate(BasedCreateView):
    model = FAQ
    fields = '__all__'
    template_name = 'admin/faq_form.html'
    success_url = 'faq_list'


# faq update
class FAQupdate(BasedUpdateView):
    model = FAQ
    fields = '__all__'
    template_name = 'admin/faq_form.html'
    success_url = 'faq_list'


# delete product image
def del_product_image(request):
    pk = request.POST.get("item_id")

    try:
        Products.objects.get(id=pk).image.delete()
    except:
        pass

    return JsonResponse('success', safe=False)


# atributs detail view
class AtributsDetailView(DetailView):
    model = Atributs
    template_name = 'admin/atributs_view.html'

    def get_context_data(self, **kwargs):
        context = super(AtributsDetailView, self).get_context_data(**kwargs)
        context['langs'] = Languages.objects.filter(
            active=True).order_by('-default')
        context['lang'] = Languages.objects.filter(default=True).first()

        lst_one = self.get_object().options.all()
        lst_two = range(1, lst_one.count() + 1)
        context['options'] = dict(pairs=zip(lst_one, lst_two))

        return context

# atributs
class AtributsList(BasedListView):
    model = Atributs
    search_fields = ['name']
    template_name = 'admin/atributs.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['langs'] = Languages.objects.filter(active=True)

        return context


# atributs create
class AtributsCreate(CreateView):
    model = Atributs
    fields = '__all__'
    template_name = 'admin/atributs_form.html'

    def get_context_data(self, **kwargs):
        context = super(AtributsCreate, self).get_context_data(**kwargs)
        context['langs'] = Languages.objects.filter(
            active=True).order_by('-default')
        context['lang'] = Languages.objects.filter(default=True).first()

        return context

    def form_valid(self, form):
        return None

    def post(self, request, *args, **kwargs):
        context = super().post(request, *args, **kwargs)
        data_dict = serialize_request(self.model, request)
        data = self.get_context_data()
        options_count = request.POST.get("options_count", 0)
        lang = Languages.objects.filter(default=True).first()

        try:
            options = collect_options(int(options_count), request)
        except:
            options = collect_options(0, request)

        if is_valid_field(data_dict, 'name') == False:
            data['request_post'] = data_dict
            lst_one = options
            lst_two = range(1, len(options) + 1)
            data['options_list'] = dict(pairs=zip(lst_one, lst_two))
            data['name_error'] = 'This field is required.'
            return render(request, self.template_name, data)


        try:
            atribut = Atributs(**data_dict)
            atribut.full_clean()
            atribut.save()

            for l in range(1, int(options_count)+1):
                opt_dict = get_option_from_post(l, request)
                opt_dict['atribut'] = atribut

                if opt_dict.get('name', {}).get(lang.code, '') == '':
                    data['request_post'] = data_dict
                    data['opt_count'] = len(options)
                    lst_one = options
                    lst_two = range(1, len(options) + 1)
                    data['options_list'] = dict(pairs=zip(lst_one, lst_two))
                    data['error_option'] = {}
                    data['error_option'][f'{l}'] = 'This field is required.'
                    return render(request, self.template_name, data)

                try:
                    option = AtributOptions.objects.create(**opt_dict)
                    option.save()
                except:
                    pass
        except:
            pass

        return redirect("atr_list")


# atributs edit
class AtributEdit(UpdateView):
    model = Atributs
    fields = '__all__'
    template_name = 'admin/atributs_form.html'

    def get_context_data(self, **kwargs):
        context = super(AtributEdit, self).get_context_data(**kwargs)
        context['langs'] = Languages.objects.filter(
            active=True).order_by('-default')
        context['lang'] = Languages.objects.filter(default=True).first()

        lst_one = self.get_object().options.all()
        lst_two = range(1, lst_one.count() + 1)
        context['options'] = dict(pairs=zip(lst_one, lst_two))

        return context

    def form_valid(self, form):
        return None

    def post(self, request, *args, **kwargs):
        context = super().post(request, *args, **kwargs)
        data_dict = serialize_request(self.model, request)
        data = self.get_context_data()
        options_count = request.POST.get("options_count", 0)
        old_count = self.get_object().options.count()
        lang = Languages.objects.filter(default=True).first()

        try:
            options = collect_options(int(options_count), request)
        except:
            options = collect_options(0, request)

        if is_valid_field(data_dict, 'name') == False:
            data['request_post'] = data_dict
            lst_one = options
            lst_two = range(1, len(options) + 1)
            data['options_list'] = dict(pairs=zip(lst_one, lst_two))
            data['name_error'] = 'This field is required.'
            return render(request, self.template_name, data)

        instance = self.get_object()

        for attr, value in data_dict.items():
            setattr(instance, attr, value)

        instance.save()


        for i in range(1, old_count + 1):
            opt_dict = get_option_from_post(i, request)

            if opt_dict.get('name', {}).get(lang.code, '') == '':
                data['request_post'] = data_dict
                data['opt_count'] = len(options)
                lst_one = options
                lst_two = range(1, len(options) + 1)
                data['options_list'] = dict(pairs=zip(lst_one, lst_two))
                data['error_option'] = {}
                data['error_option'][f'{i}'] = 'This field is required.'
                return render(request, self.template_name, data)

            try:
                option = instance.options.all()[i-1]


                for attr, value in opt_dict.items():
                    setattr(option, attr, value)
                option.save()
            except:
                pass


        for l in range(old_count+1, int(options_count)+1):
            opt_dict = get_option_from_post(l, request)
            opt_dict['atribut'] = instance

            if opt_dict.get('name', {}).get(lang.code, '') == '':
                data['request_post'] = data_dict
                data['opt_count'] = len(options)
                lst_one = options
                lst_two = range(1, len(options) + 1)
                data['options_list'] = dict(pairs=zip(lst_one, lst_two))
                data['error_option'] = {}
                data['error_option'][f'{l}'] = 'This field is required.'
                return render(request, self.template_name, data)

            try:
                option = AtributOptions.objects.create(**opt_dict)
                option.save()
            except:
                pass

        return redirect("atr_list")


# get option
def get_option(request):
    if request.method == 'GET':
        id = request.GET.get('id')
        try:
            option = AtributOptions.objects.get(id=int(id))
        except:
            return JsonResponse({'error': 'id is invalid'})

    data = {}
    data['id'] = option.id

    for lang in Languages.objects.filter(active=True):
        data[lang.code] = option.name.get(lang.code, '')

    return JsonResponse(data)


# atribut options edit
class AtributOptionEdit(UpdateView):
    model = AtributOptions
    fields = '__all__'

    def get_object(self):
        try:
            id = self.request.POST.get("id")
            return AtributOptions.objects.get(id=int(id))
        except:
            return None

    def form_valid(self, form):
        return None

    def post(self, request, *args, **kwargs):
        super().post(request, *args, **kwargs)
        data_dict = serialize_request(self.model, request)

        if is_valid_field(data_dict, 'name') == False:
            return JsonResponse({'error': 'Name is required'})

        instance = self.get_object()

        if instance:
            for attr, value in data_dict.items():
                setattr(instance, attr, value)

        instance.save()

        return JsonResponse('success', safe=False)


# colors
class ColorsList(BasedListView):
    model = Colors
    search_fields = ['name']
    template_name = 'admin/colors_list.html'


# colors create
class ColorsCreate(BasedCreateView):
    model = Colors
    template_name = 'admin/colors_form.html'
    success_url = 'color_list'


# color edit
class ColorEdit(BasedUpdateView):
    model = Colors
    success_url = 'color_list'
    template_name = 'admin/colors_form.html'



# baners list
class BanersList(BasedListView):
    model = Baners
    template_name = 'admin/baners.html'


# baner create
class BanerCreate(BasedCreateView):
    model = Baners
    template_name = 'admin/baners_form.html'
    success_url = 'baners_list'

    def get(self, request, *args, **kwargs):
        k = self.model._meta.verbose_name
        keys = [f'{k}_{lang.code}' for lang in Languages.objects.filter(active=True)]
        predelete_image(keys, self.request, '')

        return super().get(request, *args, **kwargs)
    

    def get_request_data(self):
        data_dict = super().get_request_data()
        key = self.model._meta.verbose_name
        del data_dict['baner']
        data_dict['baner'] = get_baner(key, '', self.request)

        print(data_dict)
        return data_dict
    
    
    def form_isvalid(self, form):
        obj = super().form_isvalid(form)

        print(obj)
        return obj


# baners edit
class BanerEdit(BasedUpdateView):
    model = Baners
    template_name = 'admin/baners_form.html'
    success_url = 'baners_list'

    def get(self, request, *args, **kwargs):
        k = self.model._meta.verbose_name
        keys = [f'{k}_{lang.code}' for lang in Languages.objects.filter(active=True)]
        predelete_image(keys, self.request, '')

        return super().get(request, *args, **kwargs)


    def get_request_data(self):
        data_dict = super().get_request_data()
        key = self.model._meta.verbose_name
        id = self.get_object().id
        baners = data_dict.pop('baner')

        inst_baners = self.get_object().baner

        data_dict['baner'] = get_baner(key, id, self.request, def_data=inst_baners)
        return data_dict



# delete_baner_img
def delete_baner_img(request):
    id = request.POST.get("obj_id")
    lang = request.POST.get("lang")

    try:
        baner = Baners.objects.get(id=int(id))
        baner_img = dict(baner.baner)
        img = baner_img.pop(lang)
        baner_img[lang] = ''
        file = os.path.join(img)
        default_storage.delete(file)
        baner.baner = baner_img
        baner.save()
    except TypeError as e:
        print(e)

    return JsonResponse("success", safe=False)


def get_product_data(req):
    data_dict = serialize_request(Products, req)
    category_id = req.POST.get('category', 0)
    try:
        category = Category.objects.get(id=int(category_id))
        data_dict['category'] = category
    except:
        pass

    return data_dict


# product creat
@transaction.atomic
def create_product(request):
    if request.method == 'POST':
        lang = Languages.objects.filter(active=True).filter(default=True).first()

        # product save and validate
        data_dict = get_product_data(request)

        errors = {}

        try:
            product = Products(**data_dict)
            product.full_clean()
            product.save()
        except ValidationError as e:
            errors['product'] = e.message_dict
        

        # product variant save
        item_count = request.POST.get('item_count', 0)


        for i in range(1, int(item_count) + 1):
            sub_items_count = request.POST.get(f"sub_item_cout[{i}]")

            # save variant images
            images = []
            files = request.POST.getlist(f'images[{i}]', [])

            for file in files:
                try:
                    image = ProducVariantImages(image=file)
                    image.full_clean()
                    image.save()
                    images.append(image)
                except ValidationError as e:
                    errors[f'images[{i}]'] = e.message_dict


            for l in range(1, int(sub_items_count) + 1):
                variant_data = serialize_variant(i, l, request)
                variant_data['product'] = product

                try:
                    variant = ProductVariants(**variant_data)
                    variant.full_clean()
                    variant.save()

                    variant.images.set(images)
                except ValidationError as e:
                    errors[f'variant[{i}][{l}]'] = e.message_dict

        if errors:
            print(errors)
            errors['lang'] = lang.code
            return JsonResponse(status=403, data=errors)
        else:
            return JsonResponse("success", safe=False)
        


# product create form view
class ProductCreateView(TemplateView):
    model = Products
    template_name = 'admin/products_form.html'

    def get_context_data(self, **kwargs):
        context = super(ProductCreateView, self).get_context_data(**kwargs)

        context['categories'] = Category.objects.filter(parent=None)
        context['langs'] = Languages.objects.filter(active=True)
        context['lang'] = context['langs'].filter(default=True).first()

        return context



# products edit view
class ProductEditView(DetailView):
    model = Products
    template_name = 'admin/products_form.html' 
    

    def get_context_data(self, **kwargs):
        context = super(ProductEditView, self).get_context_data(**kwargs)
        instance = self.get_object()
        variants = instance.variants.all()
        langs = Languages.objects.filter(active=True)
        lang = langs.filter(default=True)

        if lang.exists():
            lang = langs.first()
        
        
        colors = set([it.color for it in variants])
    
        variants_dict = {}

        for color in colors:
            vars = variants.filter(color=color)
            variants_dict[color.id] = vars

        
        context['langs'] = langs
        context['lang'] = lang
        context['colors'] = colors
        context['variants'] = variants_dict
        context['categories'] = Category.objects.filter(parent=None)

        print(variants_dict)

        return context
                

# get post ctg
def get_post_ctg(request):
    id = request.GET.get('id', 0)

    try:
        category = Category.objects.filter(parent=None).get(id=int(id))

        data = {}
        data['categories'] = CategorySimpleSerializer(category.children.all(), many=True, context={'request': request}).data
            #data['atributs'] = AtributSerializer(category.atributs.all(), many=True, context={'request': request}).data

        return JsonResponse(data)
    except:
        return JsonResponse("error", safe=False)
                

# get  post_ctg atributs
def get_atributs(request):
    id = request.GET.get('id', 0)

    try:
        category = Category.objects.exclude(parent=None).get(id=int(id))
        
        atributs = set()

        for atr in category.atributs.all():
            atributs.add(atr)

        for atr in category.parent.atributs.all():
            atributs.add(atr)

        atributs = AtributSerializer(atributs, many=True, context={'request': request}).data

        return JsonResponse({'atributs':atributs})
    except:
        return JsonResponse("error", safe=False)



# edit product
@transaction.atomic
def edit_product(request, pk):     
    queryset = Products.objects.all()

    try:
        instance = queryset.get(id=int(pk))
    except:
        return JsonResponse(status=404, data={'error': 'Product not found'})

    if request.method == 'POST':
        lang = Languages.objects.filter(active=True).filter(default=True).first()
        data_dict = get_product_data(request)

        errors = {}

        try:
            for attr, value in data_dict.items():
                setattr(instance, attr, value)
            instance.full_clean()
            instance.save()
        except ValidationError as e:
            errors['product'] = e.message_dict

        # product variant save
        variants = instance.variants.all()
        item_count = request.POST.get('item_count', 0)
        colors = set([it.color for it in variants])
        old_count_by_color = len(colors)

        for i in range(1, old_count_by_color+1):
            sub_items_count = request.POST.get(f"sub_item_cout[{i}]")
            color = colors[i-1]
            old_sub_items_count = variants.filter(color=color).count()

            # save variant images
            images = []
            files = request.POST.getlist(f'images[{i}]', [])

            for file in files:
                try:
                    image = ProducVariantImages(image=file)
                    image.full_clean()
                    image.save()
                    images.append(image)
                except ValidationError as e:
                    errors[f'images[{i}]'] = e.message_dict

            # edit old sub variants
            for l in range(1, int(old_sub_items_count) + 1):
                variant = variants[l-1]
                variant_data = serialize_variant(i, l, request)

                try:
                    for attr, value in variant_data.items():
                        setattr(variant, attr, value)
                    variant.full_clean()
                    variant.save()
                    variant.images.add(images)
                except ValidationError as e:
                    errors[f'variant[{i}][{l}]'] = e.message_dict

            # add new subvariants
            for j in range(int(old_sub_items_count) + 1, int(sub_items_count)):
                variant_data = serialize_variant(i, j, request)
                variant_data['product'] = instance

                try:
                    variant = ProductVariants(**variant_data)
                    variant.full_clean()
                    variant.save()
                    variant.images.set(images)
                except ValidationError as e:
                    errors[f'variant[{i}][{j}]'] = e.message_dict


        # add new variants
        for t in range(old_count_by_color+1, int(item_count) + 1):
            sub_items_count = request.POST.get(f"sub_item_cout[{t}]")

            # save variant images
            images = []
            files = request.POST.getlist(f'images[{t}]', [])

            for file in files:
                try:
                    image = ProducVariantImages(image=file)
                    image.full_clean()
                    image.save()
                    images.append(image)
                except ValidationError as e:
                    errors[f'images[{t}]'] = e.message_dict

            for k in range(1, int(sub_items_count) + 1):
                variant_data = serialize_variant(t, k, request)
                variant_data['product'] = instance

                try:
                    variant = ProductVariants(**variant_data)
                    variant.full_clean()
                    variant.save()

                    variant.images.set(images)
                except ValidationError as e:
                    errors[f'variant[{t}][{k}]'] = e.message_dict

        if errors:
            errors['lang'] = lang.code
            return JsonResponse(status=403, data=errors)
        else:
            return JsonResponse("success", safe=False)

# custom designs
class DesignsList(BasedListView):
    model = CustomDesigns
    template_name = 'admin/designs.html'
    search_fields = ['title']


# create design page
class CustomDesignCreate(BasedCreateView):
    model = CustomDesigns
    template_name = 'admin/design_form.html'
    success_url = 'designs_list'
    image_field = 'image'
    

# custom desing edit
class CustomDesignEdit(BasedUpdateView):
    model = CustomDesigns
    template_name = 'admin/design_form.html'
    success_url = 'designs_list'
    image_field = 'image'


# delete desing image
def del_design_image(request):
    id = request.POST.get("obj_id")

    try:
        dsgn = CustomDesigns.objects.get(id=int(id))
        dsgn.image.delete()
        dsgn.save()
    except TypeError as e:
        print(e)

    return JsonResponse("success", safe=False)
