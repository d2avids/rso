import datetime

import pytest
from django.conf import settings
from rest_framework.test import APIClient

from headquarters.models import CentralHeadquarter, Region
from users.models import RSOUser

USER_FIRST_NAME = 'Дмитрий'
USER_LAST_NAME = 'Воронежский'
USERNAME = 'dimka'
USER_PASSWORD = 'Ddmi36VRN'

REGION_MOSCOW = 'Москва'
REGION_MOJAISK = 'Можайск'

CENTRAL_HEADQUARTER_COMMANDER_NAME = 'Командир'
CENTRAL_HEADQUARTER_COMMANDER_SURNAME = 'ЦШ'
CENTRAL_HEADQUARTER_COMMANDER_USERNAME = 'centralhqcommander'
CENTRAL_HEADQUARTER_COMMANDER_PASSWORD = 'hqpawswfoz1'

CENTRAL_HEADQUARTER_NAME = 'Центральный штаб'
DETACHMENTS_APPEARANCE_YEAR = settings.CENTRAL_HEADQUARTER_FOUNDING_DATE
RSO_FOUNDING_CONGRESS_DATE = '1990-01-01'


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user():
    user = RSOUser.objects.create_user(
        first_name=USER_FIRST_NAME,
        last_name=USER_LAST_NAME,
        username=USERNAME,
        password=USER_PASSWORD
    )
    return user


@pytest.fixture
def region():
    region = Region.objects.create(name=REGION_MOJAISK)
    region_2 = Region.objects.create(name=REGION_MOSCOW)
    return region, region_2


@pytest.fixture
def central_headquarter():
    commander = RSOUser.objects.create_user(
        first_name=CENTRAL_HEADQUARTER_COMMANDER_NAME,
        last_name=CENTRAL_HEADQUARTER_COMMANDER_SURNAME,
        username=CENTRAL_HEADQUARTER_COMMANDER_USERNAME,
        password=CENTRAL_HEADQUARTER_COMMANDER_PASSWORD,
    )
    central_headquarter = CentralHeadquarter.objects.create(
        name=CENTRAL_HEADQUARTER_NAME,
        commander=commander,
        detachments_appearance_year=DETACHMENTS_APPEARANCE_YEAR,
        rso_founding_congress_date=datetime.date.fromisoformat(
            RSO_FOUNDING_CONGRESS_DATE
        )
    )
    return central_headquarter


@pytest.fixture
def authenticated_client(client, user):
    login_payload = {
        'username': user.username,
        'password': USER_PASSWORD,
    }
    response = client.post('/api/v1/token/login/', login_payload)
    assert response.status_code == 200
    token = response.data['auth_token']
    client.credentials(HTTP_AUTHORIZATION='Token ' + token)
    return client
