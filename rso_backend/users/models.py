from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

from .constants import (Gender, UnitType, StudyForm, 
                        MilitaryDocType, PrivacyOption, PositionsOption)


def user_upload_path(instance, filename):
    # Построение пути загрузки на основе названия пользователя и его username
    return (f'users/'
            f'{instance.user.username}/'
            f'{timezone.now().strftime("%Y/%m/%d")}/'
            f'{filename}')


class RSOUser(AbstractUser):
    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='Email'
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        verbose_name='Ник'
    )
    first_name = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name='Фамилия'
    )
    patronymic_name = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name='Отчество'
    )
    date_of_birth = models.DateField(
        blank=True,
        null=True,
        verbose_name='Дата рождения'
    )
    last_name_lat = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name='Фамилия (латиница)'
    )
    first_name_lat = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name='Имя (латиница)'
    )
    patronymic_lat = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name='Отчество (латиница)'
    )
    phone_number = models.CharField(
        max_length=30,
        default='+7',
        blank=True,
        null=True,
        verbose_name='Номер телефона'
    )
    gender = models.CharField(
        max_length=30,
        choices=Gender.choices,
        verbose_name='Пол'
    )
    region = models.ForeignKey(
        to='Region',
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        verbose_name='Регион ОО'
    )
    unit_type = models.CharField(
        max_length=150,
        choices=UnitType.choices,
        default='detachment',
        verbose_name='Тип структурной единицы'
    )
    address = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        verbose_name='Фактическое место проживания'
    )
    bio = models.TextField(
        max_length=400,
        blank=True,
        null=True,
        verbose_name='О себе'
    )
    social_vk = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        default='https://vk.com/',
        verbose_name='Ссылка на ВК'
    )
    social_tg = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        default='https://t.me/',
        verbose_name='Ссылка на Телеграм'
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
    user = models.OneToOneField(
        to=RSOUser,
        on_delete=models.CASCADE,
        related_name='education',
        verbose_name='Пользователь',
    )
    study_institution = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Образовательная организация',
    )
    study_faculty = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name='Факультет'
    )
    study_group = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Группа'
    )
    study_form = models.CharField(
        max_length=20,
        choices=StudyForm.choices,
        blank=True,
        null=True,
        verbose_name='Форма обучения'
    )
    study_year = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name='Курс'
    )
    study_specialty = models.CharField(
        max_length=40,
        blank=True,
        null=True,
        verbose_name='Специальность'
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
    user = models.OneToOneField(
        to=RSOUser,
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name='Пользователь'
    )
    snils = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        default='',
        verbose_name='СНИЛС'
    )
    inn = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name='ИНН'
    )
    # INN_file
    # pass_file
    pass_ser_num = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name='Серия и номер паспорта'
    )
    pass_town = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        default='',
        verbose_name='Город рождения'
    )
    pass_whom = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name='Кем выдан паспорт'
    )
    pass_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Дата выдачи паспорта'
    )
    pass_code = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name='Код подразделения, выдавшего паспорт'
    )
    pass_address = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name='Место регистрации по паспорту'
    )
    work_book_num = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name='Номер трудовой книжки'
    )
    international_pass = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name='Номер загранпаспорта'
    )
    mil_reg_doc_type = models.CharField(
        max_length=20,
        choices=MilitaryDocType.choices,
        blank=True,
        null=True,
        verbose_name='Тип документа воинского учета'
    )
    mil_reg_doc_ser_num = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        verbose_name='Номер и серия документа воинского учета'
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
    user = models.OneToOneField(
        to=RSOUser,
        on_delete=models.CASCADE,
        related_name='user_region',
        verbose_name='Пользователь'
    )
    reg_region = models.ForeignKey(
        to='Region',
        blank=True,
        null=True,
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
    reg_fac_same_address = models.BooleanField(
        default=False,
        verbose_name='Адреса регистрации и фактический совпадают'
    )
    fact_region = models.ForeignKey(
        to='Region',
        blank=True,
        null=True,
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
    user = models.OneToOneField(
        to=RSOUser,
        on_delete=models.CASCADE,
        related_name='privacy',
        verbose_name='Пользователь'
    )
    privacy_telephone = models.CharField(
        max_length=20,
        choices=PrivacyOption.choices,
        default='all',
        verbose_name='Кто видит номер телефона'
    )
    privacy_email = models.CharField(
        max_length=20,
        choices=PrivacyOption.choices,
        default='all',
        verbose_name='Кто видит электронную почту'
    )
    privacy_social = models.CharField(
        max_length=20,
        choices=PrivacyOption.choices,
        default='all',
        verbose_name='Кто видит ссылки на соц.сети'
    )
    privacy_about = models.CharField(
        max_length=20,
        choices=PrivacyOption.choices,
        default='all',
        verbose_name='Кто видит информацию "Обо мне"'
    )
    privacy_photo = models.CharField(
        max_length=20,
        choices=PrivacyOption.choices,
        default='all',
        verbose_name='Кто видит мои фотографии'
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
    user = models.OneToOneField(
        to=RSOUser,
        on_delete=models.CASCADE,
        related_name='media',
        verbose_name='Пользователь'
    )
    banner = models.ImageField(
        upload_to=user_upload_path,
        blank=True,
        null=True,
        verbose_name='Баннер личной страницы'
    )
    photo = models.ImageField(
        upload_to=user_upload_path,
        blank=True,
        null=True,
        verbose_name='Аватарка'
    )
    photo1 = models.ImageField(
        upload_to=user_upload_path,
        blank=True,
        null=True,
        verbose_name='Фото 1'
    )
    photo2 = models.ImageField(
        upload_to=user_upload_path,
        blank=True,
        null=True,
        verbose_name='Фото 2'
    )
    photo3 = models.ImageField(
        upload_to=user_upload_path,
        blank=True,
        null=True,
        verbose_name='Фото 3'
    )
    photo4 = models.ImageField(
        upload_to=user_upload_path,
        blank=True,
        null=True,
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
    user = models.OneToOneField(
        to=RSOUser,
        on_delete=models.CASCADE,
        related_name='statement',
        verbose_name='Пользователь'
    )
    statement = models.FileField(
        upload_to=user_upload_path,
        blank=True,
        null=True,
        verbose_name='Заявление на вступлении в РСО'
    )
    consent_personal_data = models.FileField(
        upload_to=user_upload_path,
        blank=True,
        null=True,
        verbose_name='Согласие на обработку персональных данных'
    )
    consent_personal_data_representative = models.FileField(
        upload_to=user_upload_path,
        blank=True,
        null=True,
        verbose_name='Согласие официального представителя на '
                     'обработку персональных данных несовершеннолетнего'
    )
    passport = models.FileField(
        upload_to=user_upload_path,
        blank=True,
        null=True,
        verbose_name='Паспорт гражданина РФ'
    )
    passport_representative = models.FileField(
        upload_to=user_upload_path,
        blank=True,
        null=True,
        verbose_name='Паспорт законного представителя'
    )
    snils_file = models.FileField(
        upload_to=user_upload_path,
        blank=True,
        null=True,
        verbose_name='СНИЛС'
    )
    inn_file = models.FileField(
        upload_to=user_upload_path,
        blank=True,
        null=True,
        verbose_name='ИИН'
    )
    employment_document = models.FileField(
        upload_to=user_upload_path,
        blank=True,
        null=True,
        verbose_name='Трудовая книжка'
    )
    military_document = models.FileField(
        upload_to=user_upload_path,
        blank=True,
        null=True,
        verbose_name='Военный билет'
    )
    international_passport = models.FileField(
        upload_to=user_upload_path,
        blank=True,
        null=True,
        verbose_name='Загранпаспорт'
    )
    additional_document = models.FileField(
        upload_to=user_upload_path,
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
        blank=True,
        null=True,
        verbose_name='Название'
    )

    branch = models.CharField(
        max_length=100,
        db_index=True,
        blank=True,
        null=True,
        default='региональное отделение',
        verbose_name='Региональное отделение'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'регионы'
        verbose_name = 'Регион'


class Area(models.Model):
    name = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Название направления'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'направления'
        verbose_name = 'Направление'


class Unit(models.Model):
    """Структурная единица"""
    name = models.CharField(
        max_length=100,
        db_index=True,
        blank=True,
        null=True,
        verbose_name='Название'
    )
    commander = models.OneToOneField(
        RSOUser,
        related_name='commander',
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        verbose_name='Командир'
    )
    about = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='Описание',
        default=''
    )
    emblem = models.ImageField(
        upload_to=user_upload_path,
        blank=True,
        null=True,
        verbose_name='Эмблема'
    )
    social_vk = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        default='https://vk.com/',
        verbose_name='Ссылка ВК'
    )
    social_tg = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        default='https://',
        verbose_name='Ссылка Телеграм'
    )
    banner = models.ImageField(
        upload_to=user_upload_path,
        blank=True,
        null=True,
        verbose_name='Баннер'
    )
    slogan = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        default='',
        verbose_name='Девиз'
    )
    founding_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Дата основания'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'структурные единицы'
        verbose_name = 'Структурная единица'



class Detachment(Unit):
    area = models.ForeignKey(
        Area,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        verbose_name='Направление'
    )

    def clean(self):
        if not self.commander:
            raise ValidationError('Отряд должен иметь командира.')

    # регион
    # institution = models.ForeignKey(
    #   'Institution',
    #   null=True,
    #   blank=True,
    #   on_delete=models.PROTECT,
    #   verbose_name='Учебное заведение'
    #  )
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