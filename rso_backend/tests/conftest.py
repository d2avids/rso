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
    'tests.fixtures.fixture_event',
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
    внутри одной ветки иерархии.
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
def authenticated_client_4(client, user_4):
    """Авторизованный клиент сущности юзера (простой невериф. пользователь)."""
    token, _ = Token.objects.get_or_create(user=user_4)
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    return client


@pytest.fixture
def authenticated_client_5(client, user_5):
    """Авторизованный клиент сущности юзера (простой невериф. пользователь)."""
    token, _ = Token.objects.get_or_create(user=user_5)
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
                                 UserCentralHeadquarterPosition,
                                 UserDistrictHeadquarterPosition,)
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
    reg_hq_position_trusted = UserRegionalHeadquarterPosition.objects.create(
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
    user_with_position_in_district_hq недоверенный в окружном штабе
    district_hq_1a с должностью джедай.

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
def central_hq_positions(
    central_hq, user_with_position_in_centr_hq, position_jedi,
    user_trusted_in_centr_hq
):
    """
    user_with_position_in_centr_hq недоверенный в центральном штабе
    с должностью джедай.

    user_trusted_in_central_hq доверенный в центральном штабе c должностью
    джедай.
    """
    #TODO: запись не создается. Нужно разобраться как создать для тестов.
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
