from .models import Products, Category, AtributOptions, Atributs, ProductVariants, Colors
from rest_framework import generics, views, pagination, filters
from .serializers import ProductsSerializer, Categoryserializer, ProductVariantSimpleSerializer, TopProductSerializer, FAQserializer, CategoryDetailSerializer
from .serializers import ArticleSerializer, StaticInformationSerializer, TranslationSerializer, LangsSerializer, ProductVariantDetailSerializer, ArticleDetailSerializer
from admins.models import Articles, StaticInformation, Translations, Languages, FAQ
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_list_or_404, get_object_or_404
# Create your views here.

# pagination
class BasePagination(pagination.PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 1000


# articles list
class ArticlesList(generics.ListAPIView):
    queryset = Articles.objects.filter(active=True)
    serializer_class = ArticleSerializer
    pagination_class = BasePagination


# articles detail
class ArticlesDetail(generics.RetrieveAPIView):
    queryset = Articles.objects.filter(active=True)
    serializer_class = ArticleDetailSerializer
    lookup_field = 'slug'


# static information
class StaticInfView(views.APIView):
    def get(self, request, format=None):
        try:
            obj = StaticInformation.objects.get(id=1)
        except:
            obj = StaticInformation.objects.create()

        serializer = StaticInformationSerializer(
            obj, context={'request': request})

        return Response(serializer.data)


# translations
class TranslationsView(views.APIView):
    def get(self, request, fromat=None):
        translations = Translations.objects.all()
        serializer = TranslationSerializer(
            translations, context={'request': request})
        return Response(serializer.data)


# langs list
class LangsList(generics.ListAPIView):
    queryset = Languages.objects.filter(active=True)
    serializer_class = LangsSerializer
    pagination_class = BasePagination


# category list
class CategoryList(generics.ListAPIView):
    queryset = Category.objects.filter(parent=None)
    serializer_class = Categoryserializer
    pagination_class = BasePagination


# category detail
class CategoryDetailView(generics.RetrieveAPIView):
    queryset = Category.objects.filter(parent=None)
    serializer_class = CategoryDetailSerializer


# products list
class ProductsList(generics.ListAPIView):
    serializer_class = ProductVariantSimpleSerializer
    pagination_class = BasePagination

    def get_queryset(self):
        queryset = ProductVariants.objects.filter(default=True).select_related('product').filter(product__active=True)
        ctg_id = self.request.GET.get("category")
        post_ctg_id = self.request.GET.get('post_ctg')
        query = self.request.GET.get('q', '')

        if ctg_id:
            category = get_object_or_404(Category.objects.filter(paretn=None), id=int(ctg_id)) 
            queryset = queryset.filter(product__category__parent=category)
        
        if post_ctg_id:
            post_ctg = get_object_or_404(Category.objects.filter(children=None),  id=int(post_ctg_id))
            queryset = queryset.filter(product__category=post_ctg)

        if query != '':
            products = Products.objects.filter(active=True).extra(where=[f'LOWER(name) LIKE %s'], params=[f'%{query.lower()}%'])
            queryset = queryset.filter(product__in=products)


        return queryset


# top products serializer
class TopProducts(views.APIView):
    def get(self, request, format=None):
        products = ProductVariants.objects.filter(product__active=True).filter(top=True)
        serializer = TopProductSerializer(products, many=True, context={'request': request})

        return Response(serializer.data)    


# cart view
class CartView(views.APIView):
    def post(self, request, format=None):
        products = []
        cart_products = request.POST.get('products', [])
        products = ProductVariants.objects.filter(product__active=True)
        
        for item in cart_products:
            product = get_object_or_404(products, id=int(item['id']))
            prod_dict = ProductVariantSimpleSerializer(product, context={'request': request}).data
            prod_dict['count'] = item['count']

            products.append(prod_dict)

        return Response(products)


# faq view
class FAQview(generics.ListAPIView):
    queryset = FAQ.objects.filter(active=True)
    serializer_class = FAQserializer
    pagination_class = BasePagination



# search
class Search(views.APIView):
    def get(self, request, format=None):
        query = request.GET.get('q', '')
        print(query.lower())


        if query != '':
            products_vars = ProductVariants.objects.filter(product__active=True).filter(default=True)
            products = Products.objects.all()
            products = products.extra(where=[f'LOWER(name) LIKE %s'], params=[f'%{query.lower()}%']).order_by("-id")
            products_vars = products_vars.select_related('product').filter(product__in=products)


            categories = Category.objects.filter(parent=None)
            categories = categories.extra(where=[f'LOWER(name) LIKE %s'], params=[f'%{query.lower()}%'])


            data_dict = {}
            context = {'request': request}
            data_dict['products'] = ProductVariantSimpleSerializer(products_vars, many=True, context=context).data
            data_dict['categories'] = Categoryserializer(categories, many=True, context=context).data
        else:
            return Response({'detail': 'q param is required'}, status=status.HTTP_403_FORBIDDEN)


        return Response(data_dict)