import logging

from celery import shared_task
from django.conf import settings
from rso_backend.settings import COMPETITION_ID
from competitions.models import (
    Q10Ranking, Q10Report, Q10TandemRanking, Q11Ranking,
    Q11Report, Q11TandemRanking, Q12Ranking, Q12Report,
    Q12TandemRanking, Q1Ranking, Q1Report, Q1TandemRanking, Q20Ranking,
    Q20Report, Q20TandemRanking, Q7Ranking, Q7Report, Q7TandemRanking,
    Q8Ranking, Q8Report, Q8TandemRanking, Q9Ranking, Q9Report,
    Q9TandemRanking
)

from competitions.q_calculations import (
    calculate_q18_place,
    calculate_place,
    calculate_q1_score
)

logger = logging.getLogger('tasks')


@shared_task
def calculate_q18_places_task():
    logger.info('Начинаем считать места по 18 показателю')
    calculate_q18_place(competition_id=settings.COMPETITION_ID)
    logger.info(
        'Посчитали.'
    )


@shared_task
def calculate_q7_places_task():
    """Считает места по 7 показателю."""
    logger.info('Начинаем считать места по 7 показателю')
    calculate_place(competition_id=COMPETITION_ID,
                    model_report=Q7Report,
                    model_ranking=Q7Ranking,
                    model_tandem_ranking=Q7TandemRanking)


@shared_task
def calculate_q8_places_task():
    """Считает места по 8 показателю."""
    calculate_place(competition_id=COMPETITION_ID,
                    model_report=Q8Report,
                    model_ranking=Q8Ranking,
                    model_tandem_ranking=Q8TandemRanking)


@shared_task
def calculate_q9_places_task():
    """Считает места по 9 показателю."""
    calculate_place(competition_id=COMPETITION_ID,
                    model_report=Q9Report,
                    model_ranking=Q9Ranking,
                    model_tandem_ranking=Q9TandemRanking,
                    reverse=False)


@shared_task
def calculate_q10_places_task():
    """Считает места по 10 показателю."""
    calculate_place(competition_id=COMPETITION_ID,
                    model_report=Q10Report,
                    model_ranking=Q10Ranking,
                    model_tandem_ranking=Q10TandemRanking,
                    reverse=False)


@shared_task
def calculate_q11_places_task():
    """Считает места по 11 показателю."""
    calculate_place(competition_id=COMPETITION_ID,
                    model_report=Q11Report,
                    model_ranking=Q11Ranking,
                    model_tandem_ranking=Q11TandemRanking,
                    reverse=False)


@shared_task
def calculate_q12_places_task():
    """Считает места по 12 показателю."""
    calculate_place(competition_id=COMPETITION_ID,
                    model_report=Q12Report,
                    model_ranking=Q12Ranking,
                    model_tandem_ranking=Q12TandemRanking,
                    reverse=False)


@shared_task
def calculate_q1_score_task():
    """Считает очки по 1 показателю."""
    calculate_q1_score(competition_id=COMPETITION_ID)


@shared_task
def calculate_q1_places_task():
    """Считает места по 1 показателю."""
    calculate_place(competition_id=COMPETITION_ID,
                    model_report=Q1Report,
                    model_ranking=Q1Ranking,
                    model_tandem_ranking=Q1TandemRanking)


@shared_task
def calculate_q20_places_task():
    """Считает места по 20 показателю."""
    calculate_place(competition_id=COMPETITION_ID,
                    model_report=Q20Report,
                    model_ranking=Q20Ranking,
                    model_tandem_ranking=Q20TandemRanking)
