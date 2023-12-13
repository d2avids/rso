# Generated by Django 4.2.7 on 2023-12-13 08:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('headquarters', '0010_alter_centralheadquarter_emblem_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='regionalheadquarter',
            name='case_name',
            field=models.CharField(default=1, max_length=250, verbose_name='Наименование штаба в Предложном падеже (для справок)'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='regionalheadquarter',
            name='conference_date',
            field=models.DateField(blank=True, null=True, verbose_name='Дата учр. конференции регионального штаба'),
        ),
        migrations.AddField(
            model_name='regionalheadquarter',
            name='legal_address',
            field=models.CharField(default=1, max_length=250, verbose_name='Юридический адрес (для справок)'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='regionalheadquarter',
            name='name_for_certificates',
            field=models.CharField(default=1, max_length=250, verbose_name='Наименование штаба (для справок)'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='regionalheadquarter',
            name='registry_date',
            field=models.DateField(blank=True, null=True, verbose_name='Дата регистрации в реестре молодежных и детских общественных объединений...'),
        ),
        migrations.AddField(
            model_name='regionalheadquarter',
            name='registry_number',
            field=models.CharField(default=1, max_length=250, verbose_name='Наименование штаба в Предложном падеже'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='regionalheadquarter',
            name='requisites',
            field=models.CharField(default=1, max_length=250, verbose_name='Реквизиты (для справок)'),
            preserve_default=False,
        ),
    ]