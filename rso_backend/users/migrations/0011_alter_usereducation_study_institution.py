# Generated by Django 4.2.7 on 2023-12-28 09:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('headquarters', '0016_merge_20231227_2119'),
        ('users', '0010_merge_20231227_2253'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usereducation',
            name='study_institution',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='users_education', to='headquarters.educationalinstitution', verbose_name='Образовательная организация'),
        ),
    ]
