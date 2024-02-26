from django.db import models


class StatusIndicator(models.TextChoices):
    """Статус обработки теста."""

    NOT_COUNTED = 'not_counted', 'Показатель не засчитан'
    IN_PROCESSING = 'in_processing', 'Показатель в обработке'
    PROCESSED = 'processed', 'Показатель засчитан',
