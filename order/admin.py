from django.contrib import admin
from .models import Order, OrderProducts, ShortApplication
# Register your models here.


admin.site.register(Order)
admin.site.register(OrderProducts)
admin.site.register(ShortApplication)