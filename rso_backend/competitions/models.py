from django.db import models
from django.core.exceptions import ValidationError

from rso_backend.competitions.constants import StatusIndicator


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


class CommandSchoolTest(models.Model):
    """Таблица тестов прохождения школы командного состава."""

    detachment = models.ForeignKey(
        to='headquarters.Detachment',
        on_delete=models.CASCADE,
        related_name='command_school_test',
    )
    commander_achievment = models.BooleanField(
        verbose_name=('Региональная школа командного состава'
                      ' пройдена командиром отряда'),
        default=False,
        null=False,
        blank=False
    )
    commissioner_achievment = models.BooleanField(
        verbose_name=('Региональная школа командного состава'
                      ' пройдена комиссаром отряда'),
        default=False,
        null=False,
        blank=False
    )
    commander_link = models.URLField(
        verbose_name=('Ссылка на публикацию о прохождении'
                      ' школы командного состава командиром отряда'),
    )
    commissioner_link = models.URLField(
        verbose_name=('Ссылка на публикацию о прохождении'
                      ' школы командного состава комиссаром отряда'),
    )
    place = models.IntegerField(
        verbose_name='Место в конкурсе',
        default=3
    )
    points = models.IntegerField(
        verbose_name='Перевод полученного места в баллы',
        default=0
    )
    accept = models.BooleanField(
        verbose_name='Подтверждено комиссаром РШ',
        default=False
    )
    status = models.CharField(
        verbose_name='Статус показателя',
        max_length=150,
        choices=StatusIndicator.choices,
        default=StatusIndicator.IN_PROCESSING
    )

    class Meta:
        verbose_name_plural = 'Тесты прохождения школы командного состава'
        verbose_name = 'Тест прохождения школы командного состава'

    def __str__(self):
        return f'Тест прохождения школы командного состава id {self.id}'

    def clean(self):
        if self.commander_achievment and not self.commander_link:
            raise ValidationError(
                {
                    'commander_link': (
                        'Необходимо указать ссылку на публикацию о '
                        'прохождении школы командного состава'
                        ' командиром отряда'
                    )
                }
            )
        if self.commissioner_achievment and not self.commissioner_link:
            raise ValidationError(
                {
                    'commissioner_link': (
                        'Необходимо указать ссылку на публикацию о '
                        'прохождении школы командного состава'
                        ' комиссаром отряда'
                    )
                }
            )

    def save(self, *args, **kwargs):
        """Распределение мест и баллов при сохранении объекта.

        Командир выбрал “Да” + Комиссар выбрал “Да” - 1 место (2 балла)
        Командир выбрал “Да” + Комиссар выбрал “Нет” - 2 место (1 балл)
        Командир выбрал “Нет” + Комиссар выбрал “Да” - 2 место (1 балл)
        Командир выбрал “Нет” + Комиссар выбрал “Нет” - 3 место (0 баллов)
        """
        self.clean()
        if self.commander_achievment and self.commissioner_achievment:
            self.points = 2
            self.place = 1
        if (
            self.commander_achievment and not self.commissioner_achievment
        ) or (
            not self.commander_achievment and self.commissioner_achievment
        ):
            self.points = 1
            self.place = 2
        if not self.commander_achievment and not self.commissioner_achievment:
            self.points = 0
            self.place = 3
        super().save(*args, **kwargs)
