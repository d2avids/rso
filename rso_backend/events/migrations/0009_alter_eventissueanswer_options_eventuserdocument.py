# Generated by Django 4.2.7 on 2024-01-04 02:54

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import events.utils


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("events", "0008_event_scale_eventparticipants_eventissueanswer_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="eventissueanswer",
            options={
                "ordering": ["id"],
                "verbose_name": "Ответ на вопрос участника мероприятия",
                "verbose_name_plural": "Ответы на вопросы участников мероприятий",
            },
        ),
        migrations.CreateModel(
            name="EventUserDocument",
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
                    "document",
                    models.FileField(
                        upload_to=events.utils.document_path,
                        verbose_name="Скан документа. Файл формата pdf, png, jpeg.",
                    ),
                ),
                (
                    "event",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="event_user_documents",
                        to="events.event",
                        verbose_name="Мероприятие",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="event_user_documents",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Пользователь",
                    ),
                ),
            ],
            options={
                "verbose_name": "Скан документа участника мероприятия",
                "verbose_name_plural": "Сканы документов участников мероприятий",
                "ordering": ["-id"],
            },
        ),
    ]
