# Generated by Django 4.2.7 on 2023-12-13 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('headquarters', '0011_regionalheadquarter_case_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='regionalheadquarter',
            name='first_detachment_date',
            field=models.CharField(blank=True, max_length=4, null=True, verbose_name='Официальная дата (год) появления студенческих отрядов в регионе'),
        ),
        migrations.AlterField(
            model_name='regionalheadquarter',
            name='case_name',
            field=models.CharField(blank=True, max_length=250, null=True, verbose_name='Наименование штаба в Предложном падеже (для справок)'),
        ),
        migrations.AlterField(
            model_name='regionalheadquarter',
            name='legal_address',
            field=models.CharField(blank=True, max_length=250, null=True, verbose_name='Юридический адрес (для справок)'),
        ),
        migrations.AlterField(
            model_name='regionalheadquarter',
            name='name_for_certificates',
            field=models.CharField(max_length=250, verbose_name='Наименование штаба в Им. падеже (для справок)'),
        ),
        migrations.AlterField(
            model_name='regionalheadquarter',
            name='registry_number',
            field=models.CharField(max_length=250, verbose_name='Регистрационный номер в реестре молодежных и детских общественных объединений...'),
        ),
        migrations.AlterField(
            model_name='regionalheadquarter',
            name='requisites',
            field=models.CharField(blank=True, max_length=250, null=True, verbose_name='Реквизиты (для справок)'),
        ),
    ]