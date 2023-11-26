# Generated by Django 4.2.7 on 2023-11-24 15:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('headquarters', '0002_remove_region_branch_alter_detachment_commander_and_more'),
        ('users', '0003_alter_userdocuments_user_alter_usereducation_user_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='rsouser',
            name='region',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='headquarters.region', verbose_name='Регион ОО'),
        ),
    ]
