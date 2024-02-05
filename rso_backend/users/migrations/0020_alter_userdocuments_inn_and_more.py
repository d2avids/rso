# Generated by Django 4.2.7 on 2024-01-30 12:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0019_alter_userprivacysettings_privacy_about_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userdocuments',
            name='inn',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='ИНН'),
        ),
        migrations.AlterField(
            model_name='userdocuments',
            name='international_pass',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='Загранпаспорт номер'),
        ),
        migrations.AlterField(
            model_name='userdocuments',
            name='mil_reg_doc_ser_num',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='Номер и серия документа воинского учета'),
        ),
        migrations.AlterField(
            model_name='userdocuments',
            name='pass_address',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Место регистрации по паспорту'),
        ),
        migrations.AlterField(
            model_name='userdocuments',
            name='pass_ser_num',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Номер и серия паспорта'),
        ),
        migrations.AlterField(
            model_name='userdocuments',
            name='pass_town',
            field=models.CharField(blank=True, default='', max_length=200, verbose_name='Город рождения'),
        ),
        migrations.AlterField(
            model_name='userdocuments',
            name='pass_whom',
            field=models.CharField(blank=True, max_length=230, null=True, verbose_name='Кем выдан паспорт'),
        ),
        migrations.AlterField(
            model_name='userdocuments',
            name='snils',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='СНИЛС'),
        ),
        migrations.AlterField(
            model_name='userdocuments',
            name='work_book_num',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='Трудовая книжка номер'),
        ),
        migrations.AlterField(
            model_name='userforeigndocuments',
            name='foreign_pass_whom',
            field=models.CharField(blank=True, max_length=230, null=True, verbose_name='Кем выдан'),
        ),
        migrations.AlterField(
            model_name='userforeigndocuments',
            name='inn',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='ИНН'),
        ),
        migrations.AlterField(
            model_name='userforeigndocuments',
            name='name',
            field=models.CharField(max_length=30, verbose_name='Документ, удостоверяющий личность'),
        ),
        migrations.AlterField(
            model_name='userforeigndocuments',
            name='snils',
            field=models.CharField(blank=True, max_length=30, null=True, verbose_name='СНИЛС'),
        ),
    ]
