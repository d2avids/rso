# Generated by Django 4.2.7 on 2023-12-09 06:49

import django.db.models.deletion
from django.db import migrations, models

import headquarters.utils


class Migration(migrations.Migration):

    dependencies = [
        ('headquarters', '0004_detachment_city'),
    ]

    operations = [
        migrations.AlterField(
            model_name='centralheadquarter',
            name='about',
            field=models.CharField(max_length=500, verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='centralheadquarter',
            name='emblem',
            field=models.ImageField(upload_to=headquarters.utils.image_path, verbose_name='Эмблема'),
        ),
        migrations.AlterField(
            model_name='centralheadquarter',
            name='founding_date',
            field=models.DateField(auto_now_add=True, verbose_name='Дата основания'),
        ),
        migrations.AlterField(
            model_name='centralheadquarter',
            name='slogan',
            field=models.CharField(max_length=100, verbose_name='Девиз'),
        ),
        migrations.AlterField(
            model_name='centralheadquarter',
            name='social_tg',
            field=models.CharField(default='https://', max_length=50, verbose_name='Ссылка Телеграм'),
        ),
        migrations.AlterField(
            model_name='centralheadquarter',
            name='social_vk',
            field=models.CharField(default='https://vk.com/', max_length=50, verbose_name='Ссылка ВК'),
        ),
        migrations.AlterField(
            model_name='detachment',
            name='about',
            field=models.CharField(max_length=500, verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='detachment',
            name='emblem',
            field=models.ImageField(upload_to=headquarters.utils.image_path, verbose_name='Эмблема'),
        ),
        migrations.AlterField(
            model_name='detachment',
            name='founding_date',
            field=models.DateField(auto_now_add=True, verbose_name='Дата основания'),
        ),
        migrations.AlterField(
            model_name='detachment',
            name='regional_headquarter',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='detachments', to='headquarters.regionalheadquarter', verbose_name='Привязка к РШ'),
        ),
        migrations.AlterField(
            model_name='detachment',
            name='slogan',
            field=models.CharField(max_length=100, verbose_name='Девиз'),
        ),
        migrations.AlterField(
            model_name='detachment',
            name='social_tg',
            field=models.CharField(default='https://', max_length=50, verbose_name='Ссылка Телеграм'),
        ),
        migrations.AlterField(
            model_name='detachment',
            name='social_vk',
            field=models.CharField(default='https://vk.com/', max_length=50, verbose_name='Ссылка ВК'),
        ),
        migrations.AlterField(
            model_name='districtheadquarter',
            name='about',
            field=models.CharField(max_length=500, verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='districtheadquarter',
            name='emblem',
            field=models.ImageField(upload_to=headquarters.utils.image_path, verbose_name='Эмблема'),
        ),
        migrations.AlterField(
            model_name='districtheadquarter',
            name='founding_date',
            field=models.DateField(auto_now_add=True, verbose_name='Дата основания'),
        ),
        migrations.AlterField(
            model_name='districtheadquarter',
            name='slogan',
            field=models.CharField(max_length=100, verbose_name='Девиз'),
        ),
        migrations.AlterField(
            model_name='districtheadquarter',
            name='social_tg',
            field=models.CharField(default='https://', max_length=50, verbose_name='Ссылка Телеграм'),
        ),
        migrations.AlterField(
            model_name='districtheadquarter',
            name='social_vk',
            field=models.CharField(default='https://vk.com/', max_length=50, verbose_name='Ссылка ВК'),
        ),
        migrations.AlterField(
            model_name='educationalheadquarter',
            name='about',
            field=models.CharField(max_length=500, verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='educationalheadquarter',
            name='emblem',
            field=models.ImageField(upload_to=headquarters.utils.image_path, verbose_name='Эмблема'),
        ),
        migrations.AlterField(
            model_name='educationalheadquarter',
            name='founding_date',
            field=models.DateField(auto_now_add=True, verbose_name='Дата основания'),
        ),
        migrations.AlterField(
            model_name='educationalheadquarter',
            name='slogan',
            field=models.CharField(max_length=100, verbose_name='Девиз'),
        ),
        migrations.AlterField(
            model_name='educationalheadquarter',
            name='social_tg',
            field=models.CharField(default='https://', max_length=50, verbose_name='Ссылка Телеграм'),
        ),
        migrations.AlterField(
            model_name='educationalheadquarter',
            name='social_vk',
            field=models.CharField(default='https://vk.com/', max_length=50, verbose_name='Ссылка ВК'),
        ),
        migrations.AlterField(
            model_name='localheadquarter',
            name='about',
            field=models.CharField(max_length=500, verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='localheadquarter',
            name='emblem',
            field=models.ImageField(upload_to=headquarters.utils.image_path, verbose_name='Эмблема'),
        ),
        migrations.AlterField(
            model_name='localheadquarter',
            name='founding_date',
            field=models.DateField(auto_now_add=True, verbose_name='Дата основания'),
        ),
        migrations.AlterField(
            model_name='localheadquarter',
            name='slogan',
            field=models.CharField(max_length=100, verbose_name='Девиз'),
        ),
        migrations.AlterField(
            model_name='localheadquarter',
            name='social_tg',
            field=models.CharField(default='https://', max_length=50, verbose_name='Ссылка Телеграм'),
        ),
        migrations.AlterField(
            model_name='localheadquarter',
            name='social_vk',
            field=models.CharField(default='https://vk.com/', max_length=50, verbose_name='Ссылка ВК'),
        ),
        migrations.AlterField(
            model_name='regionalheadquarter',
            name='about',
            field=models.CharField(max_length=500, verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='regionalheadquarter',
            name='emblem',
            field=models.ImageField(upload_to=headquarters.utils.image_path, verbose_name='Эмблема'),
        ),
        migrations.AlterField(
            model_name='regionalheadquarter',
            name='founding_date',
            field=models.DateField(auto_now_add=True, verbose_name='Дата основания'),
        ),
        migrations.AlterField(
            model_name='regionalheadquarter',
            name='slogan',
            field=models.CharField(max_length=100, verbose_name='Девиз'),
        ),
        migrations.AlterField(
            model_name='regionalheadquarter',
            name='social_tg',
            field=models.CharField(default='https://', max_length=50, verbose_name='Ссылка Телеграм'),
        ),
        migrations.AlterField(
            model_name='regionalheadquarter',
            name='social_vk',
            field=models.CharField(default='https://vk.com/', max_length=50, verbose_name='Ссылка ВК'),
        ),
    ]
