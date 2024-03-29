# Generated by Django 4.2.7 on 2023-12-09 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('headquarters', '0004_detachment_city'),
    ]

    operations = [
        migrations.AlterField(
            model_name='centralheadquarter',
            name='name',
            field=models.CharField(max_length=100, unique=True, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='detachment',
            name='name',
            field=models.CharField(max_length=100, unique=True, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='districtheadquarter',
            name='name',
            field=models.CharField(max_length=100, unique=True, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='educationalheadquarter',
            name='name',
            field=models.CharField(max_length=100, unique=True, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='localheadquarter',
            name='name',
            field=models.CharField(max_length=100, unique=True, verbose_name='Название'),
        ),
        migrations.AlterField(
            model_name='position',
            name='name',
            field=models.CharField(blank=True, choices=[('no_position', 'Без должности'), ('comissioner', 'Комиссар'), ('master_methodologist', 'Мастер-методист'), ('specialist', 'Специалист'), ('commander', 'Коммандир'), ('central_commander', 'Коммандир центрального штаба'), ('district_commander', 'Коммандир окружного штаба'), ('regional_commander', 'Коммандир регионального штаба'), ('local_commander', 'Коммандир местного штаба'), ('edu_commander', 'Коммандир штаба образовательной организации'), ('detachment_commander', 'Коммандир отряда'), ('candidate', 'Кандидат'), ('fighter', 'Боец')], default='candidate', max_length=35, null=True, verbose_name='Должность'),
        ),
        migrations.AlterField(
            model_name='regionalheadquarter',
            name='name',
            field=models.CharField(max_length=100, unique=True, verbose_name='Название'),
        ),
    ]
