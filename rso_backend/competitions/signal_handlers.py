from django.db.models import signals
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from competitions.models import (
    Q7,
    Q8
)


@receiver([post_save, post_delete], sender=Q7)
def create_score_q7(sender, instance, created=False, **kwargs):
    if created:
        pass
    else:
        if instance.is_verified:
            report = instance.detachment_report
            events = Q7.objects.filter(
                        detachment_report=report,
                        is_verified=True
            ).all()
            report.score = (
                report.score_calculation_sum(
                    events, 'number_of_participants'
                )
            )
            report.save()

            return report


@receiver([post_save, post_delete], sender=Q8)
def create_score_q8(sender, instance, created=False, **kwargs):
    if created:
        pass
    else:
        if instance.is_verified:
            report = instance.detachment_report
            events = Q8.objects.filter(
                        detachment_report=report,
                        is_verified=True
            ).all()
            report.score = (
                report.score_calculation_sum(
                    events, 'number_of_participants'
                )
            )
            report.save()

            return report


# @receiver(post_save, sender=PrizePlacesInDistrAndInterregEvents)
# def create_score_q9(sender, instance, created, **kwargs):
#     """
#     Сигнал для подсчета среднего призового места при сохранении отчета и
#     пересчета при изменении рег командиром.
#     Добавлено в виде сигналов, так как при изменении верифицированного отчета
#     рег.командиром, если он менял поле количества участников,
#     то баллы не пересчитывались.
#     """
#     if created:
#         pass
#     else:
#         if instance.is_verified:
#             events = PrizePlacesInDistrAndInterregEvents.objects.filter(
#                         competition=instance.competition,
#                         detachment=instance.detachment,
#                         is_verified=True
#             )
#             score_table_instance, created = Score.objects.get_or_create(
#                 detachment=instance.detachment,
#                 competition=instance.competition
#             )
#             score_table_instance.prize_places_in_distr_and_interreg_events = (
#                 instance.score_calculation_avg(
#                     events, 'prize_place'
#                 )
#             )
#             score_table_instance.save()

#             return score_table_instance


# @receiver(post_save, sender=PrizePlacesInAllRussianEvents)
# def create_score_q10(sender, instance, created, **kwargs):
#     """
#     Сигнал для подсчета среднего призового места при сохранении отчета и
#     пересчета при изменении рег командиром.
#     """
#     if created:
#         pass
#     else:
#         if instance.is_verified:
#             events = PrizePlacesInAllRussianEvents.objects.filter(
#                         competition=instance.competition,
#                         detachment=instance.detachment,
#                         is_verified=True
#             )
#             score_table_instance, created = Score.objects.get_or_create(
#                 detachment=instance.detachment,
#                 competition=instance.competition
#             )
#             score_table_instance.prize_places_in_all_russian_events = (
#                 instance.score_calculation_avg(
#                     events, 'prize_place'
#                 )
#             )
#             score_table_instance.save()

#             return score_table_instance


# def create_score_q11(sender, instance, created, **kwargs):
#     """
#     Сигнал для подсчета среднего призового места при сохранении отчета и
#     пересчета при изменении рег командиром.
#     """
#     if created:
#         pass
#     else:
#         if instance.is_verified:
#             events = PrizePlacesInDistrAndInterregLaborProjects.objects.filter(
#                         competition=instance.competition,
#                         detachment=instance.detachment,
#                         is_verified=True
#             )
#             score_table_instance, created = Score.objects.get_or_create(
#                 detachment=instance.detachment,
#                 competition=instance.competition
#             )
#             score_table_instance.prize_places_in_distr_and_interreg_labor_projects = (
#                 instance.score_calculation_avg(
#                     events, 'prize_place'
#                 )
#             )
#             score_table_instance.save()

#             return score_table_instance


# def create_score_q12(sender, instance, created, **kwargs):
#     """
#     Сигнал для подсчета среднего призового места при сохранении отчета и
#     пересчета при изменении рег командиром.
#     """
#     if created:
#         pass
#     else:
#         if instance.is_verified:
#             events = PrizePlacesInAllRussianLaborProjects.objects.filter(
#                         competition=instance.competition,
#                         detachment=instance.detachment,
#                         is_verified=True
#             )
#             score_table_instance, created = Score.objects.get_or_create(
#                 detachment=instance.detachment,
#                 competition=instance.competition
#             )
#             score_table_instance.prize_places_in_all_russian_labor_projects = (
#                 instance.score_calculation_avg(
#                     events, 'prize_place'
#                 )
#             )
#             score_table_instance.save()

#             return score_table_instance


signals.post_save.connect(
    create_score_q7,
    sender=Q7
)
signals.post_save.connect(
    create_score_q8,
    sender=Q8
)
# signals.post_save.connect(
#     create_score_q9,
#     sender=PrizePlacesInDistrAndInterregEvents
# )
# signals.post_save.connect(
#     create_score_q10,
#     sender=PrizePlacesInAllRussianEvents
# )
# signals.post_save.connect(
#     create_score_q11,
#     sender=PrizePlacesInDistrAndInterregLaborProjects
# )
# signals.post_save.connect(
#     create_score_q12,
#     sender=PrizePlacesInAllRussianLaborProjects
# )
