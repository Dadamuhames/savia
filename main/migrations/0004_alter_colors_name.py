# Generated by Django 4.1 on 2023-02-25 13:20

import admins.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_alter_atributoptions_name_alter_atributs_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='colors',
            name='name',
            field=models.JSONField(validators=[admins.models.json_field_validate], verbose_name='Name'),
        ),
    ]
