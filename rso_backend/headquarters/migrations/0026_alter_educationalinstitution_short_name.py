# Generated by Django 4.2.7 on 2024-02-02 20:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('headquarters', '0025_region_code_alter_regionalheadquarter_region'),
    ]

    operations = [
        migrations.AlterField(
            model_name='educationalinstitution',
            name='short_name',
            field=models.CharField(max_length=100, verbose_name='Короткое название образовательной организации (например, РГГУ)'),
        ),
    ]
