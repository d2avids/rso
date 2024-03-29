# Generated by Django 4.2.7 on 2024-03-24 11:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('competitions', '0008_alter_q2detachmentreport_commander_link_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='q2ranking',
            options={'verbose_name': 'Место по 2 показателю', 'verbose_name_plural': 'Места по 2 показателю'},
        ),
        migrations.AlterModelOptions(
            name='q2tandemranking',
            options={'verbose_name': 'Тандем-место по 2 показателю', 'verbose_name_plural': 'Тандем-места по 2 показателю'},
        ),
        migrations.RemoveConstraint(
            model_name='q2ranking',
            name='unique_ranking_q2ranking',
        ),
        migrations.RemoveConstraint(
            model_name='q2tandemranking',
            name='unique_tandem_ranking_q2tandemranking',
        ),
        migrations.RemoveConstraint(
            model_name='q2tandemranking',
            name='unique_main_ranking_q2tandemranking',
        ),
        migrations.RemoveConstraint(
            model_name='q2tandemranking',
            name='unique_junior_ranking_q2tandemranking',
        ),
        migrations.RemoveField(
            model_name='q2detachmentreport',
            name='individual_place',
        ),
    ]
