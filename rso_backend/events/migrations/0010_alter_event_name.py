# Generated by Django 4.2.7 on 2024-01-05 21:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0009_alter_eventissueanswer_options_eventuserdocument'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='name',
            field=models.CharField(max_length=100, verbose_name='Название мероприятия'),
        ),
    ]