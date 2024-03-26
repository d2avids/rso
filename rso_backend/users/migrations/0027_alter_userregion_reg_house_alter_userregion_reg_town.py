# Generated by Django 4.2.7 on 2024-03-03 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0026_rsouser_is_rso_member'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userregion',
            name='reg_house',
            field=models.CharField(blank=True, max_length=250, null=True, verbose_name='Улица, дом, кв. прописки'),
        ),
        migrations.AlterField(
            model_name='userregion',
            name='reg_town',
            field=models.CharField(blank=True, max_length=80, null=True, verbose_name='Населенный пункт прописки'),
        ),
    ]