import logging

from celery import shared_task

from competitions.q_calculations import calculate_q18_place

logger = logging.getLogger('tasks')


@shared_task
def calculate_q18_places_task():
    logger.info('Начинаем считать места по 18 показателю')
    calculate_q18_place()
    logger.info(
        'Посчитали.'
    )
