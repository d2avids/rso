from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

from .constants import (Gender, MilitaryDocType, PositionsOption,
                        PrivacyOption, StudyForm, UnitType)


class RSOUser(AbstractUser):
    email = models.EmailField(
        verbose_name='Email',
        max_length=254,
        unique=True,
    )
    username = models.CharField(
        verbose_name='Ник',
        max_length=150,
        unique=True
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150
    )
    patronymic_name = models.CharField(
        verbose_name='Отчество',
        max_length=150,
        blank=True,
        null=True,
    )
    date_of_birth = models.DateField(
        verbose_name='Дата рождения',
        blank=True,
        null=True,
    )
    last_name_lat = models.CharField(
        verbose_name='Фамилия (латиница)',
        max_length=150,
        blank=True,
        null=True,
    )
    first_name_lat = models.CharField(
        verbose_name='Имя (латиница)',
        max_length=150,
        blank=True,
        null=True,
    )
    patronymic_lat = models.CharField(
        verbose_name='Отчество (латиница)',
        max_length=150,
        blank=True,
        null=True,
    )
    phone_number = models.CharField(
        verbose_name='Номер телефона',
        max_length=30,
        default='+7',
        blank=True,
        null=True,
    )
    gender = models.CharField(
        verbose_name='Пол',
        max_length=30,
        choices=Gender.choices,
    )
    region = models.ForeignKey(
        to='Region',
        null=True,
        on_delete=models.PROTECT,
        verbose_name='Регион ОО'
    )
    unit_type = models.CharField(
        verbose_name='Тип структурной единицы',
        max_length=150,
        choices=UnitType.choices,
        default='detachment',
    )
    address = models.CharField(
        verbose_name='Фактическое место проживания',
        max_length=150,
        blank=True,
        null=True,
    )
    bio = models.TextField(
        max_length=400,
        blank=True,
        null=True,
        verbose_name='О себе'
    )
    social_vk = models.CharField(
        verbose_name='Ссылка на ВК',
        max_length=50,
        blank=True,
        default='https://vk.com/',
    )
    social_tg = models.CharField(
        verbose_name='Ссылка на Телеграм',
        max_length=50,
        blank=True,
        default='https://t.me/',
    )
    # ---Для несовершеннолетних---
    membership_fee = models.BooleanField(
        default=False,
        verbose_name='Членский взнос оплачен'
    )
    detachment = models.ForeignKey(
        to='Detachment',
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        verbose_name='Отряд'
    )
    position = models.CharField(
        max_length=20, 
        blank=True, 
        null=True,
        choices=PositionsOption.choices, 
        verbose_name='Должность'
    )

    class Meta:
        verbose_name_plural = 'Пользователи'
        verbose_name = 'Пользователь'

    def __str__(self):
        return (
            f'Пользователь {self.last_name} '
            f'{self.first_name}. Id: {self.id}'
        )


class UserEducation(models.Model):
    """Информация об образовательной организации пользователя."""
    user = models.ForeignKey(
        verbose_name='Пользователь',
        to=RSOUser,
        on_delete=models.CASCADE,
        related_name='education',
    )
    study_institution = models.CharField(
        verbose_name='Образовательная организация',
        max_length=200,
        blank=True,
        null=True,
    )
    study_faculty = models.CharField(
        verbose_name='Факультет',
        max_length=200,
        blank=True,
        null=True,
    )
    study_group = models.CharField(
        verbose_name='Группа',
        max_length=20,
        blank=True,
        null=True,
    )
    study_form = models.CharField(
        verbose_name='Форма обучения',
        max_length=20,
        choices=StudyForm.choices,
        blank=True,
        null=True,
    )
    study_year = models.CharField(
        verbose_name='Курс',
        max_length=10,
        blank=True,
        null=True,
    )
    study_specialty = models.CharField(
        verbose_name='Специальность',
        max_length=40,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name_plural = 'Образовательная информация пользователей'
        verbose_name = 'Образовательная информация пользователя'
        constraints = [
            models.UniqueConstraint(fields=['user'],
                                    name='unique_user_education')
        ]

    def __str__(self):
        return (
            f'Пользователь {self.user.last_name} '
            f'{self.user.first_name}. Id: {self.user.id}'
        )


class UserDocuments(models.Model):
    """Информация о документах пользователя."""
    user = models.ForeignKey(
        verbose_name='Пользователь',
        to=RSOUser,
        on_delete=models.CASCADE,
        related_name='documents',
    )
    snils = models.CharField(max_length=15, blank=True, default='',
                             verbose_name='СНИЛС')
    inn = models.CharField(
        verbose_name='ИНН',
        max_length=15,
        blank=True,
        null=True,
    )
    # INN_file
    # pass_file
    pass_ser_num = models.CharField(
        verbose_name='Номер и серия паспорта',
        max_length=15,
        blank=True,
        null=True,
    )
    pass_town = models.CharField(
        verbose_name='Город рождения',
        max_length=15,
        blank=True,
        default='',
    )
    pass_whom = models.CharField(
        max_length=15,
        verbose_name='Кем выдан паспорт',
        blank=True,
        null=True,
    )
    pass_date = models.DateField(
        verbose_name='Дата выдачи паспорта',
        blank=True,
        null=True,
    )
    pass_code = models.CharField(
        verbose_name='Код подразделения, выдавшего паспорт',
        max_length=15,
        blank=True,
        null=True
    )
    pass_address = models.CharField(
        verbose_name='Место регистрации по паспорту',
        max_length=15,
        blank=True,
        null=True,
    )
    work_book_num = models.CharField(
        verbose_name='Трудовая книжка номер',
        max_length=15,
        blank=True,
        null=True,
    )
    international_pass = models.CharField(
        verbose_name='Загранпаспорт номер',
        max_length=15,
        blank=True,
        null=True,
    )
    mil_reg_doc_type = models.CharField(
        verbose_name='Тип документа воинского учета',
        max_length=20,
        choices=MilitaryDocType.choices,
        blank=True,
        null=True,
    )
    mil_reg_doc_ser_num = models.CharField(
        verbose_name='Номер и серия документа воинского учета',
        max_length=15,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name_plural = 'Документы пользователей'
        verbose_name = 'Документы пользователя'
        constraints = [
            models.UniqueConstraint(fields=['user'],
                                    name='unique_user_documents')
        ]

    def __str__(self):
        return (
            f'Пользователь {self.user.last_name} '
            f'{self.user.first_name}. Id: {self.user.id}'
        )


class UserRegion(models.Model):
    """
    Информация о регионе и проживании (фактическом и по прописке) пользователя.
    """
    user = models.ForeignKey(
        verbose_name='Пользователь',
        to=RSOUser,
        on_delete=models.CASCADE,
        related_name='user_region',
    )
    reg_region = models.ForeignKey(
        to='Region',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='user_region_region',
        verbose_name='Регион прописки'
    )
    reg_town = models.CharField(
        max_length=40,
        blank=True,
        null=True,
        verbose_name='Населенный пункт прописки'
    )
    reg_house = models.CharField(
        max_length=40,
        blank=True,
        null=True,
        verbose_name='Улица, дом, кв. прописки'
    )
    reg_fact_same_address = models.BooleanField(
        default=False,
        verbose_name='Адреса регистрации и фактический совпадают'
    )
    fact_region = models.ForeignKey(
        to='Region',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='fact_region',
        verbose_name='Регион проживания'
    )
    fact_town = models.CharField(
        max_length=40,
        blank=True,
        null=True,
        verbose_name='Населенный пункт проживания'
    )
    fact_house = models.CharField(
        max_length=40,
        blank=True,
        null=True,
        verbose_name='Улица, дом, кв. проживания'
    )

    class Meta:
        verbose_name_plural = 'Информация о регионе пользователей'
        verbose_name = 'Информация о регионе пользователя'
        constraints = [
            models.UniqueConstraint(fields=['user'],
                                    name='unique_user_region')
        ]

    def __str__(self):
        return (
            f'Пользователь {self.user.last_name} '
            f'{self.user.first_name}. Id: {self.user.id}'
        )


class UserPrivacySettings(models.Model):
    """Настройки приватности пользователя."""
    user = models.ForeignKey(
        verbose_name='Пользователь',
        to=RSOUser,
        on_delete=models.CASCADE,
        related_name='privacy',
    )
    privacy_telephone = models.CharField(
        verbose_name='Кто видит номер телефона',
        max_length=20,
        choices=PrivacyOption.choices,
        default='all',
    )
    privacy_email = models.CharField(
        verbose_name='Кто видит электронную почту',
        max_length=20,
        choices=PrivacyOption.choices,
        default='all',
    )
    privacy_social = models.CharField(
        verbose_name='Кто видит ссылки на соц.сети',
        max_length=20,
        choices=PrivacyOption.choices,
        default='all',
    )
    privacy_about = models.CharField(
        verbose_name='Кто видит информацию "Обо мне"',
        max_length=20,
        choices=PrivacyOption.choices,
        default='all',
    )
    privacy_photo = models.CharField(
        verbose_name='Кто видит мои фотографии',
        max_length=20,
        choices=PrivacyOption.choices,
        default='all',
    )

    class Meta:
        verbose_name_plural = 'Настройки приватности пользователей'
        verbose_name = 'Настройки приватности пользователя'
        constraints = [
            models.UniqueConstraint(fields=['user'],
                                    name='unique_user_privacy_settings')
        ]

    def __str__(self):
        return (
            f'Пользователь {self.user.last_name} '
            f'{self.user.first_name}. Id: {self.user.id}'
        )


class UserMedia(models.Model):
    """Аватарка, баннер и другие медиа-файлы."""
    user = models.ForeignKey(
        verbose_name='Пользователь',
        to=RSOUser,
        on_delete=models.CASCADE,
        related_name='media',
    )
    banner = models.ImageField(
        upload_to='users/banner/%Y/%m/%d',
        blank=True,
        verbose_name='Баннер личной страницы'
    )
    photo = models.ImageField(
        upload_to='users/avatar/%Y/%m/%d',
        blank=True,
        verbose_name='Аватарка'
    )
    photo1 = models.ImageField(
        upload_to='users/photo/%Y/%m/%d',
        blank=True,
        verbose_name='Фото 1'
    )
    photo2 = models.ImageField(
        upload_to='users/photo/%Y/%m/%d',
        blank=True,
        verbose_name='Фото 2'
    )
    photo3 = models.ImageField(
        upload_to='users/photo/%Y/%m/%d',
        blank=True,
        verbose_name='Фото 3'
    )
    photo4 = models.ImageField(
        upload_to='users/photo/%Y/%m/%d',
        blank=True,
        verbose_name='Фото 4'
    )

    class Meta:
        verbose_name_plural = 'Медиа пользователей'
        verbose_name = 'Медиа пользователя'
        constraints = [
            models.UniqueConstraint(fields=['user'],
                                    name='unique_user_media')
        ]

    def __str__(self):
        return (
            f'Пользователь {self.user.last_name} '
            f'{self.user.first_name}. Id: {self.user.id}'
        )


class UserStatementDocuments(models.Model):
    """Документы пользователя для вступления в РСО."""
    user = models.ForeignKey(
        verbose_name='Пользователь',
        to=RSOUser,
        on_delete=models.CASCADE,
        related_name='statement',
    )
    statement = models.FileField(
        upload_to='users/statement/%Y/%m/%d',
        blank=True,
        null=True,
        verbose_name='Заявление на вступлении в РСО'
    )
    consent_personal_data = models.FileField(
        upload_to='users/pdconsent/%Y/%m/%d',
        blank=True,
        null=True,
        verbose_name='Согласие на обработку персональных данных'
    )
    consent_personal_data_representative = models.FileField(
        upload_to='users/pdconsent_repr/%Y/%m/%d',
        blank=True,
        null=True,
        verbose_name='Согласие официального представителя на '
                     'обработку персональных данных несовершеннолетнего'
    )
    passport = models.FileField(
        upload_to='users/passport/%Y/%m/%d',
        blank=True,
        null=True,
        verbose_name='Паспорт гражданина РФ'
    )
    passport_representative = models.FileField(
        upload_to='users/passport_repr/%Y/%m/%d',
        blank=True,
        null=True,
        verbose_name='Паспорт законного представителя'
    )
    snils_file = models.FileField(
        upload_to='users/snils/%Y/%m/%d',
        blank=True,
        null=True,
        verbose_name='СНИЛС'
    )
    inn_file = models.FileField(
        upload_to='users/inn/%Y/%m/%d',
        blank=True,
        null=True,
        verbose_name='ИИН'
    )
    employment_document = models.FileField(
        upload_to='users/inn/%Y/%m/%d',
        blank=True,
        null=True,
        verbose_name='Трудовая книжка'
    )
    military_document = models.FileField(
        upload_to='users/militarydoc/%Y/%m/%d',
        blank=True,
        null=True,
        verbose_name='Военный билет'
    )
    international_passport = models.FileField(
        upload_to='users/intpassport/%Y/%m/%d',
        blank=True,
        null=True,
        verbose_name='Загранпаспорт'
    )
    additional_document = models.FileField(
        upload_to='users/adddoc/%Y/%m/%d',
        blank=True,
        null=True,
        verbose_name='Дополнительный документ'
    )
    rso_info_from = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Откуда вы узнали про РСО?'
    )
    personal_data_agreement = models.BooleanField(
        default=False,
        verbose_name='Даю согласие на обработку моих персональных данных в '
                     'соответствии с законом от 27.07.2006 года № 152-ФЗ «О  '
                     'персональных данных», на условиях и для целей, '
                     'определенных в Согласии на обработку '
                     'персональных данных'
    )

    class Meta:
        verbose_name_plural = 'Заявления на вступление в РСО пользователей'
        verbose_name = 'Заявление на вступление в РСО пользователя'
        constraints = [
            models.UniqueConstraint(fields=['user'],
                                    name='unique_user_statement')
        ]

    def __str__(self):
        return (
            f'Пользователь {self.user.last_name} '
            f'{self.user.first_name}. Id: {self.user.id}'
        )


class Region(models.Model):
    name = models.CharField(
        max_length=100,
        db_index=True,
        verbose_name='Название'
    )
    branch = models.CharField(
        max_length=100,
        db_index=True,
        default='региональное отделение',
        verbose_name='Региональное отделение'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'регионы'
        verbose_name = 'Регион'


class Area(models.Model):
    name = models.CharField(max_length=50, blank=False, verbose_name='Название направления')

    # Направления определяются админом/ЦШ или же региональными штабами? Точно должно быть отдельной сущностью.

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'направления'
        verbose_name = 'Направление'


class Unit(models.Model):
    """Структурная единица"""
    name = models.CharField(max_length=100, db_index=True, verbose_name='Название')
    commander = models.OneToOneField(RSOUser, related_name='commander', null=True, blank=True, on_delete=models.PROTECT,
                                     verbose_name='Командир')
    about = models.CharField(max_length=500, blank=True, verbose_name='Описание', default='')
    emblem = models.ImageField(upload_to='emblems/%Y/%m/%d', blank=True, verbose_name='Эмблема')
    social_vk = models.CharField(max_length=50, blank=True, verbose_name='Ссылка ВК', default='https://vk.com/')
    social_tg = models.CharField(max_length=50, blank=True, verbose_name='Ссылка Телеграм', default='https://')
    banner = models.ImageField(upload_to='emblems/%Y/%m/%d', blank=True, verbose_name='Баннер')
    slogan = models.CharField(max_length=100, blank=True, default='', verbose_name='Девиз')
    founding_date = models.DateField(blank=True, null=True, verbose_name='Дата основания')

    # Уровень Линейный отряд, Штаб учебного заведения, Региональное отделение, (Направление)
    # area = models.ForeignKey('Area', null=True, blank=True, on_delete=models.PROTECT, verbose_name='Направление')
    #
    # flag = models.ImageField(upload_to='flags/%Y/%m/%d', blank=True, verbose_name='Флаг')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'структурные единицы'
        verbose_name = 'Структурная единица'



class Detachment(Unit):
    area = models.ForeignKey(Area, null=False, blank=False, on_delete=models.PROTECT, verbose_name='Направление')

    def clean(self):
        if not self.commander:
            raise ValidationError('Отряд должен иметь командира.')

    # регион
    # institution = models.ForeignKey('Institution', null=True, blank=True, on_delete=models.PROTECT,
    #                                verbose_name='Учебное заведение')
    # город
    # Местный штаб

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'отряды'
        verbose_name = 'Отряд'



# Штаб Образовательной Организации
# Регион
# Учебное заведение
# Местный штаб
#
# МестныйШтаб
# Регион
# Номер участника в реестре
# Дата участника в реестре
#
# Региональный Штаб
# Регион
# Год появления Отрядов в регионе
# Дата учредительной конференции
# Номер участника в реестре
# Дата участника в реестре
# Окружной штаб
#
# Окружной Штаб


# class Event(models.Model):
# Формат (онлайн)
# Масштаб
# Название
# Адрес
# Ссылка на конференцию
# Количество участников
# Баннер
# О мероприятии
# Направление (?)
# Вид заявок
# Кто может отправлять заявку
# Многодневное
# Дата начала
# Время начала
# Дата конца
# Время конца
# Дата и время окончания регистрации
# Нужен паспорт
# Нужен СНИЛС
# Нужен ИНН
# Нужна Трудовая книжка
# Нужен Военный билет или приписное свидетельство
# Нужно согласие на обработку персональных данных
# Дополнительный вопрос 1
# Дополнительный вопрос 2
# Дополнительный вопрос 3
