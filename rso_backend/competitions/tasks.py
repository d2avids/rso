import logging

from celery import shared_task
from competitions.models import Q10Ranking, Q10Report, Q10TandemRanking, Q11Ranking, Q11Report, Q11TandemRanking, Q12Ranking, Q12Report, Q12TandemRanking, Q7Ranking, Q7Report, Q7TandemRanking, Q8Ranking, Q8Report, Q8TandemRanking, Q9Ranking, Q9Report, Q9TandemRanking

from competitions.q_calculations import calculate_q18_place, calculate_place

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
    calculate_place(competition_id=2,
                    model_report=Q7Report,
                    model_ranking=Q7Ranking,
                    model_tandem_ranking=Q7TandemRanking)


@shared_task
def calculate_q8_places_task():
    calculate_place(competition_id=2,
                    model_report=Q8Report,
                    model_ranking=Q8Ranking,
                    model_tandem_ranking=Q8TandemRanking)


@shared_task
def calculate_q9_places_task():
    calculate_place(competition_id=2,
                    model_report=Q9Report,
                    model_ranking=Q9Ranking,
                    model_tandem_ranking=Q9TandemRanking,
                    reverse=False)


@shared_task
def calculate_q10_places_task():
    calculate_place(competition_id=2,
                    model_report=Q10Report,
                    model_ranking=Q10Ranking,
                    model_tandem_ranking=Q10TandemRanking,
                    reverse=False)


@shared_task
def calculate_q11_places_task():
    calculate_place(competition_id=2,
                    model_report=Q11Report,
                    model_ranking=Q11Ranking,
                    model_tandem_ranking=Q11TandemRanking,
                    reverse=False)


@shared_task
def calculate_q12_places_task():
    calculate_place(competition_id=2,
                    model_report=Q12Report,
                    model_ranking=Q12Ranking,
                    model_tandem_ranking=Q12TandemRanking,
                    reverse=False)
