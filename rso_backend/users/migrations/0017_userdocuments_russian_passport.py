# Generated by Django 4.2.7 on 2024-01-06 12:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0016_usermembercertlogs'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdocuments',
            name='russian_passport',
            field=models.BooleanField(default=True, verbose_name='Паспорт гражданина РФ'),
        ),
    ]
