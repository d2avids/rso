import logging

from celery import shared_task

from competitions.q_calculations import calculate_q18_place, calculate_q7_place

logger = logging.getLogger('tasks')


@shared_task
def calculate_q18_places_task():
    logger.info('Начинаем считать места по 18 показателю')
    calculate_q18_place()
    logger.info(
        'Посчитали.'
    )


@shared_task
def calculate_q7_places_task():
    logger.info('Начинаем считать места по 7 показателю')
    calculate_q7_place(competition_id=2)
    logger.info(
        'Посчитали!'
    )
