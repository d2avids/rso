# Generated by Django 4.2.7 on 2024-01-25 07:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('headquarters', '0024_merge_20240125_1038'),
    ]

    operations = [
        migrations.AddField(
            model_name='region',
            name='code',
            field=models.SmallIntegerField(blank=True, null=True, verbose_name='Код региона'),
        ),
        migrations.AlterField(
            model_name='regionalheadquarter',
            name='region',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='headquarters', to='headquarters.region', verbose_name='Регион'),
        ),
    ]
