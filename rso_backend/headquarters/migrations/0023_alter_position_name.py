# Generated by Django 4.2.7 on 2024-01-21 11:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('headquarters', '0022_alter_usercentralheadquarterposition_user_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='position',
            name='name',
            field=models.CharField(default=1, max_length=43, unique=True, verbose_name='Должность'),
            preserve_default=False,
        ),
    ]
