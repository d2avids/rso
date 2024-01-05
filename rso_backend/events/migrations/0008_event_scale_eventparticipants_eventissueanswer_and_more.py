# Generated by Django 4.2.7 on 2024-01-03 19:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("events", "0007_event_author"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="scale",
            field=models.CharField(
                choices=[
                    ("detachments", "Отрядное"),
                    ("educationals", "Мероприятие ОО"),
                    ("locals", "Городское"),
                    ("regionals", "Региональное"),
                    ("districts", "Мероприятие ОО"),
                    ("central", "Отрядное ОО"),
                ],
                default="detachments",
                max_length=20,
                verbose_name="Масштаб",
            ),
        ),
        migrations.CreateModel(
            name="EventParticipants",
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
                    "event",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="event_participants",
                        to="events.event",
                        verbose_name="Мероприятие",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="event_participants",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Пользователь",
                    ),
                ),
            ],
            options={
                "verbose_name": "Участник мероприятия",
                "verbose_name_plural": "Участники мероприятий",
                "ordering": ["-id"],
            },
        ),
        migrations.CreateModel(
            name="EventIssueAnswer",
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
                ("answer", models.TextField(verbose_name="Ответ")),
                (
                    "event",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="issue_answers",
                        to="events.event",
                        verbose_name="Мероприятие",
                    ),
                ),
                (
                    "issue",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="answers",
                        to="events.eventadditionalissue",
                        verbose_name="Вопрос",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="issue_answers",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Пользователь",
                    ),
                ),
            ],
            options={
                "verbose_name": "Ответ на вопрос участника мероприятия",
                "verbose_name_plural": "Ответы на вопросы участников мероприятий",
                "ordering": ["-id"],
            },
        ),
        migrations.CreateModel(
            name="EventApplications",
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
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Дата создания заявки"
                    ),
                ),
                (
                    "event",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="event_applications",
                        to="events.event",
                        verbose_name="Мероприятие",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="event_applications",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Пользователь",
                    ),
                ),
            ],
            options={
                "verbose_name": "Заявка на участие в мероприятии",
                "verbose_name_plural": "Заявки на участие в мероприятиях",
                "ordering": ["-id"],
            },
        ),
        migrations.AddConstraint(
            model_name="eventparticipants",
            constraint=models.UniqueConstraint(
                fields=("event", "user"), name="unique_event_participant"
            ),
        ),
        migrations.AddConstraint(
            model_name="eventissueanswer",
            constraint=models.UniqueConstraint(
                fields=("event", "user", "issue"), name="unique_issue_answer"
            ),
        ),
        migrations.AddConstraint(
            model_name="eventapplications",
            constraint=models.UniqueConstraint(
                fields=("event", "user"), name="unique_event_application"
            ),
        ),
    ]