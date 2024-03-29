# Generated by Django 4.2.7 on 2023-12-03 12:05

import django.db.models.deletion
from django.db import migrations, models

import headquarters.utils


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, verbose_name='Название направления')),
            ],
            options={
                'verbose_name': 'Направление',
                'verbose_name_plural': 'направления',
            },
        ),
        migrations.CreateModel(
            name='CentralHeadquarter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название')),
                ('about', models.CharField(blank=True, max_length=500, null=True, verbose_name='Описание')),
                ('emblem', models.ImageField(blank=True, null=True, upload_to=headquarters.utils.image_path, verbose_name='Эмблема')),
                ('social_vk', models.CharField(blank=True, default='https://vk.com/', max_length=50, null=True, verbose_name='Ссылка ВК')),
                ('social_tg', models.CharField(blank=True, default='https://', max_length=50, null=True, verbose_name='Ссылка Телеграм')),
                ('banner', models.ImageField(blank=True, null=True, upload_to=headquarters.utils.image_path, verbose_name='Баннер')),
                ('slogan', models.CharField(blank=True, max_length=100, null=True, verbose_name='Девиз')),
                ('founding_date', models.DateField(blank=True, null=True, verbose_name='Дата основания')),
            ],
            options={
                'verbose_name': 'Центральный штаб',
                'verbose_name_plural': 'Центральные штабы',
            },
        ),
        migrations.CreateModel(
            name='Detachment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название')),
                ('about', models.CharField(blank=True, max_length=500, null=True, verbose_name='Описание')),
                ('emblem', models.ImageField(blank=True, null=True, upload_to=headquarters.utils.image_path, verbose_name='Эмблема')),
                ('social_vk', models.CharField(blank=True, default='https://vk.com/', max_length=50, null=True, verbose_name='Ссылка ВК')),
                ('social_tg', models.CharField(blank=True, default='https://', max_length=50, null=True, verbose_name='Ссылка Телеграм')),
                ('banner', models.ImageField(blank=True, null=True, upload_to=headquarters.utils.image_path, verbose_name='Баннер')),
                ('slogan', models.CharField(blank=True, max_length=100, null=True, verbose_name='Девиз')),
                ('founding_date', models.DateField(blank=True, null=True, verbose_name='Дата основания')),
                ('area', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='headquarters.area', verbose_name='Направление')),
            ],
            options={
                'verbose_name': 'Отряд',
                'verbose_name_plural': 'Отряды',
            },
        ),
        migrations.CreateModel(
            name='DistrictHeadquarter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название')),
                ('about', models.CharField(blank=True, max_length=500, null=True, verbose_name='Описание')),
                ('emblem', models.ImageField(blank=True, null=True, upload_to=headquarters.utils.image_path, verbose_name='Эмблема')),
                ('social_vk', models.CharField(blank=True, default='https://vk.com/', max_length=50, null=True, verbose_name='Ссылка ВК')),
                ('social_tg', models.CharField(blank=True, default='https://', max_length=50, null=True, verbose_name='Ссылка Телеграм')),
                ('banner', models.ImageField(blank=True, null=True, upload_to=headquarters.utils.image_path, verbose_name='Баннер')),
                ('slogan', models.CharField(blank=True, max_length=100, null=True, verbose_name='Девиз')),
                ('founding_date', models.DateField(blank=True, null=True, verbose_name='Дата основания')),
                ('central_headquarter', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='district_headquarters', to='headquarters.centralheadquarter', verbose_name='Привязка к ЦШ')),
            ],
            options={
                'verbose_name': 'Окружной штаб',
                'verbose_name_plural': 'Окружные штабы',
            },
        ),
        migrations.CreateModel(
            name='EducationalHeadquarter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название')),
                ('about', models.CharField(blank=True, max_length=500, null=True, verbose_name='Описание')),
                ('emblem', models.ImageField(blank=True, null=True, upload_to=headquarters.utils.image_path, verbose_name='Эмблема')),
                ('social_vk', models.CharField(blank=True, default='https://vk.com/', max_length=50, null=True, verbose_name='Ссылка ВК')),
                ('social_tg', models.CharField(blank=True, default='https://', max_length=50, null=True, verbose_name='Ссылка Телеграм')),
                ('banner', models.ImageField(blank=True, null=True, upload_to=headquarters.utils.image_path, verbose_name='Баннер')),
                ('slogan', models.CharField(blank=True, max_length=100, null=True, verbose_name='Девиз')),
                ('founding_date', models.DateField(blank=True, null=True, verbose_name='Дата основания')),
            ],
            options={
                'verbose_name': 'Образовательный штаб',
                'verbose_name_plural': 'Образовательные штабы',
            },
        ),
        migrations.CreateModel(
            name='LocalHeadquarter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название')),
                ('about', models.CharField(blank=True, max_length=500, null=True, verbose_name='Описание')),
                ('emblem', models.ImageField(blank=True, null=True, upload_to=headquarters.utils.image_path, verbose_name='Эмблема')),
                ('social_vk', models.CharField(blank=True, default='https://vk.com/', max_length=50, null=True, verbose_name='Ссылка ВК')),
                ('social_tg', models.CharField(blank=True, default='https://', max_length=50, null=True, verbose_name='Ссылка Телеграм')),
                ('banner', models.ImageField(blank=True, null=True, upload_to=headquarters.utils.image_path, verbose_name='Баннер')),
                ('slogan', models.CharField(blank=True, max_length=100, null=True, verbose_name='Девиз')),
                ('founding_date', models.DateField(blank=True, null=True, verbose_name='Дата основания')),
            ],
            options={
                'verbose_name': 'Местный штаб',
                'verbose_name_plural': 'Местные штабы',
            },
        ),
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, verbose_name='Должность')),
            ],
            options={
                'verbose_name': 'Должность',
                'verbose_name_plural': 'Должности',
            },
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=100, verbose_name='Название')),
            ],
            options={
                'verbose_name': 'Регион',
                'verbose_name_plural': 'Регионы',
            },
        ),
        migrations.CreateModel(
            name='RegionalHeadquarter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Название')),
                ('about', models.CharField(blank=True, max_length=500, null=True, verbose_name='Описание')),
                ('emblem', models.ImageField(blank=True, null=True, upload_to=headquarters.utils.image_path, verbose_name='Эмблема')),
                ('social_vk', models.CharField(blank=True, default='https://vk.com/', max_length=50, null=True, verbose_name='Ссылка ВК')),
                ('social_tg', models.CharField(blank=True, default='https://', max_length=50, null=True, verbose_name='Ссылка Телеграм')),
                ('banner', models.ImageField(blank=True, null=True, upload_to=headquarters.utils.image_path, verbose_name='Баннер')),
                ('slogan', models.CharField(blank=True, max_length=100, null=True, verbose_name='Девиз')),
                ('founding_date', models.DateField(blank=True, null=True, verbose_name='Дата основания')),
                ('district_headquarter', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='regional_headquarters', to='headquarters.districtheadquarter', verbose_name='Привязка к ОШ')),
                ('region', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='headquarters', to='headquarters.region', verbose_name='Регион')),
            ],
            options={
                'verbose_name': 'Региональный штаб',
                'verbose_name_plural': 'Региональные штабы',
            },
        ),
        migrations.CreateModel(
            name='UserRegionalHeadquarterPosition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_trusted', models.BooleanField(default=False, verbose_name='Доверенный')),
                ('headquarter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='members', to='headquarters.regionalheadquarter', verbose_name='Региональный штаб')),
                ('position', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='headquarters.position', verbose_name='Должность')),
            ],
            options={
                'verbose_name': 'Член регионального штаба',
                'verbose_name_plural': 'Члены региональных штабов',
            },
        ),
        migrations.CreateModel(
            name='UserLocalHeadquarterPosition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_trusted', models.BooleanField(default=False, verbose_name='Доверенный')),
                ('headquarter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='members', to='headquarters.localheadquarter', verbose_name='Локальный штаб')),
                ('position', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='headquarters.position', verbose_name='Должность')),
            ],
            options={
                'verbose_name': 'Член локального штаба',
                'verbose_name_plural': 'Члены локальных штабов',
            },
        ),
        migrations.CreateModel(
            name='UserEducationalHeadquarterPosition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_trusted', models.BooleanField(default=False, verbose_name='Доверенный')),
                ('headquarter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='members', to='headquarters.educationalheadquarter', verbose_name='Образовательный штаб')),
                ('position', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='headquarters.position', verbose_name='Должность')),
            ],
            options={
                'verbose_name': 'Член образовательного штаба',
                'verbose_name_plural': 'Члены образовательных штабов',
            },
        ),
        migrations.CreateModel(
            name='UserDistrictHeadquarterPosition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_trusted', models.BooleanField(default=False, verbose_name='Доверенный')),
                ('headquarter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='members', to='headquarters.districtheadquarter', verbose_name='Окружной штаб')),
                ('position', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='headquarters.position', verbose_name='Должность')),
            ],
            options={
                'verbose_name': 'Член окружного штаба',
                'verbose_name_plural': 'Члены окружных штабов',
            },
        ),
        migrations.CreateModel(
            name='UserDetachmentPosition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_trusted', models.BooleanField(default=False, verbose_name='Доверенный')),
                ('headquarter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='members', to='headquarters.detachment', verbose_name='Отряд')),
                ('position', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='headquarters.position', verbose_name='Должность')),
            ],
            options={
                'verbose_name': 'Член отряда',
                'verbose_name_plural': 'Члены отрядов',
            },
        ),
        migrations.CreateModel(
            name='UserDetachmentApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('detachment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applications', to='headquarters.detachment', verbose_name='Отряд, в который была подана заявка на вступление')),
            ],
            options={
                'verbose_name': 'Заявка на вступление в отряд',
                'verbose_name_plural': 'Заявки на вступление в отряды',
            },
        ),
        migrations.CreateModel(
            name='UserCentralHeadquarterPosition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_trusted', models.BooleanField(default=False, verbose_name='Доверенный')),
                ('headquarter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='members', to='headquarters.centralheadquarter', verbose_name='Центральный штаб')),
                ('position', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='headquarters.position', verbose_name='Должность')),
            ],
            options={
                'verbose_name': 'Член центрального штаба',
                'verbose_name_plural': 'Члены центрального штаба',
            },
        ),
        migrations.AddField(
            model_name='localheadquarter',
            name='regional_headquarter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='local_headquarters', to='headquarters.regionalheadquarter', verbose_name='Привязка к РШ'),
        ),
        migrations.CreateModel(
            name='EducationalInstitution',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('short_name', models.CharField(max_length=50, verbose_name='Короткое название образовательной организации (например, РГГУ)')),
                ('name', models.CharField(max_length=250, unique=True, verbose_name='Полное название образовательной организации')),
                ('rector', models.CharField(blank=True, max_length=250, null=True, verbose_name='ФИО ректора образовательной организации')),
                ('rector_email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='Электронная почта ректора')),
                ('region', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='institutions', to='headquarters.region', verbose_name='Регион')),
            ],
            options={
                'verbose_name': 'Образовательная организация',
                'verbose_name_plural': 'Образовательные организации',
            },
        ),
        migrations.AddField(
            model_name='educationalheadquarter',
            name='educational_institution',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='headquarters', to='headquarters.educationalinstitution', verbose_name='Образовательная организация'),
        ),
        migrations.AddField(
            model_name='educationalheadquarter',
            name='local_headquarter',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='educational_headquarters', to='headquarters.localheadquarter', verbose_name='Привязка к МШ'),
        ),
        migrations.AddField(
            model_name='educationalheadquarter',
            name='regional_headquarter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='educational_headquarters', to='headquarters.regionalheadquarter', verbose_name='Привязка к РШ'),
        ),
        migrations.AddField(
            model_name='detachment',
            name='educational_headquarter',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='detachments', to='headquarters.educationalheadquarter', verbose_name='Привязка к ШОО'),
        ),
        migrations.AddField(
            model_name='detachment',
            name='local_headquarter',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='detachments', to='headquarters.localheadquarter', verbose_name='Привязка к МШ'),
        ),
        migrations.AddField(
            model_name='detachment',
            name='regional_headquarter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='detachments', to='headquarters.regionalheadquarter', verbose_name='Привязка к РШ'),
        ),
    ]
