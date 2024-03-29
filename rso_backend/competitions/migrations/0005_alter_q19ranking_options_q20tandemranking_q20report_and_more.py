# Generated by Django 4.2.7 on 2024-03-24 00:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        (
            "headquarters",
            "0029_alter_centralheadquarter_name_alter_detachment_name_and_more",
        ),
        ("competitions", "0004_alter_q13tandemranking_place_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="q19ranking",
            options={
                "verbose_name": "Место по 19 показателю",
                "verbose_name_plural": "Места по 19 показателю",
            },
        ),
        migrations.CreateModel(
            name="Q20TandemRanking",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "place",
                    models.PositiveSmallIntegerField(
                        verbose_name="Итоговое место по показателю 20"
                    ),
                ),
                (
                    "competition",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(class)s",
                        to="competitions.competitions",
                        verbose_name="Конкурс",
                    ),
                ),
                (
                    "detachment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(class)s_main_detachment",
                        to="headquarters.detachment",
                        verbose_name="Отряд-наставник",
                    ),
                ),
                (
                    "junior_detachment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(class)s_junior_detachment",
                        to="headquarters.detachment",
                        verbose_name="Младший отряд",
                    ),
                ),
            ],
            options={
                "verbose_name": "Тандем-место по 20 показателю",
                "verbose_name_plural": "Тандем-места по 20 показателю",
            },
        ),
        migrations.CreateModel(
            name="Q20Report",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("is_verified", models.BooleanField(default=False)),
                (
                    "link_emblem",
                    models.URLField(
                        blank=True,
                        max_length=1000,
                        null=True,
                        verbose_name="Ссылка на фото эмблемы",
                    ),
                ),
                (
                    "link_emblem_img",
                    models.URLField(
                        blank=True,
                        max_length=1000,
                        null=True,
                        verbose_name="Ссылка на изображение эмблемы",
                    ),
                ),
                (
                    "link_flag",
                    models.URLField(
                        blank=True,
                        max_length=1000,
                        null=True,
                        verbose_name="Ссылка на фото флага",
                    ),
                ),
                (
                    "link_flag_img",
                    models.URLField(
                        blank=True,
                        max_length=1000,
                        null=True,
                        verbose_name="Ссылка на изображение флага",
                    ),
                ),
                (
                    "link_banner",
                    models.URLField(
                        blank=True,
                        max_length=1000,
                        null=True,
                        verbose_name="Ссылка на фото знамени",
                    ),
                ),
                (
                    "link_banner_img",
                    models.URLField(
                        blank=True,
                        max_length=1000,
                        null=True,
                        verbose_name="Ссылка на изображение знамени",
                    ),
                ),
                (
                    "score",
                    models.PositiveSmallIntegerField(default=0, verbose_name="Очки"),
                ),
                (
                    "competition",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(class)s_competition_reports",
                        to="competitions.competitions",
                        verbose_name="Конкурс",
                    ),
                ),
                (
                    "detachment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(class)s_detachment_reports",
                        to="headquarters.detachment",
                        verbose_name="Отряд",
                    ),
                ),
            ],
            options={
                "verbose_name": "Отчет по 20 показателю",
                "verbose_name_plural": "Отчеты по 20 показателю",
            },
        ),
        migrations.CreateModel(
            name="Q20Ranking",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "place",
                    models.PositiveSmallIntegerField(
                        verbose_name="Итоговое место по показателю 20"
                    ),
                ),
                (
                    "competition",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(class)s",
                        to="competitions.competitions",
                        verbose_name="Конкурс",
                    ),
                ),
                (
                    "detachment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(class)s",
                        to="headquarters.detachment",
                        verbose_name="Отряд",
                    ),
                ),
            ],
            options={
                "verbose_name": "Место по 20 показателю",
                "verbose_name_plural": "Места по 20 показателю",
            },
        ),
    ]
