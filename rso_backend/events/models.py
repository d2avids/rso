from django.db import models
from events.constants import FORMAT_CHOICES


class Event(models.Model):
    format = models.CharField(
        max_length=7,
        choices=FORMAT_CHOICES,
    )

    class EventDirection(models.TextChoices):
        voluntary = 'voluntary', 'Добровольческое'
        educational = 'educational', 'Образовательное'
        patriotic = 'patriotic', 'Патриотическое'
        sport = 'sport', 'Спортивное'
        creative = 'creative', 'Творческое'

    direction = models.CharField(
        max_length=20,
        choices=EventDirection.choices
    )
