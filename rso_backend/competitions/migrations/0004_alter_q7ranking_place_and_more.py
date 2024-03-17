# Generated by Django 4.2.7 on 2024-03-17 05:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        (
            "headquarters",
            "0029_alter_centralheadquarter_name_alter_detachment_name_and_more",
        ),
        ("competitions", "0003_alter_q13ranking_options_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="q7ranking",
            name="place",
            field=models.PositiveSmallIntegerField(
                verbose_name="Итоговое место по показателю 7"
            ),
        ),
        migrations.AlterField(
            model_name="q7tandemranking",
            name="junior_detachment",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="%(class)s_junior_detachment",
                to="headquarters.detachment",
                verbose_name="Младший отряд",
            ),
        ),
        migrations.AlterField(
            model_name="q7tandemranking",
            name="place",
            field=models.PositiveSmallIntegerField(
                verbose_name="Итоговое место по показателю 7"
            ),
        ),
    ]
