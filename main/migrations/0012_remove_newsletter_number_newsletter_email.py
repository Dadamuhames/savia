# Generated by Django 4.1 on 2023-03-08 13:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_baners_active'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='newsletter',
            name='number',
        ),
        migrations.AddField(
            model_name='newsletter',
            name='email',
            field=models.EmailField(default='dadad@gmail.com', max_length=254, verbose_name='Email'),
            preserve_default=False,
        ),
    ]
