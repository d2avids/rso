# Generated by Django 4.2.7 on 2024-01-07 10:02

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("headquarters", "0019_alter_position_name"),
        ("events", "0010_alter_event_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="MultiEventApplication",
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
                    "organizer_id",
                    models.PositiveIntegerField(
                        verbose_name="Идентификатор организатора"
                    ),
                ),
                (
                    "is_approved",
                    models.BooleanField(default=False, verbose_name="Одобрено"),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Дата и время создания заявки"
                    ),
                ),
                (
                    "detachment",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="multi_event_applications",
                        to="headquarters.detachment",
                        verbose_name="Отряд",
                    ),
                ),
                (
                    "educational_headquarter",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="multi_event_applications",
                        to="headquarters.educationalheadquarter",
                        verbose_name="Образовательный штаб",
                    ),
                ),
                (
                    "event",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="multi_event_applications",
                        to="events.event",
                        verbose_name="Мероприятие",
                    ),
                ),
                (
                    "local_headquarter",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="multi_event_applications",
                        to="headquarters.localheadquarter",
                        verbose_name="Местный штаб",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="multi_event_applications",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Боец",
                    ),
                ),
            ],
            options={
                "verbose_name": "Заявка на участие в многоэтапном мероприятии",
                "verbose_name_plural": "Заявки на участие в многоэтапном мероприятии",
                "ordering": ["-id"],
            },
        ),
        migrations.AddConstraint(
            model_name="multieventapplication",
            constraint=models.UniqueConstraint(
                fields=("event", "local_headquarter"),
                name="unique_local_headquarter_application",
            ),
        ),
        migrations.AddConstraint(
            model_name="multieventapplication",
            constraint=models.UniqueConstraint(
                fields=("event", "educational_headquarter"),
                name="unique_educational_headquarter_application",
            ),
        ),
        migrations.AddConstraint(
            model_name="multieventapplication",
            constraint=models.UniqueConstraint(
                fields=("event", "detachment"), name="unique_detachment_application"
            ),
        ),
        migrations.AddConstraint(
            model_name="multieventapplication",
            constraint=models.UniqueConstraint(
                fields=("event", "user"), name="unique_user_application"
            ),
        ),
    ]
