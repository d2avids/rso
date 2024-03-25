from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from competitions.utils import (
    get_certificate_scans_path, document_path, round_math
)


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
            )
        ]


class QBaseReport(models.Model):
    competition = models.ForeignKey(
        'Competitions',
        on_delete=models.CASCADE,
        related_name='%(class)s_competition_reports',
        verbose_name='Конкурс',
    )
    detachment = models.ForeignKey(
        'headquarters.Detachment',
        on_delete=models.CASCADE,
        related_name='%(class)s_detachment_reports',
        verbose_name='Отряд',
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=('competition', 'detachment'),
                name='unique_report_%(class)s'
            )
        ]


class QBaseReportIsVerified(models.Model):
    is_verified = models.BooleanField(default=False)

    class Meta:
        abstract = True


class QBaseTandemRanking(models.Model):
    competition = models.ForeignKey(
        'Competitions',
        on_delete=models.CASCADE,
        related_name='%(class)s',
        verbose_name='Конкурс'
    )
    detachment = models.ForeignKey(
        'headquarters.Detachment',
        on_delete=models.CASCADE,
        related_name='%(class)s_main_detachment',
        verbose_name='Отряд-наставник'
    )
    junior_detachment = models.ForeignKey(
        'headquarters.Detachment',
        on_delete=models.CASCADE,
        related_name='%(class)s_junior_detachment',
        verbose_name='Младший отряд'
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=('competition', 'detachment', 'junior_detachment'),
                name='unique_tandem_ranking_%(class)s'
            ),
            models.UniqueConstraint(
                fields=('competition', 'detachment'),
                name='unique_main_ranking_%(class)s'
            ),
            models.UniqueConstraint(
                fields=('competition', 'junior_detachment'),
                name='unique_junior_ranking_%(class)s'
            )
        ]


class QBaseRanking(models.Model):
    competition = models.ForeignKey(
        'Competitions',
        on_delete=models.CASCADE,
        related_name='%(class)s',
        verbose_name='Конкурс'
    )
    detachment = models.ForeignKey(
        'headquarters.Detachment',
        on_delete=models.CASCADE,
        related_name='%(class)s',
        verbose_name='Отряд'
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=('competition', 'detachment'),
                name='unique_ranking_%(class)s'
            )
        ]


class Links(models.Model):
    """Абстрактная модель для ссылок."""
    link = models.URLField(
        verbose_name='Ссылка',
        max_length=300
    )

    def __str__(self):
        return (f'Ссылка участия в конкурсе, id {self.id}')

    class Meta:
        abstract = True


class CalcBase:
    """
    Добавляет методы калькуляции очков для экземпляра.
    """

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
        ).get('average') or 10
        return average_prize


class ParticipationBase(models.Model):
    """Абстрактная модель для участия в мероприятиях."""
    class PrizePlaces(models.IntegerChoices):
        FIRST_PLACE = 1, 'Первое место'
        SECOND_PLACE = 2, 'Второе место'
        THIRD_PLACE = 3, 'Третье место'

    event_name = models.CharField(
        verbose_name='Название мероприятия',
        max_length=150
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


class Q1Report(QBaseReport):
    """
    Отчет по 1 показателю -'Численность членов линейного студенческого
    отряда в соответствии с объемом уплаченных членских взносов.'

    Баллы за оплаченный членский взнос:
    10 человек в отряде  – за каждого уплатившего 1 балл
    11-20 человек – за каждого уплатившего 0.75 балла
    21 и более человек – за каждого уплатившего 0.5 балла

    Создается и заполняется переодической таской 15 апреля.
    """
    score = (
        models.FloatField(
            verbose_name='Баллы за оплаченный членский взнос',
            validators=[MinValueValidator(0)],
        )
    )

    class Meta:
        verbose_name = 'Отчет по 1 показателю'
        verbose_name_plural = 'Отчеты по 1 показателю'


class Q1TandemRanking(QBaseTandemRanking):
    """
    Рейтинг для тандема-участников.
    Создается и заполняется переодической таской.
    """
    place = models.PositiveSmallIntegerField(
        verbose_name='Итоговое место по показателю 1'
    )

    class Meta:
        verbose_name = 'Тандем-место по 1 показателю'
        verbose_name_plural = 'Тандем-места по 1 показателю'


class Q1Ranking(QBaseRanking):
    """
    Рейтинг для старт-участников.
    Создается и заполняется переодической таской.
    """
    place = models.PositiveSmallIntegerField(
        verbose_name='Итоговое место по показателю 1'
    )

    class Meta:
        verbose_name = 'Место по 1 показателю'
        verbose_name_plural = 'Места по 1 показателю'


class Q2Ranking(QBaseRanking):
    place = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(3)],
        default=3,
        verbose_name='Итоговое место по показателю'
    )

    class Meta:
        verbose_name = 'Место по 2 показателю'
        verbose_name_plural = 'Места по 2 показателю'


class Q2TandemRanking(QBaseTandemRanking):
    place = models.FloatField(
        verbose_name='Итоговое место по показателю в тандеме',
        default=3.0,
    )
    class Meta:
        verbose_name = 'Тандем-место по 2 показателю'
        verbose_name_plural = 'Тандем-места по 2 показателю'


class Q2DetachmentReport(QBaseReport, QBaseReportIsVerified):
    commander_achievement = models.BooleanField(
        verbose_name=('Региональная школа командного состава'
                      ' пройдена командиром отряда'),
        default=False,
        null=False,
        blank=False
    )
    commissioner_achievement = models.BooleanField(
        verbose_name=('Региональная школа командного состава'
                      ' пройдена комиссаром отряда'),
        default=False,
        null=False,
        blank=False
    )
    commander_link = models.URLField(
        verbose_name=('Ссылка на публикацию о прохождении'
                      ' школы командного состава командиром отряда'),
        null=True,
        blank=True
    )
    commissioner_link = models.URLField(
        verbose_name=('Ссылка на публикацию о прохождении'
                      ' школы командного состава комиссаром отряда'),
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Отчет по 2 показателю'
        verbose_name_plural = 'Отчеты по 2 показателю'


class Q3Ranking(QBaseRanking):
    place = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(8)],
        default=3,
        verbose_name='Итоговое место по показателю'
    )

    class Meta:
        verbose_name = 'Место по 3 показателю'
        verbose_name_plural = 'Места по 3 показателю'


class Q3TandemRanking(QBaseTandemRanking):
    place = models.FloatField(
        verbose_name='Итоговое место по показателю в тандеме',
        default=8.0,
    )

    class Meta:
        verbose_name = 'Тандем-место по 3 показателю'
        verbose_name_plural = 'Тандем-места по 3 показателю'


class Q4Ranking(QBaseRanking):
    place = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(8)],
        default=3,
        verbose_name='Итоговое место по показателю'
    )

    class Meta:
        verbose_name = 'Место по 4 показателю'
        verbose_name_plural = 'Места по 4 показателю'


class Q4TandemRanking(QBaseTandemRanking):
    place = models.FloatField(
        verbose_name='Итоговое место по показателю в тандеме',
        default=8.0,
    )

    class Meta:
        verbose_name = 'Тандем-место по 4 показателю'
        verbose_name_plural = 'Тандем-места по 4 показателю'


class Q5TandemRanking(QBaseTandemRanking):
    place = models.FloatField(
        verbose_name='Итоговое место по показателю',
        default=20.0
    )

    class Meta:
        verbose_name = 'Тандем-места по 13 показателю'
        verbose_name_plural = 'Тандем-места по 13 показателю'


class Q5Ranking(QBaseRanking):
    place = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        default=20,
        verbose_name='Итоговое место по показателю'
    )

    class Meta:
        verbose_name = 'Места по 13 показателю'
        verbose_name_plural = 'Места по 13 показателю'


class Q5DetachmentReport(QBaseReport):
    june_15_detachment_members = models.PositiveSmallIntegerField(default=1)


class Q5EducatedParticipant(models.Model):
    detachment_report = models.ForeignKey(
        'Q5DetachmentReport', on_delete=models.CASCADE, verbose_name='Отчет'
    )
    name = models.CharField(
        max_length=200, verbose_name='ФИО участника, прошедшего '
                                     'профессиональное обучение',
    )
    document = models.FileField(
        verbose_name='Документ, подтверждающий прохождение '
                     'профессионального обучения.'
    )
    is_verified = models.BooleanField(default=False)


class Q7TandemRanking(QBaseTandemRanking):
    """
    Рейтинг для тандема-участников.
    Создается и заполняется переодической таской.
    """
    place = models.PositiveSmallIntegerField(
        verbose_name='Итоговое место по показателю 7'
    )

    class Meta:
        verbose_name = 'Тандем-место по 7 показателю'
        verbose_name_plural = 'Тандем-места по 7 показателю'


class Q7Ranking(QBaseRanking):
    """
    Рейтинг для старт-участников.
    Создается и заполняется переодической таской.
    """
    place = models.PositiveSmallIntegerField(
        verbose_name='Итоговое место по показателю 7'
    )

    class Meta:
        verbose_name = 'Место по 7 показателю'
        verbose_name_plural = 'Места по 7 показателю'


class Q7Report(CalcBase, QBaseReport):
    """
    Отчет о участии в мероприятиях.
    Поля: отряд, конкурс, очки + FK поле на мероприятия в которых участвовали.
    Очки - сумма участий sum(number_of_participants).
    Отчет имеет методы для подсчета очков (из абстрактной модели).
    """
    score = (
        models.PositiveSmallIntegerField(
            verbose_name='Общее количество участий',
            default=0  # чем больше, тем выше итоговое место в рейтинге
        )
    )

    class Meta:
        verbose_name = 'Отчет по 7 показателю'
        verbose_name_plural = 'Отчеты по 7 показателю'


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
        validators=[MinValueValidator(0), MaxValueValidator(1000)]
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
        verbose_name = 'Q7 участия'
        verbose_name_plural = ('Q7 участия')
        constraints = [
            models.UniqueConstraint(
                fields=('detachment_report', 'event_name'),
                name='unique_participation_in_distr_and_interreg_events'
            )
        ]


class Q8TandemRanking(QBaseTandemRanking):
    """
    Рейтинг для тандема-участников.
    Создается и заполняется переодической таской.
    """
    place = models.PositiveSmallIntegerField(
        verbose_name='Итоговое место по показателю 8'
    )

    class Meta:
        verbose_name = 'Тандем-место по 8 показателю'
        verbose_name_plural = 'Тандем-места по 8 показателю'


class Q8Ranking(QBaseRanking):
    """
    Рейтинг для старт-участников.
    Создается и заполняется переодической таской.
    """
    place = models.PositiveSmallIntegerField(
        verbose_name='Итоговое место по показателю 8'
    )

    class Meta:
        verbose_name = 'Место по 8 показателю'
        verbose_name_plural = 'Места по 8 показателю'


class Q8Report(CalcBase, QBaseReport):
    """
    Отчет о участии в мероприятиях.
    Поля: отряд, конкурс, очки + FK поле на мероприятия в которых участвовали.
    Очки - сумма участий sum(number_of_participants).
    Отчет имеет методы для подсчета очков (из абстрактной модели).
    """
    score = (
        models.PositiveSmallIntegerField(
            verbose_name='Общее количество участий',
            default=0  # чем больше, тем выше итоговое место в рейтинге
        )
    )

    class Meta:
        verbose_name = 'Отчет по 8 показателю'
        verbose_name_plural = 'Отчеты по 8 показателю'


class LinksQ8(Links):
    """
    Ссылки на участие во всероссийских мероприятиях.

    Хранит пользовательские ссылки на социальные сети с фотоотчетом
    с наименованием мероприятия и наименованием ЛСО,
    принявшем в нем участие.
    """
    event = models.ForeignKey(
        to='Q8',
        on_delete=models.CASCADE,
        related_name='links',
        verbose_name='Участие во всероссийских мероприятиях'
    )

    class Meta:
        verbose_name_plural = (
            'Ссылки на фотоотчет участия СО во всероссийских мероприятиях'
        )
        verbose_name = (
            'Ссылка на фотоотчет участия СО во всероссийском мероприятии'
        )
        constraints = [
            models.UniqueConstraint(
                fields=('event', 'link'),
                name='unique_event_link_all_russian_events'
            )
        ]


class Q8(ParticipationBase):
    """
    Участие членов студенческого отряда во всероссийских
    мероприятиях. Модель для хранения каждого участия.
    """
    number_of_participants = models.PositiveIntegerField(
        verbose_name='Количество участников',
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(1000)]
    )
    detachment_report = models.ForeignKey(
        'Q8Report',
        on_delete=models.CASCADE,
        related_name='participation_data',
        verbose_name='Отчет отряда',
    )

    def __str__(self):
        return (f'Участие СО во всероссийских '
                f'мероприятиях, id {self.id}')

    class Meta:
        verbose_name = 'Q8 участие'
        verbose_name_plural = 'Q8 участия'
        constraints = [
            models.UniqueConstraint(
                fields=('detachment_report', 'event_name'),
                name='unique_participation_in_all_russian_events'
            )
        ]


class Q9TandemRanking(QBaseTandemRanking):
    """
    Рейтинг для тандема-участников.
    Создается и заполняется переодической таской.
    """
    place = models.PositiveSmallIntegerField(
        verbose_name='Итоговое место по показателю 9'
    )

    class Meta:
        verbose_name = 'Тандем-место по 9 показателю'
        verbose_name_plural = 'Тандем-места по 9 показателю'


class Q9Ranking(QBaseRanking):
    """
    Рейтинг для старт-участников.
    Создается и заполняется переодической таской.
    """
    place = models.PositiveSmallIntegerField(
        verbose_name='Итоговое место по показателю 9'
    )

    class Meta:
        verbose_name = 'Место по 9 показателю'
        verbose_name_plural = 'Места по 9 показателю'


class Q9Report(CalcBase, QBaseReport):
    """
    Отчет призовых местах в окружных и межрегиональных мероприятиях.
    Поля: отряд, конкурс, очки + FK поле на мероприятия в которых участвовали.
    Очки - среднее призовых мест avg(prize_place).
    Отчет имеет методы для подсчета очков (из абстрактной модели).
    """
    score = (
        models.FloatField(
            verbose_name='Среднее призовое место',
            validators=[MinValueValidator(0), MaxValueValidator(4)],
            default=4  # чем меньше, тем выше итоговое место в рейтинге
        )
    )

    class Meta:
        verbose_name = 'Отчет по 9 показателю'
        verbose_name_plural = 'Отчеты по 9 показателям'


class Q9(ParticipationBase):
    """
    Призовые места в окружных и межрегиональных мероприятиях и
    конкурсах РСО.
    Модель для хранения каждого места.
    """
    prize_place = models.IntegerField(
        choices=ParticipationBase.PrizePlaces.choices,
        verbose_name='Призовое место'
    )
    detachment_report = models.ForeignKey(
        'Q9Report',
        on_delete=models.CASCADE,
        related_name='participation_data',
        verbose_name='Отчет отряда',
    )

    def __str__(self):
        return (f'Призовое место СО в окружных '
                f'и межрегиональных  мероприятиях, id {self.id}')

    class Meta:
        verbose_name = ('Q9 призовое место')
        verbose_name_plural = ('Q9 призовые места')
        constraints = [
            models.UniqueConstraint(
                fields=('detachment_report', 'event_name'),
                name='unique_prize_places_in_distr_and_interreg_events'
            )
        ]


class Q10TandemRanking(QBaseTandemRanking):
    """
    Рейтинг для тандема-участников.
    Создается и заполняется переодической таской.
    """
    place = models.PositiveSmallIntegerField(
        verbose_name='Итоговое место по показателю 10'
    )

    class Meta:
        verbose_name = 'Тандем-место по 10 показателю'
        verbose_name_plural = 'Тандем-места по 10 показателю'


class Q10Ranking(QBaseRanking):
    """
    Рейтинг для старт-участников.
    Создается и заполняется переодической таской.
    """
    place = models.PositiveSmallIntegerField(
        verbose_name='Итоговое место по показателю 10'
    )

    class Meta:
        verbose_name = 'Место по 10 показателю'
        verbose_name_plural = 'Места по 10 показателю'


class Q10Report(CalcBase, QBaseReport):
    """
    Отчет призовых местах во всероссийских мероприятиях и
    конкурсах РСО.
    Поля: отряд, конкурс, очки + FK поле на мероприятия в которых участвовали.
    Очки - cреднее призовых мест avg(prize_place).
    Отчет имеет методы для подсчета очков (из абстрактной модели).
    """
    score = (
        models.FloatField(
            verbose_name='Среднее призовое место',
            validators=[MinValueValidator(0), MaxValueValidator(4)],
            default=4  # чем меньше, тем выше итоговое место в рейтинге
        )
    )

    class Meta:
        verbose_name = 'Отчет по 10 показателю'
        verbose_name_plural = 'Отчеты по 10 показателям'


class Q10(ParticipationBase):
    """
    Призовые места во всероссийских мероприятиях и
    конкурсах РСО.
    Модель для хранения каждого места.
    """
    prize_place = models.IntegerField(
        choices=ParticipationBase.PrizePlaces.choices,
        verbose_name='Призовое место'
    )
    detachment_report = models.ForeignKey(
        'Q10Report',
        on_delete=models.CASCADE,
        related_name='participation_data',
        verbose_name='Отчет отряда',
    )

    def __str__(self):
        return (f'Призовое место СО во всероссийских '
                f'мероприятиях и конкурсах РСО, id {self.id}')

    class Meta:
        verbose_name = (
            'Q10 призовое место'
        )
        verbose_name_plural = (
            'Q10 призовые места'
        )
        constraints = [
            models.UniqueConstraint(
                fields=('detachment_report', 'event_name'),
                name='unique_prize_places_in_all_russian_events'
            )
        ]


class Q11TandemRanking(QBaseTandemRanking):
    """
    Рейтинг для тандема-участников.
    Создается и заполняется переодической таской.
    """
    place = models.PositiveSmallIntegerField(
        verbose_name='Итоговое место по показателю 11'
    )

    class Meta:
        verbose_name = 'Тандем-место по 11 показателю'
        verbose_name_plural = 'Тандем-места по 11 показателю'


class Q11Ranking(QBaseRanking):
    """
    Рейтинг для старт-участников.
    Создается и заполняется переодической таской.
    """
    place = models.PositiveSmallIntegerField(
        verbose_name='Итоговое место по показателю 11'
    )

    class Meta:
        verbose_name = 'Место по 11 показателю'
        verbose_name_plural = 'Места по 11 показателю'


class Q11Report(CalcBase, QBaseReport):
    """
    Отчет призовых местах отряда на окружных и межрегиональных
    трудовых проектах.
    Поля: отряд, конкурс, очки + FK поле на мероприятия в которых участвовали.
    Очки - среднее призовых мест avg(prize_place).
    Отчет имеет методы для подсчета очков (из абстрактной модели).
    """
    score = (
        models.FloatField(
            verbose_name='Среднее призовое место',
            validators=[MinValueValidator(0), MaxValueValidator(4)],
            default=4  # чем меньше, тем выше итоговое место в рейтинге
        )
    )

    class Meta:
        verbose_name = 'Отчет по 11 показателю'
        verbose_name_plural = 'Отчеты по 11 показателям'


class Q11(ParticipationBase):
    """
    Призовые места отряда на окружных и межрегиональных
    трудовых проектах.
    Модель для хранения каждого места.
    """
    prize_place = models.IntegerField(
        choices=ParticipationBase.PrizePlaces.choices,
        verbose_name='Призовое место'
    )
    detachment_report = models.ForeignKey(
        'Q11Report',
        on_delete=models.CASCADE,
        related_name='participation_data',
        verbose_name='Отчет отряда',
    )

    def __str__(self):
        return (f'Призовое место СО в окружных '
                f'и межрегиональных  трудовых проектах, id {self.id}')

    class Meta:
        verbose_name = ('Q11 призовое место')
        verbose_name_plural = ('Q11 призовые места')
        constraints = [
            models.UniqueConstraint(
                fields=('detachment_report', 'event_name'),
                name='unique_prize_places_in_distr_and_interreg_labor_projects'
            )
        ]


class Q12TandemRanking(QBaseTandemRanking):
    """
    Рейтинг для тандема-участников.
    Создается и заполняется переодической таской.
    """
    place = models.PositiveSmallIntegerField(
        verbose_name='Итоговое место по показателю 12'
    )

    class Meta:
        verbose_name = 'Тандем-место по 12 показателю'
        verbose_name_plural = 'Тандем-места по 12 показателю'


class Q12Ranking(QBaseRanking):
    """
    Рейтинг для старт-участников.
    Создается и заполняется переодической таской.
    """
    place = models.PositiveSmallIntegerField(
        verbose_name='Итоговое место по показателю 12'
    )

    class Meta:
        verbose_name = 'Место по 12 показателю'
        verbose_name_plural = 'Места по 12 показателю'


class Q12Report(CalcBase, QBaseReport):
    """
    Отчет призовых местах отряда на всероссийских
    трудовых проектах.
    Поля: отряд, конкурс, очки + FK поле на мероприятия в которых участвовали.
    Очки - cреднее призовых мест avg(prize_place).
    Отчет имеет методы для подсчета очков (из абстрактной модели).
    """
    score = (
        models.FloatField(
            verbose_name='Среднее призовое место',
            validators=[MinValueValidator(0), MaxValueValidator(4)],
            default=4  # чем меньше, тем выше итоговое место в рейтинге
        )
    )

    class Meta:
        verbose_name = 'Отчет по 12 показателю'
        verbose_name_plural = 'Отчеты по 12 показателям'


class Q12(ParticipationBase):
    """
    Призовые места отряда на всероссийских
    трудовых проектах.
    Модель для хранения каждого места.
    """
    prize_place = models.IntegerField(
        choices=ParticipationBase.PrizePlaces.choices,
        verbose_name='Призовое место'
    )
    detachment_report = models.ForeignKey(
        'Q12Report',
        on_delete=models.CASCADE,
        related_name='participation_data',
        verbose_name='Отчет отряда',
    )

    def __str__(self):
        return (f'Призовое место СО на всероссийских'
                f' трудовых проектах, id {self.id}')

    class Meta:
        verbose_name = ('Q12 призовое место')
        verbose_name_plural = ('Q12 призовые места')
        constraints = [
            models.UniqueConstraint(
                fields=('detachment_report', 'event_name'),
                name='unique_prize_places_in_all_russian_labor_projects'
            )
        ]


class Q13TandemRanking(QBaseTandemRanking):
    place = models.FloatField(
        verbose_name='Итоговое место по показателю',
        default=6.0
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
    score = models.FloatField(verbose_name='Очки', default=1000)


class Q19TandemRanking(QBaseTandemRanking):
    """
    Рейтинг для тандема-участников.
    Создается и заполняется переодической таской.
    """
    place = models.PositiveSmallIntegerField(
        verbose_name='Итоговое место по показателю 19',
        validators=[MinValueValidator(1), MaxValueValidator(2)],
    )

    class Meta:
        verbose_name = 'Тандем-место по 19 показателю'
        verbose_name_plural = 'Тандем-места по 19 показателю'


class Q19Ranking(QBaseRanking):
    """
    Рейтинг для старт-участников.
    Создается и заполняется переодической таской.
    """
    place = models.PositiveSmallIntegerField(
        verbose_name='Итоговое место по показателю 19'
    )

    class Meta:
        verbose_name = 'Место по 19 показателю'
        verbose_name_plural = 'Места по 19 показателю'


class Q19Report(QBaseReport, QBaseReportIsVerified):
    """
    Отчет по показателю 'Отсутствие нарушений техники безопасности,
    охраны труда и противопожарной безопасности.'
    Поля: отряд, конкурс, флаг верификации и имеются или нет нарушения.
    Очки - 1.
    """
    class SafetyViolationsChoices(models.TextChoices):
        NONE = 'Отсутствуют', 'Отсутствуют'
        SOME = 'Имеются', 'Имеются'
    safety_violations = models.CharField(
        max_length=16,
        choices=SafetyViolationsChoices.choices,
        default=SafetyViolationsChoices.SOME,
        verbose_name='Нарушения техники безопасности'
    )

    class Meta:
        verbose_name = 'Отчет по 19 показателю'
        verbose_name_plural = 'Отчеты по 19 показателю'


class Q20TandemRanking(QBaseTandemRanking):
    """
    Рейтинг для тандема-участников.
    Создается и заполняется переодической таской.
    """
    place = models.PositiveSmallIntegerField(
        verbose_name='Итоговое место по показателю 20'
    )

    class Meta:
        verbose_name = 'Тандем-место по 20 показателю'
        verbose_name_plural = 'Тандем-места по 20 показателю'


class Q20Ranking(QBaseRanking):
    """
    Рейтинг для старт-участников.
    Создается и заполняется переодической таской.
    """
    place = models.PositiveSmallIntegerField(
        verbose_name='Итоговое место по показателю 20'
    )

    class Meta:
        verbose_name = 'Место по 20 показателю'
        verbose_name_plural = 'Места по 20 показателю'


class Q20Report(QBaseReport, QBaseReportIsVerified):
    """
    Отчет по показателю 'Соответствие требованиями положения
    символики и атрибутике форменной одежды и символики отрядов'
    Поля: отряд, конкурс, флаг верификации и необязательные поля ссылок.
    Очки - 1.

    # TODO: Примечание ниже для понятности. Временно.
    # Очки считаются после сохранения верифицированной заявки (сигналом
    после верификации), если заявка не верифицирована - очков ноль.
    # Далее при подсчете они будут в конце рейтинга. Т.е. они будут в рейтинге,
    но на последних местах среди нулей.
    # То есть не отправить хуже, чем не верифицировать, те, кто не
    отправил будут делить самое последнее место на всех при подсчете в
    финальной таске.
    """
    link_emblem = models.URLField(
        verbose_name='Ссылка на фото эмблемы',
        max_length=300,
        blank=True,
        null=True
    )
    link_emblem_img = models.URLField(
        verbose_name='Ссылка на изображение эмблемы',
        max_length=300,
        blank=True,
        null=True
    )
    link_flag = models.URLField(
        verbose_name='Ссылка на фото флага',
        max_length=300,
        blank=True,
        null=True
    )
    link_flag_img = models.URLField(
        verbose_name='Ссылка на изображение флага',
        max_length=300,
        blank=True,
        null=True
    )
    link_banner = models.URLField(
        verbose_name='Ссылка на фото знамени',
        max_length=300,
        blank=True,
        null=True
    )
    link_banner_img = models.URLField(
        verbose_name='Ссылка на изображение знамени',
        max_length=300,
        blank=True,
        null=True
    )
    score = models.PositiveSmallIntegerField(
        verbose_name='Очки',
        default=0  # Чем больше, тем выше рейтинг
    )

    class Meta:
        verbose_name = 'Отчет по 20 показателю'
        verbose_name_plural = 'Отчеты по 20 показателю'
