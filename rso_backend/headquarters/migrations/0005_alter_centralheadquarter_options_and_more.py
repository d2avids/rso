# Generated by Django 4.2.7 on 2023-11-25 10:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('headquarters', '0004_alter_detachment_educational_headquarter'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='centralheadquarter',
            options={'verbose_name': 'Центральный штаб', 'verbose_name_plural': 'Центральные штабы'},
        ),
        migrations.AlterModelOptions(
            name='detachment',
            options={'verbose_name': 'Отряд', 'verbose_name_plural': 'Отряды'},
        ),
        migrations.AlterModelOptions(
            name='districtheadquarter',
            options={'verbose_name': 'Окружной штаб', 'verbose_name_plural': 'Окружные штабы'},
        ),
        migrations.AlterModelOptions(
            name='educationalheadquarter',
            options={'verbose_name': 'Образовательный штаб', 'verbose_name_plural': 'Образовательные штабы'},
        ),
        migrations.AlterModelOptions(
            name='localheadquarter',
            options={'verbose_name': 'Местный штаб', 'verbose_name_plural': 'Местные штабы'},
        ),
        migrations.AlterModelOptions(
            name='regionalheadquarter',
            options={'verbose_name': 'Региональный штаб', 'verbose_name_plural': 'Региональные штабы'},
        ),
        migrations.AddField(
            model_name='detachment',
            name='local_headquarter',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='detachments', to='headquarters.localheadquarter', verbose_name='Привязка к МШ'),
        ),
        migrations.AddField(
            model_name='detachment',
            name='regional_headquarter',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='detachments', to='headquarters.regionalheadquarter', verbose_name='Привязка к РШ'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='educationalheadquarter',
            name='regional_headquarter',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='educational_headquarters', to='headquarters.regionalheadquarter', verbose_name='Привязка к РШ'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='educationalheadquarter',
            name='local_headquarter',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='educational_headquarters', to='headquarters.localheadquarter', verbose_name='Привязка к МШ'),
        ),
    ]