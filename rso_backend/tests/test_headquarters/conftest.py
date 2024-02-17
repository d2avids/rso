import datetime

import pytest
from django.conf import settings
from rest_framework.test import APIClient

from headquarters.models import (CentralHeadquarter, Detachment, Position,
                                 DistrictHeadquarter, EducationalHeadquarter,
                                 LocalHeadquarter, UserDetachmentPosition,
                                 UserEducationalHeadquarterPosition,
                                 RegionalHeadquarter,
                                 UserLocalHeadquarterPosition,
                                 UserRegionalHeadquarterPosition,
                                 UserCentralHeadquarterPosition)
from tests.conftest import (client, educational_institution, area, area_2,
                            educational_institution_2, region)
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
def user_with_position_in_edu_hq():
    """Пользователь принятый в образовательный штаб.

     Будет назначен на должность.
    """

    user_with_position_in_edu_hq = RSOUser.objects.create_user(
        first_name='HavePosition',
        last_name='InEduHq',
        username='positionedEDUHQ',
        password=PASSWORD
    )
    return user_with_position_in_edu_hq


@pytest.fixture
def user_with_position_in_local_hq():
    """Пользователь принятый в местный штаб.

     Будет назначен на должность.
    """

    user_with_position_in_local_hq = RSOUser.objects.create_user(
        first_name='HavePosition',
        last_name='InLocalHq',
        username='positionedLOCALHQ',
        password=PASSWORD
    )
    return user_with_position_in_local_hq


@pytest.fixture
def user_with_position_in_regional_hq():
    """Пользователь принятый в региональный штаб.

     Будет назначен на должность.
    """

    user_with_position_in_regional_hq = RSOUser.objects.create_user(
        first_name='HavePosition',
        last_name='InRegionalHq',
        username='positionedREGIONALHQ',
        password=PASSWORD
    )
    return user_with_position_in_regional_hq


@pytest.fixture
def user_with_position_in_district_hq():
    """Пользователь принятый в окружный штаб.

     Будет назначен на должность.
    """

    user_with_position_in_district_hq = RSOUser.objects.create_user(
        first_name='HavePosition',
        last_name='InDistrictHq',
        username='positionedDISTRICTHQ',
        password=PASSWORD
    )
    return user_with_position_in_district_hq


@pytest.fixture
def user_with_position_in_centr_hq():
    """Пользователь принятый в центральный штаб.

     Будет назначен на должность.
    """

    user_with_position_in_centr_hq = RSOUser.objects.create_user(
        first_name='HavePosition',
        last_name='InCentrHq',
        username='positionedCENTRHQ',
        password=PASSWORD
    )
    return user_with_position_in_centr_hq


@pytest.fixture
def user_trusted_in_detachment():
    user_trusted_in_detachment = RSOUser.objects.create_user(
        first_name='Юзер',
        last_name='Доверенный',
        username='trusted',
        password=PASSWORD
    )
    return user_trusted_in_detachment


@pytest.fixture
def user_trusted_in_edu_hq():
    user_trusted_in_edu_hq = RSOUser.objects.create_user(
        first_name='Юзер',
        last_name='Доверенный',
        username='trustedEDUHQ',
        password=PASSWORD
    )
    return user_trusted_in_edu_hq


@pytest.fixture
def user_trusted_in_local_hq():
    user_trusted_in_local_hq = RSOUser.objects.create_user(
        first_name='Юзер',
        last_name='Доверенный',
        username='trustedLOCALHQ',
        password=PASSWORD
    )
    return user_trusted_in_local_hq


@pytest.fixture
def user_trusted_in_regional_hq():
    user_trusted_in_regional_hq = RSOUser.objects.create_user(
        first_name='Юзер',
        last_name='Доверенный',
        username='trustedREGIONALHQ',
        password=PASSWORD
    )
    return user_trusted_in_regional_hq


@pytest.fixture
def user_trusted_in_district_hq():
    user_trusted_in_district_hq = RSOUser.objects.create_user(
        first_name='Юзер',
        last_name='Доверенный',
        username='trustedDISTRICTHQ',
        password=PASSWORD
    )
    return user_trusted_in_district_hq


@pytest.fixture
def user_trusted_in_centr_hq():
    user_trusted_in_centr_hq = RSOUser.objects.create_user(
        first_name='Юзер',
        last_name='Доверенный',
        username='trustedCENTRHQ',
        password=PASSWORD
    )
    return user_trusted_in_centr_hq


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
def authenticated_user_with_position_in_detachment(
    user_with_position_in_detachment, client
):
    """Аутентифицированный пользователь с должностью в отряде."""

    login_payload = {
        'username': 'positionedDETACHMENT',
        'password': PASSWORD,
    }
    response = client.post('/api/v1/token/login/', login_payload)
    assert response.status_code == 200
    token = response.data['auth_token']
    client.credentials(HTTP_AUTHORIZATION='Token ' + token)
    return client


@pytest.fixture
def authenticated_user_with_position_in_edu_hq(
    user_with_position_in_edu_hq, client
):
    """Аутентифицированный пользователь с должностью в обр. штабе."""

    login_payload = {
        'username': 'positionedEDUHQ',
        'password': PASSWORD,
    }
    response = client.post('/api/v1/token/login/', login_payload)
    assert response.status_code == 200
    token = response.data['auth_token']
    client.credentials(HTTP_AUTHORIZATION='Token ' + token)
    return client


@pytest.fixture
def authenticated_user_with_position_in_local_hq(
    user_with_position_in_local_hq, client
):
    """Аутентифицированный пользователь с должностью в мест. штабе."""

    login_payload = {
        'username': 'positionedLOCALHQ',
        'password': PASSWORD,
    }
    response = client.post('/api/v1/token/login/', login_payload)
    assert response.status_code == 200
    token = response.data['auth_token']
    client.credentials(HTTP_AUTHORIZATION='Token ' + token)
    return client


@pytest.fixture
def authenticated_user_with_position_in_regional_hq(
    user_with_position_in_regional_hq, client
):
    """Аутентифицированный пользователь с должностью в рег. штабе."""

    login_payload = {
        'username': 'positionedREGIONALHQ',
        'password': PASSWORD,
    }
    response = client.post('/api/v1/token/login/', login_payload)
    assert response.status_code == 200
    token = response.data['auth_token']
    client.credentials(HTTP_AUTHORIZATION='Token ' + token)
    return client


@pytest.fixture
def authenticated_user_with_position_in_distr_hq(
    user_with_position_in_district_hq, client
):
    """Аутентифицированный пользователь с должностью в дист. штабе."""

    login_payload = {
        'username': 'positionedDISTRICTHQ',
        'password': PASSWORD,
    }
    response = client.post('/api/v1/token/login/', login_payload)
    assert response.status_code == 200
    token = response.data['auth_token']
    client.credentials(HTTP_AUTHORIZATION='Token ' + token)
    return client

@pytest.fixture
def authenticated_user_with_position_in_centr_hq(
    user_with_position_in_centr_hq, client
):
    """Аутентифицированный пользователь с должностью в центр. штабе."""

    login_payload = {
        'username': 'positionedCENTRHQ',
        'password': PASSWORD,
    }
    response = client.post('/api/v1/token/login/', login_payload)
    assert response.status_code == 200
    token = response.data['auth_token']
    client.credentials(HTTP_AUTHORIZATION='Token ' + token)
    return client


@pytest.fixture
def authenticated_trusted_in_detachment(user_trusted_in_detachment, client):
    """Аутентифицированный доверенный юзер отряда."""

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
def authenticated_trusted_in_edu_hq(user_trusted_in_edu_hq, client):
    """Аутентифицированный доверенный юзер обр. штаба ."""

    login_payload = {
        'username': 'trustedEDUHQ',
        'password': PASSWORD,
    }
    response = client.post('/api/v1/token/login/', login_payload)
    assert response.status_code == 200
    token = response.data['auth_token']
    client.credentials(HTTP_AUTHORIZATION='Token ' + token)
    return client


@pytest.fixture
def authenticated_trusted_in_local_hq(user_trusted_in_local_hq, client):
    """Аутентифицированный доверенный юзер мест. штаба."""

    login_payload = {
        'username': 'trustedLOCALHQ',
        'password': PASSWORD,
    }
    response = client.post('/api/v1/token/login/', login_payload)
    assert response.status_code == 200
    token = response.data['auth_token']
    client.credentials(HTTP_AUTHORIZATION='Token ' + token)
    return client


@pytest.fixture
def authenticated_trusted_in_regional_hq(user_trusted_in_regional_hq, client):
    """Аутентифицированный доверенный юзер рег. штаба."""

    login_payload = {
        'username': 'trustedREGIONALHQ',
        'password': PASSWORD,
    }
    response = client.post('/api/v1/token/login/', login_payload)
    assert response.status_code == 200
    token = response.data['auth_token']
    client.credentials(HTTP_AUTHORIZATION='Token ' + token)
    return client

@pytest.fixture
def authenticated_trusted_in_district_hq(user_trusted_in_district_hq, client):
    """Аутентифицированный доверенный юзер дист. штаба."""

    login_payload = {
        'username': 'trustedDISTRICTHQ',
        'password': PASSWORD,
    }
    response = client.post('/api/v1/token/login/', login_payload)
    assert response.status_code == 200
    token = response.data['auth_token']
    client.credentials(HTTP_AUTHORIZATION='Token ' + token)
    return client

@pytest.fixture
def authenticated_trusted_in_centr_hq(user_trusted_in_centr_hq, client):
    """Аутентифицированный доверенный юзер центр. штаба."""

    login_payload = {
        'username': 'trustedCENTRHQ',
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
def positions_for_detachments():
    """Альтернативные должности."""

    position_dart = Position.objects.create(
        name='Дарт'
    )
    position_master = Position.objects.create(
        name='Магистр'
    )
    return position_dart, position_master


@pytest.fixture
def detachment_positions(
    detachment_1a, user_with_position_in_detachment, position_jedi,
    user_trusted_in_detachment
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
    det_position_trusted = UserDetachmentPosition.objects.create(
        headquarter=detachment_1a,
        user=user_trusted_in_detachment,
        position=position_jedi,
        is_trusted=True
    )
    return det_position_regular, det_position_trusted

@pytest.fixture
def edu_hq_positions(
    edu_hq_1a, user_with_position_in_edu_hq, position_jedi,
    user_trusted_in_edu_hq
):
    """
    user_with_position_in_edu_hq недоверенный в образовательном штабе edu_hq_1a
    с должностью джедай.

    user_trusted_in_edu_hq доверенный в образовательном штабе edu_hq_1a
    с должностью джедай.
    """

    edu_hq_position_regular = UserEducationalHeadquarterPosition.objects.create(
        headquarter=edu_hq_1a,
        user=user_with_position_in_edu_hq,
        position=position_jedi,
        is_trusted=False
    )
    edu_hq_position_trusted = UserEducationalHeadquarterPosition.objects.create(
        headquarter=edu_hq_1a,
        user=user_trusted_in_edu_hq,
        position=position_jedi,
        is_trusted=True
    )
    return edu_hq_position_regular, edu_hq_position_trusted

@pytest.fixture
def local_hq_positions(
    local_hq_1a, user_with_position_in_local_hq, position_jedi,
    user_trusted_in_local_hq
):
    """
    user_with_position_in_local_hq недоверенный в местном штабе local_hq_1a
    с должностью джедай.

    user_trusted_in_local_hq доверенный в местном штабе local_hq_1a
    с должностью джедай.
    """

    local_hq_position_regular = UserLocalHeadquarterPosition.objects.create(
        headquarter=local_hq_1a,
        user=user_with_position_in_local_hq,
        position=position_jedi,
        is_trusted=False
    )
    local_hq_position_trusted = UserLocalHeadquarterPosition.objects.create(
        headquarter=local_hq_1a,
        user=user_trusted_in_local_hq,
        position=position_jedi,
        is_trusted=True
    )
    return local_hq_position_regular, local_hq_position_trusted


@pytest.fixture
def regional_hq_positions(
    regional_hq_1a, user_with_position_in_regional_hq, position_jedi,
    user_trusted_in_regional_hq
):
    """
    user_with_position_in_regional_hq недоверенный в рег. штабе regional_hq_1a
    с должностью джедай.

    user_trusted_in_regional_hq доверенный в  рег. штабе regional_hq_1a
    с должностью джедай.
    """

    reg_hq_position_regular = UserRegionalHeadquarterPosition.objects.create(
        headquarter=regional_hq_1a,
        user=user_with_position_in_regional_hq,
        position=position_jedi,
        is_trusted=False
    )
    reg_hq_position_trusted = UserLocalHeadquarterPosition.objects.create(
        headquarter=regional_hq_1a,
        user=user_trusted_in_regional_hq,
        position=position_jedi,
        is_trusted=True
    )
    return reg_hq_position_regular, reg_hq_position_trusted

@pytest.fixture
def district_hq_positions(
    district_hq_1a, user_with_position_in_district_hq, position_jedi,
    user_trusted_in_district_hq
):
    """
    user_with_position_in_district_hq недоверенный в окружном штабе district_hq_1a
    с должностью джедай.

    user_trusted_in_district_hq доверенный в окружном штабе district_hq_1a
    с должностью джедай.
    """

    distr_hq_position_regular = UserDistrictHeadquarterPosition.objects.create(
        headquarter=district_hq_1a,
        user=user_with_position_in_district_hq,
        position=position_jedi,
        is_trusted=False
    )
    distr_hq_position_trusted = UserDistrictHeadquarterPosition.objects.create(
        headquarter=district_hq_1a,
        user=user_trusted_in_district_hq,
        position=position_jedi,
        is_trusted=True
    )
    return distr_hq_position_regular, distr_hq_position_trusted

@pytest.fixture
def central_hq_position(
    central_hq, user_with_position_in_centr_hq, position_jedi,
    user_trusted_in_centr_hq
):
    """
    user_with_position_in_centr_hq недоверенный в центральном штабе
    с должностью джедай.

    user_trusted_in_central_hq доверенный в центральном штабе c должностью
    джедай.
    """

    central_hq_position_regular = UserCentralHeadquarterPosition.objects.create(
        headquarter=central_hq,
        user=user_with_position_in_centr_hq,
        position=position_jedi,
        is_trusted=False
    )
    central_hq_position_trusted = UserCentralHeadquarterPosition.objects.create(
        headquarter=central_hq,
        user=user_trusted_in_centr_hq,
        position=position_jedi,
        is_trusted=True
    )

    return central_hq_position_regular, central_hq_position_trusted
