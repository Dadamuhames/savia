from django.db import models
from main.models import ProductVariants
# Create your models here.


# short applications
class ShortApplication(models.Model):
    STATUS = [('На рассмотрении', "На рассмотрении"),
              ("Рассмотрено", "Рассмотрено"), ("Отклонено", "Отклонено")]

    full_name = models.CharField('Full name', max_length=255)
    nbm = models.CharField('Nbm', max_length=255)
    product = models.ForeignKey(
        ProductVariants, blank=True, null=True, on_delete=models.SET_NULL)
    comment = models.TextField('Comment', blank=True, null=True)
    status = models.CharField(
        'Status', default='На рассмотрении', max_length=255, choices=STATUS)
