# Generated by Django 4.2.7 on 2023-12-26 13:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_membercert'),
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
