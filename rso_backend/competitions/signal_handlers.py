from django.db.models import Q, signals, Sum
from django.db.models.signals import post_save
from django.dispatch import receiver

from competitions.models import ParticipationInDistrAndInterregEvents, Score


@receiver(post_save, sender=ParticipationInDistrAndInterregEvents)
def create_score(sender, instance, created, **kwargs):
    """
    Сигнал для пересчета баллов при сохранении отчета и
    пересчета рег командиром.
    Добавлено в виде сигналов, так как при изменении отчета рег.командиром,
    если он менял поле количества участников, то баллы не пересчитывались.
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
                instance.score_calculation(events, instance)
            )
            score_table_instance.save()

        return score_table_instance


signals.post_save.connect(
    create_score,
    sender=ParticipationInDistrAndInterregEvents
)
