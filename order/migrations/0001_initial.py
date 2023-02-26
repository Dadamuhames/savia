# Generated by Django 4.1 on 2023-02-25 11:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShortApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=255, verbose_name='Full name')),
                ('nbm', models.CharField(max_length=255, verbose_name='Nbm')),
                ('comment', models.TextField(blank=True, null=True, verbose_name='Comment')),
                ('status', models.CharField(choices=[('На рассмотрении', 'На рассмотрении'), ('Рассмотрено', 'Рассмотрено'), ('Отклонено', 'Отклонено')], default='На рассмотрении', max_length=255, verbose_name='Status')),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.productvariants')),
            ],
        ),
    ]
