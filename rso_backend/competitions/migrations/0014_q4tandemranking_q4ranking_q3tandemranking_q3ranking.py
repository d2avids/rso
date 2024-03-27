# Generated by Django 4.2.7 on 2024-03-24 19:39

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('headquarters', '0029_alter_centralheadquarter_name_alter_detachment_name_and_more'),
        ('competitions', '0013_alter_q2detachmentreport_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Q4TandemRanking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('place', models.FloatField(default=8.0, verbose_name='Итоговое место по показателю в тандеме')),
                ('competition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s', to='competitions.competitions', verbose_name='Конкурс')),
                ('detachment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_main_detachment', to='headquarters.detachment', verbose_name='Отряд-наставник')),
                ('junior_detachment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_junior_detachment', to='headquarters.detachment', verbose_name='Младший отряд')),
            ],
            options={
                'verbose_name': 'Тандем-место по 2 показателю',
                'verbose_name_plural': 'Тандем-места по 2 показателю',
            },
        ),
        migrations.CreateModel(
            name='Q4Ranking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('place', models.PositiveSmallIntegerField(default=3, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(8)], verbose_name='Итоговое место по показателю')),
                ('competition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s', to='competitions.competitions', verbose_name='Конкурс')),
                ('detachment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s', to='headquarters.detachment', verbose_name='Отряд')),
            ],
            options={
                'verbose_name': 'Место по 2 показателю',
                'verbose_name_plural': 'Места по 2 показателю',
            },
        ),
        migrations.CreateModel(
            name='Q3TandemRanking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('place', models.FloatField(default=8.0, verbose_name='Итоговое место по показателю в тандеме')),
                ('competition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s', to='competitions.competitions', verbose_name='Конкурс')),
                ('detachment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_main_detachment', to='headquarters.detachment', verbose_name='Отряд-наставник')),
                ('junior_detachment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s_junior_detachment', to='headquarters.detachment', verbose_name='Младший отряд')),
            ],
            options={
                'verbose_name': 'Тандем-место по 2 показателю',
                'verbose_name_plural': 'Тандем-места по 2 показателю',
            },
        ),
        migrations.CreateModel(
            name='Q3Ranking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('place', models.PositiveSmallIntegerField(default=3, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(8)], verbose_name='Итоговое место по показателю')),
                ('competition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s', to='competitions.competitions', verbose_name='Конкурс')),
                ('detachment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='%(class)s', to='headquarters.detachment', verbose_name='Отряд')),
            ],
            options={
                'verbose_name': 'Место по 2 показателю',
                'verbose_name_plural': 'Места по 2 показателю',
            },
        ),
    ]