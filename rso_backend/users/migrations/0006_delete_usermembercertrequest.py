# Generated by Django 4.2.7 on 2023-12-19 06:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_usercertinternal_alter_rsouser_email_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='UserMemberCertRequest',
        ),
    ]
