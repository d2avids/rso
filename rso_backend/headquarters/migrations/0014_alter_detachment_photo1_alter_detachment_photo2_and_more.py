# Generated by Django 4.2.7 on 2023-12-18 15:26

import headquarters.utils
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('headquarters', '0013_remove_regionalheadquarter_first_detachment_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='detachment',
            name='photo1',
            field=models.ImageField(blank=True, null=True, upload_to=headquarters.utils.image_path, verbose_name='Фото 1'),
        ),
        migrations.AlterField(
            model_name='detachment',
            name='photo2',
            field=models.ImageField(blank=True, null=True, upload_to=headquarters.utils.image_path, verbose_name='Фото 2'),
        ),
        migrations.AlterField(
            model_name='detachment',
            name='photo3',
            field=models.ImageField(blank=True, null=True, upload_to=headquarters.utils.image_path, verbose_name='Фото 3'),
        ),
        migrations.AlterField(
            model_name='detachment',
            name='photo4',
            field=models.ImageField(blank=True, null=True, upload_to=headquarters.utils.image_path, verbose_name='Фото 4'),
        ),
    ]
