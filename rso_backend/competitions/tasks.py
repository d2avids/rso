import logging

from celery import shared_task

from rso_backend.settings import COMPETITION_ID


from competitions.q_calculations import calculate_q2_place

logger = logging.getLogger('tasks')

@shared_task
def calculate_q2_place_task():
    logger.info('Начинаем считать места по 2 показателю')
    calculate_q2_place()
    logger.info(
        'Посчитали.'
    )
