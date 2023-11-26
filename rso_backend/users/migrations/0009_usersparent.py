# Generated by Django 4.2.7 on 2023-11-26 12:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('headquarters', '0013_alter_usercentralheadquarterposition_options_and_more'),
        ('users', '0008_rsouser_is_verified'),
    ]

    operations = [
        migrations.CreateModel(
            name='UsersParent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parent_last_name', models.CharField(max_length=150, verbose_name='Фамилия')),
                ('parent_first_name', models.CharField(max_length=150, verbose_name='Имя')),
                ('parent_patronymic_name', models.CharField(max_length=150, verbose_name='Отчество')),
                ('parent_date_of_birth', models.DateField(verbose_name='Дата рождения')),
                ('relationship', models.CharField(choices=[('father', 'Отец'), ('mother', 'Мать'), ('guardian', 'Опекун')], max_length=8, verbose_name='Кем является')),
                ('parent_phone_number', models.CharField(default='+7', max_length=30, verbose_name='Номер телефона')),
                ('russian_passport', models.BooleanField(default=True, verbose_name='Паспорт гражданина РФ')),
                ('passport_number', models.CharField(max_length=50, verbose_name='Номер и серия')),
                ('passport_date', models.DateField(verbose_name='Дата выдачи')),
                ('passport_authority', models.CharField(max_length=150, verbose_name='Кем выдан')),
                ('city', models.CharField(max_length=50, verbose_name='Населенный пункт')),
                ('address', models.CharField(max_length=200, verbose_name='Улица, дом, квартира')),
                ('region', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='headquarters.region', verbose_name='Регион')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='parent', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
        ),
    ]
