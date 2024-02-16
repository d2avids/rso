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

