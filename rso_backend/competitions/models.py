from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from competitions.utils import get_certificate_scans_path


class Competitions(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=255,
        unique=True
    )
    created_at = models.DateTimeField(
        verbose_name='Дата и время создания',
        auto_now_add=True
    )
    start_date = models.DateField(
        verbose_name='Дата начала',
        null=True,
        blank=True
    )
    end_date = models.DateField(
        verbose_name='Дата окончания',
        null=True,
        blank=True
    )

    def __str__(self):
        return f'{self.name} id {self.id}'

    class Meta:
        verbose_name_plural = 'Конкурсы'
        verbose_name = 'Конкурс'


class CompetitionApplications(models.Model):
    competition = models.ForeignKey(
        to='Competitions',
        on_delete=models.CASCADE,
        related_name='competition_applications',
        verbose_name='Конкурс',
    )
    detachment = models.ForeignKey(
        to='headquarters.Detachment',
        on_delete=models.CASCADE,
        related_name='competition_applications',
        verbose_name='Отряд',
        null=True,
        blank=True
    )
    junior_detachment = models.ForeignKey(
        to='headquarters.Detachment',
        on_delete=models.CASCADE,
        related_name='junior_competition_applications',
        verbose_name='Младший отряд',
    )
    created_at = models.DateTimeField(
        verbose_name='Дата и время создания заявки',
        auto_now_add=True
    )
    is_confirmed_by_junior = models.BooleanField(
        verbose_name='Подтверждено младшим отрядом',
        default=False
    )

    def __str__(self):
        return (f'Заявка id {self.id} на участие '
                f'в конкурсе id {self.competition.id}')

    class Meta:
        verbose_name_plural = 'Заявки на участие в конкурсе'
        verbose_name = 'Заявка на участие в конкурсе'
        constraints = [
            models.UniqueConstraint(
                fields=('competition', 'detachment'),
                name='unique_detachment_application_for_competition'
            ),
            models.UniqueConstraint(
                fields=('competition', 'junior_detachment'),
                name='unique_junior_detachment_application'
            ),
            models.UniqueConstraint(
                fields=('detachment', 'junior_detachment'),
                name='unique_tandem_application'
            )
        ]


class CompetitionParticipants(models.Model):
    competition = models.ForeignKey(
        to='Competitions',
        on_delete=models.CASCADE,
        related_name='competition_participants',
        verbose_name='Конкурс',
    )
    junior_detachment = models.ForeignKey(
        to='headquarters.Detachment',
        on_delete=models.CASCADE,
        related_name='junior_competition_participants',
        verbose_name='Младший отряд',
    )
    detachment = models.ForeignKey(
        to='headquarters.Detachment',
        on_delete=models.CASCADE,
        related_name='competition_participants',
        verbose_name='Отряд',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(
        verbose_name='Дата и время создания заявки',
        auto_now_add=True
    )

    def __str__(self):
        return f'Участник(и) id {self.id} в конкурсе id {self.competition.id}'

    class Meta:
        verbose_name_plural = 'Участники конкурса'
        verbose_name = 'Участник конкурса'
        constraints = [
            models.UniqueConstraint(
                fields=('competition', 'detachment'),
                name='unique_detachment_participant'
            ),
            models.UniqueConstraint(
                fields=('competition', 'junior_detachment'),
                name='unique_junior_detachment_participant'
            ),
            models.UniqueConstraint(
                fields=('detachment', 'junior_detachment'),
                name='unique_tandem_participant'
            )
        ]


class Score(models.Model):
    """
    Таблица для хранения очков отрядов за верифицированные отчеты.
    """
    detachment = models.ForeignKey(
        to='headquarters.Detachment',
        on_delete=models.CASCADE,
        related_name='competition_scores',
        verbose_name='Отряд'
    )
    competition = models.ForeignKey(
        to='Competitions',
        on_delete=models.CASCADE,
        related_name='competition_scores',
        verbose_name='Конкурс'
    )
    participation_in_distr_and_interreg_events = (
        models.PositiveSmallIntegerField(
            verbose_name='Оценка',
            default=0
        )
    )

    def __str__(self):
        return (
            f'Оценки отряда {self.detachment.name} '
            f'в конкурсе {self.competition.name}'
        )

    class Meta:
        verbose_name_plural = 'Оценки отрядов'
        verbose_name = 'Оценка отряда'
        constraints = [
            models.UniqueConstraint(
                fields=('detachment', 'competition'),
                name='unique_competition_score'
            )
        ]


class LinksOfParticipationInDistrAndInterregEvents(models.Model):
    """
    Ссылки на участие в окружных и межрегиональных мероприятиях.

    Хранит пользовательские ссылки на социальные сети с фотоотчетом
    с наименованием мероприятия и наименованием ЛСО,
    принявшем в нем участие.
    """
    link = models.URLField(
        verbose_name='Ссылка',
        max_length=500
    )
    event = models.ForeignKey(
        to='ParticipationInDistrAndInterregEvents',
        on_delete=models.CASCADE,
        related_name='links',
        verbose_name='Участие в окружных и межрегиональных мероприятиях'
    )

    def __str__(self):
        return (f'Ссылка участия в конкурсе, id {self.id}')

    class Meta:
        verbose_name_plural = (
            'Ссылки на фотоотчет участия СО в окружных и '
            'межрегиональных мероприятиях'
        )
        verbose_name = (
            'Ссылка на фотоотчет участия СО в окружном '
            'или межрегиональном мероприятии'
        )
        constraints = [
            models.UniqueConstraint(
                fields=('event', 'link'),
                name='unique_event_link'
            )
        ]


class ParticipationInDistrAndInterregEvents(models.Model):
    """
    Участие членов студенческого отряда в окружных и межрегиональных
    мероприятиях. Модель для хранения каждого участия.
    """
    event_name = models.CharField(
        verbose_name='Название мероприятия',
        max_length=255
    )
    certificate_scans = models.FileField(
        verbose_name='Сканы сертификатов',
        upload_to=get_certificate_scans_path,
        blank=True,
        null=True
    )
    number_of_participants = models.PositiveIntegerField(
        verbose_name='Количество участников',
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    created_at = models.DateTimeField(
        verbose_name='Дата и время создания заявки',
        auto_now_add=True
    )
    competition = models.ForeignKey(
        to='Competitions',
        on_delete=models.CASCADE,
        related_name='participation_in_distr_and_interreg_events',
        verbose_name='Конкурс',
    )
    detachment = models.ForeignKey(
        to='headquarters.Detachment',
        on_delete=models.CASCADE,
        related_name='participation_in_distr_and_interreg_events',
        verbose_name='Отряд'
    )
    is_verified = models.BooleanField(
        verbose_name='Подтверждено',
        default=False
    )

    def __str__(self):
        return (f'Участие СО {self.detachment.name} в окружных '
                f'и межрегиональных  мероприятиях, id {self.id}')

    class Meta:
        verbose_name = 'Участие в окружных и межрегиональных мероприятиях'
        ordering = ['-competition__id']
        verbose_name = 'Участие в окружных и межрегиональных мероприятиях'
        verbose_name_plural = 'Участия в окружных и межрегиональных мероприятиях'
        constraints = [
            models.UniqueConstraint(
                fields=('competition', 'detachment', 'event_name'),
                name='unique_participation_in_distr_and_interreg_events'
            )
        ]
