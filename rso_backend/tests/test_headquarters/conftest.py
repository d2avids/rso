import datetime

import pytest
from django.conf import settings
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from headquarters.models import (Area, CentralHeadquarter, Detachment,
                                 DistrictHeadquarter, EducationalHeadquarter,
                                 EducationalInstitution, LocalHeadquarter,
                                 Position, Region, RegionalHeadquarter,
                                 UserDetachmentPosition)
from tests.conftest import (client, educational_institution, area, area_2,
                            educational_institution_2, region, region_2)
from users.models import RSOUser


"""
Тестовые данные представляют собой древовидную структуру.
Отряды/штабы одного уровня испульзуются в тестах с проверкой 
одноуровнего доступа к эндпоинтам.
Тестовая структура РСО:
Один центральный штаб. Один командир центрального штаба.
Далее идет разветвление.
- Окружной Штаб №1 делится на два Региональных штаба(РШ_1а и РШ_1б);
- Региональный штаб №1a делится на два Местных штаба(МШ_1а и МШ_1б);
- Местный штаб №1a делится на два Образовательных штаба(ОШ_1а и ОШ_1б);
- Образовательный штаб №1a делится на два Отряда(Отряд_1а и Отряд_1б).

В каждом штабе/отряде уникальный командир.
Кроме того созданы сущности:
- Анонимный пользователь;
- Простой неверифицированный пользователь;
- Пользователь принятый в отдряд и назначенный на должность;
- Доверенный пользователь в отряде;
- Админ.
"""

PASSWORD = 'p@ssWord!123'

@pytest.fixture
def anonymous_client():
    """Неаутентифицированный клиент, аноним."""

    return APIClient()

@pytest.fixture
def user_unverified():
    """Простой неверифицированный пользователь."""

    user_unverified = RSOUser.objects.create_user(
        first_name='unverified',
        last_name='unverified',
        username='unverified',
        password=PASSWORD
    )
    return user_unverified

@pytest.fixture
def user_with_position():
    """Пользователь принятый в отряд и назначенный на должность."""

    user_with_position = RSOUser.objects.create_user(
        first_name='HavePosition',
        last_name='HavePosition',
        username='positioned',
        password=PASSWORD
    )
    return user_with_position

@pytest.fixture
def user_trusted():
    user_trusted = RSOUser.objects.create_user(
        first_name='Юзер',
        last_name='Доверенный',
        username='trusted',
        password=PASSWORD
    )
    return user_trusted

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
def distr_commander_1a():
    distr_commander_1a = RSOUser.objects.create_user(
        first_name='Командир',
        last_name='Окружной',
        username='distr_com_1a',
        password=PASSWORD
    )
    return distr_commander_1a


@pytest.fixture
def distr_commander_1b():
    distr_commander_1b = RSOUser.objects.create_user(
        first_name='Командир',
        last_name='Окружной',
        username='distr_com_1b',
        password=PASSWORD
    )
    return distr_commander_1b


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
def regional_commander_1b():
    regional_commander_1b = RSOUser.objects.create_user(
        first_name='Командир',
        last_name='Региональный',
        username='regional_com_1b',
        password=PASSWORD
    )
    return regional_commander_1b


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
def local_commander_1b():
    local_commander_1b = RSOUser.objects.create_user(
        first_name='Командир',
        last_name='Местный',
        username='local_com_1b',
        password=PASSWORD
    )
    return local_commander_1b


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
def edu_commander_1b():
    edu_commander_1b = RSOUser.objects.create_user(
        first_name='Командир',
        last_name='Образовательный',
        username='edu_com_1b',
        password=PASSWORD
    )
    return edu_commander_1b


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
def detachment_commander_1b():
    detachment_commander_1b = RSOUser.objects.create_user(
        first_name='Командир',
        last_name='Отрядный',
        username='detachment_com_1b',
        password=PASSWORD
    )
    return detachment_commander_1b


@pytest.fixture
def authenticated_unverified(user_unverified, client):
    """Аутентифицированный неверифицированный клиент."""

    login_payload = {
        'username': 'unverified',
        'password': PASSWORD,
    }
    response = client.post('/api/v1/token/login/', login_payload)
    assert response.status_code == 200
    token = response.data['auth_token']
    client.credentials(HTTP_AUTHORIZATION='Token ' + token)
    return client


@pytest.fixture
def authenticated_user_with_position(user_with_position, client):
    """Аутентифицированный пользователь с должностью."""

    login_payload = {
        'username': 'positioned',
        'password': PASSWORD,
    }
    response = client.post('/api/v1/token/login/', login_payload)
    assert response.status_code == 200
    token = response.data['auth_token']
    client.credentials(HTTP_AUTHORIZATION='Token ' + token)
    return client

@pytest.fixture
def authenticated_trusted(user_trusted, client):
    """Аутентифицированный доверенный клиент."""

    login_payload = {
        'username': 'trusted',
        'password': PASSWORD,
    }
    response = client.post('/api/v1/token/login/', login_payload)
    assert response.status_code == 200
    token = response.data['auth_token']
    client.credentials(HTTP_AUTHORIZATION='Token ' + token)
    return client


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
def authenticated_distr_commander_1b(distr_commander_1b, client):
    """Аутентифицированный командир окружного штаба."""

    login_payload = {
        'username': 'distr_com_1b',
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


@pytest.fixture
def authenticated_regional_commander_1b(regional_commander_1b, client):
    """Аутентифицированный командир регионального штаба."""

    login_payload = {
        'username': 'regional_com_1b',
        'password': PASSWORD,
    }
    response = client.post('/api/v1/token/login/', login_payload)
    assert response.status_code == 200
    token = response.data['auth_token']
    client.credentials(HTTP_AUTHORIZATION='Token ' + token)
    return client


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
def authenticated_local_commander_1b(local_commander_1b, client):
    """Аутентифицированный командир местного штаба."""

    login_payload = {
        'username': 'local_com_1b',
        'password': PASSWORD,
    }
    response = client.post('/api/v1/token/login/', login_payload)
    assert response.status_code == 200
    token = response.data['auth_token']
    client.credentials(HTTP_AUTHORIZATION='Token ' + token)
    return client


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
def authenticated_edu_commander_1b(edu_commander_1b, client):
    """Аутентифицированный командир образовательного штаба."""

    login_payload = {
        'username': 'edu_com_1b',
        'password': PASSWORD,
    }
    response = client.post('/api/v1/token/login/', login_payload)
    assert response.status_code == 200
    token = response.data['auth_token']
    client.credentials(HTTP_AUTHORIZATION='Token ' + token)
    return client


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
def authenticated_det_com_1b(detachment_commander_1b, client):
    """Аутентифицированный командир отряда."""

    login_payload = {
        'username': 'detachment_com_1b',
        'password': PASSWORD,
    }
    response = client.post('/api/v1/token/login/', login_payload)
    assert response.status_code == 200
    token = response.data['auth_token']
    client.credentials(HTTP_AUTHORIZATION='Token ' + token)
    return client


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
def district_hq_1b(distr_commander_1b, central_hq):
    """Окружной штаб."""

    district_hq = DistrictHeadquarter.objects.create(
        name='Окружной штаб 1b',
        commander=distr_commander_1b,
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
def regional_hq_1b(district_hq_1a, regional_commander_1b, region):
    """Региональный штаб. Привязка к окружному штабу 1а."""

    regional_hq = RegionalHeadquarter.objects.create(
        name='Региональный штаб 1b',
        commander=regional_commander_1b,
        district_headquarter=district_hq_1a,
        region=region,
        conference_date=datetime.date.fromisoformat('2022-09-30'),
        founding_date='2022',
    )
    return regional_hq

@pytest.fixture
def local_hq_1a(regional_hq_1a, local_commander_1a):
    """Местный штаб. Привязка к региональному штабу 1а."""

    local_hq = LocalHeadquarter.objects.create(
        name='Местный штаб 1a',
        commander=local_commander_1a,
        regional_headquarter=regional_hq_1a,
        founding_date='2022-01-01',
    )
    return local_hq


@pytest.fixture
def local_hq_1b(regional_hq_1a, local_commander_1b):
    """Местный штаб. Привязка к региональному штабу 1а."""

    local_hq = LocalHeadquarter.objects.create(
        name='Местный штаб 1b',
        commander=local_commander_1b,
        regional_headquarter=regional_hq_1a,
        founding_date='2022-01-01',
    )
    return local_hq


@pytest.fixture
def edu_hq_1a(local_hq_1a, edu_commander_1a, regional_hq_1a, educational_institution):
    """Образовательный штаб. Привязка к местному штабу 1а."""

    edu_hq = EducationalHeadquarter.objects.create(
        name='Образовательный штаб 1a',
        commander=edu_commander_1a,
        local_headquarter=local_hq_1a,
        regional_headquarter=regional_hq_1a,
        educational_institution=educational_institution,
        founding_date=datetime.date.fromisoformat('2022-07-31'),
    )
    return edu_hq

@pytest.fixture
def edu_hq_1b(local_hq_1a, edu_commander_1b, regional_hq_1a, educational_institution_2):
    """Образовательный штаб. Привязка к местному штабу 1а."""

    edu_hq = EducationalHeadquarter.objects.create(
        name='Образовательный штаб 1b',
        commander=edu_commander_1b,
        local_headquarter=local_hq_1a,
        regional_headquarter=regional_hq_1a,
        educational_institution=educational_institution_2,
        founding_date=datetime.date.fromisoformat('2022-07-31'),
    )
    return edu_hq


@pytest.fixture
def detachment_1a(
        regional_hq_1a, edu_hq_1a, detachment_commander_1a, region, area,
        educational_institution
):
    """Отряд. Привязка к образовательному штабу 1а."""

    detachment_1a = Detachment.objects.create(
        name='Отряд 1a',
        commander=detachment_commander_1a,
        regional_headquarter=regional_hq_1a,
        region=region,
        educational_headquarter=edu_hq_1a,
        educational_institution=educational_institution,
        area=area,
        founding_date=datetime.date.fromisoformat('2022-06-30'),
    )
    return detachment_1a

@pytest.fixture
def detachment_1b(
        regional_hq_1a, edu_hq_1a, detachment_commander_1b, region, area_2,
        educational_institution
):
    """Отряд. Привязка к образовательному штабу 1а."""

    detachment_1b = Detachment.objects.create(
        name='Отряд 1b',
        commander=detachment_commander_1b,
        regional_headquarter=regional_hq_1a,
        region=region,
        educational_headquarter=edu_hq_1a,
        educational_institution=educational_institution,
        area=area_2,
        founding_date=datetime.date.fromisoformat('2022-06-30'),
    )
    return detachment_1b


@pytest.fixture
def position_jedi():
    """Должность джедай"""

    position_jedi = Position.objects.create(
        name='Джедай'
    )
    return position_jedi


@pytest.fixture
def position_dart():
    """Должность Дарт"""

    position_dart = Position.objects.create(
        name='Дарт'
    )
    return position_dart


@pytest.fixture
def detachment_positions(
    detachment_1a, user_with_position, position_jedi
):
    """user_with_position в отряде detachment_1a с должностью джедай."""

    detachment_position = UserDetachmentPosition.objects.create(
        headquarter=detachment_1a,
        user=user_with_position,
        position=position_jedi,
        is_trusted=False
    )
    return detachment_position
