# Generated by Django 4.2.7 on 2024-02-05 21:13

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0021_alter_usereducation_study_specialty'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserVerificationLogs',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now_add=True, verbose_name='Дата действия')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Сообщение лога')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='verification_logs', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
                ('verification_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='verificator_logs', to=settings.AUTH_USER_MODEL, verbose_name='Верифицирующий пользователь')),
            ],
            options={
                'verbose_name': 'Лог верификации юзеров.',
                'verbose_name_plural': 'Логи верификации юзеров.',
            },
        ),
    ]
