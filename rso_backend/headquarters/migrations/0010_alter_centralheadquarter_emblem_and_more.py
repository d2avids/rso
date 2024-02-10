# Generated by Django 4.2.7 on 2023-12-09 07:35

from django.db import migrations, models

import headquarters.utils


class Migration(migrations.Migration):

    dependencies = [
        ('headquarters', '0009_alter_centralheadquarter_founding_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='centralheadquarter',
            name='emblem',
            field=models.ImageField(blank=True, null=True, upload_to=headquarters.utils.image_path, verbose_name='Эмблема'),
        ),
        migrations.AlterField(
            model_name='detachment',
            name='emblem',
            field=models.ImageField(blank=True, null=True, upload_to=headquarters.utils.image_path, verbose_name='Эмблема'),
        ),
        migrations.AlterField(
            model_name='districtheadquarter',
            name='emblem',
            field=models.ImageField(blank=True, null=True, upload_to=headquarters.utils.image_path, verbose_name='Эмблема'),
        ),
        migrations.AlterField(
            model_name='educationalheadquarter',
            name='emblem',
            field=models.ImageField(blank=True, null=True, upload_to=headquarters.utils.image_path, verbose_name='Эмблема'),
        ),
        migrations.AlterField(
            model_name='localheadquarter',
            name='emblem',
            field=models.ImageField(blank=True, null=True, upload_to=headquarters.utils.image_path, verbose_name='Эмблема'),
        ),
        migrations.AlterField(
            model_name='regionalheadquarter',
            name='emblem',
            field=models.ImageField(blank=True, null=True, upload_to=headquarters.utils.image_path, verbose_name='Эмблема'),
        ),
    ]
