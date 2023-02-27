from django.db import models
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator, FileExtensionValidator
from easy_thumbnails.fields import ThumbnailerImageField
from colorfield.fields import ColorField
from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from admins.models import Languages
from django.utils.text import slugify
from admins.models import unique_slug_generator, json_field_validate
import cyrtranslit
from admins.models import MetaTags
# Create your models here.


# colors
class Colors(models.Model):
    name = models.JSONField('Name', validators=[json_field_validate])
    slug = models.SlugField('Slug', editable=False, unique=True, blank=True, null=True)
    hex = ColorField(default='#FF0000')

    def save(self, *args, **kwargs):  # new
        if not self.slug:
            lng = Languages.objects.filter(active=True).filter(default=True).first()
            str = cyrtranslit.to_latin(self.name.get(lng.code, '')[:50])
            slug = slugify(str)
            self.slug = unique_slug_generator(self, slug)

        return super().save(*args, **kwargs)


# atributs
class Atributs(models.Model):
    name = models.JSONField("name", validators=[json_field_validate])


# atribut option
class AtributOptions(models.Model):
    name = models.JSONField("Name", validators=[json_field_validate])
    atribut = models.ForeignKey(Atributs, on_delete=models.CASCADE, related_name='options')



# category
class Category(models.Model):
    name = models.JSONField('Name', validators=[json_field_validate])
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, related_name='children')
    deckription = models.JSONField("Deckription", blank=True, null=True)
    icon = ThumbnailerImageField(upload_to='ctg_icons', blank=True, null=True)
    atributs = models.ManyToManyField(Atributs, blank=True, null=True)
    image = ThumbnailerImageField(upload_to='ctg_image', blank=True, null=True)
    cotalog = models.FileField(
        'Cotalog for download', upload_to='cotalog_fiels', blank=True, null=True)
    


# products
class Products(models.Model):
    name = models.JSONField('Name', validators=[json_field_validate])
    subtitle = models.JSONField('Subtitle', blank=True, null=True)
    slug = models.SlugField('Slug', editable=False, unique=True, blank=True, null=True)
    type = models.JSONField("Type", blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', blank=True, null=True)
    description = models.JSONField('Descr', blank=True, null=True)
    active = models.BooleanField('Active', default=True)
    meta = models.ForeignKey(MetaTags, on_delete=models.CASCADE, blank=True, null=True)
    image = ThumbnailerImageField(
        upload_to='product_images', blank=True, null=True)

    def save(self, *args, **kwargs):  # new
        if not self.slug:
            lng = Languages.objects.filter(
                active=True).filter(default=True).first()
            str = cyrtranslit.to_latin(self.name.get(lng.code, '')[:50])
            slug = slugify(str)
            self.slug = unique_slug_generator(self, slug)

        return super().save(*args, **kwargs)


@receiver(pre_save, sender=Products)
def delete_variants(sender, instance, **kwargs):
    try:
        obj = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        # Object is new, so field hasn't technically changed, but you may want to do something else here.
        pass
    else:
        if obj.category != instance.category:  # Field has changed
            ProductVariants.objects.filter(product=obj).delete()


# product images
class ProducVariantImages(models.Model):
    image = ThumbnailerImageField(upload_to='variant_images', blank=True, null=True)

# product variant
class ProductVariants(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='variants')
    price = models.FloatField('Price', validators=[MinValueValidator(0)])
    color = models.ForeignKey(Colors, on_delete=models.CASCADE)
    slug = models.SlugField('Slug', editable=False, unique=True)
    options = models.ManyToManyField(AtributOptions, blank=True, null=True)
    images = models.ManyToManyField(ProducVariantImages, blank=True, null=True)
    code = models.CharField('Code', max_length=255)
    top = models.BooleanField('Top', default=False)
    default = models.BooleanField("Default", default=False)

    def save(self, *args, **kwargs):  # new
        if not self.slug:
            lng = Languages.objects.filter(active=True).filter(default=True).first()
            str = cyrtranslit.to_latin(self.product.name.get(lng.code, 'prod') + self.color.name.get(lng.code, 'color'))
            slug = slugify(str[:50])
            self.slug = unique_slug_generator(self, slug, Products)

        variants = ProductVariants.objects.filter(product=self.product).exclude(pk=self.pk)
        if variants.count() > 1 and self.default:
            for variant in variants:
                variant.default = False
                variant.save()

        return super().save(*args, **kwargs)





