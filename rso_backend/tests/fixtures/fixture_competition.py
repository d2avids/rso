import datetime

from competitions.models import (
    Q10, Q11, Q12, Q7, Q8, Q9, CompetitionApplications, 
    CompetitionParticipants, Competitions, LinksQ7, LinksQ8,
    Q10Report, Q11Report, Q12Report, Q19Report, Q7Report, Q8Report, Q9Report
)
import pytest
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from headquarters.models import (
    Detachment, Position, RegionalHeadquarter,
    UserRegionalHeadquarterPosition
)
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
def auth_token(user):
    token, _ = Token.objects.get_or_create(
        user=user
    )
    return token

@pytest.fixture
def user_commissar_regional_headquarter(
    position_commissar, regional_headquarter
):
    """Комиссар рег штаба. Регион 1."""
    user = RSOUser.objects.create_user(
        first_name='Коммисар',
        last_name='Рег штаба',
        username='username2RegCom',
        password='ВторойПарольRegCom'
    )
    position_commissar = UserRegionalHeadquarterPosition.objects.create(
        user=user,
        position=position_commissar,
        headquarter=regional_headquarter
    )
    return user


@pytest.fixture
def authenticated_client_commissar_regional_headquarter(
    user_commissar_regional_headquarter
):
    """Авторизованный клиент комиссара рег штаба. Регион 1."""
    client = APIClient()
    token, _ = Token.objects.get_or_create(
        user=user_commissar_regional_headquarter
    )
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    return client


@pytest.fixture
def user_commissar_regional_headquarter_2(
    position_commissar, regional_headquarter_2
):
    """Комиссар рег штаба. Регион 2."""
    user = RSOUser.objects.create_user(
        first_name='Коммисар2',
        last_name='Рег штаба2',
        username='username2RegCom2',
        password='ВторойПарольRegCom2'
    )
    position_commissar = UserRegionalHeadquarterPosition.objects.create(
        user=user,
        position=position_commissar,
        headquarter=regional_headquarter_2
    )
    return user


@pytest.fixture
def authenticated_client_commissar_regional_headquarter_2(
    user_commissar_regional_headquarter_2
):
    """Авторизованный клиент комиссара рег штаба. Регион 2."""
    client = APIClient()
    token, _ = Token.objects.get_or_create(
        user=user_commissar_regional_headquarter_2
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
def detachment_competition(
    user, regional_headquarter_competition,
    region, educational_institution, area
):
    """Отряд региона 1"""
    detachment = Detachment.objects.create(
        name='Отряд',
        commander=user,
        regional_headquarter=regional_headquarter_competition,
        region=region,
        educational_institution=educational_institution,
        area=area,
        banner='path/to/banner.png',
        founding_date=datetime.date.fromisoformat("2022-02-28"),
    )
    return detachment


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
    detachment_competition, competition, junior_detachment
):
    """Заявка на участие в конкурсе."""
    application = CompetitionApplications.objects.create(
        competition=competition,
        detachment=detachment_competition,
        junior_detachment=junior_detachment
    )
    return application


@pytest.fixture
def application_competition_tandem_confirm_junior(
    detachment_competition, competition, junior_detachment
):
    """Подтвержденная младшим отрядом заявка на участие в конкурсе."""
    application = CompetitionApplications.objects.create(
        competition=competition,
        detachment=detachment_competition,
        junior_detachment=junior_detachment
    )
    application.is_confirmed_by_junior = True
    application.save()
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


@pytest.fixture
def participants_competition_tandem(
    competition, detachment_competition, junior_detachment
):
    """Участники конкурса - тандем, регион 1."""
    return CompetitionParticipants.objects.create(
        competition=competition,
        detachment=detachment_competition,
        junior_detachment=junior_detachment
    )


@pytest.fixture
def participants_competition_start(
    competition, junior_detachment_3
):
    """Участник конкурса - старт, регион 1."""
    return CompetitionParticipants.objects.create(
        competition=competition,
        junior_detachment=junior_detachment_3
    )


@pytest.fixture
def participants_competition_start_2(
    competition, junior_detachment_2
):
    """Участники конкурса - старт, регион 2."""
    return CompetitionParticipants.objects.create(
        competition=competition,
        junior_detachment=junior_detachment_2
    )


@pytest.fixture
def position_commissar():
    """Должность комиссара."""
    return Position.objects.create(
        name='Комиссар',
    )


@pytest.fixture
def report_question7_not_verif(
    competition, participants_competition_tandem,
    junior_detachment
):
    """
    Не верифицированный отчет отряда по участию в областных и межрегиональных
    мероприятиях. Подал отчет участник отряда
    тандем-младший отряд - участник конкурса. Регион 1.
    """
    report, _ = Q7Report.objects.get_or_create(
        competition=competition,
        detachment=junior_detachment
    )
    event = Q7.objects.create(
        event_name='Мероприятие 1',
        number_of_participants=10,
        detachment_report=report,
    )
    LinksQ7.objects.create(
        link='https://example.com/q7_1',
        event=event
    )
    return event


@pytest.fixture
def report_question7_verif(
    competition, participants_competition_tandem,
    junior_detachment
):
    """
    Верифицированный отчет отряда по участию в областных и межрегиональных
    мероприятиях. Подал отчет участник отряда
    тандем-младший отряд - участник конкурса. Регион 1.
    """
    report, _ = Q7Report.objects.get_or_create(
        competition=competition,
        detachment=junior_detachment
    )
    event = Q7.objects.create(
        event_name='Мероприятие 1',
        number_of_participants=10,
        detachment_report=report,
    )
    LinksQ7.objects.create(
        link='https://example.com/q7_1',
        event=event
    )
    event.is_verified = True
    event.save()
    return event


@pytest.fixture
def report_question7_verif_second(
    competition, participants_competition_tandem,
    junior_detachment
):
    """
    Второй верифицированный отчет отряда по участию в областных
    и межрегиональных мероприятиях. Подал отчет участник отряда
    тандем-младший отряд - участник конкурса. Регион 1.
    """
    report, _ = Q7Report.objects.get_or_create(
        competition=competition,
        detachment=junior_detachment
    )
    event = Q7.objects.create(
        event_name='Мероприятие 2',
        number_of_participants=100,
        detachment_report=report,
    )
    LinksQ7.objects.create(
        link='https://example.com/q7_12',
        event=event
    )
    event.is_verified = True
    event.save()
    return event


@pytest.fixture
def report_question7_not_verif2(
    competition, participants_competition_start,
    junior_detachment_3
):
    """
    Не верифицированный отчет отряда по участию в областных и межрегиональных
    мероприятиях. Подал отчет участник отряда
    старт- участник конкурса. Регион 1.
    """
    report, _ = Q7Report.objects.get_or_create(
        competition=competition,
        detachment=junior_detachment_3
    )
    event = Q7.objects.create(
        event_name='Мероприятие 1',
        number_of_participants=100,
        detachment_report=report,
    )
    LinksQ7.objects.create(
        link='https://example.com/q7_2',
        event=event
    )
    return report


@pytest.fixture
def report_question7_verif2(
    competition, participants_competition_start,
    junior_detachment_3
):
    """
    Верифицированный отчет отряда по участию в областных и межрегиональных
    мероприятиях. Подал отчет участник отряда
    старт- участник конкурса. Регион 1
    """
    report, _ = Q7Report.objects.get_or_create(
        competition=competition,
        detachment=junior_detachment_3
    )
    event = Q7.objects.create(
        event_name='Мероприятие 1',
        number_of_participants=100,
        detachment_report=report,
    )
    LinksQ7.objects.create(
        link='https://example.com/q7_2',
        event=event
    )
    event.is_verified = True
    event.save()
    return event


@pytest.fixture
def report_question7_not_verif3(
    competition, participants_competition_start_2,
    junior_detachment_2
):
    """
    Не верифицированный отчет отряда по участию в областных и межрегиональных
    мероприятиях. Подал отчет участник отряда
    старт- участник конкурса. Регион 2.
    """
    report, _ = Q7Report.objects.get_or_create(
        competition=competition,
        detachment=junior_detachment_2
    )
    event = Q7.objects.create(
        event_name='Мероприятие 1',
        number_of_participants=20,
        detachment_report=report,
    )
    LinksQ7.objects.create(
        link='https://example.com/q7_3',
        event=event
    )
    return report


@pytest.fixture
def report_question7_verif3(
    competition, participants_competition_start_2,
    junior_detachment_2
):
    """
    Верифицированный отчет отряда по участию в областных и межрегиональных
    мероприятиях. Подал отчет участник отряда
    старт- участник конкурса. Регион 2.
    """
    report, _ = Q7Report.objects.get_or_create(
        competition=competition,
        detachment=junior_detachment_2
    )
    event = Q7.objects.create(
        event_name='Мероприятие 1',
        number_of_participants=20,
        detachment_report=report,
    )
    LinksQ7.objects.create(
        link='https://example.com/q7_3',
        event=event
    )
    event.is_verified = True
    event.save()
    return event


@pytest.fixture
def report_question8_not_verif(
    competition, participants_competition_tandem,
    junior_detachment
):
    """
    Не верифицированный отчет отряда по участию во всероссийских
    мероприятиях. Подал отчет участник отряда
    тандем-младший отряд - участник конкурса. Регион 1.
    """
    report, _ = Q8Report.objects.get_or_create(
        competition=competition,
        detachment=junior_detachment
    )
    event = Q8.objects.create(
        event_name='Мероприятие 1',
        number_of_participants=10,
        detachment_report=report,
    )
    LinksQ8.objects.create(
        link='https://example.com/q7_1',
        event=event
    )
    return event


@pytest.fixture
def report_question8_verif(
    competition, participants_competition_tandem,
    junior_detachment
):
    """
    Верифицированный отчет отряда по участию во всероссийских
    мероприятиях. Подал отчет участник отряда
    тандем-младший отряд - участник конкурса. Регион 1.
    """
    report, _ = Q8Report.objects.get_or_create(
        competition=competition,
        detachment=junior_detachment
    )
    event = Q8.objects.create(
        event_name='Мероприятие 1',
        number_of_participants=10,
        detachment_report=report,
    )
    LinksQ8.objects.create(
        link='https://example.com/q7_1',
        event=event
    )
    event.is_verified = True
    event.save()
    return event


@pytest.fixture
def report_question8_verif_second(
    competition, participants_competition_tandem,
    junior_detachment
):
    """
    Второй верифицированный отчет отряда по участию во
    всероссийских мероприятиях. Подал отчет участник отряда
    тандем-младший отряд - участник конкурса. Регион 1.
    """
    report, _ = Q8Report.objects.get_or_create(
        competition=competition,
        detachment=junior_detachment
    )
    event = Q8.objects.create(
        event_name='Мероприятие 2',
        number_of_participants=100,
        detachment_report=report,
    )
    LinksQ8.objects.create(
        link='https://example.com/q7_12',
        event=event
    )
    event.is_verified = True
    event.save()
    return event


@pytest.fixture
def report_question8_not_verif2(
    competition, participants_competition_start,
    junior_detachment_3
):
    """
    Не верифицированный отчет отряда по участию во всероссийских
    мероприятиях. Подал отчет участник отряда
    старт- участник конкурса. Регион 1.
    """
    report, _ = Q8Report.objects.get_or_create(
        competition=competition,
        detachment=junior_detachment_3
    )
    event = Q8.objects.create(
        event_name='Мероприятие 1',
        number_of_participants=100,
        detachment_report=report,
    )
    LinksQ8.objects.create(
        link='https://example.com/q7_2',
        event=event
    )
    return report


@pytest.fixture
def report_question8_verif2(
    competition, participants_competition_start,
    junior_detachment_3
):
    """
    Верифицированный отчет отряда по участию вво всероссийских
    мероприятиях. Подал отчет участник отряда
    старт- участник конкурса. Регион 1
    """
    report, _ = Q8Report.objects.get_or_create(
        competition=competition,
        detachment=junior_detachment_3
    )
    event = Q8.objects.create(
        event_name='Мероприятие 1',
        number_of_participants=100,
        detachment_report=report,
    )
    LinksQ8.objects.create(
        link='https://example.com/q7_2',
        event=event
    )
    event.is_verified = True
    event.save()
    return event


@pytest.fixture
def report_question8_not_verif3(
    competition, participants_competition_start_2,
    junior_detachment_2
):
    """
    Не верифицированный отчет отряда по участию во всероссийских
    мероприятиях. Подал отчет участник отряда
    старт- участник конкурса. Регион 2.
    """
    report, _ = Q8Report.objects.get_or_create(
        competition=competition,
        detachment=junior_detachment_2
    )
    event = Q8.objects.create(
        event_name='Мероприятие 1',
        number_of_participants=20,
        detachment_report=report,
    )
    LinksQ8.objects.create(
        link='https://example.com/q7_3',
        event=event
    )
    return report


@pytest.fixture
def report_question8_verif3(
    competition, participants_competition_start_2,
    junior_detachment_2
):
    """
    Верифицированный отчет отряда по участию во всероссийских
    мероприятиях. Подал отчет участник отряда
    старт- участник конкурса. Регион 2.
    """
    report, _ = Q8Report.objects.get_or_create(
        competition=competition,
        detachment=junior_detachment_2
    )
    event = Q8.objects.create(
        event_name='Мероприятие 1',
        number_of_participants=20,
        detachment_report=report,
    )
    LinksQ8.objects.create(
        link='https://example.com/q7_3',
        event=event
    )
    event.is_verified = True
    event.save()
    return event


@pytest.fixture
def report_question9_not_verif(
    competition, participants_competition_tandem,
    junior_detachment
):
    """
    Не верифицированный отчет отряда по занятому призовому месту в
    областных и межрегиональных мероприятиях.
    Подал отчет участник отряда
    тандем-младший отряд - участник конкурса. Регион 1.
    """
    report, _ = Q9Report.objects.get_or_create(
        competition=competition,
        detachment=junior_detachment
    )
    event = Q9.objects.create(
        event_name='Мероприятие 1',
        prize_place=2,
        detachment_report=report
    )
    return event


@pytest.fixture
def report_question9_verif(
    competition, participants_competition_tandem,
    junior_detachment
):
    """
    Верифицированный отчет отряда по занятому призовому месту в
    областных и межрегиональных мероприятиях.
    Подал отчет участник отряда
    тандем-младший отряд - участник конкурса. Регион 1.
    """
    report, _ = Q9Report.objects.get_or_create(
        competition=competition,
        detachment=junior_detachment
    )
    event = Q9.objects.create(
        event_name='Мероприятие 1',
        prize_place=2,
        detachment_report=report
    )
    event.is_verified = True
    event.save()
    return event


@pytest.fixture
def report_question9_verif_second(
    competition, participants_competition_tandem,
    junior_detachment
):
    """
    Второй верифицированный отчет отряда по занятому призовому месту в
    областных и межрегиональных мероприятиях.
    Подал отчет участник отряда
    тандем-младший отряд - участник конкурса. Регион 1.
    """
    report, _ = Q9Report.objects.get_or_create(
        competition=competition,
        detachment=junior_detachment
    )
    event = Q9.objects.create(
        event_name='Мероприятие 2',
        prize_place=1,
        detachment_report=report
    )
    event.is_verified = True
    event.save()
    return event


@pytest.fixture
def report_question9_not_verif2(
    competition, participants_competition_start,
    junior_detachment_3
):
    """
    Не верифицированный отчет отряда по занятому призовому месту в
    областных и межрегиональных мероприятиях.
    Подал отчет участник отряда
    старт- участник конкурса. Регион 1.
    """
    report, _ = Q9Report.objects.get_or_create(
        competition=competition,
        detachment=junior_detachment_3
    )
    event = Q9.objects.create(
        event_name='Мероприятие 3',
        prize_place=1,
        detachment_report=report
    )
    return event


@pytest.fixture
def report_question9_verif2(
    competition, participants_competition_start,
    junior_detachment_3
):
    """
    Верифицированный отчет отряда по занятому призовому месту в
    областных и межрегиональных мероприятиях.
    Подал отчет участник отряда
    старт- участник конкурса. Регион 1
    """
    report, _ = Q9Report.objects.get_or_create(
        competition=competition,
        detachment=junior_detachment_3
    )
    event = Q9.objects.create(
        event_name='Мероприятие 3',
        prize_place=1,
        detachment_report=report
    )
    event.is_verified = True
    event.save()
    return event


@pytest.fixture
def report_question9_not_verif3(
    competition, participants_competition_start_2,
    junior_detachment_2
):
    """
    Не верифицированный отчет отряда по занятому призовому месту в
    областных и межрегиональных мероприятиях.
    Подал отчет участник отряда
    старт- участник конкурса. Регион 2.
    """
    report, _ = Q9Report.objects.get_or_create(
        competition=competition,
        detachment=junior_detachment_2
    )
    event = Q9.objects.create(
        event_name='Мероприятие 6',
        prize_place=3,
        detachment_report=report
    )
    return event


@pytest.fixture
def report_question9_verif3(
    competition, participants_competition_start_2,
    junior_detachment_2
):
    """
    Верифицированный отчет отряда по занятому призовому месту в
    областных и межрегиональных мероприятиях.
    Подал отчет участник отряда
    старт- участник конкурса. Регион 2.
    """
    report, _ = Q9Report.objects.get_or_create(
        competition=competition,
        detachment=junior_detachment_2
    )
    event = Q9.objects.create(
        event_name='Мероприятие 6',
        prize_place=3,
        detachment_report=report
    )
    event.is_verified = True
    event.save()
    return event


@pytest.fixture
def report_question10_not_verif(
    competition, participants_competition_tandem,
    junior_detachment
):
    """
    Не верифицированный отчет отряда по занятому призовому месту в
    областных и межрегиональных мероприятиях.
    Подал отчет участник отряда
    тандем-младший отряд - участник конкурса. Регион 1.
    """
    report, _ = Q10Report.objects.get_or_create(
        competition=competition,
        detachment=junior_detachment
    )
    event = Q10.objects.create(
        event_name='Мероприятие 1',
        prize_place=2,
        detachment_report=report
    )
    return event


@pytest.fixture
def report_question10_verif(
    competition, participants_competition_tandem,
    junior_detachment
):
    """
    Верифицированный отчет отряда по занятому призовому месту в
    областных и межрегиональных мероприятиях.
    Подал отчет участник отряда
    тандем-младший отряд - участник конкурса. Регион 1.
    """
    report, _ = Q10Report.objects.get_or_create(
        competition=competition,
        detachment=junior_detachment
    )
    event = Q10.objects.create(
        event_name='Мероприятие 1',
        prize_place=2,
        detachment_report=report
    )
    event.is_verified = True
    event.save()
    return event


@pytest.fixture
def report_question10_verif_second(
    competition, participants_competition_tandem,
    junior_detachment
):
    """
    Второй верифицированный отчет отряда по занятому призовому месту в
    областных и межрегиональных мероприятиях.
    Подал отчет участник отряда
    тандем-младший отряд - участник конкурса. Регион 1.
    """
    report, _ = Q10Report.objects.get_or_create(
        competition=competition,
        detachment=junior_detachment
    )
    event = Q10.objects.create(
        event_name='Мероприятие 2',
        prize_place=1,
        detachment_report=report
    )
    event.is_verified = True
    event.save()
    return event


@pytest.fixture
def report_question10_not_verif2(
    competition, participants_competition_start,
    junior_detachment_3
):
    """
    Не верифицированный отчет отряда по занятому призовому месту в
    областных и межрегиональных мероприятиях.
    Подал отчет участник отряда
    старт- участник конкурса. Регион 1.
    """
    report, _ = Q10Report.objects.get_or_create(
        competition=competition,
        detachment=junior_detachment_3
    )
    event = Q10.objects.create(
        event_name='Мероприятие 3',
        prize_place=1,
        detachment_report=report
    )
    return event


@pytest.fixture
def report_question10_verif2(
    competition, participants_competition_start,
    junior_detachment_3
):
    """
    Верифицированный отчет отряда по занятому призовому месту в
    областных и межрегиональных мероприятиях.
    Подал отчет участник отряда
    старт- участник конкурса. Регион 1
    """
    report, _ = Q10Report.objects.get_or_create(
        competition=competition,
        detachment=junior_detachment_3
    )
    event = Q10.objects.create(
        event_name='Мероприятие 3',
        prize_place=1,
        detachment_report=report
    )
    event.is_verified = True
    event.save()
    return event


@pytest.fixture
def report_question10_not_verif3(
    competition, participants_competition_start_2,
    junior_detachment_2
):
    """
    Не верифицированный отчет отряда по занятому призовому месту в
    областных и межрегиональных мероприятиях.
    Подал отчет участник отряда
    старт- участник конкурса. Регион 2.
    """
    report, _ = Q10Report.objects.get_or_create(
        competition=competition,
        detachment=junior_detachment_2
    )
    event = Q10.objects.create(
        event_name='Мероприятие 6',
        prize_place=3,
        detachment_report=report
    )
    return event


@pytest.fixture
def report_question10_verif3(
    competition, participants_competition_start_2,
    junior_detachment_2
):
    """
    Верифицированный отчет отряда по занятому призовому месту в
    областных и межрегиональных мероприятиях.
    Подал отчет участник отряда
    старт- участник конкурса. Регион 2.
    """
    report, _ = Q10Report.objects.get_or_create(
        competition=competition,
        detachment=junior_detachment_2
    )
    event = Q10.objects.create(
        event_name='Мероприятие 6',
        prize_place=3,
        detachment_report=report
    )
    event.is_verified = True
    event.save()
    return event


@pytest.fixture
def report_question11_not_verif(
    competition, participants_competition_tandem,
    junior_detachment
):
    """
    Не верифицированный отчет отряда по занятому призовому месту в
    областных и межрегиональных мероприятиях.
    Подал отчет участник отряда
    тандем-младший отряд - участник конкурса. Регион 1.
    """
    report, _ = Q11Report.objects.get_or_create(
        competition=competition,
        detachment=junior_detachment
    )
    event = Q11.objects.create(
        event_name='Мероприятие 1',
        prize_place=2,
        detachment_report=report
    )
    return event


@pytest.fixture
def report_question11_verif(
    competition, participants_competition_tandem,
    junior_detachment
):
    """
    Верифицированный отчет отряда по занятому призовому месту в
    областных и межрегиональных мероприятиях.
    Подал отчет участник отряда
    тандем-младший отряд - участник конкурса. Регион 1.
    """
    report, _ = Q11Report.objects.get_or_create(
        competition=competition,
        detachment=junior_detachment
    )
    event = Q11.objects.create(
        event_name='Мероприятие 1',
        prize_place=2,
        detachment_report=report
    )
    event.is_verified = True
    event.save()
    return event


@pytest.fixture
def report_question11_verif_second(
    competition, participants_competition_tandem,
    junior_detachment
):
    """
    Второй верифицированный отчет отряда по занятому призовому месту в
    областных и межрегиональных мероприятиях.
    Подал отчет участник отряда
    тандем-младший отряд - участник конкурса. Регион 1.
    """
    report, _ = Q11Report.objects.get_or_create(
        competition=competition,
        detachment=junior_detachment
    )
    event = Q11.objects.create(
        event_name='Мероприятие 2',
        prize_place=1,
        detachment_report=report
    )
    event.is_verified = True
    event.save()
    return event


@pytest.fixture
def report_question11_not_verif2(
    competition, participants_competition_start,
    junior_detachment_3
):
    """
    Не верифицированный отчет отряда по занятому призовому месту в
    областных и межрегиональных мероприятиях.
    Подал отчет участник отряда
    старт- участник конкурса. Регион 1.
    """
    report, _ = Q11Report.objects.get_or_create(
        competition=competition,
        detachment=junior_detachment_3
    )
    event = Q11.objects.create(
        event_name='Мероприятие 3',
        prize_place=1,
        detachment_report=report
    )
    return event


@pytest.fixture
def report_question11_verif2(
    competition, participants_competition_start,
    junior_detachment_3
):
    """
    Верифицированный отчет отряда по занятому призовому месту в
    областных и межрегиональных мероприятиях.
    Подал отчет участник отряда
    старт- участник конкурса. Регион 1
    """
    report, _ = Q11Report.objects.get_or_create(
        competition=competition,
        detachment=junior_detachment_3
    )
    event = Q11.objects.create(
        event_name='Мероприятие 3',
        prize_place=1,
        detachment_report=report
    )
    event.is_verified = True
    event.save()
    return event


@pytest.fixture
def report_question11_not_verif3(
    competition, participants_competition_start_2,
    junior_detachment_2
):
    """
    Не верифицированный отчет отряда по занятому призовому месту в
    областных и межрегиональных мероприятиях.
    Подал отчет участник отряда
    старт- участник конкурса. Регион 2.
    """
    report, _ = Q11Report.objects.get_or_create(
        competition=competition,
        detachment=junior_detachment_2
    )
    event = Q11.objects.create(
        event_name='Мероприятие 6',
        prize_place=3,
        detachment_report=report
    )
    return event


@pytest.fixture
def report_question11_verif3(
    competition, participants_competition_start_2,
    junior_detachment_2
):
    """
    Верифицированный отчет отряда по занятому призовому месту в
    областных и межрегиональных мероприятиях.
    Подал отчет участник отряда
    старт- участник конкурса. Регион 2.
    """
    report, _ = Q11Report.objects.get_or_create(
        competition=competition,
        detachment=junior_detachment_2
    )
    event = Q11.objects.create(
        event_name='Мероприятие 6',
        prize_place=3,
        detachment_report=report
    )
    event.is_verified = True
    event.save()
    return event


@pytest.fixture
def report_question12_not_verif(
    competition, participants_competition_tandem,
    junior_detachment
):
    """
    Не верифицированный отчет отряда по занятому призовому месту в
    областных и межрегиональных мероприятиях.
    Подал отчет участник отряда
    тандем-младший отряд - участник конкурса. Регион 1.
    """
    report, _ = Q12Report.objects.get_or_create(
        competition=competition,
        detachment=junior_detachment
    )
    event = Q12.objects.create(
        event_name='Мероприятие 1',
        prize_place=2,
        detachment_report=report
    )
    return event


@pytest.fixture
def report_question12_verif(
    competition, participants_competition_tandem,
    junior_detachment
):
    """
    Верифицированный отчет отряда по занятому призовому месту в
    областных и межрегиональных мероприятиях.
    Подал отчет участник отряда
    тандем-младший отряд - участник конкурса. Регион 1.
    """
    report, _ = Q12Report.objects.get_or_create(
        competition=competition,
        detachment=junior_detachment
    )
    event = Q12.objects.create(
        event_name='Мероприятие 1',
        prize_place=2,
        detachment_report=report
    )
    event.is_verified = True
    event.save()
    return event


@pytest.fixture
def report_question12_verif_second(
    competition, participants_competition_tandem,
    junior_detachment
):
    """
    Второй верифицированный отчет отряда по занятому призовому месту в
    областных и межрегиональных мероприятиях.
    Подал отчет участник отряда
    тандем-младший отряд - участник конкурса. Регион 1.
    """
    report, _ = Q12Report.objects.get_or_create(
        competition=competition,
        detachment=junior_detachment
    )
    event = Q12.objects.create(
        event_name='Мероприятие 2',
        prize_place=1,
        detachment_report=report
    )
    event.is_verified = True
    event.save()
    return event


@pytest.fixture
def report_question12_not_verif2(
    competition, participants_competition_start,
    junior_detachment_3
):
    """
    Не верифицированный отчет отряда по занятому призовому месту в
    областных и межрегиональных мероприятиях.
    Подал отчет участник отряда
    старт- участник конкурса. Регион 1.
    """
    report, _ = Q12Report.objects.get_or_create(
        competition=competition,
        detachment=junior_detachment_3
    )
    event = Q12.objects.create(
        event_name='Мероприятие 3',
        prize_place=1,
        detachment_report=report
    )
    return event


@pytest.fixture
def report_question12_verif2(
    competition, participants_competition_start,
    junior_detachment_3
):
    """
    Верифицированный отчет отряда по занятому призовому месту в
    областных и межрегиональных мероприятиях.
    Подал отчет участник отряда
    старт- участник конкурса. Регион 1
    """
    report, _ = Q12Report.objects.get_or_create(
        competition=competition,
        detachment=junior_detachment_3
    )
    event = Q12.objects.create(
        event_name='Мероприятие 3',
        prize_place=1,
        detachment_report=report
    )
    event.is_verified = True
    event.save()
    return event


@pytest.fixture
def report_question12_not_verif3(
    competition, participants_competition_start_2,
    junior_detachment_2
):
    """
    Не верифицированный отчет отряда по занятому призовому месту в
    областных и межрегиональных мероприятиях.
    Подал отчет участник отряда
    старт- участник конкурса. Регион 2.
    """
    report, _ = Q12Report.objects.get_or_create(
        competition=competition,
        detachment=junior_detachment_2
    )
    event = Q12.objects.create(
        event_name='Мероприятие 6',
        prize_place=3,
        detachment_report=report
    )
    return event


@pytest.fixture
def report_question12_verif3(
    competition, participants_competition_start_2,
    junior_detachment_2
):
    """
    Верифицированный отчет отряда по занятому призовому месту в
    областных и межрегиональных мероприятиях.
    Подал отчет участник отряда
    старт- участник конкурса. Регион 2.
    """
    report, _ = Q12Report.objects.get_or_create(
        competition=competition,
        detachment=junior_detachment_2
    )
    event = Q12.objects.create(
        event_name='Мероприятие 6',
        prize_place=3,
        detachment_report=report
    )
    event.is_verified = True
    event.save()
    return event


@pytest.fixture
def report_question19_verif(
    competition, participants_competition_tandem,
    junior_detachment
):
    """
    Верифицированный отчет отряда по 'Отсутствие нарушений
    техники безопасности, охраны труда и противопожарной
    безопасности'
    Подал отчет участник отряда
    тандем-младший отряд - участник конкурса. Регион 1.
    """
    report, _ = Q19Report.objects.get_or_create(
        competition=competition,
        detachment=junior_detachment,
        safety_violations=Q19Report.SafetyViolationsChoices.NONE.value
    )
    report.is_verified = True
    report.save()
    return report


@pytest.fixture
def report_question19_verif2(
    competition, participants_competition_start,
    junior_detachment_3
):
    """
    Верифицированный отчет отряда по 'Отсутствие нарушений
    техники безопасности, охраны труда и противопожарной
    безопасности'
    Подал отчет участник отряда
    старт- участник конкурса. Регион 1
    """
    report, _ = Q19Report.objects.get_or_create(
        competition=competition,
        detachment=junior_detachment_3,
        safety_violations=Q19Report.SafetyViolationsChoices.NONE.value
    )
    report.is_verified = True
    report.save()
    return report
