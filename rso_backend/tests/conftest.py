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
from users.models import RSOUser

USER_FIRST_NAME = 'Дмитрий'
USER_LAST_NAME = 'Воронежский'
USERNAME = 'dimka'
USER_PASSWORD = 'Ddmi36VRN'

SECOND_USER_FIRST_NAME = 'Имя2'
SECOND_USER_LAST_NAME = 'Фамилия2'
SECOND_USERNAME = 'Никнейм2'
SECOND_USER_PASSWORD = 'UScz1335erP3251AssW'

REGION_MOSCOW = 'Москва'
REGION_MOJAISK = 'Можайск'

CENTRAL_HEADQUARTER_COMMANDER_NAME = 'Командир'
CENTRAL_HEADQUARTER_COMMANDER_SURNAME = 'ЦШ'
CENTRAL_HEADQUARTER_COMMANDER_USERNAME = 'centralhqcommander'
CENTRAL_HEADQUARTER_COMMANDER_PASSWORD = 'hqpawswfoz1'

CENTRAL_HEADQUARTER_NAME = 'Центральный штаб'
DETACHMENTS_APPEARANCE_YEAR = settings.CENTRAL_HEADQUARTER_FOUNDING_DATE
RSO_FOUNDING_CONGRESS_DATE = '1990-01-01'

EDUCATIONAL_INSTITUTION_NAME = 'Образовательная организация'
EDUCATIONAL_INSTITUTION_SHORT_NAME = 'Образов. организация'
SECOND_EDUCATIONAL_INSTITUTION_NAME = 'Другая образовательная организация'
SECOND_EDUCATIONAL_INSTITUTION_SHORT_NAME = 'Др'


pytest_plugins = [
    'tests.fixtures.fixture_competition',
    'tests.fixtures.fixture_user',
    'tests.fixtures.fixture_headquarter',
]


@pytest.fixture
def client():
    """Неавторизованный клиент."""
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
def user_2():
    user = RSOUser.objects.create_user(
        first_name=SECOND_USER_FIRST_NAME,
        last_name=SECOND_USER_LAST_NAME,
        username=SECOND_USERNAME,
        password=SECOND_USER_PASSWORD
    )
    return user


@pytest.fixture
def user_3():
    user = RSOUser.objects.create_user(
        first_name='Имя3',
        last_name='Фамилия3',
        username='username3',
        password='ТретийПароль'
    )
    return user


@pytest.fixture
def user_4():
    user = RSOUser.objects.create_user(
        first_name='Имя4',
        last_name='Фамилия4',
        username='username4',
        password='ЧетвертыйПароль'
    )
    return user


@pytest.fixture
def user_5():
    user = RSOUser.objects.create_user(
        first_name='Имя5',
        last_name='Фамилия5',
        username='username5',
        password='ПятыйПароль'
    )
    return user


@pytest.fixture
def user_6():
    user = RSOUser.objects.create_user(
        first_name='Имя6',
        last_name='Фамилия6',
        username='username6',
        password='ШестойПароль'
    )
    return user


@pytest.fixture
def user_uncommander_untrusted():
    user = RSOUser.objects.create_user(
        first_name='Имя7',
        last_name='Фамилия7',
        username='username7',
        password='sEvenPassw0rd!'
    )
    return user


@pytest.fixture
def user_uncommander_untrusted_2():
    user = RSOUser.objects.create_user(
        first_name='Имя8',
        last_name='Фамилия8',
        username='username8',
        password='Passw0rd!!'
    )
    return user


@pytest.fixture
def user_commander():
    """Командир всех структурных единиц выше отряда региона 1."""
    user = RSOUser.objects.create_user(
        first_name='Командир',
        last_name='Всего',
        username='командир',
        password='ПарольКомандира'
    )
    return user


@pytest.fixture
def user_commander_2():
    """Командир всех структурных единиц выше отряда региона 2."""
    user = RSOUser.objects.create_user(
        first_name='Командир2',
        last_name='Всего2',
        username='командир2',
        password='ПарольКомандира2'
    )
    return user


@pytest.fixture
def user_commander_2b():
    """Еще один командир всех структурных единиц выше отряда региона 2.

    Используется для проверок одноуровневых доступов
    внутри однйо ветки иерархии.
    """
    user = RSOUser.objects.create_user(
        first_name='Командир2бэ',
        last_name='Всего2бэ',
        username='командир2бэ',
        password='ПарольКомандира2бэ'
    )
    return user


@pytest.fixture
def authenticated_client(client, user):
    """Авторизованный клиент сущности юзера (простой невериф. пользователь).

    Командир отряда, если вызывать вместе с detachment фикстурй.
    """
    token, _ = Token.objects.get_or_create(user=user)
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    return client


@pytest.fixture
def authenticated_client_2(client, user_2):
    """Авторизованный клиент сущности юзера (простой невериф. пользователь).

    Командир отряда, если вызывать вместе с detachment_2 фикстурй.
    """
    login_payload = {
        'username': SECOND_USERNAME,
        'password': SECOND_USER_PASSWORD,
    }
    response = client.post('/api/v1/token/login/', login_payload)
    assert response.status_code == 200
    token = response.data['auth_token']
    client.credentials(HTTP_AUTHORIZATION='Token ' + token)
    return client


@pytest.fixture
def authenticated_client_3(client, user_3):
    """Авторизованный клиент сущности юзера (простой невериф. пользователь)."""
    token, _ = Token.objects.get_or_create(user=user_3)
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    return client


@pytest.fixture
def authenticated_client_6(client, user_6):
    """Авторизованный клиент сущности юзера (простой невериф. пользователь).

    Командир отряда, если вызывать вместе с detachment_3 фикстурой.
    Создатель мероприятия отрядного уровня, если вызвать вместе
    с event_detachment.
    """
    token, _ = Token.objects.get_or_create(user=user_6)
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    return client


@pytest.fixture
def free_authenticated_client():
    """Авторизованный клиент, который нигде не командир."""
    user = RSOUser.objects.create_user(
        first_name='Свободный',
        last_name='Юзер',
        username='free',
        password='ПарольСвободный'
    )
    client = APIClient()
    token, _ = Token.objects.get_or_create(user=user)
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    return client


@pytest.fixture
def authenticated_client_7(client, user_uncommander_untrusted):
    """Авторизованный клиент сущности юзера (некомандир, недоверенный)."""
    login_payload = {
        'username': user_uncommander_untrusted.username,
        'password': 'sEvenPassw0rd!',
    }
    response = client.post('/api/v1/token/login/', login_payload)
    assert response.status_code == 200
    token = response.data['auth_token']
    client.credentials(HTTP_AUTHORIZATION='Token ' + token)
    return client


@pytest.fixture
def authenticated_client_8(client, user_uncommander_untrusted_2):
    """Авторизованный клиент сущности юзера (некомандир, недоверенный)."""
    login_payload = {
        'username': user_uncommander_untrusted_2.username,
        'password': 'Passw0rd!!',
    }
    client = APIClient()
    response = client.post('/api/v1/token/login/', login_payload)
    assert response.status_code == 200
    token = response.data['auth_token']
    client.credentials(HTTP_AUTHORIZATION='Token ' + token)
    return client


@pytest.fixture
def authenticated_client_9(client, user_uncommander_untrusted_2):
    """Авторизованный клиент сущности юзера командира ОбрШ по ветке 2."""
    login_payload = {
        'username': 'командир2бэ',
        'password': 'ПарольКомандира2бэ',
    }
    client = APIClient()
    response = client.post('/api/v1/token/login/', login_payload)
    assert response.status_code == 200
    token = response.data['auth_token']
    client.credentials(HTTP_AUTHORIZATION='Token ' + token)
    return client


@pytest.fixture
def admin_client():
    user = RSOUser.objects.create_user(username='admin',
                                       password='admin_password')
    user.is_staff = True
    user.is_superuser = True
    user.save()

    client = APIClient()
    token, _ = Token.objects.get_or_create(user=user)
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    return client


@pytest.fixture
def educational_institution(region):
    edu = EducationalInstitution.objects.create(
        name='Образовательная организация',
        short_name='Образов. организация',
        region=region
    )
    return edu


@pytest.fixture
def educational_institution_2(region_2):
    edu = EducationalInstitution.objects.create(
        name='Вторая образовательная организация',
        short_name='Вторая образов. организация',
        region=region_2
    )
    return edu


@pytest.fixture
def educational_institutions(regions):
    edu_1 = EducationalInstitution.objects.create(
        name=EDUCATIONAL_INSTITUTION_NAME,
        short_name=EDUCATIONAL_INSTITUTION_SHORT_NAME,
        region=regions[0]
    )
    edu_2 = EducationalInstitution.objects.create(
        name=SECOND_EDUCATIONAL_INSTITUTION_NAME,
        short_name=EDUCATIONAL_INSTITUTION_SHORT_NAME,
        region=regions[1]
    )
    return edu_1, edu_2


@pytest.fixture
def region():
    region = Region.objects.create(name='Регион 1')
    return region


@pytest.fixture
def region_2():
    region = Region.objects.create(name='Регион 2')
    return region


@pytest.fixture
def regions():
    region = Region.objects.create(name=REGION_MOJAISK)
    region_2 = Region.objects.create(name=REGION_MOSCOW)
    return region, region_2


@pytest.fixture
def area():
    area = Area.objects.create(name='Направление 1')
    return area


@pytest.fixture
def area_2():
    area = Area.objects.create(name='Направление 2')
    return area


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
def central_headquarter_2(user_commander_2):
    central_headquarter = CentralHeadquarter.objects.create(
        name='Второй центральный штаб',
        commander=user_commander_2,
        detachments_appearance_year=2018,
        rso_founding_congress_date=datetime.date.fromisoformat(
            "2022-12-31"
        )
    )
    return central_headquarter


@pytest.fixture
def district_headquarter(central_headquarter, user_commander):
    district_headquarter = DistrictHeadquarter.objects.create(
        name='Окружный штаб',
        commander=user_commander,
        central_headquarter=central_headquarter,
        founding_date=datetime.date.fromisoformat("2022-11-13"),
    )
    return district_headquarter


@pytest.fixture
def district_headquarter_2(central_headquarter_2, user_commander_2):
    district_headquarter = DistrictHeadquarter.objects.create(
        name='Второй окружный штаб',
        commander=user_commander_2,
        central_headquarter=central_headquarter_2,
        founding_date=datetime.date.fromisoformat("2022-10-31"),
    )
    return district_headquarter


@pytest.fixture
def regional_headquarter(district_headquarter, region, user_commander):
    regional_headquarter = RegionalHeadquarter.objects.create(
        name='Региональный штаб',
        commander=user_commander,
        region=region,
        district_headquarter=district_headquarter,
        conference_date=datetime.date.fromisoformat("2022-09-30"),
        founding_date=2022,
    )
    return regional_headquarter


@pytest.fixture
def regional_headquarter_2(district_headquarter_2, region_2, user_commander_2):
    regional_headquarter = RegionalHeadquarter.objects.create(
        name='Второй региональный штаб',
        commander=user_commander_2,
        region=region_2,
        district_headquarter=district_headquarter_2,
        conference_date=datetime.date.fromisoformat("2022-08-31"),
        founding_date=2022,
    )
    return regional_headquarter


@pytest.fixture
def local_headquarter(regional_headquarter, user_commander):
    local_headquarter = LocalHeadquarter.objects.create(
        name='Локальный штаб',
        commander=user_commander,
        regional_headquarter=regional_headquarter,
        founding_date=datetime.date.fromisoformat("2022-07-31"),
    )
    return local_headquarter


@pytest.fixture
def local_headquarter_2(regional_headquarter_2, user_commander_2):
    local_headquarter = LocalHeadquarter.objects.create(
        name='Второй локальный штаб',
        commander=user_commander_2,
        regional_headquarter=regional_headquarter_2,
        founding_date=datetime.date.fromisoformat("2022-06-30"),
    )
    return local_headquarter


@pytest.fixture
def educational_headquarter(
    local_headquarter, regional_headquarter, educational_institution,
    user_commander
):
    educational_headquarter = EducationalHeadquarter.objects.create(
        name='Образовательный штаб',
        commander=user_commander,
        local_headquarter=local_headquarter,
        regional_headquarter=regional_headquarter,
        educational_institution=educational_institution,
        founding_date=datetime.date.fromisoformat("2022-05-31"),
    )
    return educational_headquarter


@pytest.fixture
def educational_headquarter_2(
    local_headquarter_2, regional_headquarter_2, educational_institution_2,
    user_commander_2
):
    educational_headquarter = EducationalHeadquarter.objects.create(
        name='Второй образовательный штаб',
        commander=user_commander_2,
        local_headquarter=local_headquarter_2,
        regional_headquarter=regional_headquarter_2,
        educational_institution=educational_institution_2,
        founding_date=datetime.date.fromisoformat("2022-04-30"),
    )
    return educational_headquarter


@pytest.fixture
def educational_headquarter_2b(
    local_headquarter_2, regional_headquarter_2, educational_institution_2,
    user_commander_2b
):
    educational_headquarter = EducationalHeadquarter.objects.create(
        name='Второй бэ образовательный штаб',
        commander=user_commander_2b,
        local_headquarter=local_headquarter_2,
        regional_headquarter=regional_headquarter_2,
        educational_institution=educational_institution_2,
        founding_date=datetime.date.fromisoformat("2022-04-30"),
    )
    return educational_headquarter


@pytest.fixture
def detachment(
    user, regional_headquarter,
    region, educational_institution, area
):
    """Стандартный отряд региона 1"""
    detachment = Detachment.objects.create(
        name='Отряд',
        commander=user,
        regional_headquarter=regional_headquarter,
        region=region,
        educational_institution=educational_institution,
        area=area,
        banner='path/to/banner.png',
        founding_date=datetime.date.fromisoformat("2022-02-28"),
    )
    return detachment


@pytest.fixture
def detachment_2(
    user_commander_2b, regional_headquarter_2, region_2,
    educational_institution_2, area_2
):
    """Стандартный отряд региона 2"""
    detachment = Detachment.objects.create(
        name='Второй отряд',
        commander=user_commander_2b,
        regional_headquarter=regional_headquarter_2,
        region=region_2,
        educational_institution=educational_institution_2,
        area=area_2,
        founding_date=datetime.date.fromisoformat("2023-03-31"),
    )
    return detachment


@pytest.fixture
def detachment_3(
        user_6, regional_headquarter,
        region, educational_institution, area
):
    """Такой же отряд как и 1(тот же регион), но с другим командиром"""
    detachment = Detachment.objects.create(
        name='Третий отряд',
        commander=user_6,
        regional_headquarter=regional_headquarter,
        region=region,
        area=area,
        educational_institution=educational_institution,
        founding_date=datetime.date.fromisoformat("2023-01-20"),
    )
    return detachment
