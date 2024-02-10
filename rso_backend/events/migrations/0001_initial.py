# Generated by Django 4.2.7 on 2023-12-28 09:13

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import events.utils


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('format', models.CharField(choices=[('ONLINE', 'Онлайн'), ('OFFLINE', 'Оффлайн')], default='OFFLINE', max_length=7, verbose_name='Тип мероприятия')),
                ('direction', models.CharField(choices=[('voluntary', 'Добровольческое'), ('educational', 'Образовательное'), ('patriotic', 'Патриотическое'), ('sport', 'Спортивное'), ('creative', 'Творческое')], default='voluntary', max_length=20, verbose_name='Масштаб мероприятия')),
                ('status', models.CharField(choices=[('active', 'Активный'), ('inactive', 'Завершенный')], default='active', max_length=20, verbose_name='Статус мероприятия')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('name', models.CharField(max_length=100, verbose_name='Название мероприятия,')),
                ('banner', models.ImageField(blank=True, null=True, upload_to=events.utils.image_path, verbose_name='Баннер')),
                ('conference_link', models.CharField(max_length=250, verbose_name='Ссылка на конференцию')),
                ('address', models.CharField(blank=True, max_length=250, null=True, verbose_name='Адрес проведения (если мероприятие оффлайн)')),
                ('participants_number', models.PositiveIntegerField(verbose_name='Количество участников')),
                ('description', models.TextField(verbose_name='О мероприятии')),
                ('application_type', models.CharField(choices=[('personal', 'Персональная'), ('group', 'Групповая'), ('multi_stage', 'Мультиэтапная')], default='group', max_length=20, verbose_name='Вид принимаемых к подаче на мероприятие заявок')),
                ('available_structural_units', models.CharField(choices=[('detachments', 'Отряды'), ('educationals', 'Образовательные штабы'), ('locals', 'Местные штабы'), ('regionals', 'Региональные штабы'), ('districts', 'Окружные штабы'), ('central', 'Центральные штабы')], default='detachments', max_length=30, verbose_name='Объекты, имеющие возможность формировать групповые заявки')),
            ],
            options={
                'verbose_name': 'Мероприятие',
                'verbose_name_plural': 'Мероприятия',
            },
        ),
        migrations.CreateModel(
            name='EventTimeData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_duration_type', models.CharField(choices=[('one_day', 'Однодневное'), ('multiple_days', 'Многодневное')], default='one_day', max_length=20, verbose_name='Продолжительность мероприятия')),
                ('start_date', models.DateField(verbose_name='Дата начала мероприятия')),
                ('start_time', models.TimeField(verbose_name='Время начала мероприятия')),
                ('end_date', models.DateField(verbose_name='Дата окончания мероприятия')),
                ('end_time', models.TimeField(verbose_name='Время окончания мероприятия')),
                ('registration_end_date', models.DateField(verbose_name='Дата окончания регистрации')),
                ('registration_end_time', models.TimeField(verbose_name='Время окончания регистрации')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='time_data', to='events.event', verbose_name='Мероприятие')),
            ],
            options={
                'verbose_name': 'Информация о времени мероприятия',
                'verbose_name_plural': 'Информация о времени мероприятий',
            },
        ),
        migrations.CreateModel(
            name='EventOrganizationData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('organizer_phone_number', models.CharField(blank=True, default='+7', max_length=30, null=True, verbose_name='Номер телефона')),
                ('organizer_email', models.EmailField(blank=True, max_length=250, null=True, verbose_name='Email')),
                ('organization', models.CharField(blank=True, max_length=250, null=True, verbose_name='Организация')),
                ('telegram', models.CharField(blank=True, max_length=50, null=True, verbose_name='Телеграмм')),
                ('is_contact_person', models.BooleanField(default=False, verbose_name='Сделать контактным лицом')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='organization_data', to='events.event', verbose_name='Мероприятие')),
                ('organizer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь-организатор')),
            ],
            options={
                'verbose_name': 'Информация об организаторах мероприятия',
                'verbose_name_plural': 'Информация об организаторах мероприятий',
            },
        ),
        migrations.CreateModel(
            name='EventDocumentData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('passport', models.BooleanField(default=False, verbose_name='Паспорт')),
                ('snils', models.BooleanField(default=False, verbose_name='СНИЛС')),
                ('inn', models.BooleanField(default=False, verbose_name='ИНН')),
                ('work_book', models.BooleanField(default=False, verbose_name='Трудовая книжка')),
                ('military_document', models.BooleanField(default=False, verbose_name='Военный билет или приписное свидетельство')),
                ('consent_personal_data', models.BooleanField(default=False, verbose_name='Согласие на обработку персональных данных')),
                ('additional_info', models.TextField(verbose_name='Расскажите, с какими документами необходимо просто ознакомиться, а какие скачать и заполнить')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents_data', to='events.event', verbose_name='Мероприятие')),
            ],
            options={
                'verbose_name': 'Список необходимых документов для мероприятия',
                'verbose_name_plural': 'Список необходимых документов для мероприятий',
            },
        ),
        migrations.CreateModel(
            name='EventDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document', models.FileField(blank=True, null=True, upload_to=events.utils.document_path, verbose_name='Файл формата pdf, png, jpeg')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='events.event', verbose_name='Мероприятие')),
            ],
            options={
                'verbose_name': 'Документы мероприятия',
                'verbose_name_plural': 'Документы мероприятий',
            },
        ),
        migrations.CreateModel(
            name='EventAdditionalIssues',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('issue', models.TextField(verbose_name='Вопрос')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='additional_issues', to='events.event', verbose_name='Мероприятие')),
            ],
            options={
                'verbose_name': 'Дополнительные вопросы мероприятия',
                'verbose_name_plural': 'Дополнительные вопросы мероприятий',
            },
        ),
        migrations.AddConstraint(
            model_name='eventtimedata',
            constraint=models.UniqueConstraint(fields=('event',), name='unique_event_time_data'),
        ),
        migrations.AddConstraint(
            model_name='eventdocumentdata',
            constraint=models.UniqueConstraint(fields=('event',), name='unique_event_document_data'),
        ),
    ]
