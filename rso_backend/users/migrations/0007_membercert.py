# Generated by Django 4.2.7 on 2023-12-26 11:54

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_usercertinternal_usercertexternal'),
    ]

    operations = [
        migrations.CreateModel(
            name='MemberCert',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cert_start_date', models.DateField(auto_now_add=True, verbose_name='Дата начала действия справки')),
                ('cert_end_date', models.DateField(verbose_name='Дата окончания действия справки')),
                ('recipient', models.CharField(max_length=250, verbose_name='Справка выдана для предоставления')),
                ('issue_date', models.DateField(auto_now_add=True, verbose_name='Дата выдачи справки')),
                ('number', models.CharField(default='б/н', max_length=40, verbose_name='Номер справки')),
                ('signatory', models.CharField(max_length=250, verbose_name='ФИО подписывающего лица')),
                ('position_procuration', models.CharField(max_length=250, verbose_name='Должность подписывающего лица, доверенность')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='member_cert', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Выданная справка о членстве в РСО.',
                'verbose_name_plural': 'Выданные справки о членстве в РСО.',
            },
        ),
    ]
