import pytest

from competitions.models import (
    Q19Ranking, Q19TandemRanking, Q7TandemRanking, Q7Ranking, Q8Ranking, Q8TandemRanking,
    Q9Ranking, Q9TandemRanking
)


@pytest.fixture
def q7_tandem_ranking(
    competition, detachment_competition, junior_detachment,
    report_question7_verif
):
    return Q7TandemRanking.objects.create(
        place=1,
        competition=competition,
        detachment=detachment_competition,
        junior_detachment=junior_detachment
    )


@pytest.fixture
def q7_ranking(
    competition, junior_detachment_3, report_question7_verif2
):
    """Стартовая заявка."""
    return Q7Ranking.objects.create(
        place=2,
        competition=competition,
        detachment=junior_detachment_3
    )

@pytest.fixture
def q8_tandem_ranking(
    competition, detachment_competition, junior_detachment,
    report_question8_verif
):
    return Q8TandemRanking.objects.create(
        place=1,
        competition=competition,
        detachment=detachment_competition,
        junior_detachment=junior_detachment
    )


@pytest.fixture
def q8_ranking(
    competition, junior_detachment_3, report_question8_verif2
):
    """Стартовая заявка."""
    return Q8Ranking.objects.create(
        place=2,
        competition=competition,
        detachment=junior_detachment_3
    )


@pytest.fixture
def q19_tandem_ranking(
    competition, detachment_competition, junior_detachment,
    report_question19_verif
):
    return Q19TandemRanking.objects.create(
        place=1,
        competition=competition,
        detachment=detachment_competition,
        junior_detachment=junior_detachment
    )


@pytest.fixture
def q19_ranking(
    competition, junior_detachment_3, report_question19_verif2
):
    """Стартовая заявка."""
    return Q19Ranking.objects.create(
        place=2,
        competition=competition,
        detachment=junior_detachment_3
    )
