from django.contrib import admin
from .models import Products, ProductVariants, Colors, AtributOptions, Atributs
# Register your models here.



admin.site.register(ProductVariants)
admin.site.register(Products)
admin.site.register(Colors)
admin.site.register(Atributs)
admin.site.register(AtributOptions)