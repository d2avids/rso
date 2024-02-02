# Generated by Django 4.2.7 on 2024-02-02 20:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('headquarters', '0026_alter_educationalinstitution_short_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='educationalinstitution',
            name='name',
            field=models.CharField(max_length=300, unique=True, verbose_name='Полное название образовательной организации'),
        ),
    ]