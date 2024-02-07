# Generated by Django 4.2.7 on 2024-02-05 21:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('headquarters', '0027_alter_educationalinstitution_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='detachment',
            name='educational_institution',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='detachments', to='headquarters.educationalinstitution', verbose_name='Привязка к учебному заведению'),
        ),
    ]
