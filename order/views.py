from django.shortcuts import render
from .models import Order, ShortApplication, OrderProducts
from main.models import ProductVariants, Products
from rest_framework import generics, views, pagination, filters
from admins.models import Articles, StaticInformation, Translations, Languages, FAQ
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_list_or_404, get_object_or_404
from .serializers import ShortAplicatinSerializer, OrderProductSerializer, OrderSierializer

# Create your views here.                                       


# aplication create view
class AplicationCreateView(generics.CreateAPIView):
    queryset = ShortApplication.objects.all()
    serializer_class = ShortAplicatinSerializer


# order create view
class OrderCreateView(generics.CreateAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSierializer


    def perform_create(self, serializer):
        order = serializer.save()
        products_list = self.request.data.get("products", [])
        products = ProductVariants.objects.filter(product__active=True)
        total_price = 0

        for item in products_list:
            product = get_object_or_404(products, id=int(item.get("id", 0)))
            count = float(item.get("count", 1))
            price = product.price * count
            total_price += price
            
            order_prod_data = {
                'variant': product,
                'order': order,
                'count': count,
                'price': price
            }

            order_product = OrderProducts.objects.create(**order_prod_data)
            order_product.save()
                

        order.total_price = total_price
        order.save()

        return order