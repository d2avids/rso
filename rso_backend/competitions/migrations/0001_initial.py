# Generated by Django 4.2.7 on 2024-01-30 14:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('headquarters', '0025_region_code_alter_regionalheadquarter_region'),
    ]

    operations = [
        migrations.CreateModel(
            name='Competitions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True, verbose_name='Название')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания')),
                ('start_date', models.DateField(blank=True, null=True, verbose_name='Дата начала')),
                ('end_date', models.DateField(blank=True, null=True, verbose_name='Дата окончания')),
            ],
            options={
                'verbose_name': 'Конкурс',
                'verbose_name_plural': 'Конкурсы',
            },
        ),
        migrations.CreateModel(
            name='CompetitionParticipants',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания заявки')),
                ('competition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='competition_participants', to='competitions.competitions', verbose_name='Конкурс')),
                ('detachment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='competition_participants', to='headquarters.detachment', verbose_name='Отряд')),
                ('junior_detachment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='junior_competition_participants', to='headquarters.detachment', verbose_name='Младший отряд')),
            ],
            options={
                'verbose_name': 'Участник конкурса',
                'verbose_name_plural': 'Участники конкурса',
            },
        ),
        migrations.CreateModel(
            name='CompetitionApplications',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата и время создания заявки')),
                ('is_confirmed_by_junior', models.BooleanField(default=False, verbose_name='Подтверждено младшим отрядом')),
                ('competition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='competition_applications', to='competitions.competitions', verbose_name='Конкурс')),
                ('detachment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='competition_applications', to='headquarters.detachment', verbose_name='Отряд')),
                ('junior_detachment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='junior_competition_applications', to='headquarters.detachment', verbose_name='Младший отряд')),
            ],
            options={
                'verbose_name': 'Заявка на участие в конкурсе',
                'verbose_name_plural': 'Заявки на участие в конкурсе',
            },
        ),
        migrations.AddConstraint(
            model_name='competitionparticipants',
            constraint=models.UniqueConstraint(fields=('competition', 'detachment'), name='unique_detachment_participant'),
        ),
        migrations.AddConstraint(
            model_name='competitionparticipants',
            constraint=models.UniqueConstraint(fields=('competition', 'junior_detachment'), name='unique_junior_detachment_participant'),
        ),
        migrations.AddConstraint(
            model_name='competitionparticipants',
            constraint=models.UniqueConstraint(fields=('detachment', 'junior_detachment'), name='unique_tandem_participant'),
        ),
        migrations.AddConstraint(
            model_name='competitionapplications',
            constraint=models.UniqueConstraint(fields=('competition', 'detachment'), name='unique_detachment_application_for_competition'),
        ),
        migrations.AddConstraint(
            model_name='competitionapplications',
            constraint=models.UniqueConstraint(fields=('competition', 'junior_detachment'), name='unique_junior_detachment_application'),
        ),
        migrations.AddConstraint(
            model_name='competitionapplications',
            constraint=models.UniqueConstraint(fields=('detachment', 'junior_detachment'), name='unique_tandem_application'),
        ),
    ]
