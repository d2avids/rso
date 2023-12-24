# Generated by Django 4.2.7 on 2023-12-18 15:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import users.utils


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_alter_usermembershiplogs_period'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserCertInternal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cert_start_date', models.DateField(auto_now_add=True, verbose_name='Дата начала действия справки')),
                ('cert_end_date', models.DateField(verbose_name='Дата окончания действия справки')),
                ('recipient', models.CharField(max_length=250, verbose_name='Справка выдана для предоставления')),
                ('issue_date', models.DateField(auto_now_add=True, verbose_name='Дата выдачи справки')),
                ('number', models.CharField(default='б/н', max_length=40, verbose_name='Номер справки')),
            ],
            options={
                'verbose_name': 'Выданная внутренняя справка.',
                'verbose_name_plural': 'Выданные внутренние справки.',
            },
        ),
        migrations.AlterField(
            model_name='rsouser',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True, verbose_name='Email'),
        ),
        migrations.AlterField(
            model_name='usermedia',
            name='banner',
            field=models.ImageField(blank=True, null=True, upload_to=users.utils.image_path, verbose_name='Баннер личной страницы'),
        ),
        migrations.AlterField(
            model_name='usermedia',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to=users.utils.image_path, verbose_name='Аватарка'),
        ),
        migrations.AlterField(
            model_name='usermedia',
            name='photo1',
            field=models.ImageField(blank=True, null=True, upload_to=users.utils.image_path, verbose_name='Фото 1'),
        ),
        migrations.AlterField(
            model_name='usermedia',
            name='photo2',
            field=models.ImageField(blank=True, null=True, upload_to=users.utils.image_path, verbose_name='Фото 2'),
        ),
        migrations.AlterField(
            model_name='usermedia',
            name='photo3',
            field=models.ImageField(blank=True, null=True, upload_to=users.utils.image_path, verbose_name='Фото 3'),
        ),
        migrations.AlterField(
            model_name='usermedia',
            name='photo4',
            field=models.ImageField(blank=True, null=True, upload_to=users.utils.image_path, verbose_name='Фото 4'),
        ),
        migrations.CreateModel(
            name='UserCertExternal',
            fields=[
                ('usercertinternal_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='users.usercertinternal')),
                ('signatory', models.CharField(max_length=250, verbose_name='ФИО подписывающего лица')),
                ('position_procuration', models.CharField(max_length=250, verbose_name='Должность подписывающего лица, доверенность')),
            ],
            options={
                'verbose_name': 'Выданная справка о членстве в РСО.',
                'verbose_name_plural': 'Выданные справки о членстве в РСО.',
            },
            bases=('users.usercertinternal',),
        ),
        migrations.CreateModel(
            name='UserMemberCertRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='membership_cert', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь, подавший заявку на справку')),
            ],
            options={
                'verbose_name': 'Заявка на справку о членстве в РСО',
                'verbose_name_plural': 'Заявки на справку о членстве в РСО',
            },
        ),
        migrations.AddField(
            model_name='usercertinternal',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cert_info', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
    ]