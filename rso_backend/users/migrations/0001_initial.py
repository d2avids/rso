# Generated by Django 4.2.7 on 2023-12-03 12:05

import django.contrib.auth.models
import django.db.models.deletion
import django.utils.timezone
import users.utils
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('headquarters', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='RSOUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='Email')),
                ('username', models.CharField(max_length=150, unique=True, verbose_name='Ник')),
                ('first_name', models.CharField(max_length=150, verbose_name='Имя')),
                ('last_name', models.CharField(max_length=150, verbose_name='Фамилия')),
                ('patronymic_name', models.CharField(blank=True, max_length=150, null=True, verbose_name='Отчество')),
                ('date_of_birth', models.DateField(blank=True, null=True, verbose_name='Дата рождения')),
                ('last_name_lat', models.CharField(blank=True, max_length=150, null=True, verbose_name='Фамилия (латиница)')),
                ('first_name_lat', models.CharField(blank=True, max_length=150, null=True, verbose_name='Имя (латиница)')),
                ('patronymic_lat', models.CharField(blank=True, max_length=150, null=True, verbose_name='Отчество (латиница)')),
                ('phone_number', models.CharField(blank=True, default='+7', max_length=30, null=True, verbose_name='Номер телефона')),
                ('gender', models.CharField(choices=[('male', 'Мужской'), ('female', 'Женский')], max_length=30, verbose_name='Пол')),
                ('address', models.CharField(blank=True, max_length=150, null=True, verbose_name='Фактическое место проживания')),
                ('bio', models.TextField(blank=True, max_length=400, null=True, verbose_name='О себе')),
                ('social_vk', models.CharField(blank=True, default='https://vk.com/', max_length=50, verbose_name='Ссылка на ВК')),
                ('social_tg', models.CharField(blank=True, default='https://t.me/', max_length=50, verbose_name='Ссылка на Телеграм')),
                ('is_verified', models.BooleanField(default=False, verbose_name='Статус верификации')),
                ('membership_fee', models.BooleanField(default=False, verbose_name='Членский взнос оплачен')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('region', models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='headquarters.region', verbose_name='Регион ОО')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'Пользователь',
                'verbose_name_plural': 'Пользователи',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='UserVerificationRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='veirification', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь, подавший заявку на верификацию')),
            ],
            options={
                'verbose_name': 'Заявка на верификацию',
                'verbose_name_plural': 'Заявки на верификацию',
            },
        ),
        migrations.CreateModel(
            name='UserStatementDocuments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('statement', models.FileField(blank=True, null=True, upload_to=users.utils.document_path, verbose_name='Заявление на вступлении в РСО')),
                ('consent_personal_data', models.FileField(blank=True, null=True, upload_to=users.utils.document_path, verbose_name='Согласие на обработку персональных данных')),
                ('consent_personal_data_representative', models.FileField(blank=True, null=True, upload_to=users.utils.document_path, verbose_name='Согласие официального представителя на обработку персональных данных несовершеннолетнего')),
                ('passport', models.FileField(blank=True, null=True, upload_to=users.utils.document_path, verbose_name='Паспорт гражданина РФ')),
                ('passport_representative', models.FileField(blank=True, null=True, upload_to=users.utils.document_path, verbose_name='Паспорт законного представителя')),
                ('snils_file', models.FileField(blank=True, null=True, upload_to=users.utils.document_path, verbose_name='СНИЛС')),
                ('inn_file', models.FileField(blank=True, null=True, upload_to=users.utils.document_path, verbose_name='ИИН')),
                ('employment_document', models.FileField(blank=True, null=True, upload_to=users.utils.document_path, verbose_name='Трудовая книжка')),
                ('military_document', models.FileField(blank=True, null=True, upload_to=users.utils.document_path, verbose_name='Военный билет')),
                ('international_passport', models.FileField(blank=True, null=True, upload_to=users.utils.document_path, verbose_name='Загранпаспорт')),
                ('additional_document', models.FileField(blank=True, null=True, upload_to=users.utils.document_path, verbose_name='Дополнительный документ')),
                ('rso_info_from', models.CharField(blank=True, max_length=200, null=True, verbose_name='Откуда вы узнали про РСО?')),
                ('personal_data_agreement', models.BooleanField(default=False, verbose_name='Даю согласие на обработку моих персональных данных в соответствии с законом от 27.07.2006 года № 152-ФЗ «О  персональных данных», на условиях и для целей, определенных в Согласии на обработку персональных данных')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='statement', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Заявление на вступление в РСО пользователя',
                'verbose_name_plural': 'Заявления на вступление в РСО пользователей',
            },
        ),
        migrations.CreateModel(
            name='UsersParent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parent_last_name', models.CharField(blank=True, max_length=150, null=True, verbose_name='Фамилия')),
                ('parent_first_name', models.CharField(blank=True, max_length=150, null=True, verbose_name='Имя')),
                ('parent_patronymic_name', models.CharField(blank=True, max_length=150, null=True, verbose_name='Отчество')),
                ('parent_date_of_birth', models.DateField(blank=True, null=True, verbose_name='Дата рождения')),
                ('relationship', models.CharField(blank=True, choices=[('father', 'Отец'), ('mother', 'Мать'), ('guardian', 'Опекун')], max_length=8, null=True, verbose_name='Кем является')),
                ('parent_phone_number', models.CharField(blank=True, default='+7', max_length=30, null=True, verbose_name='Номер телефона')),
                ('russian_passport', models.BooleanField(default=True, verbose_name='Паспорт гражданина РФ')),
                ('passport_number', models.CharField(blank=True, max_length=50, null=True, verbose_name='Номер и серия')),
                ('passport_date', models.DateField(blank=True, null=True, verbose_name='Дата выдачи')),
                ('passport_authority', models.CharField(blank=True, max_length=150, null=True, verbose_name='Кем выдан')),
                ('city', models.CharField(blank=True, max_length=50, null=True, verbose_name='Населенный пункт')),
                ('address', models.CharField(blank=True, max_length=200, null=True, verbose_name='Улица, дом, квартира')),
                ('region', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='headquarters.region', verbose_name='Регион')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='parent', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Законный представитель несовершеннолетнего',
                'verbose_name_plural': 'Законные представители несовершеннолетних',
            },
        ),
        migrations.CreateModel(
            name='UserRegion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reg_town', models.CharField(blank=True, max_length=40, null=True, verbose_name='Населенный пункт прописки')),
                ('reg_house', models.CharField(blank=True, max_length=40, null=True, verbose_name='Улица, дом, кв. прописки')),
                ('reg_fact_same_address', models.BooleanField(default=False, verbose_name='Адреса регистрации и фактический совпадают')),
                ('fact_town', models.CharField(blank=True, max_length=40, null=True, verbose_name='Населенный пункт проживания')),
                ('fact_house', models.CharField(blank=True, max_length=40, null=True, verbose_name='Улица, дом, кв. проживания')),
                ('fact_region', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='fact_region', to='headquarters.region', verbose_name='Регион проживания')),
                ('reg_region', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='user_region_region', to='headquarters.region', verbose_name='Регион прописки')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='user_region', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Информация о регионе пользователя',
                'verbose_name_plural': 'Информация о регионе пользователей',
            },
        ),
        migrations.CreateModel(
            name='UserPrivacySettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('privacy_telephone', models.CharField(choices=[('all', 'Все'), ('detachment_members', 'Члены отряда'), ('management_members', 'Руководство')], default='all', max_length=20, verbose_name='Кто видит номер телефона')),
                ('privacy_email', models.CharField(choices=[('all', 'Все'), ('detachment_members', 'Члены отряда'), ('management_members', 'Руководство')], default='all', max_length=20, verbose_name='Кто видит электронную почту')),
                ('privacy_social', models.CharField(choices=[('all', 'Все'), ('detachment_members', 'Члены отряда'), ('management_members', 'Руководство')], default='all', max_length=20, verbose_name='Кто видит ссылки на соц.сети')),
                ('privacy_about', models.CharField(choices=[('all', 'Все'), ('detachment_members', 'Члены отряда'), ('management_members', 'Руководство')], default='all', max_length=20, verbose_name='Кто видит информацию "Обо мне"')),
                ('privacy_photo', models.CharField(choices=[('all', 'Все'), ('detachment_members', 'Члены отряда'), ('management_members', 'Руководство')], default='all', max_length=20, verbose_name='Кто видит мои фотографии')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='privacy', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Настройки приватности пользователя',
                'verbose_name_plural': 'Настройки приватности пользователей',
            },
        ),
        migrations.CreateModel(
            name='UserMedia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('banner', models.ImageField(blank=True, upload_to=users.utils.image_path, verbose_name='Баннер личной страницы')),
                ('photo', models.ImageField(blank=True, upload_to=users.utils.image_path, verbose_name='Аватарка')),
                ('photo1', models.ImageField(blank=True, upload_to=users.utils.image_path, verbose_name='Фото 1')),
                ('photo2', models.ImageField(blank=True, upload_to=users.utils.image_path, verbose_name='Фото 2')),
                ('photo3', models.ImageField(blank=True, upload_to=users.utils.image_path, verbose_name='Фото 3')),
                ('photo4', models.ImageField(blank=True, upload_to=users.utils.image_path, verbose_name='Фото 4')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='media', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Медиа пользователя',
                'verbose_name_plural': 'Медиа пользователей',
            },
        ),
        migrations.CreateModel(
            name='UserEducation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('study_institution', models.CharField(blank=True, max_length=200, null=True, verbose_name='Образовательная организация')),
                ('study_faculty', models.CharField(blank=True, max_length=200, null=True, verbose_name='Факультет')),
                ('study_form', models.CharField(blank=True, choices=[('full_time', 'очная'), ('part_time', 'очно-заочная'), ('extramural_studies', 'заочная'), ('distant_studies', 'дистанционное')], max_length=20, null=True, verbose_name='Форма обучения')),
                ('study_year', models.CharField(blank=True, max_length=10, null=True, verbose_name='Курс')),
                ('study_specialty', models.CharField(blank=True, max_length=40, null=True, verbose_name='Специальность')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='education', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Образовательная информация пользователя',
                'verbose_name_plural': 'Образовательная информация пользователей',
            },
        ),
        migrations.CreateModel(
            name='UserDocuments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('snils', models.CharField(blank=True, default='', max_length=15, verbose_name='СНИЛС')),
                ('inn', models.CharField(blank=True, max_length=15, null=True, verbose_name='ИНН')),
                ('pass_ser_num', models.CharField(blank=True, max_length=15, null=True, verbose_name='Номер и серия паспорта')),
                ('pass_town', models.CharField(blank=True, default='', max_length=15, verbose_name='Город рождения')),
                ('pass_whom', models.CharField(blank=True, max_length=15, null=True, verbose_name='Кем выдан паспорт')),
                ('pass_date', models.DateField(blank=True, null=True, verbose_name='Дата выдачи паспорта')),
                ('pass_code', models.CharField(blank=True, max_length=15, null=True, verbose_name='Код подразделения, выдавшего паспорт')),
                ('pass_address', models.CharField(blank=True, max_length=15, null=True, verbose_name='Место регистрации по паспорту')),
                ('work_book_num', models.CharField(blank=True, max_length=15, null=True, verbose_name='Трудовая книжка номер')),
                ('international_pass', models.CharField(blank=True, max_length=15, null=True, verbose_name='Загранпаспорт номер')),
                ('mil_reg_doc_type', models.CharField(blank=True, choices=[('military_certificate', 'Удостоверение гражданина подлежащего вызову на срочную военную службу'), ('military_ticket', 'Военный билет')], max_length=20, null=True, verbose_name='Тип документа воинского учета')),
                ('mil_reg_doc_ser_num', models.CharField(blank=True, max_length=15, null=True, verbose_name='Номер и серия документа воинского учета')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Документы пользователя',
                'verbose_name_plural': 'Документы пользователей',
            },
        ),
        migrations.CreateModel(
            name='ProfessionalEduction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('study_institution', models.CharField(blank=True, max_length=200, null=True, verbose_name='Образовательная организация')),
                ('years_of_study', models.CharField(blank=True, max_length=9, null=True, validators=[users.utils.validate_years], verbose_name='Годы обучения')),
                ('exam_score', models.CharField(blank=True, max_length=20, null=True, verbose_name='Оценка')),
                ('qualification', models.CharField(blank=True, max_length=100, null=True, verbose_name='Квалификация')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='proffesional_education', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Дополнительное профессиональное образование.',
                'verbose_name_plural': 'Дополнительные профессиональные образования.',
            },
        ),
        migrations.AddConstraint(
            model_name='userstatementdocuments',
            constraint=models.UniqueConstraint(fields=('user',), name='unique_user_statement'),
        ),
        migrations.AddConstraint(
            model_name='userregion',
            constraint=models.UniqueConstraint(fields=('user',), name='unique_user_region'),
        ),
        migrations.AddConstraint(
            model_name='userprivacysettings',
            constraint=models.UniqueConstraint(fields=('user',), name='unique_user_privacy_settings'),
        ),
        migrations.AddConstraint(
            model_name='usermedia',
            constraint=models.UniqueConstraint(fields=('user',), name='unique_user_media'),
        ),
        migrations.AddConstraint(
            model_name='usereducation',
            constraint=models.UniqueConstraint(fields=('user',), name='unique_user_education'),
        ),
        migrations.AddConstraint(
            model_name='userdocuments',
            constraint=models.UniqueConstraint(fields=('user',), name='unique_user_documents'),
        ),
    ]
