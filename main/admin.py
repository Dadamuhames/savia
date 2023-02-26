from django.contrib import admin
from .models import Products, ProductVariants, Colors
# Register your models here.



admin.site.register(ProductVariants)
admin.site.register(Products)
admin.site.register(Colors)