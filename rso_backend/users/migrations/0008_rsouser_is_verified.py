# Generated by Django 4.2.7 on 2023-11-26 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_remove_usereducation_study_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='rsouser',
            name='is_verified',
            field=models.BooleanField(default=False, verbose_name='Статус верификации'),
        ),
    ]