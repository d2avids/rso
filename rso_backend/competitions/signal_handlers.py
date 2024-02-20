from django.db.models import signals
from django.db.models.signals import post_save
from django.dispatch import receiver

from competitions.models import (
    ParticipationInAllRussianEvents, ParticipationInDistrAndInterregEvents,
    PrizePlacesInDistrAndInterregEvents, Score
)


@receiver(post_save, sender=ParticipationInDistrAndInterregEvents)
def create_score_q7(sender, instance, created, **kwargs):
    """
    Сигнал для подсчета баллов при верификации отчета и
    пересчета при изменении рег командиром.
    Добавлено в виде сигналов, так как при изменении верифицированного отчета
    рег.командиром, если он менял поле количества участников,
    то баллы не пересчитывались.
    """
    if created:
        pass
    else:
        if instance.is_verified:
            events = ParticipationInDistrAndInterregEvents.objects.filter(
                        competition=instance.competition,
                        detachment=instance.detachment,
                        is_verified=True
            )
            score_table_instance, created = Score.objects.get_or_create(
                detachment=instance.detachment,
                competition=instance.competition
            )
            score_table_instance.participation_in_distr_and_interreg_events = (
                instance.score_calculation_sum(
                    events, 'number_of_participants'
                )
            )
            score_table_instance.save()

            return score_table_instance


@receiver(post_save, sender=ParticipationInAllRussianEvents)
def create_score_q8(sender, instance, created, **kwargs):
    """
    Сигнал для подсчета баллов при верификации отчета и
    пересчета при изменении рег командиром.
    Добавлено в виде сигналов, так как при изменении верифицированного отчета
    рег.командиром, если он менял поле количества участников,
    то баллы не пересчитывались.
    """
    if created:
        pass
    else:
        if instance.is_verified:
            events = ParticipationInAllRussianEvents.objects.filter(
                        competition=instance.competition,
                        detachment=instance.detachment,
                        is_verified=True
            )
            score_table_instance, created = Score.objects.get_or_create(
                detachment=instance.detachment,
                competition=instance.competition
            )
            score_table_instance.participation_in_all_russian_events = (
                instance.score_calculation_sum(
                    events, 'number_of_participants'
                )
            )
            score_table_instance.save()

            return score_table_instance


@receiver(post_save, sender=PrizePlacesInDistrAndInterregEvents)
def create_score_q9(sender, instance, created, **kwargs):
    """
    Сигнал для подсчета среднего призового места при сохранении отчета и
    пересчета при изменении рег командиром.
    Добавлено в виде сигналов, так как при изменении верифицированного отчета
    рег.командиром, если он менял поле количества участников,
    то баллы не пересчитывались.
    """
    if created:
        pass
    else:
        if instance.is_verified:
            events = PrizePlacesInDistrAndInterregEvents.objects.filter(
                        competition=instance.competition,
                        detachment=instance.detachment,
                        is_verified=True
            )
            score_table_instance, created = Score.objects.get_or_create(
                detachment=instance.detachment,
                competition=instance.competition
            )
            score_table_instance.participation_in_all_russian_events = (
                instance.score_calculation_avg(
                    events, 'prize_place'
                )
            )
            score_table_instance.save()

            return score_table_instance


signals.post_save.connect(
    create_score_q7,
    sender=ParticipationInDistrAndInterregEvents
)
signals.post_save.connect(
    create_score_q8,
    sender=ParticipationInAllRussianEvents
)
signals.post_save.connect(
    create_score_q9,
    sender=PrizePlacesInDistrAndInterregEvents
)
