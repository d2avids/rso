# Generated by Django 4.2.7 on 2024-02-18 12:29

import competitions.utils
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        (
            "headquarters",
            "0029_alter_centralheadquarter_name_alter_detachment_name_and_more",
        ),
        ("competitions", "0002_score_participationindistrandinterregevents_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="LinksOfParticipationInAllRussianEvents",
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
                ("link", models.URLField(max_length=500, verbose_name="Ссылка")),
            ],
            options={
                "verbose_name": "Ссылка на фотоотчет участия СО во всероссийском мероприятии",
                "verbose_name_plural": "Ссылки на фотоотчет участия СО во всероссийских мероприятиях",
            },
        ),
        migrations.CreateModel(
            name="ParticipationInAllRussianEvents",
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
                    "event_name",
                    models.CharField(
                        max_length=255, verbose_name="Название мероприятия"
                    ),
                ),
                (
                    "certificate_scans",
                    models.FileField(
                        blank=True,
                        null=True,
                        upload_to=competitions.utils.get_certificate_scans_path,
                        verbose_name="Сканы сертификатов",
                    ),
                ),
                (
                    "number_of_participants",
                    models.PositiveIntegerField(
                        default=0,
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(100),
                        ],
                        verbose_name="Количество участников",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Дата и время создания заявки"
                    ),
                ),
                (
                    "is_verified",
                    models.BooleanField(default=False, verbose_name="Подтверждено"),
                ),
            ],
            options={
                "verbose_name": "Участие во всероссийских мероприятиях",
                "verbose_name_plural": "Участия во всероссийских мероприятиях",
                "ordering": ["-competition__id"],
            },
        ),
        migrations.RemoveConstraint(
            model_name="linksofparticipationindistrandinterregevents",
            name="unique_event_link",
        ),
        migrations.AddConstraint(
            model_name="linksofparticipationindistrandinterregevents",
            constraint=models.UniqueConstraint(
                fields=("event", "link"),
                name="unique_event_link_distr_and_interreg_events",
            ),
        ),
        migrations.AddField(
            model_name="participationinallrussianevents",
            name="competition",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="participation_in_all_russian_events",
                to="competitions.competitions",
                verbose_name="Конкурс",
            ),
        ),
        migrations.AddField(
            model_name="participationinallrussianevents",
            name="detachment",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="participation_in_all_russian_events",
                to="headquarters.detachment",
                verbose_name="Отряд",
            ),
        ),
        migrations.AddField(
            model_name="linksofparticipationinallrussianevents",
            name="event",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="links",
                to="competitions.participationinallrussianevents",
                verbose_name="Участие во всероссийских мероприятиях",
            ),
        ),
        migrations.AddConstraint(
            model_name="participationinallrussianevents",
            constraint=models.UniqueConstraint(
                fields=("competition", "detachment", "event_name"),
                name="unique_participation_in_all_russian_events",
            ),
        ),
        migrations.AddConstraint(
            model_name="linksofparticipationinallrussianevents",
            constraint=models.UniqueConstraint(
                fields=("event", "link"), name="unique_event_link_all_russian_events"
            ),
        ),
    ]
