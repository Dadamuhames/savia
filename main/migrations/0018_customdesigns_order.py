# Generated by Django 4.1 on 2023-03-12 15:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0017_category_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='customdesigns',
            name='order',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='order'),
        ),
    ]