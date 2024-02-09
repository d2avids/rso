import datetime

import pytest
from django.conf import settings
from rest_framework.test import APIClient
from competitions.models import CompetitionApplications, Competitions

from headquarters.models import (Area, CentralHeadquarter, Detachment, DistrictHeadquarter, EducationalHeadquarter, EducationalInstitution, LocalHeadquarter,
                                 Region, RegionalHeadquarter)
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

EDUCATIONAL_INSTITUTION_NAME = 'Образовательная организация'
EDUCATIONAL_INSTITUTION_SHORT_NAME = 'Образов. организация'
SECOND_EDUCATIONAL_INSTITUTION_NAME = 'Другая образовательная организация'
SECOND_EDUCATIONAL_INSTITUTION_SHORT_NAME = 'Др'


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
        first_name='Имя2',
        last_name='Фамилия2',
        username='username2',
        password='ВторойПароль'
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
def authenticated_client(client, user):
    """Авторизованный клиент сущности юзера (простой невериф. пользователь)."""
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def authenticated_client_2(client, user_2):
    """Авторизованный клиент сущности юзера (простой невериф. пользователь)."""
    client.force_authenticate(user=user_2)
    return client


@pytest.fixture
def authenticated_client_3(client, user_3):
    """Авторизованный клиент сущности юзера (простой невериф. пользователь)."""
    client.force_authenticate(user=user_3)
    return client


@pytest.fixture
def admin_client():
    user = RSOUser.objects.create_user(username='admin',
                                       password='admin_password')
    user.is_staff = True
    user.is_superuser = True
    user.save()

    client = APIClient()
    client.force_authenticate(user=user)
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
def central_headquarter_2(user_2):
    central_headquarter = CentralHeadquarter.objects.create(
        name='Второй центральный штаб',
        commander=user_2,
        detachments_appearance_year=2018,
        rso_founding_congress_date=datetime.date.fromisoformat(
            "2022-12-31"
        )
    )
    return central_headquarter


@pytest.fixture
def district_headquarter(central_headquarter, user):
    district_headquarter = DistrictHeadquarter.objects.create(
        name='Окружный штаб',
        commander=user,
        central_headquarter=central_headquarter,
        founding_date=datetime.date.fromisoformat("2022-11-13"),
    )
    return district_headquarter


@pytest.fixture
def district_headquarter_2(central_headquarter_2, user_2):
    district_headquarter = DistrictHeadquarter.objects.create(
        name='Второй окружный штаб',
        commander=user_2,
        central_headquarter=central_headquarter_2,
        founding_date=datetime.date.fromisoformat("2022-10-31"),
    )
    return district_headquarter


@pytest.fixture
def regional_headquarter(district_headquarter, region, user):
    regional_headquarter = RegionalHeadquarter.objects.create(
        name='Региональный штаб',
        commander=user,
        region=region,
        district_headquarter=district_headquarter,
        conference_date=datetime.date.fromisoformat("2022-09-30"),
        founding_date=2022,
    )
    return regional_headquarter


@pytest.fixture
def regional_headquarter_2(district_headquarter_2, region_2, user_2):
    regional_headquarter = RegionalHeadquarter.objects.create(
        name='Второй региональный штаб',
        commander=user_2,
        region=region_2,
        district_headquarter=district_headquarter_2,
        conference_date=datetime.date.fromisoformat("2022-08-31"),
        founding_date=2022,
    )
    return regional_headquarter


@pytest.fixture
def local_headquarter(regional_headquarter, user):
    local_headquarter = LocalHeadquarter.objects.create(
        name='Локальный штаб',
        commander=user,
        regional_headquarter=regional_headquarter,
        founding_date=datetime.date.fromisoformat("2022-07-31"),
    )
    return local_headquarter


@pytest.fixture
def local_headquarter_2(regional_headquarter_2, user_2):
    local_headquarter = LocalHeadquarter.objects.create(
        name='Второй локальный штаб',
        commander=user_2,
        regional_headquarter=regional_headquarter_2,
        founding_date=datetime.date.fromisoformat("2022-06-30"),
    )
    return local_headquarter


@pytest.fixture
def educational_headquarter(
    local_headquarter, regional_headquarter, educational_institution,
    user
):
    educational_headquarter = EducationalHeadquarter.objects.create(
        name='Образовательный штаб',
        commander=user,
        local_headquarter=local_headquarter,
        regional_headquarter=regional_headquarter,
        educational_institution=educational_institution,
        founding_date=datetime.date.fromisoformat("2022-05-31"),
    )
    return educational_headquarter


@pytest.fixture
def educational_headquarter_2(
    local_headquarter_2, regional_headquarter_2, educational_institution_2,
    user_2
):
    educational_headquarter = EducationalHeadquarter.objects.create(
        name='Второй образовательный штаб',
        commander=user_2,
        local_headquarter=local_headquarter_2,
        regional_headquarter=regional_headquarter_2,
        educational_institution=educational_institution_2,
        founding_date=datetime.date.fromisoformat("2022-04-30"),
    )
    return educational_headquarter


@pytest.fixture
def detachment(
    user, educational_headquarter, local_headquarter, regional_headquarter,
    region, educational_institution, area
):
    detachment = Detachment.objects.create(
        name='Отряд',
        commander=user,
        educational_headquarter=educational_headquarter,
        local_headquarter=local_headquarter,
        regional_headquarter=regional_headquarter,
        region=region,
        educational_institution=educational_institution,
        area=area,
        founding_date=datetime.date.fromisoformat("2022-02-28"),
    )
    return detachment


@pytest.fixture
def detachment_2(
    user_2, educational_headquarter_2, local_headquarter_2,
    regional_headquarter_2, region_2, educational_institution_2, area_2
):
    detachment = Detachment.objects.create(
        name='Второй отряд',
        commander=user_2,
        educational_headquarter=educational_headquarter_2,
        local_headquarter=local_headquarter_2,
        regional_headquarter=regional_headquarter_2,
        region=region_2,
        educational_institution=educational_institution_2,
        area=area_2,
        founding_date=datetime.date.fromisoformat("2023-03-31"),
    )
    return detachment


@pytest.fixture
def junior_detachment(user_3, regional_headquarter, region, area):
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
def application_competition(user, detachment, competition, junior_detachment):
    """Заявка на участие в конкурсе."""
    application = CompetitionApplications.objects.create(
        competition=competition,
        detachment=detachment,
        junior_detachment=junior_detachment
    )
    return application

@pytest.fixture
def application_competition_2(user_2, detachment_2, competition_2, junior_detachment_2):
    """Вторая заявка на участие в конкурсе."""
    application = CompetitionApplications.objects.create(
        competition=competition_2,
        detachment=detachment_2,
        junior_detachment=junior_detachment_2
    )
    return application
