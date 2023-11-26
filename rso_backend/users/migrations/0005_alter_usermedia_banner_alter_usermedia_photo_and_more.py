# Generated by Django 4.2.7 on 2023-11-24 21:26

from django.db import migrations, models

import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_rsouser_region'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usermedia',
            name='banner',
            field=models.ImageField(blank=True, upload_to=users.models.image_path, verbose_name='Баннер личной страницы'),
        ),
        migrations.AlterField(
            model_name='usermedia',
            name='photo',
            field=models.ImageField(blank=True, upload_to=users.models.image_path, verbose_name='Аватарка'),
        ),
        migrations.AlterField(
            model_name='usermedia',
            name='photo1',
            field=models.ImageField(blank=True, upload_to=users.models.image_path, verbose_name='Фото 1'),
        ),
        migrations.AlterField(
            model_name='usermedia',
            name='photo2',
            field=models.ImageField(blank=True, upload_to=users.models.image_path, verbose_name='Фото 2'),
        ),
        migrations.AlterField(
            model_name='usermedia',
            name='photo3',
            field=models.ImageField(blank=True, upload_to=users.models.image_path, verbose_name='Фото 3'),
        ),
        migrations.AlterField(
            model_name='usermedia',
            name='photo4',
            field=models.ImageField(blank=True, upload_to=users.models.image_path, verbose_name='Фото 4'),
        ),
        migrations.AlterField(
            model_name='userstatementdocuments',
            name='additional_document',
            field=models.FileField(blank=True, null=True, upload_to=users.models.document_path, verbose_name='Дополнительный документ'),
        ),
        migrations.AlterField(
            model_name='userstatementdocuments',
            name='consent_personal_data',
            field=models.FileField(blank=True, null=True, upload_to=users.models.document_path, verbose_name='Согласие на обработку персональных данных'),
        ),
        migrations.AlterField(
            model_name='userstatementdocuments',
            name='consent_personal_data_representative',
            field=models.FileField(blank=True, null=True, upload_to=users.models.document_path, verbose_name='Согласие официального представителя на обработку персональных данных несовершеннолетнего'),
        ),
        migrations.AlterField(
            model_name='userstatementdocuments',
            name='employment_document',
            field=models.FileField(blank=True, null=True, upload_to=users.models.document_path, verbose_name='Трудовая книжка'),
        ),
        migrations.AlterField(
            model_name='userstatementdocuments',
            name='inn_file',
            field=models.FileField(blank=True, null=True, upload_to=users.models.document_path, verbose_name='ИИН'),
        ),
        migrations.AlterField(
            model_name='userstatementdocuments',
            name='international_passport',
            field=models.FileField(blank=True, null=True, upload_to=users.models.document_path, verbose_name='Загранпаспорт'),
        ),
        migrations.AlterField(
            model_name='userstatementdocuments',
            name='military_document',
            field=models.FileField(blank=True, null=True, upload_to=users.models.document_path, verbose_name='Военный билет'),
        ),
        migrations.AlterField(
            model_name='userstatementdocuments',
            name='passport',
            field=models.FileField(blank=True, null=True, upload_to=users.models.document_path, verbose_name='Паспорт гражданина РФ'),
        ),
        migrations.AlterField(
            model_name='userstatementdocuments',
            name='passport_representative',
            field=models.FileField(blank=True, null=True, upload_to=users.models.document_path, verbose_name='Паспорт законного представителя'),
        ),
        migrations.AlterField(
            model_name='userstatementdocuments',
            name='snils_file',
            field=models.FileField(blank=True, null=True, upload_to=users.models.document_path, verbose_name='СНИЛС'),
        ),
        migrations.AlterField(
            model_name='userstatementdocuments',
            name='statement',
            field=models.FileField(blank=True, null=True, upload_to=users.models.document_path, verbose_name='Заявление на вступлении в РСО'),
        ),
    ]