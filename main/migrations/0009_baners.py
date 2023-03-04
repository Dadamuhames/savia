# Generated by Django 4.1 on 2023-03-03 18:14

from django.db import migrations, models
import easy_thumbnails.fields


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_remove_products_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='Baners',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('baner', easy_thumbnails.fields.ThumbnailerImageField(upload_to='baners', verbose_name='Baner')),
                ('link', models.URLField(blank=True, null=True, verbose_name='Link')),
            ],
        ),
    ]
