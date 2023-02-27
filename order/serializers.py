from rest_framework import serializers
from .models import Order, OrderProducts, ShortApplication



# short apl serializer
class ShortAplicatinSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShortApplication
        exclude = ['status']


# order product serializer
class OrderProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderProducts
        fields = '__all__'



# order serializer
class OrderSierializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'


