# Generated by Django 4.2.7 on 2023-12-27 18:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_merge_20231227_2119'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='usercertinternal',
            name='user',
        ),
        migrations.DeleteModel(
            name='UserCertExternal',
        ),
        migrations.DeleteModel(
            name='UserCertInternal',
        ),
    ]