import logging

from celery import shared_task
from users.models import RSOUser

logger = logging.getLogger('tasks')


@shared_task
def reset_membership_fee():
    RSOUser.objects.update(membership_fee=False)
    logger.info(
        'Успешно сброшен статус оплаты для всех пользователей.'
    )


@shared_task
def debug_periodic_task():
    """Периодическая таска. Выполняется каждые 1,5 мин при DEBUG=True.

    Лог выполнения сохраняется в logs/tasks_logs.log
    """
    print('debug_periodic_task')
    logger.debug(
        'Выполнена тестовая периодическая задача для проверки корректной '
        'работы Celery воркера и Celery Beat локально и на сервере.'
    )
