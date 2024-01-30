from datetime import date

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

from users.constants import (Gender, MilitaryDocType, PrivacyOption,
                             RelationshipType, StudyForm)
from users.utils import document_path, image_path, validate_years


class RSOUser(AbstractUser):
    email = models.EmailField(
        verbose_name='Email',
        max_length=254,
        null=True,
        blank=True
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
        to='headquarters.Region',
        null=True,
        on_delete=models.PROTECT,
        verbose_name='Регион ОО'
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
    is_verified = models.BooleanField(
        verbose_name='Статус верификации',
        default=False,
    )
    membership_fee = models.BooleanField(
        default=False,
        verbose_name='Членский взнос оплачен'
    )

    class Meta:
        verbose_name_plural = 'Пользователи'
        verbose_name = 'Пользователь'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        try:
            UserEducation.objects.get_or_create(user=self)
            UserDocuments.objects.get_or_create(user=self)
            UserForeignDocuments.objects.get_or_create(user=self)
            UserRegion.objects.get_or_create(user=self)
            UserPrivacySettings.objects.get_or_create(user=self)
            UserMedia.objects.get_or_create(user=self)
            UserStatementDocuments.objects.get_or_create(user=self)
            UserParent.objects.get_or_create(user=self)
        except Exception:
            raise

    def clean(self):
        super().clean()
        if self.email and RSOUser.objects.exclude(pk=self.pk).filter(
                email__iexact=self.email
        ).exists():
            raise ValidationError('Данный Email уже зарегистрирован.')

    def __str__(self):
        return (
            f'Пользователь {self.last_name} '
            f'{self.first_name}. Id: {self.id}'
        )


class UserEducation(models.Model):
    """Информация об образовательной организации пользователя."""

    user = models.OneToOneField(
        verbose_name='Пользователь',
        to='RSOUser',
        on_delete=models.CASCADE,
        related_name='education',
    )
    study_institution = models.ForeignKey(
        to='headquarters.EducationalInstitution',
        on_delete=models.CASCADE,
        related_name='users_education',
        verbose_name='Образовательная организация',
        blank=True,
        null=True,
    )
    study_faculty = models.CharField(
        verbose_name='Факультет',
        max_length=200,
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


class UserProfessionalEducation(models.Model):
    """Дополнительное профессиональное образование."""

    user = models.ForeignKey(
        verbose_name='Пользователь',
        to='RSOUser',
        on_delete=models.CASCADE,
        related_name='professional_education',
    )
    study_institution = models.CharField(
        verbose_name='Образовательная организация',
        max_length=200,
        blank=True,
        null=True
    )
    years_of_study = models.CharField(
        verbose_name='Годы обучения',
        blank=True,
        null=True,
        max_length=9,
        validators=[validate_years]
    )
    exam_score = models.CharField(
        verbose_name='Оценка',
        max_length=20,
        blank=True,
        null=True
    )
    qualification = models.CharField(
        verbose_name='Квалификация',
        max_length=100,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name_plural = 'Дополнительные профессиональные образования.'
        verbose_name = 'Дополнительное профессиональное образование.'

    def __str__(self):
        return (
            f'Пользователь {self.user.last_name} '
            f'{self.user.first_name}. Id: {self.user.id}'
        )


class UserDocuments(models.Model):
    """Информация о документах пользователя."""

    user = models.OneToOneField(
        verbose_name='Пользователь',
        to='RSOUser',
        on_delete=models.CASCADE,
        related_name='documents',
    )
    russian_passport = models.BooleanField(
        verbose_name='Паспорт гражданина РФ',
        default=True,
    )
    snils = models.CharField(
        max_length=30, blank=True, null=True,
        verbose_name='СНИЛС'
    )
    inn = models.CharField(
        verbose_name='ИНН',
        max_length=30,
        blank=True,
        null=True,
    )
    pass_ser_num = models.CharField(
        verbose_name='Номер и серия паспорта',
        max_length=20,
        blank=True,
        null=True,
    )
    pass_town = models.CharField(
        verbose_name='Город рождения',
        max_length=200,
        blank=True,
        default='',
    )
    pass_whom = models.CharField(
        max_length=230,
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
        max_length=100,
        blank=True,
        null=True,
    )
    work_book_num = models.CharField(
        verbose_name='Трудовая книжка номер',
        max_length=30,
        blank=True,
        null=True,
    )
    international_pass = models.CharField(
        verbose_name='Загранпаспорт номер',
        max_length=30,
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
        max_length=30,
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


class UserForeignDocuments(models.Model):
    """Информация о документах пользователя-инстранца."""

    user = models.OneToOneField(
        verbose_name='Пользователь',
        to='RSOUser',
        on_delete=models.CASCADE,
        related_name='foreign_documents',
    )
    name = models.CharField(
        max_length=30,
        verbose_name='Документ, удостоверяющий личность'
    )
    snils = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        verbose_name='СНИЛС'
    )
    inn = models.CharField(
        verbose_name='ИНН',
        max_length=30,
        blank=True,
        null=True,
    )
    foreign_pass_num = models.CharField(
        verbose_name='Серия и номер',
        max_length=50,
        blank=True,
        null=True,
    )
    foreign_pass_whom = models.CharField(
        max_length=230,
        verbose_name='Кем выдан',
        blank=True,
        null=True,
    )
    foreign_pass_date = models.DateField(
        verbose_name='Дата выдачи',
        blank=True,
        null=True,
    )
    work_book_num = models.CharField(
        verbose_name='Трудовая книжка: серия, номер',
        max_length=15,
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name_plural = 'Документы иностранных пользователей'
        verbose_name = 'Документы иностранного пользователя'
        constraints = [
            models.UniqueConstraint(fields=['user'],
                                    name='unique_user_foreign_documents')
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
        verbose_name='Пользователь',
        to='RSOUser',
        on_delete=models.CASCADE,
        related_name='user_region',
    )
    reg_region = models.ForeignKey(
        to='headquarters.Region',
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
        to='headquarters.Region',
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

    user = models.OneToOneField(
        verbose_name='Пользователь',
        to='RSOUser',
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

    user = models.OneToOneField(
        verbose_name='Пользователь',
        to='RSOUser',
        on_delete=models.CASCADE,
        related_name='media',
    )
    banner = models.ImageField(
        upload_to=image_path,
        blank=True,
        null=True,
        verbose_name='Баннер личной страницы'
    )
    photo = models.ImageField(
        upload_to=image_path,
        blank=True,
        null=True,
        verbose_name='Аватарка'
    )
    photo1 = models.ImageField(
        upload_to=image_path,
        blank=True,
        null=True,
        verbose_name='Фото 1'
    )
    photo2 = models.ImageField(
        upload_to=image_path,
        blank=True,
        null=True,
        verbose_name='Фото 2'
    )
    photo3 = models.ImageField(
        upload_to=image_path,
        blank=True,
        null=True,
        verbose_name='Фото 3'
    )
    photo4 = models.ImageField(
        upload_to=image_path,
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
        verbose_name='Пользователь',
        to='RSOUser',
        on_delete=models.CASCADE,
        related_name='statement',
    )
    statement = models.FileField(
        upload_to=document_path,
        blank=True,
        null=True,
        verbose_name='Заявление на вступлении в РСО'
    )
    consent_personal_data = models.FileField(
        upload_to=document_path,
        blank=True,
        null=True,
        verbose_name='Согласие на обработку персональных данных'
    )
    consent_personal_data_representative = models.FileField(
        upload_to=document_path,
        blank=True,
        null=True,
        verbose_name='Согласие официального представителя на '
                     'обработку персональных данных несовершеннолетнего'
    )
    passport = models.FileField(
        upload_to=document_path,
        blank=True,
        null=True,
        verbose_name='Паспорт гражданина РФ'
    )
    passport_representative = models.FileField(
        upload_to=document_path,
        blank=True,
        null=True,
        verbose_name='Паспорт законного представителя'
    )
    snils_file = models.FileField(
        upload_to=document_path,
        blank=True,
        null=True,
        verbose_name='СНИЛС'
    )
    inn_file = models.FileField(
        upload_to=document_path,
        blank=True,
        null=True,
        verbose_name='ИИН'
    )
    employment_document = models.FileField(
        upload_to=document_path,
        blank=True,
        null=True,
        verbose_name='Трудовая книжка'
    )
    military_document = models.FileField(
        upload_to=document_path,
        blank=True,
        null=True,
        verbose_name='Военный билет'
    )
    international_passport = models.FileField(
        upload_to=document_path,
        blank=True,
        null=True,
        verbose_name='Загранпаспорт'
    )
    additional_document = models.FileField(
        upload_to=document_path,
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
            models.UniqueConstraint(
                fields=['user'],
                name='unique_user_statement'
            )
        ]

    def __str__(self):
        return (
            f'Пользователь {self.user.last_name} '
            f'{self.user.first_name}. Id: {self.user.id}'
        )


class UserParent(models.Model):
    """Законный представитель несовершеннолетнего."""
    user = models.OneToOneField(
        verbose_name='Пользователь',
        to='RSOUser',
        on_delete=models.CASCADE,
        related_name='parent',
    )
    parent_last_name = models.CharField(
        null=True,
        blank=True,
        max_length=150,
        verbose_name='Фамилия',
    )
    parent_first_name = models.CharField(
        null=True,
        blank=True,
        max_length=150,
        verbose_name='Имя',
    )
    parent_patronymic_name = models.CharField(
        null=True,
        blank=True,
        max_length=150,
        verbose_name='Отчество',
    )
    parent_date_of_birth = models.DateField(
        null=True,
        blank=True,
        verbose_name='Дата рождения',
    )
    relationship = models.CharField(
        null=True,
        blank=True,
        verbose_name='Кем является',
        max_length=8,
        choices=RelationshipType.choices,
    )
    parent_phone_number = models.CharField(
        null=True,
        blank=True,
        verbose_name='Номер телефона',
        max_length=30,
        default='+7',
    )
    russian_passport = models.BooleanField(
        verbose_name='Паспорт гражданина РФ',
        default=True,
    )
    passport_number = models.CharField(
        null=True,
        blank=True,
        verbose_name='Номер и серия',
        max_length=50,

    )
    passport_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Дата выдачи',
    )
    passport_authority = models.CharField(
        null=True,
        blank=True,
        verbose_name='Кем выдан',
        max_length=150,
    )
    region = models.ForeignKey(
        null=True,
        blank=True,
        to='headquarters.Region',
        on_delete=models.PROTECT,
        verbose_name='Регион'
    )
    city = models.CharField(
        null=True,
        blank=True,
        verbose_name='Населенный пункт',
        max_length=50,
    )
    address = models.CharField(
        null=True,
        blank=True,
        verbose_name='Улица, дом, квартира',
        max_length=200,
    )

    class Meta:
        verbose_name_plural = 'Законные представители несовершеннолетних'
        verbose_name = 'Законный представитель несовершеннолетнего'

    def __str__(self):
        return (
            f'Представитель {self.parent_last_name} '
            f'{self.parent_first_name}. Id: {self.user.id}'
        )


class UserVerificationRequest(models.Model):
    """Таблица для хранения заявок на верификацию."""
    user = models.ForeignKey(
        to='RSOUser',
        on_delete=models.CASCADE,
        related_name='veirification',
        verbose_name='Пользователь, подавший заявку на верификацию',
    )

    class Meta:
        verbose_name_plural = 'Заявки на верификацию'
        verbose_name = 'Заявка на верификацию'

    def __str__(self):
        return (
            f'Пользователь {self.user.last_name} {self.user.first_name} '
            f'{self.user.username} подал заявку.'
        )


class UserMembershipLogs(models.Model):
    """Таблица для хранения логов об оплате членского взноса."""

    user = models.ForeignKey(
        to='RSOUser',
        on_delete=models.CASCADE,
        related_name='membership_logs',
        verbose_name='Пользователь',
    )
    status_changed_by = models.ForeignKey(
        to='RSOUser',
        on_delete=models.CASCADE,
        related_name='changed_membership_logs',
        verbose_name='Пользователь, изменивший статус оплаты другому'
    )
    date = models.DateField(
        verbose_name='Дата действия',
        auto_now_add=True,
    )
    period = models.CharField(
        verbose_name='Период',
        max_length=30,
        editable=False,
    )
    status = models.CharField(
        verbose_name='Статус',
        max_length=50
    )
    description = models.TextField(
        verbose_name='Сообщение лога',
        blank=True,
        null=True
    )

    class Meta:
        verbose_name_plural = 'Логи оплаты членских взносов'
        verbose_name = 'Лог оплаты членского взноса'

    def save(self, *args, **kwargs):
        """Устанавливает поле period в зависимости от текущей даты.

        Если дата до 1 января, то период - текущий год-текущий год + 1.
        Если дата после 1 января, то период - предыдущий год-текущий год.
        """
        current_date = date.today()
        current_year = current_date.year
        if date(current_year, 1, 1) <= current_date < date(
                current_year, 10, 1
        ):
            self.period = f"{current_year - 1}-{current_year}"
        elif date(current_year, 10, 1) <= current_date <= date(
                current_year, 12, 31
        ):
            self.period = f"{current_year}-{current_year + 1}"
        else:
            self.period = "Неопределенный"
        super(UserMembershipLogs, self).save(*args, **kwargs)


class MemberCert(models.Model):
    user = models.ForeignKey(
        to='RSOUser',
        on_delete=models.CASCADE,
        related_name='member_cert',
        verbose_name='Пользователь',
    )
    cert_start_date = models.DateField(
        verbose_name='Дата начала действия справки',
        auto_now_add=True,
        null=False,
        blank=False,
    )
    cert_end_date = models.DateField(
        verbose_name='Дата окончания действия справки',
        null=False,
        blank=False,
    )
    recipient = models.CharField(
        verbose_name='Справка выдана для предоставления',
        null=False,
        blank=False,
        max_length=250
    )
    issue_date = models.DateField(
        verbose_name='Дата выдачи справки',
        auto_now_add=True,
    )
    number = models.CharField(
        verbose_name='Номер справки',
        default=' ',
        max_length=40
    )
    signatory = models.CharField(
        verbose_name='ФИО подписывающего лица',
        max_length=250,
        blank=True,
        null=True
    )
    position_procuration = models.CharField(
        verbose_name='Должность подписывающего лица, доверенность',
        max_length=250,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name_plural = 'Выданные справки о членстве в РСО.'
        verbose_name = 'Выданная справка о членстве в РСО.'

    def __str__(self):
        return (
            f'Пользователь {self.signatory} выдал справку'
            f' пользователю {self.user.username}.'
        )


class UserMemberCertLogs(models.Model):
    """Таблица для хранения логов о выдаче справок."""

    user = models.ForeignKey(
        to='RSOUser',
        on_delete=models.CASCADE,
        related_name='membercert_logs',
        verbose_name='Пользователь',
    )
    cert_issued_by = models.ForeignKey(
        to='RSOUser',
        on_delete=models.CASCADE,
        related_name='issued_membercert_logs',
        verbose_name='Пользователь, выдавший справку'
    )
    date = models.DateField(
        verbose_name='Дата действия',
        auto_now_add=True,
    )
    description = models.TextField(
        verbose_name='Сообщение лога',
        blank=True,
        null=True
    )
    cert_type = models.CharField(
        verbose_name='Тип справки',
        max_length=50
    )

    class Meta:
        verbose_name_plural = 'Логи выдачи справок о членстве в РСО.'
        verbose_name = 'Лог выдачи справки о членстве в РСО.'
