import pytest
from events.models import (Event, EventAdditionalIssue, EventApplications,
                           EventIssueAnswer, EventOrganizationData,
                           EventParticipants)
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
from users.models import RSOUser


@pytest.fixture
def user_event_organizer():
    """Пользователь из модели организаторов эвентов."""
    user = RSOUser.objects.create_user(
        first_name='Организатор',
        last_name='Эвентов',
        username='usernameOrg',
        password='ПарольОрганизатора',
    )
    return user


@pytest.fixture
def authenticated_client_event_organizer(user_event_organizer):
    """
    Аутентифицированный клиент для организатора мероприятий.
    Не забудь при использовании еще создать фикстуру
    организатора event_organizer.
    """
    client = APIClient()
    token, _ = Token.objects.get_or_create(user=user_event_organizer)
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    return client


@pytest.fixture
def authenticated_verifed_client_5(client, user_5):
    """Верифицированный аутентифицированный клиент."""
    user_5.is_verified = True
    user_5.save()
    token, _ = Token.objects.get_or_create(user=user_5)
    client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
    return client


@pytest.fixture
def event_individual(user_event_organizer, regional_headquarter):
    """Индивидуальное мероприятие."""
    event = Event.objects.create(
        name='Test Event',
        author=user_event_organizer,
        conference_link='https://example.com',
        address='address',
        participants_number=100,
        description='desc',
        org_regional_headquarter=regional_headquarter,
        application_type='Персональная',
    )
    return event


@pytest.fixture
def issue_individual(event_individual):
    """Вопрос по мероприятию."""
    return EventAdditionalIssue.objects.create(
        event=event_individual,
        issue='Вопрос по мероприятию',
    )


@pytest.fixture
def issue_individual2(event_individual):
    """Второй вопрос по мероприятию."""
    return EventAdditionalIssue.objects.create(
        event=event_individual,
        issue='Второй вопрос по мероприятию',
    )


@pytest.fixture
def issues_individual(event_individual, issue_individual, issue_individual2):
    """
    Вопросы по мероприятию.
    Создает фикстуры и возвращает два вопроса.
    """
    return EventAdditionalIssue.objects.filter(
        event=event_individual
    )


@pytest.fixture
def answer_individual(event_individual, user_5, issue_individual):
    """Ответ на вопрос по мероприятию от user_5."""
    return EventIssueAnswer.objects.create(
        event=event_individual,
        user=user_5,
        issue=issue_individual,
        answer='Ответ на вопрос',
    )


@pytest.fixture
def answer_individual2(event_individual, user_5, issue_individual2):
    """Второй ответ на вопрос по мероприятию от user_5."""
    return EventIssueAnswer.objects.create(
        event=event_individual,
        user=user_5,
        issue=issue_individual2,
        answer='Второй ответ на вопрос',
    )


@pytest.fixture
def answers_individual(
    event_individual, answer_individual, answer_individual2
):
    """
    Ответы на вопросы по мероприятию.
    Создает фикстуры и возвращает два ответа.
    """
    return EventIssueAnswer.objects.filter(
        event=event_individual
    )


@pytest.fixture
def event_organizer_individual(user_event_organizer, event_individual):
    """Пользователь из модели организаторов эвентов."""
    organizer = EventOrganizationData.objects.create(
        event=event_individual,
        organizer=user_event_organizer
    )
    return organizer


@pytest.fixture
def application_individual(
    event_individual, user_5, issue_individual, answer_individual
):
    """
    Неподтвержденная заявка на индивидуальное мероприятие
    от user_5. После подтверждения заявка удаляется.
    """
    application = EventApplications.objects.create(
        event=event_individual,
        user=user_5
    )
    return application


@pytest.fixture
def application_individual2(
    event_individual, user_4, issue_individual, answer_individual
):
    """
    Неподтвержденная заявка на индивидуальное мероприятие
    от user_4. После подтверждения заявка удаляется.
    """
    application = EventApplications.objects.create(
        event=event_individual,
        user=user_4
    )
    return application


@pytest.fixture
def participant_individual_event(
    event_individual, user_5
):
    """Участник индивидуального эвента (user_5)."""
    participant = EventParticipants.objects.create(
        event=event_individual,
        user=user_5
    )
    return participant
