import datetime

import pytest
from competitions.models import CompetitionApplications, Competitions
from rest_framework.authtoken.models import Token
from headquarters.models import Detachment, RegionalHeadquarter
from users.models import RSOUser


@pytest.fixture
def user_commander_regional_headquarter():
    user = RSOUser.objects.create_user(
        first_name='Командир',
        last_name='Рег штаба',
        username='username2Reg',
        password='ВторойПарольReg'
    )
    return user


@pytest.fixture
def authenticated_client_commander_regional_headquarter(
    client, user_commander_regional_headquarter
):
    """Авторизованный клиент командира рег штаба."""
    token, _ = Token.objects.get_or_create(
        user=user_commander_regional_headquarter
    )
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    return client


@pytest.fixture
def regional_headquarter_competition(
    district_headquarter, region, user_commander_regional_headquarter
):
    regional_headquarter = RegionalHeadquarter.objects.create(
        name='Второй региональный штаб',
        commander=user_commander_regional_headquarter,
        region=region,
        district_headquarter=district_headquarter,
        conference_date=datetime.date.fromisoformat("2022-08-31"),
        founding_date=2022,
    )
    return regional_headquarter


@pytest.fixture
def junior_detachment(user_3, regional_headquarter, region, area):
    """Стандартный младший отряд региона 1"""
    junior_detachment = Detachment.objects.create(
        name='Младший отряд',
        commander=user_3,
        regional_headquarter=regional_headquarter,
        region=region,
        founding_date=datetime.date.fromisoformat("2024-01-31"),
        banner='path/to/banner.jpg',
        area=area
    )
    return junior_detachment


@pytest.fixture
def junior_detachment_2(user_4, regional_headquarter_2, region_2, area_2):
    """Стандартный младший отряд региона 2"""
    junior_detachment = Detachment.objects.create(
        name='Второй младший отряд',
        commander=user_4,
        regional_headquarter=regional_headquarter_2,
        region=region_2,
        founding_date=datetime.date.fromisoformat("2024-01-28"),
        banner='path/to/banner2.jpg',
        area=area_2
    )
    return junior_detachment


@pytest.fixture
def junior_detachment_3(user_5, regional_headquarter, region, area):
    """Такой же младший отряд как и 1(тот же регион), но с другим командиром"""
    junior_detachment = Detachment.objects.create(
        name='Третий младший отряд',
        commander=user_5,
        regional_headquarter=regional_headquarter,
        region=region,
        founding_date=datetime.date.fromisoformat("2024-01-30"),
        banner='path/to/banner3.jpg',
        area=area
    )
    return junior_detachment


@pytest.fixture
def competition():
    return Competitions.objects.create(
        name='Конкурс',
    )


@pytest.fixture
def competition_2():
    return Competitions.objects.create(
        name='Второй конкурс',
    )


@pytest.fixture
def application_competition_tandem(
    detachment, competition, junior_detachment
):
    """Заявка на участие в конкурсе."""
    application = CompetitionApplications.objects.create(
        competition=competition,
        detachment=detachment,
        junior_detachment=junior_detachment
    )
    return application


@pytest.fixture
def application_competition_start(competition, junior_detachment):
    """Старт заявка на участие в конкурсе."""
    application = CompetitionApplications.objects.create(
        competition=competition,
        junior_detachment=junior_detachment
    )
    return application


@pytest.fixture
def application_competition_start_2(
    competition, junior_detachment_3
):
    """Вторая старт заявка на участие в конкурсе."""
    application = CompetitionApplications.objects.create(
        competition=competition,
        junior_detachment=junior_detachment_3
    )
    return application
