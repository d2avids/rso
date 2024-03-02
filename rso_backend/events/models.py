from django.core.exceptions import ValidationError
from django.db import models

from events.constants import HEADQUARTERS_MODELS_MAPPING
from events.utils import document_path, image_path


class Event(models.Model):
    class EventFormat(models.TextChoices):
        ONLINE = 'Онлайн', 'Онлайн'
        OFFLINE = 'Оффлайн', 'Оффлайн'

    class EventDirection(models.TextChoices):
        VOLUNTARY = 'Добровольческое', 'Добровольческое'
        EDUCATIONAL = 'Образовательное', 'Образовательное'
        PATRIOTIC = 'Патриотическое', 'Патриотическое'
        SPORT = 'Спортивное', 'Спортивное'
        CREATIVE = 'Творческое', 'Творческое'

    class EventStatus(models.TextChoices):
        ACTIVE = 'Активный', 'Активный'
        INACTIVE = 'Завершенный', 'Завершенный'

    class EventApplicationType(models.TextChoices):
        PERSONAL = 'Персональная', 'Персональная'
        GROUP = 'Групповая', 'Групповая'
        MULTI_STAGE = 'Мультиэтапная', 'Мультиэтапная'

    class EventAvailableStructuralUnit(models.TextChoices):
        DETACHMENTS = 'Отряды', 'Отряды'
        EDUCATIONALS = 'Образовательные штабы', 'Образовательные штабы'
        LOCALS = 'Местные штабы', 'Местные штабы'
        REGIONALS = 'Региональные штабы', 'Региональные штабы'
        DISTRICTS = 'Окружные штабы', 'Окружные штабы'
        CENTRAL = 'Центральные штабы', 'Центральные штабы'

    class EventScale(models.TextChoices):
        DETACHMENTS = 'Отрядное', 'Отрядное'
        EDUCATIONALS = 'Образовательное', 'Мероприятие Образовательного Штаба'
        LOCALS = 'Городское', 'Городское'
        REGIONALS = 'Региональное', 'Региональное'
        DISTRICTS = 'Окружное', 'Мероприятие Окружного Штаба'
        CENTRAL = 'Всероссийское', 'Мероприятие ЦШ'

    author = models.ForeignKey(
        to='users.RSOUser',
        on_delete=models.CASCADE,
        verbose_name='Создатель мероприятия',
    )
    scale = models.CharField(
        max_length=20,
        choices=EventScale.choices,
        default=EventScale.DETACHMENTS,
        verbose_name='Масштаб'
    )
    format = models.CharField(
        max_length=7,
        choices=EventFormat.choices,
        default=EventFormat.OFFLINE,
        verbose_name='Тип мероприятия'
    )
    direction = models.CharField(
        max_length=20,
        choices=EventDirection.choices,
        default=EventDirection.VOLUNTARY,
        verbose_name='Масштаб мероприятия'
    )
    status = models.CharField(
        max_length=20,
        choices=EventStatus.choices,
        default=EventStatus.ACTIVE,
        verbose_name='Статус мероприятия'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    name = models.CharField(
        max_length=100,
        verbose_name='Название мероприятия'
    )
    banner = models.ImageField(
        upload_to=image_path,
        blank=True,
        null=True,
        verbose_name='Баннер'
    )
    conference_link = models.CharField(
        max_length=250,
        verbose_name='Ссылка на конференцию',
    )
    address = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        verbose_name='Адрес проведения (если мероприятие оффлайн)',
    )
    participants_number = models.PositiveIntegerField(
        verbose_name='Количество участников'
    )
    description = models.TextField(
        verbose_name='О мероприятии'
    )
    application_type = models.CharField(
        max_length=20,
        choices=EventApplicationType.choices,
        default=EventApplicationType.GROUP,
        verbose_name='Вид принимаемых к подаче на мероприятие заявок'
    )
    available_structural_units = models.CharField(
        max_length=30,
        choices=EventAvailableStructuralUnit.choices,
        default=EventAvailableStructuralUnit.DETACHMENTS,
        verbose_name='Объекты, имеющие возможность '
                     'формировать групповые заявки',
        blank=True,
        null=True
    )
    # Ссылка на штаб/отряд организовавший мероприятие
    # Заполнено может быть только одно поле из шести
    org_central_headquarter = models.ForeignKey(
        to='headquarters.CentralHeadquarter',
        on_delete=models.CASCADE,
        related_name='events',
        null=True,
        blank=True,
        verbose_name='Центральный штаб-организатор',
    )
    org_district_headquarter = models.ForeignKey(
        to='headquarters.DistrictHeadquarter',
        on_delete=models.CASCADE,
        related_name='events',
        null=True,
        blank=True,
        verbose_name='Окружной штаб-организатор',
    )
    org_regional_headquarter = models.ForeignKey(
        to='headquarters.RegionalHeadquarter',
        on_delete=models.CASCADE,
        related_name='events',
        null=True,
        blank=True,
        verbose_name='Региональный штаб-организатор',
    )
    org_local_headquarter = models.ForeignKey(
        to='headquarters.LocalHeadquarter',
        on_delete=models.CASCADE,
        related_name='events',
        null=True,
        blank=True,
        verbose_name='Местный штаб-организатор',
    )
    org_educational_headquarter = models.ForeignKey(
        to='headquarters.EducationalHeadquarter',
        on_delete=models.CASCADE,
        related_name='events',
        null=True,
        blank=True,
        verbose_name='Образовательный штаб-организатор',
    )
    org_detachment = models.ForeignKey(
        to='headquarters.Detachment',
        on_delete=models.CASCADE,
        related_name='events',
        null=True,
        blank=True,
        verbose_name='Отряд-организатор',
    )

    class Meta:
        ordering = ['-id']
        verbose_name_plural = 'Мероприятия'
        verbose_name = 'Мероприятие'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        EventTimeData.objects.get_or_create(event_id=self.id)
        EventDocumentData.objects.get_or_create(event_id=self.id)
        EventOrganizationData.objects.get_or_create(
            event_id=self.id,
            organizer=self.author,
        )

    def clean(self):
        filled_fields = [bool(getattr(self, field)) for field in [
            'org_central_headquarter',
            'org_district_headquarter',
            'org_regional_headquarter',
            'org_local_headquarter',
            'org_educational_headquarter',
            'org_detachment',]]
        if sum(filled_fields) != 1:
            raise ValidationError(
                'Структурная единица-организатор должна быть '
                'заполнена в одном из полей и только в одном.'
            )

    def __str__(self):
        return f'{self.name} id {self.id}'


class EventTimeData(models.Model):
    class EventDurationType(models.TextChoices):
        ONE_DAY = 'Однодневное', 'Однодневное'
        MULTIPLE_DAYS = 'Многодневное', 'Многодневное'

    event = models.OneToOneField(
        to='Event',
        on_delete=models.CASCADE,
        related_name='time_data',
        verbose_name='Мероприятие'
    )
    event_duration_type = models.CharField(
        max_length=20,
        choices=EventDurationType.choices,
        default=EventDurationType.ONE_DAY,
        verbose_name='Продолжительность мероприятия',
        blank=True,
        null=True,
    )
    start_date = models.DateField(
        verbose_name='Дата начала мероприятия',
        blank=True,
        null=True,
    )
    start_time = models.TimeField(
        verbose_name='Время начала мероприятия',
        blank=True,
        null=True,
    )
    end_date = models.DateField(
        verbose_name='Дата окончания мероприятия',
        blank=True,
        null=True,
    )
    end_time = models.TimeField(
        verbose_name='Время окончания мероприятия',
        blank=True,
        null=True,
    )
    registration_end_date = models.DateField(
        verbose_name='Дата окончания регистрации',
        blank=True,
        null=True,
    )
    registration_end_time = models.TimeField(
        verbose_name='Время окончания регистрации',
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name_plural = 'Информация о времени мероприятий'
        verbose_name = 'Информация о времени мероприятия'
        constraints = [
            models.UniqueConstraint(fields=['event'],
                                    name='unique_event_time_data')
        ]

    def __str__(self):
        return (
            f'{self.event.name} id {self.event.id} начинается '
            f'{self.start_date, self.start_time}, '
            f'заканчивается {self.end_date, self.end_time}'
        )


class EventDocument(models.Model):
    """ Таблица для хранения документов мероприятий """
    event = models.ForeignKey(
        to='Event',
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name='Мероприятие'
    )
    document = models.FileField(
        upload_to=document_path,
        verbose_name='Файл формата pdf, png, jpeg'
    )

    class Meta:
        verbose_name_plural = 'Документы мероприятий'
        verbose_name = 'Документы мероприятия'

    def __str__(self):
        return f'Документ мероприятия {self.event.name} id {self.event.id}'


class EventDocumentData(models.Model):
    """Список необходимых документов для участия в мероприятии."""
    event = models.OneToOneField(
        to='Event',
        on_delete=models.CASCADE,
        related_name='document_data',
        verbose_name='Мероприятие'
    )
    passport = models.BooleanField(
        default=False,
        verbose_name='Паспорт'
    )
    snils = models.BooleanField(
        default=False,
        verbose_name='СНИЛС'
    )
    inn = models.BooleanField(
        default=False,
        verbose_name='ИНН'
    )
    work_book = models.BooleanField(
        default=False,
        verbose_name='Трудовая книжка'
    )
    military_document = models.BooleanField(
        default=False,
        verbose_name='Военный билет или приписное свидетельство',
    )
    consent_personal_data = models.BooleanField(
        default=False,
        verbose_name='Согласие на обработку персональных данных'
    )
    additional_info = models.TextField(
        verbose_name='Расскажите, с какими документами необходимо '
                     'просто ознакомиться, а какие скачать и заполнить',
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name_plural = 'Список необходимых документов для мероприятий'
        verbose_name = 'Список необходимых документов для мероприятия'
        constraints = [
            models.UniqueConstraint(fields=['event'],
                                    name='unique_event_document_data')
        ]


class EventOrganizationData(models.Model):
    event = models.ForeignKey(
        to='Event',
        on_delete=models.CASCADE,
        related_name='organization_data',
        verbose_name='Мероприятие'
    )
    organizer = models.ForeignKey(
        to='users.RSOUser',
        on_delete=models.CASCADE,
        related_name='events',
        verbose_name='Пользователь-организатор',
        blank=True,
        null=True,
    )
    organizer_phone_number = models.CharField(
        max_length=30,
        default='+7',
        blank=True,
        null=True,
        verbose_name='Номер телефона',
    )
    organizer_email = models.EmailField(
        max_length=250,
        blank=True,
        null=True,
        verbose_name='Email',
    )
    organization = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        verbose_name='Организация'
    )
    telegram = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Телеграмм'
    )
    is_contact_person = models.BooleanField(
        default=False,
        verbose_name='Сделать контактным лицом',
    )

    class Meta:
        verbose_name_plural = 'Организаторы мероприятий'
        verbose_name = 'Организатор'

    def save(self, *args, **kwargs):
        if self.organizer:
            if not self.organizer_phone_number:
                self.organizer_phone_number = (
                    self.organizer.phone_number if hasattr(
                        self.organizer, 'phone_number'
                    ) else None
                )
            if not self.organizer_email:
                self.organizer_email = (
                    self.organizer.email if hasattr(
                        self.organizer, 'email'
                    ) else None
                )
            if not self.telegram:
                self.telegram = (
                    self.organizer.social_tg if hasattr(
                        self.organizer, 'social_tg'
                    ) else None
                )
            if not self.organization:
                self.organization = (
                    self.organizer.education.study_institution if hasattr(
                        self.organizer, 'education') and hasattr(
                        self.organizer.education, 'study_institution'
                    ) else None
                )
        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f'{self.organizer.first_name, self.organizer.last_name} '
            f'- {self.organizer_phone_number}, '
            f'id {self.organizer} - организатора '
            f'мероприятия {self.event.name}, id {self.event.id}'
        )


class EventAdditionalIssue(models.Model):
    """Таблица для хранения дополнительных вопросов участникам мероприятий."""
    event = models.ForeignKey(
        to='Event',
        on_delete=models.CASCADE,
        related_name='additional_issues',
        verbose_name='Мероприятие'
    )
    issue = models.TextField(
        verbose_name='Вопрос',
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ['-id']
        verbose_name_plural = 'Дополнительные вопросы мероприятий'
        verbose_name = 'Дополнительные вопросы мероприятия'

    def __str__(self):
        return (
            f'Вопрос по мероприятию {self.event.name}, '
            f'id {self.event.id}: {self.issue[:25]}...'
        )


class EventApplications(models.Model):
    """Таблица для хранения индивидуальных заявок на участие в мероприятиях."""
    event = models.ForeignKey(
        to='Event',
        on_delete=models.CASCADE,
        related_name='event_applications',
        verbose_name='Мероприятие'
    )
    user = models.ForeignKey(
        to='users.RSOUser',
        on_delete=models.CASCADE,
        related_name='event_applications',
        verbose_name='Пользователь',
    )
    created_at = models.DateTimeField(
        verbose_name='Дата создания заявки',
        auto_now_add=True,
    )

    class Meta:
        ordering = ['-id']
        verbose_name_plural = 'Заявки на участие в мероприятиях'
        verbose_name = 'Заявка на участие в мероприятии'
        constraints = [
            models.UniqueConstraint(
                fields=('event', 'user'),
                name='unique_event_application'
            ),
        ]

    def __str__(self):
        return (
            f'Заявка пользователя {self.user.last_name} '
            f'{self.user.first_name}. Id: {self.user.id}'
            f' на участие в мероприятии {self.event.name}. Id: {self.event.id}'
        )


class EventIssueAnswer(models.Model):
    """Таблица для хранения ответов на вопросы участников мероприятий."""
    event = models.ForeignKey(
        to='Event',
        on_delete=models.CASCADE,
        related_name='issue_answers',
        verbose_name='Мероприятие',
    )
    user = models.ForeignKey(
        to='users.RSOUser',
        on_delete=models.CASCADE,
        related_name='issue_answers',
        verbose_name='Пользователь',
    )
    issue = models.ForeignKey(
        to='EventAdditionalIssue',
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='Вопрос',
    )
    answer = models.TextField(
        verbose_name='Ответ',
    )

    class Meta:
        ordering = ['id']
        verbose_name_plural = 'Ответы на вопросы участников мероприятий'
        verbose_name = 'Ответ на вопрос участника мероприятия'
        constraints = [
            models.UniqueConstraint(
                fields=('event', 'user', 'issue'),
                name='unique_issue_answer'
            )
        ]


class EventParticipants(models.Model):
    """Таблица для хранения участников мероприятий."""
    event = models.ForeignKey(
        to='Event',
        on_delete=models.CASCADE,
        related_name='event_participants',
        verbose_name='Мероприятие'
    )
    user = models.ForeignKey(
        to='users.RSOUser',
        on_delete=models.CASCADE,
        related_name='event_participants',
        verbose_name='Пользователь',
    )

    class Meta:
        ordering = ['-id']
        verbose_name_plural = 'Участники мероприятий'
        verbose_name = 'Участник мероприятия'
        constraints = [
            models.UniqueConstraint(
                fields=('event', 'user'),
                name='unique_event_participant'
            ),
        ]


class EventUserDocument(models.Model):
    """
    Таблица для хранения заполненных сканов документов
    участников мероприятий.
    """
    event = models.ForeignKey(
        to='Event',
        on_delete=models.CASCADE,
        related_name='event_user_documents',
        verbose_name='Мероприятие',
    )
    user = models.ForeignKey(
        to='users.RSOUser',
        on_delete=models.CASCADE,
        related_name='event_user_documents',
        verbose_name='Пользователь',
    )
    document = models.FileField(
        verbose_name='Скан документа. Файл формата pdf, png, jpeg.',
        upload_to=document_path,
    )

    class Meta:
        ordering = ['-id']
        verbose_name_plural = 'Сканы документов участников мероприятий'
        verbose_name = 'Скан документа участника мероприятия'

    def __str__(self):
        return (
            f'Скан документа пользователя {self.user.last_name} '
            f'{self.user.first_name}. Id: {self.user.id}'
            f' на участие в мероприятии {self.event.name}. Id: {self.event.id}'
        )


class GroupEventApplication(models.Model):
    """Таблица для хранения заявок на участие в групповом мероприятии."""
    event = models.ForeignKey(
        to='Event',
        on_delete=models.CASCADE,
        related_name='group_event_applications',
        verbose_name='Мероприятие',
    )
    author = models.ForeignKey(
        to='users.RSOUser',
        on_delete=models.CASCADE,
        related_name='group_event_applications',
        verbose_name='Автор заявки'
    )
    created_at = models.DateTimeField(
        verbose_name='Дата и время создания заявки',
        auto_now_add=True
    )
    applicants = models.ManyToManyField(
        to='users.RSOUser',
        through='GroupEventApplicant',
        verbose_name='Участники',
        blank=True,
    )

    class Meta:
        ordering = ['-id']
        verbose_name_plural = 'Заявки на участие в групповых мероприятиях'
        verbose_name = 'Заявка на участие в групповом мероприятии'

    def __str__(self):
        return f'Заявка {self.event.name} id {self.id}'


class GroupEventApplicant(models.Model):
    """Таблица для хранения поданных в груп. заявке участников мероприятия."""
    application = models.ForeignKey(
        to='GroupEventApplication',
        on_delete=models.CASCADE,
        related_name='group_applicants',
        verbose_name='Заявка на участие'
    )
    user = models.ForeignKey(
        to='users.RSOUser',
        on_delete=models.CASCADE,
        related_name='group_event_applicant',
        verbose_name='Участник'
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Участник группового мероприятия'
        verbose_name_plural = 'Участники групповых мероприятий'
        constraints = [
            models.UniqueConstraint(
                fields=['application', 'user'],
                name='unique_group_event_application_participant'
            ),
        ]

    def __str__(self):
        return f'{self.user} в заявке {self.application}'


class MultiEventApplication(models.Model):
    """Таблица для хранения заявок на участие в многоэтапном мероприятии."""
    event = models.ForeignKey(
        to='Event',
        on_delete=models.CASCADE,
        related_name='multi_event_applications',
        verbose_name='Мероприятие',
    )
    central_headquarter = models.ForeignKey(
        to='headquarters.CentralHeadquarter',
        on_delete=models.CASCADE,
        related_name='multi_event_applications',
        null=True,
        blank=True,
        verbose_name='Центральный штаб',
    )
    district_headquarter = models.ForeignKey(
        to='headquarters.DistrictHeadquarter',
        on_delete=models.CASCADE,
        related_name='multi_event_applications',
        null=True,
        blank=True,
        verbose_name='Окружной штаб',
    )
    regional_headquarter = models.ForeignKey(
        to='headquarters.RegionalHeadquarter',
        on_delete=models.CASCADE,
        related_name='multi_event_applications',
        null=True,
        blank=True,
        verbose_name='Региональный штаб',
    )
    local_headquarter = models.ForeignKey(
        to='headquarters.LocalHeadquarter',
        on_delete=models.CASCADE,
        related_name='multi_event_applications',
        null=True,
        blank=True,
        verbose_name='Местный штаб',
    )
    educational_headquarter = models.ForeignKey(
        to='headquarters.EducationalHeadquarter',
        on_delete=models.CASCADE,
        related_name='multi_event_applications',
        null=True,
        blank=True,
        verbose_name='Образовательный штаб',
    )
    detachment = models.ForeignKey(
        to='headquarters.Detachment',
        on_delete=models.CASCADE,
        related_name='multi_event_applications',
        null=True,
        blank=True,
        verbose_name='Отряд',
    )
    organizer_id = models.PositiveIntegerField(
        verbose_name='Идентификатор организатора',
    )
    is_approved = models.BooleanField(
        verbose_name='Одобрено',
        default=False
    )
    participants_count = models.PositiveIntegerField(
        verbose_name='Количество участников',
        default=0
    )
    emblem = models.TextField(
        verbose_name='Путь к эмблеме',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(
        verbose_name='Дата и время создания заявки',
        auto_now_add=True
    )

    class Meta:
        ordering = ['-id']
        verbose_name_plural = 'Заявки на участие в многоэтапных мероприятиях'
        verbose_name = 'Заявка на участие в многоэтапном мероприятии'
        constraints = [
            models.UniqueConstraint(
                fields=('event', 'central_headquarter'),
                name='unique_central_headquarter_application'
            ),
            models.UniqueConstraint(
                fields=('event', 'district_headquarter'),
                name='unique_district_headquarter_application'
            ),
            models.UniqueConstraint(
                fields=('event', 'regional_headquarter'),
                name='unique_regional_headquarter_application'
            ),
            models.UniqueConstraint(
                fields=('event', 'local_headquarter'),
                name='unique_local_headquarter_application'
            ),
            models.UniqueConstraint(
                fields=('event', 'educational_headquarter'),
                name='unique_educational_headquarter_application'
            ),
            models.UniqueConstraint(
                fields=('event', 'detachment'),
                name='unique_detachment_application'
            ),
        ]

    def clean(self):
        filled_fields = [bool(getattr(self, field)) for field in [
            'central_headquarter',
            'district_headquarter',
            'regional_headquarter',
            'local_headquarter',
            'educational_headquarter',
            'detachment',]]
        if sum(filled_fields) != 1:
            raise ValidationError(
                'В одной заявке может быть подана только одна структурная'
                'единица'
            )

    def __str__(self):
        return f'Заявка {self.event.name} id {self.id}'
