# Generated by Django 4.2.7 on 2024-03-21 04:46

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("competitions", "0010_alter_q10ranking_options_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="q1report",
            name="score",
            field=models.FloatField(
                validators=[django.core.validators.MinValueValidator(0)],
                verbose_name="Баллы за оплаченный членский взнос",
            ),
        ),
    ]
