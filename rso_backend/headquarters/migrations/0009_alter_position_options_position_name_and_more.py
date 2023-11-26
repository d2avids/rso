# Generated by Django 4.2.7 on 2023-11-25 21:49

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('headquarters', '0008_position'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='position',
            options={'verbose_name': 'Должность', 'verbose_name_plural': 'Должности'},
        ),
        migrations.AddField(
            model_name='position',
            name='name',
            field=models.CharField(default=1, max_length=150, verbose_name='Должность'),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='UserRegionalHeadquarterPosition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_trusted', models.BooleanField(default=False, verbose_name='Доверенный')),
                ('headquarter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='headquarters.regionalheadquarter', verbose_name='Региональный штаб')),
                ('position', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='headquarters.position', verbose_name='Должность')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserLocalHeadquarterPosition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_trusted', models.BooleanField(default=False, verbose_name='Доверенный')),
                ('headquarter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='headquarters.localheadquarter', verbose_name='Локальный штаб')),
                ('position', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='headquarters.position', verbose_name='Должность')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserEducationalHeadquarterPosition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_trusted', models.BooleanField(default=False, verbose_name='Доверенный')),
                ('headquarter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='headquarters.educationalheadquarter', verbose_name='Образовательный штаб')),
                ('position', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='headquarters.position', verbose_name='Должность')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserDistrictHeadquarterPosition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_trusted', models.BooleanField(default=False, verbose_name='Доверенный')),
                ('headquarter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='headquarters.districtheadquarter', verbose_name='Окружной штаб')),
                ('position', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='headquarters.position', verbose_name='Должность')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserDetachmentPosition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('detachment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='headquarters.detachment', verbose_name='Отряд')),
            ],
        ),
        migrations.CreateModel(
            name='UserCentralHeadquarterPosition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_trusted', models.BooleanField(default=False, verbose_name='Доверенный')),
                ('headquarter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='headquarters.centralheadquarter', verbose_name='Центральный штаб')),
                ('position', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='headquarters.position', verbose_name='Должность')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]