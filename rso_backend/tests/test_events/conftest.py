import datetime

import pytest
from django.conf import settings

from events.models import Event
from headquarters.models import (CentralHeadquarter, Detachment,
                                 DistrictHeadquarter, EducationalHeadquarter,
                                 LocalHeadquarter, Position,
                                 RegionalHeadquarter, UserDetachmentPosition)
from users.models import RSOUser

PASSWORD = 'p@ssWord!123'


@pytest.fixture
def group_event_detachment(user_6, regional_headquarter):
    event = Event.objects.create(
        name='Test Event',
        format='Онлайн',
        status='Активный',
        scale='Отрядный',
        author=user_6,
        conference_link='https://example.com',
        address='address',
        participants_number=100,
        description='desc',
        available_structural_units='Отряды',
        org_regional_headquarter=regional_headquarter,

    )
    return event


@pytest.fixture
def detachment_commander_1a():
    detachment_commander_1a = RSOUser.objects.create_user(
        first_name='Командир',
        last_name='Отрядный',
        username='detachment_com_1a',
        password=PASSWORD
    )
    return detachment_commander_1a


@pytest.fixture
def authenticated_det_com_1a(detachment_commander_1a, client):
    """Аутентифицированный командир отряда."""

    login_payload = {
        'username': 'detachment_com_1a',
        'password': PASSWORD,
    }
    response = client.post('/api/v1/token/login/', login_payload)
    assert response.status_code == 200
    token = response.data['auth_token']
    client.credentials(HTTP_AUTHORIZATION='Token ' + token)
    return client


@pytest.fixture
def detachment_1a(regional_headquarter, region, area, detachment_commander_1a, educational_institution):
    """Отряд. Привязка к образовательному штабу 1а."""

    detachment_1a = Detachment.objects.create(
        name='Отряд 1a',
        commander=detachment_commander_1a,
        regional_headquarter=regional_headquarter,
        educational_institution=educational_institution,
        region=region,
        area=area,
        founding_date=datetime.date.fromisoformat("2022-10-31"),
    )
    return detachment_1a


@pytest.fixture
def user_with_position_in_detachment():
    """Пользователь принятый в отряд и назначенный на должность."""

    user_with_position_in_detachment = RSOUser.objects.create_user(
        first_name='HavePosition',
        last_name='InDetachment',
        username='positionedDETACHMENT',
        password=PASSWORD
    )
    return user_with_position_in_detachment


@pytest.fixture
def position_jedi():
    """Должность джедай"""

    position_jedi = Position.objects.create(
        name='Джедай'
    )
    return position_jedi


@pytest.fixture
def detachment_positions(
    detachment_1a, user_with_position_in_detachment, position_jedi,
):
    """
    user_with_position_in_detachment недоверенный в отряде detachment_1a
    с должностью джедай.

    user_trusted_in_detachment доверенный в отряде detachment_1a
    с должностью джедай.
    """

    det_position_regular = UserDetachmentPosition.objects.create(
        headquarter=detachment_1a,
        user=user_with_position_in_detachment,
        position=position_jedi,
        is_trusted=False
    )
    return det_position_regular


@pytest.fixture
def edu_commander_1a():
    edu_commander_1a = RSOUser.objects.create_user(
        first_name='Командир',
        last_name='Образовательный',
        username='edu_com_1a',
        password=PASSWORD
    )
    return edu_commander_1a


@pytest.fixture
def edu_hq_1a(edu_commander_1a, regional_headquarter, educational_institution):
    """Образовательный штаб. Привязка к местному штабу 1а."""

    edu_hq = EducationalHeadquarter.objects.create(
        name='Образовательный штаб 1a',
        commander=edu_commander_1a,
        regional_headquarter=regional_headquarter,
        educational_institution=educational_institution,
        founding_date=datetime.date.fromisoformat('2022-07-31'),
    )
    return edu_hq


@pytest.fixture
def authenticated_edu_commander_1a(edu_commander_1a, client):
    """Аутентифицированный командир образовательного штаба."""

    login_payload = {
        'username': 'edu_com_1a',
        'password': PASSWORD,
    }
    response = client.post('/api/v1/token/login/', login_payload)
    assert response.status_code == 200
    token = response.data['auth_token']
    client.credentials(HTTP_AUTHORIZATION='Token ' + token)
    return client


@pytest.fixture
def local_commander_1a():
    local_commander_1a = RSOUser.objects.create_user(
        first_name='Командир',
        last_name='Местный',
        username='local_com_1a',
        password=PASSWORD
    )
    return local_commander_1a


@pytest.fixture
def local_hq_1a(regional_headquarter, local_commander_1a):
    """Местный штаб. Привязка к региональному штабу 1а."""

    local_hq = LocalHeadquarter.objects.create(
        name='Местный штаб 1a',
        commander=local_commander_1a,
        regional_headquarter=regional_headquarter,
        founding_date='2022-01-01',
    )
    return local_hq


@pytest.fixture
def authenticated_local_commander_1a(local_commander_1a, client):
    """Аутентифицированный командир местного штаба."""

    login_payload = {
        'username': 'local_com_1a',
        'password': PASSWORD,
    }
    response = client.post('/api/v1/token/login/', login_payload)
    assert response.status_code == 200
    token = response.data['auth_token']
    client.credentials(HTTP_AUTHORIZATION='Token ' + token)
    return client


@pytest.fixture
def centr_commander():
    centr_commander = RSOUser.objects.create_user(
        first_name='Командир',
        last_name='Центральный',
        username='centr_com',
        password=PASSWORD
    )
    return centr_commander


@pytest.fixture
def regional_commander_1a():
    regional_commander_1a = RSOUser.objects.create_user(
        first_name='Командир',
        last_name='Региональный',
        username='regional_com_1a',
        password=PASSWORD
    )
    return regional_commander_1a


@pytest.fixture
def distr_commander_1a():
    distr_commander_1a = RSOUser.objects.create_user(
        first_name='Командир',
        last_name='Окружной',
        username='distr_com_1a',
        password=PASSWORD
    )
    return distr_commander_1a


@pytest.fixture
def central_hq(centr_commander):
    """Центральный штаб."""

    central_hq = CentralHeadquarter.objects.create(
        name='Центральный штаб',
        commander=centr_commander,
        detachments_appearance_year=(
            settings.CENTRAL_HEADQUARTER_FOUNDING_DATE
        ),
        rso_founding_congress_date=datetime.date.fromisoformat('1990-01-01')
    )
    return central_hq


@pytest.fixture
def district_hq_1a(distr_commander_1a, central_hq):
    """Окружной штаб."""

    district_hq = DistrictHeadquarter.objects.create(
        name='Окружной штаб 1a',
        commander=distr_commander_1a,
        central_headquarter=central_hq,
        founding_date=datetime.date.fromisoformat('2022-11-13'),
    )
    return district_hq


@pytest.fixture
def regional_hq_1a(district_hq_1a, regional_commander_1a, region):
    """Региональный штаб. Привязка к окружному штабу 1а."""

    regional_hq = RegionalHeadquarter.objects.create(
        name='Региональный штаб 1a',
        commander=regional_commander_1a,
        district_headquarter=district_hq_1a,
        region=region,
        conference_date=datetime.date.fromisoformat('2022-09-30'),
        founding_date='2022',
    )
    return regional_hq


@pytest.fixture
def authenticated_centr_commander(centr_commander, client):
    """Аутентифицированный командир центрального штаба."""

    login_payload = {
        'username': 'centr_com',
        'password': PASSWORD,
    }
    response = client.post('/api/v1/token/login/', login_payload)
    assert response.status_code == 200
    token = response.data['auth_token']
    client.credentials(HTTP_AUTHORIZATION='Token ' + token)
    return client


@pytest.fixture
def authenticated_distr_commander_1a(distr_commander_1a, client):
    """Аутентифицированный командир окружного штаба."""

    login_payload = {
        'username': 'distr_com_1a',
        'password': PASSWORD,
    }
    response = client.post('/api/v1/token/login/', login_payload)
    assert response.status_code == 200
    token = response.data['auth_token']
    client.credentials(HTTP_AUTHORIZATION='Token ' + token)
    return client


@pytest.fixture
def authenticated_regional_commander_1a(regional_commander_1a, client):
    """Аутентифицированный командир регионального штаба."""

    login_payload = {
        'username': 'regional_com_1a',
        'password': PASSWORD,
    }
    response = client.post('/api/v1/token/login/', login_payload)
    assert response.status_code == 200
    token = response.data['auth_token']
    client.credentials(HTTP_AUTHORIZATION='Token ' + token)
    return client
