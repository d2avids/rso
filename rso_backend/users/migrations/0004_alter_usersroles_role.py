# Generated by Django 4.2.7 on 2023-12-09 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_usersroles'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usersroles',
            name='role',
            field=models.CharField(blank=True, choices=[('admin', 'Администратор'), ('central_commander', 'Коммандир центрального штаба'), ('district_commander', 'Коммандир окружного штаба'), ('regional_commander', 'Коммандир регионального штаба'), ('local_commander', 'Коммандир местного штаба'), ('edu_commander', 'Коммандир штаба образовательной организации'), ('detachment_commander', 'Коммандир отряда'), ('candidate', 'Кандидат'), ('fighter', 'Боец'), ('comissar', 'Комиссар'), ('medic', 'Медик'), ('master_methodologist', 'Мастер-методист')], default='candidate', max_length=35, null=True, verbose_name='Роль пользователя'),
        ),
    ]