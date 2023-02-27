from django.db import models
from main.models import ProductVariants
from django.core.validators import MaxValueValidator, MinValueValidator, FileExtensionValidator
# Create your models here.


# short applications
class ShortApplication(models.Model):
    STATUS = [('На рассмотрении', "На рассмотрении"),
              ("Рассмотрено", "Рассмотрено"), ("Отклонено", "Отклонено")]

    full_name = models.CharField('Full name', max_length=255)
    nbm = models.CharField('Nbm', max_length=255)
    status = models.CharField(
        'Status', default='На рассмотрении', max_length=255, choices=STATUS)



# order
class Order(models.Model):
    STATUS = [('На рассмотрении', "На рассмотрении"),
              ("Рассмотрено", "Рассмотрено"), ("Отклонено", "Отклонено")]

    full_name = models.CharField("Full name", max_length=255)
    nbm = models.CharField("Nbm", max_length=255)
    total_price = models.FloatField('Price', validators=[MinValueValidator(1)], blank=True, null=True)
    status = models.CharField('Status', default='На рассмотрении', max_length=255, choices=STATUS)


# order products
class OrderProducts(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='products')
    variant = models.ForeignKey(ProductVariants, on_delete=models.CASCADE)
    price = models.FloatField('Price', validators=[MinValueValidator(1)])   
    count = models.PositiveIntegerField('Count', default=1)
