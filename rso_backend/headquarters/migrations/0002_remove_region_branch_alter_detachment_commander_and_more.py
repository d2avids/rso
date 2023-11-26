# Generated by Django 4.2.7 on 2023-11-24 15:37

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('headquarters', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='region',
            name='branch',
        ),
        migrations.AlterField(
            model_name='detachment',
            name='commander',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Командир'),
        ),
        migrations.CreateModel(
            name='RegionalHeadquarter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=100, verbose_name='Название')),
                ('about', models.CharField(blank=True, default='', max_length=500, verbose_name='Описание')),
                ('emblem', models.ImageField(blank=True, upload_to='emblems/%Y/%m/%d', verbose_name='Эмблема')),
                ('social_vk', models.CharField(blank=True, default='https://vk.com/', max_length=50, verbose_name='Ссылка ВК')),
                ('social_tg', models.CharField(blank=True, default='https://', max_length=50, verbose_name='Ссылка Телеграм')),
                ('banner', models.ImageField(blank=True, upload_to='emblems/%Y/%m/%d', verbose_name='Баннер')),
                ('slogan', models.CharField(blank=True, default='', max_length=100, verbose_name='Девиз')),
                ('founding_date', models.DateField(blank=True, null=True, verbose_name='Дата основания')),
                ('commander', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Командир')),
                ('region', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='headquarters', to='headquarters.region', verbose_name='Регион')),
            ],
            options={
                'verbose_name': 'Структурная единица',
                'verbose_name_plural': 'структурные единицы',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='LocalHeadquarter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=100, verbose_name='Название')),
                ('about', models.CharField(blank=True, default='', max_length=500, verbose_name='Описание')),
                ('emblem', models.ImageField(blank=True, upload_to='emblems/%Y/%m/%d', verbose_name='Эмблема')),
                ('social_vk', models.CharField(blank=True, default='https://vk.com/', max_length=50, verbose_name='Ссылка ВК')),
                ('social_tg', models.CharField(blank=True, default='https://', max_length=50, verbose_name='Ссылка Телеграм')),
                ('banner', models.ImageField(blank=True, upload_to='emblems/%Y/%m/%d', verbose_name='Баннер')),
                ('slogan', models.CharField(blank=True, default='', max_length=100, verbose_name='Девиз')),
                ('founding_date', models.DateField(blank=True, null=True, verbose_name='Дата основания')),
                ('commander', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Командир')),
            ],
            options={
                'verbose_name': 'Структурная единица',
                'verbose_name_plural': 'структурные единицы',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='EducationalInstitution',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('short_name', models.CharField(max_length=50, verbose_name='Короткое название образовательной организации (например, РГГУ)')),
                ('name', models.CharField(max_length=250, unique=True, verbose_name='Полное название образовательной организации')),
                ('rector', models.CharField(blank=True, max_length=250, null=True, verbose_name='ФИО ректора образовательной организации')),
                ('rector_email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='Электронная почта ректора')),
                ('region', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='institutions', to='headquarters.region', verbose_name='Регион')),
            ],
        ),
        migrations.CreateModel(
            name='EducationalHeadquarter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=100, verbose_name='Название')),
                ('about', models.CharField(blank=True, default='', max_length=500, verbose_name='Описание')),
                ('emblem', models.ImageField(blank=True, upload_to='emblems/%Y/%m/%d', verbose_name='Эмблема')),
                ('social_vk', models.CharField(blank=True, default='https://vk.com/', max_length=50, verbose_name='Ссылка ВК')),
                ('social_tg', models.CharField(blank=True, default='https://', max_length=50, verbose_name='Ссылка Телеграм')),
                ('banner', models.ImageField(blank=True, upload_to='emblems/%Y/%m/%d', verbose_name='Баннер')),
                ('slogan', models.CharField(blank=True, default='', max_length=100, verbose_name='Девиз')),
                ('founding_date', models.DateField(blank=True, null=True, verbose_name='Дата основания')),
                ('commander', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Командир')),
            ],
            options={
                'verbose_name': 'Структурная единица',
                'verbose_name_plural': 'структурные единицы',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DistrictHeadquarter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=100, verbose_name='Название')),
                ('about', models.CharField(blank=True, default='', max_length=500, verbose_name='Описание')),
                ('emblem', models.ImageField(blank=True, upload_to='emblems/%Y/%m/%d', verbose_name='Эмблема')),
                ('social_vk', models.CharField(blank=True, default='https://vk.com/', max_length=50, verbose_name='Ссылка ВК')),
                ('social_tg', models.CharField(blank=True, default='https://', max_length=50, verbose_name='Ссылка Телеграм')),
                ('banner', models.ImageField(blank=True, upload_to='emblems/%Y/%m/%d', verbose_name='Баннер')),
                ('slogan', models.CharField(blank=True, default='', max_length=100, verbose_name='Девиз')),
                ('founding_date', models.DateField(blank=True, null=True, verbose_name='Дата основания')),
                ('commander', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Командир')),
            ],
            options={
                'verbose_name': 'Структурная единица',
                'verbose_name_plural': 'структурные единицы',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CentralHeadquarter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=100, verbose_name='Название')),
                ('about', models.CharField(blank=True, default='', max_length=500, verbose_name='Описание')),
                ('emblem', models.ImageField(blank=True, upload_to='emblems/%Y/%m/%d', verbose_name='Эмблема')),
                ('social_vk', models.CharField(blank=True, default='https://vk.com/', max_length=50, verbose_name='Ссылка ВК')),
                ('social_tg', models.CharField(blank=True, default='https://', max_length=50, verbose_name='Ссылка Телеграм')),
                ('banner', models.ImageField(blank=True, upload_to='emblems/%Y/%m/%d', verbose_name='Баннер')),
                ('slogan', models.CharField(blank=True, default='', max_length=100, verbose_name='Девиз')),
                ('founding_date', models.DateField(blank=True, null=True, verbose_name='Дата основания')),
                ('commander', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Командир')),
            ],
            options={
                'verbose_name': 'Структурная единица',
                'verbose_name_plural': 'структурные единицы',
                'abstract': False,
            },
        ),
    ]