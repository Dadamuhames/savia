# Generated by Django 4.1 on 2023-03-11 14:40

import admins.models
from django.db import migrations, models
import easy_thumbnails.fields


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0014_remove_productvariants_code'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomDesigns',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.JSONField(validators=[admins.models.json_field_validate], verbose_name='Design name')),
                ('image', easy_thumbnails.fields.ThumbnailerImageField(upload_to='design_images')),
            ],
        ),
        migrations.AlterField(
            model_name='baners',
            name='baner',
            field=models.JSONField(validators=[admins.models.json_field_validate], verbose_name='Baner'),
        ),
    ]
