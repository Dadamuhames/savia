from .models import Products, Category, AtributOptions, Atributs, Colors, ProductVariants, ProducVariantImages, Baners, Newsletter, CustomDesigns
from admins.models import Languages
from rest_framework import serializers
from django.conf import settings
from django.core.files.storage import default_storage
import os
from easy_thumbnails.templatetags.thumbnail import thumbnail_url, get_thumbnailer
from admins.models import Articles, StaticInformation, Languages, Translations, MetaTags, FAQ


class ThumbnailSerializer(serializers.BaseSerializer):
    def __init__(self, alias, instance=None, **kwargs):
        super().__init__(instance, **kwargs)
        self.alias = alias

    def to_representation(self, instance):
        alias = settings.THUMBNAIL_ALIASES.get('').get(self.alias)
        if alias is None:
            return None

        size = alias.get('size')
        url = None

        if instance:
            orig_url = instance.path.split('.')
            thb_url = '.'.join(orig_url) + f'.{size[0]}x{size[1]}_q85.{orig_url[-1]}'
            if default_storage.exists(thb_url):
                print("if")
                last_url = instance.url.split('.')
                url = '.'.join(last_url) + f'.{size[0]}x{size[1]}_q85.{last_url[-1]}'
            else:
                print('else')
                url = get_thumbnailer(instance)[self.alias].url

        if url == '' or url is None:
            return None

        request = self.context.get('request', None)
        if request is not None:
            return request.build_absolute_uri(url)

        return url


# field lang serializer
class JsonFieldSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        language = self.context['request'].headers.get('Language')
        default_lang = Languages.objects.filter(default=True).first().code

        if not language:
            language = default_lang

        data = instance.get(language)

        if data is None or data == '':
            data = instance.get(default_lang)

        return data


# meta serializer
class MetaFieldSerializer(serializers.ModelSerializer):
    meta_keys = JsonFieldSerializer()
    meta_deck = JsonFieldSerializer()

    class Meta:
        model = MetaTags
        exclude = ['id']


# articles
class ArticleSerializer(serializers.ModelSerializer):
    title = JsonFieldSerializer()
    subtitle = JsonFieldSerializer()
    body = JsonFieldSerializer()
    created_date = serializers.DateField(format="%d.%m.%Y")
    image = ThumbnailSerializer(alias='prod_photo')
    author = serializers.ReadOnlyField(source='author.username')
    meta = MetaFieldSerializer()

    class Meta:
        model = Articles
        fields = '__all__'


# article detail serializer
class ArticleDetailSerializer(serializers.ModelSerializer):
    title = JsonFieldSerializer()
    subtitle = JsonFieldSerializer()
    body = JsonFieldSerializer()
    created_date = serializers.DateField(format="%d.%m.%Y")
    image = ThumbnailSerializer(alias='original')
    meta = MetaFieldSerializer()

    class Meta:
        model = Articles
        fields = '__all__'


# static information
class StaticInformationSerializer(serializers.ModelSerializer):
    title = JsonFieldSerializer()
    subtitle = JsonFieldSerializer()
    deskription = JsonFieldSerializer()
    about_us = JsonFieldSerializer()
    adres = JsonFieldSerializer()
    work_time = JsonFieldSerializer()
    logo_first = ThumbnailSerializer(alias='prod_photo')
    logo_second = ThumbnailSerializer(alias='prod_photo')

    class Meta:
        model = StaticInformation
        exclude = ['id']


# translation serializer
class TranslationSerializer(serializers.Serializer):
    def to_representation(self, instance):
        data = {}

        for item in instance:
            val = JsonFieldSerializer(item.value, context={'request': self.context.get('request')}).data
            key = str(item.group.sub_text) + '.' + str(item.key)
            data[key] = val

        return data


# langs serializer
class LangsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Languages
        fields = '__all__'


# FAQ serializer
class FAQserializer(serializers.ModelSerializer):
    question = JsonFieldSerializer()
    answer = JsonFieldSerializer()

    class Meta:
        model = FAQ
        exclude = ['active']


# atribut options serializer
class AtributOptionsSerializer(serializers.ModelSerializer):
    name = JsonFieldSerializer()

    class Meta:
        model = AtributOptions
        exclude = ['atribut']


# atribut serializer
class AtributSerializer(serializers.ModelSerializer):
    name = JsonFieldSerializer()
    options = AtributOptionsSerializer(many=True)

    class Meta:
        model = Atributs
        fields = '__all__'


# color serializer
class ColorSerializer(serializers.ModelSerializer):
    name = JsonFieldSerializer()

    class Meta:
        model = Colors
        fields = '__all__'


# ctg parent serializer
class CategoryChildrenSerializer(serializers.ModelSerializer):
    name = JsonFieldSerializer()

    class Meta:
        model = Category
        fields = ['name', 'id']


# category serializer
class Categoryserializer(serializers.ModelSerializer):
    name = JsonFieldSerializer()
    deckription = JsonFieldSerializer()
    icon = ThumbnailSerializer(alias='ten')
    image = ThumbnailSerializer(alias='ten')

    class Meta:
        model = Category
        fields = '__all__'


# category simple serializer
class CategorySimpleSerializer(serializers.ModelSerializer):
    name = JsonFieldSerializer()

    class Meta:
        model = Category
        fields = ['name', 'id']


    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['parent'] = JsonFieldSerializer(instance.parent.name, context={'request': self.context.get('request', {})}).data

        return data


# category detail serializer
class CategoryDetailSerializer(Categoryserializer):
    children = CategoryChildrenSerializer(many=True)


# product simple serializer
class ProductSimpleSerializer(serializers.ModelSerializer):
    name = JsonFieldSerializer()
    subtitle = JsonFieldSerializer()
    category  = CategorySimpleSerializer()

    class Meta:
        model =Products
        fields = ['name', 'slug', 'subtitle', 'category']


# product serializer
class ProductsSerializer(ProductSimpleSerializer):
    type = JsonFieldSerializer()
    category = CategorySimpleSerializer()
    description = JsonFieldSerializer()

    class Meta:
        model = Products
        fields = '__all__'



# product variant serializer
class ProductVariantSimpleSerializer(serializers.ModelSerializer):
    product = ProductSimpleSerializer()
    #image = ThumbnailSerializer(alias='product_img')

    class Meta:
        model = ProductVariants
        exclude = ['options', 'top', 'default', 'images']

    
    def to_representation(self, instance):
        data = super().to_representation(instance)

        image = instance.images.first()
        if image:
            data['image'] = ThumbnailSerializer(instance=image.image, alias='prod_photo', context={'request': self.context.get("request", {})}).data

        return data


# top product serializer
class TopProductSerializer(serializers.Serializer):
    def to_representation(self, instance):
        data = []
        print(instance)
        categories = set()
        context = {'request': self.context.get('request', {})}

        for product in instance:
            try:
                ctg = product.product.category.parent
                categories.add(ctg)
            except:
                pass


        for ctg in categories:
            ctg_dict = Categoryserializer(ctg, context=context).data
            products_list = instance.filter(product__category__parent=ctg)
            serializer = ProductVariantSimpleSerializer(products_list, many=True, context={'request': self.context.get('request', {})})
            ctg_dict['products'] = serializer.data

            data.append(ctg_dict)

        

        return {'products': data}


# product variant images
class ProductVariantImagesSerializer(serializers.ModelSerializer):
    image = ThumbnailSerializer(alias='product_img')
    
    class Meta:
        model = ProducVariantImages
        fields = '__all__'



# product variant detail serializer
class ProductVariantDetailSerializer(ProductVariantSimpleSerializer):
    product = ProductsSerializer()
    images = ProductVariantImagesSerializer(many=True)


    class Meta:
        model = ProductVariants
        fields = '__all__'

    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['atributs'] = []
        context = {'request': self.context.get("request")}

        variants = instance.product.variants.all()                        
        atributs = []
        for atr in instance.product.category.atributs.all():
            atributs.append(atr)

        for atr in instance.product.category.parent.atributs.all():
            atributs.append(atr)

        for atr in atributs:
            atr_data = AtributSerializer(atr, context=context).data
            options = atr_data['options']
            
            opt_lst = [it for it in instance.options.all()]

            for opt in opt_lst:
                if opt.atribut == atr:
                    opt_lst.remove(opt)

            for opt in options:
                lst = opt_lst.copy()
                opshn = AtributOptions.objects.get(id=int(opt['id']))             
                lst.append(opshn)
                id_lst = [it.id for it in lst]
                
                variant = variants.filter(color=instance.color)
                for id in id_lst:
                    variant = variant.filter(options=id)

                if not variant.exists(): 
                    opt['variant'] = None
                else:
                    opt['variant'] = variant.first().slug

                
                

            data['atributs'].append(atr_data)

        colors = set()

        for var in variants:
            colors.add(var.color)

        data['colors'] = []

        for color in colors:
            serializer = ColorSerializer(color, context=context).data
            variant = variants.filter(color=color)

            for opt in instance.options.all():
                variant = variant.filter(options=opt)

            if variant.count() == 0:
                serializer['variant'] = None
            else:
                serializer['variant'] = variant.first().slug

            data['colors'].append(serializer)


        return data
    

# baner image serializer
class BanerImageSerializer(ThumbnailSerializer):
    def to_representation(self, instance):
        request = self.context.get('request')
        alias = settings.THUMBNAIL_ALIASES.get('').get(self.alias)
        if alias is None:
            return None

        size = alias.get('size')
        url = None

        if instance and default_storage.exists(instance):
            open_url = default_storage.open(instance).name
            orig_url = open_url.split('.')
            thb_url = '.'.join(orig_url) + \
                f'.{size[0]}x{size[1]}_q85.{orig_url[-1]}'
            if default_storage.exists(thb_url):
                url = thb_url
            else:
                url = get_thumbnailer(open_url)[self.alias]
        else:
            return '/static/src/img/default.png'

        if url == '' or url is None:
            return None

        if request is not None:
            final_url = '/media/' + str(url).split('/media/')[-1].replace('\\', "/")
            return request.build_absolute_uri(final_url)

        return url


# baner
class BanerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Baners
        exclude = ['baner', 'active']

    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        context = {'request': self.context.get('request')}
        
        img_path = JsonFieldSerializer(instance.baner, context=context).data
        data['image'] = BanerImageSerializer(alias='original', instance=img_path, context=context).data

        return data


# newslatters
class NewsletterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Newsletter
        fields = '__all__'




# custon design serializer
class CustomDesighSerializer(serializers.ModelSerializer):
    title = JsonFieldSerializer()
    image = ThumbnailSerializer(alias='prod_photo')

    class Meta:
        model = CustomDesigns
        fields = '__all__'