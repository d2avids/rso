from django.db import models

from events.utils import document_path, image_path


class Event(models.Model):
    class EventFormat(models.TextChoices):
        ONLINE = 'ONLINE', 'Онлайн'
        OFFLINE = 'OFFLINE', 'Оффлайн'

    class EventDirection(models.TextChoices):
        VOLUNTARY = 'voluntary', 'Добровольческое'
        EDUCATIONAL = 'educational', 'Образовательное'
        PATRIOTIC = 'patriotic', 'Патриотическое'
        SPORT = 'sport', 'Спортивное'
        CREATIVE = 'creative', 'Творческое'

    class EventStatus(models.TextChoices):
        ACTIVE = 'active', 'Активный'
        INACTIVE = 'inactive', 'Завершенный'

    class EventApplicationType(models.TextChoices):
        PERSONAL = 'personal', 'Персональная'
        GROUP = 'group', 'Групповая'
        MULTI_STAGE = 'multi_stage', 'Мультиэтапная'

    class EventAvailableStructuralUnit(models.TextChoices):
        DETACHMENTS = 'detachments', 'Отряды'
        EDUCATIONALS = 'educationals', 'Образовательные штабы'
        LOCALS = 'locals', 'Местные штабы'
        REGIONALS = 'regionals', 'Региональные штабы'
        DISTRICTS = 'districts', 'Окружные штабы'
        CENTRAL = 'central', 'Центральные штабы'

    class EventScale(models.TextChoices):
        DETACHMENTS = 'detachments', 'Отрядное'
        EDUCATIONALS = 'educationals', 'Мероприятие ОО'
        LOCALS = 'locals', 'Городское'
        REGIONALS = 'regionals', 'Региональное'
        DISTRICTS = 'districts', 'Мероприятие ОО'
        CENTRAL = 'central', 'Отрядное ОО'

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
        verbose_name='Название мероприятия,'
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
                     'формировать групповые заявки'
    )

    class Meta:
        verbose_name_plural = 'Мероприятия'
        verbose_name = 'Мероприятие'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        try:
            EventTimeData.objects.get_or_create(event_id=self.id)
            EventDocumentData.objects.get_or_create(event_id=self.id)
        except Exception:
            raise

    def __str__(self):
        return f'{self.name} id {self.id}'


class EventTimeData(models.Model):
    class EventDurationType(models.TextChoices):
        ONE_DAY = 'one_day', 'Однодневное'
        MULTIPLE_DAYS = 'multiple_days', 'Многодневное'

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
    # application = models.ForeignKey(
    #     to='EventApplications',
    #     on_delete=models.CASCADE,
    #     related_name='answers',
    #     verbose_name='Заявка',
    # )
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
        ordering = ['-id']
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
