# Generated by Django 4.2.7 on 2024-03-21 16:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0027_alter_userregion_reg_house_alter_userregion_reg_town'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usereducation',
            name='study_year',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='Курс'),
        ),
    ]