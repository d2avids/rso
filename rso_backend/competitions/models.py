import re
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from competitions.utils import get_certificate_scans_path, document_path


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


# class Score(models.Model):
#     """
#     Таблица для хранения очков отрядов за верифицированные отчеты.
#     """
#     detachment = models.ForeignKey(
#         to='headquarters.Detachment',
#         on_delete=models.CASCADE,
#         related_name='competition_scores',
#         verbose_name='Отряд'
#     )
#     competition = models.ForeignKey(
#         to='Competitions',
#         on_delete=models.CASCADE,
#         related_name='competition_scores',
#         verbose_name='Конкурс'
#     )
#     participation_in_distr_and_interreg_events = ( # чем больше, тем выше место
#         models.PositiveSmallIntegerField(
#             verbose_name='Общее количество участий',
#             default=0
#         )
#     )
#     participation_in_all_russian_events = ( # чем больше, тем выше место
#         models.PositiveSmallIntegerField(
#             verbose_name='Общее количество участий',
#             default=0
#         )
#     )
#     prize_places_in_distr_and_interreg_events = ( # чем меньше, тем выше место
#         models.FloatField(
#             verbose_name='Среднее место',
#             default=100.0
#         )
#     )
#     prize_places_in_all_russian_events = ( # чем меньше, тем выше место
#         models.FloatField(
#             verbose_name='Среднее место',
#             default=100.0
#         )
#     )
#     prize_places_in_distr_and_interreg_labor_projects = ( # чем меньше, тем выше место
#         models.FloatField(
#             verbose_name='Среднее место',
#             default=100.0
#         )
#     )
#     prize_places_in_all_russian_labor_projects = ( # чем меньше, тем выше место
#         models.FloatField(
#             verbose_name='Среднее место',
#             default=100.0
#         )
#     )

#     def __str__(self):
#         return (
#             f'Оценки отряда {self.detachment.name} '
#             f'в конкурсе {self.competition.name}'
#         )

#     class Meta:
#         verbose_name_plural = 'Оценки отрядов'
#         verbose_name = 'Оценка отряда'
#         constraints = [
#             models.UniqueConstraint(
#                 fields=('detachment', 'competition'),
#                 name='unique_competition_score'
#             )
#         ]


class Links(models.Model):
    """Абстрактная модель для ссылок."""
    link = models.URLField(
        verbose_name='Ссылка',
        max_length=500
    )

    def __str__(self):
        return (f'Ссылка участия в конкурсе, id {self.id}')

    class Meta:
        abstract = True


class Report(models.Model):
    """Абстрактная модель для отчетов."""
    competition = models.ForeignKey(
        'Competitions',
        on_delete=models.CASCADE,
        related_name='%(class)s_competition_reports',
    )
    detachment = models.ForeignKey(
        'headquarters.Detachment',
        on_delete=models.CASCADE,
        related_name='%(class)s_detachment_reports',
    )

    class Meta:
        abstract = True

    def score_calculation_sum(self, events, field_name: str):
        """
        Функция вычисления очков.
        Считает сумму по всем полям total_participants.
        """
        total_participants = events.aggregate(
            sum=models.Sum(field_name)
        ).get('sum') or 0
        return total_participants

    def score_calculation_avg(self, events, field_name: str):
        """
        Функция вычисления среднего места.
        Считает среднее число мест по всем полям prize_place.
        """
        average_prize = events.aggregate(
            average=models.Avg(field_name)
        ).get('average') or 0
        return average_prize


class ParticipationBase(models.Model):
    """Абстрактная модель для участия в мероприятиях."""
    class PrizePlaces(models.IntegerChoices):
        FIRST_PLACE = 1, 'Первое место'
        SECOND_PLACE = 2, 'Второе место'
        THIRD_PLACE = 3, 'Третье место'

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
    created_at = models.DateTimeField(
        verbose_name='Дата и время создания заявки',
        auto_now_add=True
    )
    is_verified = models.BooleanField(
        verbose_name='Подтверждено',
        default=False
    )

    class Meta:
        abstract = True


class QTandemRanking(models.Model):
    detachment = models.OneToOneField(
        'headquarters.Detachment',
        on_delete=models.CASCADE,
        related_name='%(class)s_main_detachment',
        verbose_name='Отряд-наставник',
        blank=True,
        null=True,
    )
    junior_detachment = models.OneToOneField(
        'headquarters.Detachment',
        on_delete=models.CASCADE,
        related_name='%(class)s_junior_detachment',
        verbose_name='Младший отряд',
        # Не может быть пустым
        # blank=True,
        # null=True,
    )

    class Meta:
        abstract = True


class QRanking(models.Model):
    detachment = models.OneToOneField(
        'headquarters.Detachment',
        on_delete=models.CASCADE,
        related_name='%(class)s',
        verbose_name='Отряд'
    )

    class Meta:
        abstract = True


class Q7TandemRanking(QTandemRanking):
    place = models.PositiveSmallIntegerField(
        verbose_name='Итоговое место по показателю',
        default=12  # TODO: Убрать, т.к. пустым быть не может, создается при подсчете селери таской
    )


class Q7Ranking(QRanking):
    place = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(6)],
        default=6, # TODO: Убрать, т.к. пустым быть не может, создается при подсчете селери таской
        verbose_name='Итоговое место по показателю'
    )


class Q7Report(Report):
    score = (  # чем больше, тем выше место
        models.PositiveSmallIntegerField(
            verbose_name='Общее количество участий',
            default=0
        )
    )
    pass


class LinksQ7(Links):
    """
    Ссылки на участие в окружных и межрегиональных мероприятиях.

    Хранит пользовательские ссылки на социальные сети с фотоотчетом
    с наименованием мероприятия и наименованием ЛСО,
    принявшем в нем участие.
    """
    event = models.ForeignKey(
        to='Q7',
        on_delete=models.CASCADE,
        related_name='links',
        verbose_name='Участие в окружных и межрегиональных мероприятиях'
    )

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
                name='unique_event_link_distr_and_interreg_events'
            )
        ]


class Q7(ParticipationBase):
    """
    Участие членов студенческого отряда в окружных и межрегиональных
    мероприятиях. Модель для хранения каждого участия.
    """
    number_of_participants = models.PositiveIntegerField(
        verbose_name='Количество участников',
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    detachment_report = models.ForeignKey(
        'Q7Report',
        on_delete=models.CASCADE,
        related_name='participation_data',
        verbose_name='Отчет отряда',
    )

    def __str__(self):
        return (f'Участие СО в окружных '
                f'и межрегиональных  мероприятиях, id {self.id}')

    class Meta:
        verbose_name = 'Участие в окружных и межрегиональных мероприятиях'
        verbose_name = 'Участие в окружных и межрегиональных мероприятиях'
        verbose_name_plural = ('Участия в окружных и межрегиональных '
                               'мероприятиях')
        constraints = [
            models.UniqueConstraint(
                fields=('detachment_report', 'event_name'),
                name='unique_participation_in_distr_and_interreg_events'
            )
        ]


# class LinksOfParticipationInAllRussianEvents(Links):
#     """
#     Ссылки на участие во всероссийских мероприятиях.

#     Хранит пользовательские ссылки на социальные сети с фотоотчетом
#     с наименованием мероприятия и наименованием ЛСО,
#     принявшем в нем участие.
#     """
#     event = models.ForeignKey(
#         to='ParticipationInAllRussianEvents',
#         on_delete=models.CASCADE,
#         related_name='links',
#         verbose_name='Участие во всероссийских мероприятиях'
#     )

#     class Meta:
#         verbose_name_plural = (
#             'Ссылки на фотоотчет участия СО во всероссийских мероприятиях'
#         )
#         verbose_name = (
#             'Ссылка на фотоотчет участия СО во всероссийском мероприятии'
#         )
#         constraints = [
#             models.UniqueConstraint(
#                 fields=('event', 'link'),
#                 name='unique_event_link_all_russian_events'
#             )
#         ]


# class ParticipationInAllRussianEvents(Report):
#     """
#     Участие членов студенческого отряда во всероссийских
#     мероприятиях. Модель для хранения каждого участия.
#     """
#     number_of_participants = models.PositiveIntegerField(
#         verbose_name='Количество участников',
#         default=0,
#         validators=[MinValueValidator(0), MaxValueValidator(100)]
#     )

#     def __str__(self):
#         return (f'Участие СО {self.detachment.name} во всероссийских '
#                 f'мероприятиях, id {self.id}')

#     class Meta:
#         ordering = ['-competition__id']
#         verbose_name = 'Участие во всероссийских мероприятиях'
#         verbose_name_plural = 'Участия во всероссийских мероприятиях'
#         constraints = [
#             models.UniqueConstraint(
#                 fields=('competition', 'detachment', 'event_name'),
#                 name='unique_participation_in_all_russian_events'
#             )
#         ]


# class PrizePlacesInDistrAndInterregEvents(Report):
#     """
#     Призовые места в окружных и межрегиональных мероприятиях и
#     конкурсах РСО.
#     Модель для хранения каждого места.
#     """
#     prize_place = models.IntegerField(
#         choices=Report.PrizePlaces.choices,
#         verbose_name='Призовое место'
#     )

#     def __str__(self):
#         return (f'Призовое место СО {self.detachment.name} в окружных '
#                 f'и межрегиональных  мероприятиях, id {self.id}')

#     class Meta:
#         ordering = ['-competition__id']
#         verbose_name = (
#             'Призовое место в окружных и межрегиональных мероприятиях '
#             'и конкурсах РСО'
#         )
#         verbose_name_plural = (
#             'Призовые места в окружных и межрегиональных мероприятиях '
#             'и конкурсах РСО'
#         )
#         constraints = [
#             models.UniqueConstraint(
#                 fields=('competition', 'detachment', 'event_name'),
#                 name='unique_prize_places_in_distr_and_interreg_events'
#             )
#         ]


# class PrizePlacesInAllRussianEvents(Report):
#     """
#     Призовые места всероссийских мероприятиях и
#     конкурсах РСО.
#     Модель для хранения каждого места.
#     """
#     prize_place = models.IntegerField(
#         choices=Report.PrizePlaces.choices,
#         verbose_name='Призовое место'
#     )

#     def __str__(self):
#         return (f'Призовое место СО {self.detachment.name} во всероссийских '
#                 f'мероприятиях и конкурсах РСО, id {self.id}')

#     class Meta:
#         ordering = ['-competition__id']
#         verbose_name = (
#             'Призовое место во всероссийских мероприятиях и конкурсах РСО'
#         )
#         verbose_name_plural = (
#             'Призовые места во всероссийских мероприятиях и конкурсах РСО'
#         )
#         constraints = [
#             models.UniqueConstraint(
#                 fields=('competition', 'detachment', 'event_name'),
#                 name='unique_prize_places_in_all_russian_events'
#             )
#         ]


# class PrizePlacesInDistrAndInterregLaborProjects(Report):
#     """
#     Призовые места отряда на окружных и межрегиональных
#     трудовых проектах.
#     Модель для хранения каждого места.
#     """
#     prize_place = models.IntegerField(
#         choices=Report.PrizePlaces.choices,
#         verbose_name='Призовое место'
#     )

#     def __str__(self):
#         return (f'Призовое место СО {self.detachment.name} в окружных '
#                 f'и межрегиональных  трудовых проектах, id {self.id}')

#     class Meta:
#         ordering = ['-competition__id']
#         verbose_name = (
#             'Призовое место в окружных и межрегиональных '
#             'трудовых проектах'
#         )
#         verbose_name_plural = (
#             'Призовые места в окружных и межрегиональных '
#             'трудовых проектах'
#         )
#         constraints = [
#             models.UniqueConstraint(
#                 fields=('competition', 'detachment', 'event_name'),
#                 name='unique_prize_places_in_distr_and_interreg_labor_projects'
#             )
#         ]


# class PrizePlacesInAllRussianLaborProjects(Report):
#     """
#     Призовые места отряда на всероссийских
#     трудовых проектах.
#     Модель для хранения каждого места.
#     """
#     prize_place = models.IntegerField(
#         choices=Report.PrizePlaces.choices,
#         verbose_name='Призовое место'
#     )

#     def __str__(self):
#         return (f'Призовое место СО {self.detachment.name} на всероссийских'
#                 f' трудовых проектах, id {self.id}')

#     class Meta:
#         ordering = ['-competition__id']
#         verbose_name = (
#             'Призовое место на всероссийских'
#             'трудовых проектах'
#         )
#         verbose_name_plural = (
#             'Призовые места на всероссийских '
#             'трудовых проектах'
#         )
#         constraints = [
#             models.UniqueConstraint(
#                 fields=('competition', 'detachment', 'event_name'),
#                 name='unique_prize_places_in_all_russian_labor_projects'
#             )
#         ]


class QBaseReport(models.Model):
    competition = models.ForeignKey(
        'Competitions',
        on_delete=models.CASCADE,
        related_name='%(class)s_competition_reports',
    )
    detachment = models.ForeignKey(
        'headquarters.Detachment',
        on_delete=models.CASCADE,
        related_name='%(class)s_detachment_reports',
    )

    class Meta:
        abstract = True


class QBaseReportIsVerified(models.Model):
    is_verified = models.BooleanField(default=False)

    class Meta:
        abstract = True


class QBaseTandemRanking(models.Model):
    detachment = models.OneToOneField(
        'headquarters.Detachment',
        on_delete=models.CASCADE,
        related_name='%(class)s_main_detachment',
        verbose_name='Отряд-наставник',
        blank=True,
        null=True,
    )
    junior_detachment = models.OneToOneField(
        'headquarters.Detachment',
        on_delete=models.CASCADE,
        related_name='%(class)s_junior_detachment',
        verbose_name='Младший отряд',
        blank=True,
        null=True,
    )

    class Meta:
        abstract = True


class QBaseRanking(models.Model):
    detachment = models.OneToOneField(
        'headquarters.Detachment',
        on_delete=models.CASCADE,
        related_name='%(class)s',
        verbose_name='Отряд'
    )

    class Meta:
        abstract = True


class Q13TandemRanking(QBaseTandemRanking):
    place = models.PositiveSmallIntegerField(
        verbose_name='Итоговое место по показателю',
        default=12
    )

    class Meta:
        verbose_name = 'Тандем-места по 13 показателю'
        verbose_name_plural = 'Тандем-места по 13 показателю'


class Q13Ranking(QBaseRanking):
    place = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(6)],
        default=6,
        verbose_name='Итоговое место по показателю'
    )

    class Meta:
        verbose_name = 'Места по 13 показателю'
        verbose_name_plural = 'Места по 13 показателю'



class Q13DetachmentReport(QBaseReport):
    pass


class Q13EventOrganization(models.Model):
    """Пример модели с данными для заполнения (которые по кнопке "добавить...") """

    class EventType(models.TextChoices):
        SPORT = 'Спортивное', 'Спортивное'
        INTELLECTUAL = 'Интеллектуальное', 'Интеллектуальное'
        CREATIVE = 'Творческое', 'Творческое'
        VOLUNTARY = 'Волонтерское', 'Волонтерское'
        INTERNAL = 'Внутреннее', 'Внутреннее'

    event_type = models.CharField(
        max_length=16,
        choices=EventType.choices,
        default=EventType.INTERNAL,
        verbose_name='Тип мероприятия'
    )
    event_link = models.URLField(verbose_name='Ссылка на пуб.', max_length=500)
    detachment_report = models.ForeignKey(
        'Q13DetachmentReport',
        on_delete=models.CASCADE,
        related_name='organization_data',
        verbose_name='Отчет отряда',
    )
    is_verified = models.BooleanField(default=False)


class Q18TandemRanking(QBaseTandemRanking):
    place = models.PositiveSmallIntegerField(
        verbose_name='Итоговое место по показателю'
    )

    class Meta:
        verbose_name = 'Тандем-места по 18 показателю'
        verbose_name_plural = 'Тандем-места по 18 показателю'


class Q18Ranking(QBaseRanking):
    place = models.PositiveSmallIntegerField(
        verbose_name='Итоговое место по показателю'
    )

    class Meta:
        verbose_name = 'Места по 18 показателю'
        verbose_name_plural = 'Места по 18 показателю'


class Q18DetachmentReport(QBaseReport, QBaseReportIsVerified):
    """Модель с полями для заполнения."""
    participants_number = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(1000)],
        verbose_name='Количество бойцов, принявших участие во '
                     'Всероссийском дне ударного труда'
    )
    june_15_detachment_members = models.PositiveSmallIntegerField(default=1)
    score = models.FloatField(verbose_name='Очки', default=0)
