from http import HTTPStatus
import pytest

from events.models import EventApplications, EventOrganizationData, EventParticipants
from events.serializers import AnswerSerializer


@pytest.mark.django_db(transaction=True, reset_sequences=True)
class TestEventAdditionalIssueViewSet:
    event_url = '/api/v1/events/'
    answers_url = '/answers/'

    answer = {
        "issue": 1,
        "answer": "Ответ на вопрос"
    }
    answer2 = {
        "issue": 2,
        "answer": "Ответ на второй вопрос"
    }
    answers = [answer, answer2]

    def test_create_answer_not_auth(
            self, client, event_individual, issue
    ):
        """Проверка, что неавторизованный пользователь не имеет
        доступа к эндпоинту."""
        response = client.post(
            f'{self.event_url}{event_individual.id}{self.answers_url}',
            data=self.answer
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Response code is not 401'
        )

    def test_create_answer_auth(
            self, free_authenticated_client, event_individual, issues
    ):
        """Проверка, что авторизованный пользователь может отправлять
        ответ на вопрос."""
        response = free_authenticated_client.post(
            f'{self.event_url}{event_individual.id}{self.answers_url}',
            data=self.answers,
            format='json'
        )
        assert response.status_code == HTTPStatus.CREATED, (
            'Response code is not 201'
        )

    def test_create_answer_auth_not_all(
            self, free_authenticated_client, event_individual, issues
    ):
        """Проверка, что авторизованный пользователь не может ответить
        только на часть вопросов. Сразу нужны ответы на все вопросы."""
        response = free_authenticated_client.post(
            f'{self.event_url}{event_individual.id}{self.answers_url}',
            data=[self.answer],
            format='json'
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Response code is not 400'
        )

    def test_answers_me_not_auth(
            self, client, event_individual, issues
    ):
        """Проверка, что неавторизованный пользователь не имеет
        доступа к эндпоинту."""
        response = client.get(
            f'{self.event_url}{event_individual.id}{self.answers_url}me/'
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Response code is not 401'
        )

    def test_answers_me_auth_without_self_answers(
            self, authenticated_client_2, event_individual, answers
    ):
        """Проверка, что авторизованный пользователь не получает
        ответы, если у него нет вопросов."""
        response = authenticated_client_2.get(
            f'{self.event_url}{event_individual.id}{self.answers_url}me/'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200'
        )
        assert response.data == [], (
            'Response data is not empty'
        )

    def test_answers_me_auth_with_self_answers(
            self, authenticated_client_5, event_individual, answers, issues,
            user_5
    ):
        """Проверка, что авторизованный пользователь получает
        ответы, если у него есть вопросы."""
        response = authenticated_client_5.get(
            f'{self.event_url}{event_individual.id}{self.answers_url}me/'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200'
        )
        data = response.data
        assert len(data) == 2, 'Response data is not 2 objects'
        assert data[0] == {
            'id': answers[0].id,
            'issue': issues[0].issue,
            'answer': answers[0].answer,
            'event': event_individual.id,
            'user': user_5.id
        }
        assert data[1] == {
            'id': answers[1].id,
            'issue': issues[1].issue,
            'answer': answers[1].answer,
            'event': event_individual.id,
            'user': user_5.id
        }

    def test_answer_delete_event_organizer(
            self, authenticated_client_event_organizer,
            event_individual, answer, event_organizer
    ):
        """Проверка, что пользователь из модели организаторов
        может удалить ответ"""
        response = authenticated_client_event_organizer.delete(
            f'{self.event_url}{event_individual.id}'
            f'{self.answers_url}{answer.id}/'
        )
        assert response.status_code == HTTPStatus.NO_CONTENT, (
            'Response code is not 204'
        )

    def test_answer_delete_auth(
            self, free_authenticated_client, event_individual, answer
    ):
        """Проверка, что авторизованный пользователь не может удалить ответ"""
        response = free_authenticated_client.delete(
            f'{self.event_url}{event_individual.id}'
            f'{self.answers_url}{answer.id}/'
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Response code is not 403'
        )

    def test_answer_delete_author(
            self, authenticated_client_5, event_individual, answer
    ):
        """Проверка, что автор не может удалить ответ"""
        response = authenticated_client_5.delete(
            f'{self.event_url}{event_individual.id}'
            f'{self.answers_url}{answer.id}/'
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Response code is not 403'
        )

    def test_answer_delete_not_auth(
            self, client, event_individual, answer
    ):
        """Проверка, что неавторизованный пользователь не может
        удалить ответ"""
        response = client.delete(
            f'{self.event_url}{event_individual.id}'
            f'{self.answers_url}{answer.id}/'
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Response code is not 401'
        )

    def test_answer_put_event_organizer(
            self, authenticated_client_event_organizer,
            event_individual, answer2, event_organizer
    ):
        """Проверка, что пользователь из модели организаторов
        может изменить ответ"""
        response = authenticated_client_event_organizer.put(
            f'{self.event_url}{event_individual.id}'
            f'{self.answers_url}{answer2.id}/',
            data=self.answer
        )
        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200'
        )
        assert response.data['answer'] == self.answer['answer'], (
            'Response data is not correct'
        )

    def test_answer_put_author_with_application(
            self, authenticated_client_5, event_individual, answer2,
            application_individual
    ):
        """Проверка, что автор может изменить ответ пока заявка
        не подтверждена"""
        response = authenticated_client_5.put(
            f'{self.event_url}{event_individual.id}'
            f'{self.answers_url}{answer2.id}/',
            data=self.answer
        )
        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200'
        )
        assert response.data['answer'] == self.answer['answer'], (
            'Response data is not correct'
        )

    def test_answer_put_author_without_application(
            self, authenticated_client_5, event_individual, answer2
    ):
        """Проверка, что автор не может изменить ответ когда заявка
        уже подтверждена"""
        response = authenticated_client_5.put(
            f'{self.event_url}{event_individual.id}'
            f'{self.answers_url}{answer2.id}/',
            data=self.answer
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Response code is not 403'
        )

    def test_answer_put_auth(
            self, free_authenticated_client, event_individual, answer2
    ):
        """Проверка, что авторизованный пользователь не может
        изменить ответ"""
        response = free_authenticated_client.put(
            f'{self.event_url}{event_individual.id}'
            f'{self.answers_url}{answer2.id}/',
            data=self.answer
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Response code is not 403'
        )

    def test_answer_put_not_auth(
            self, client, event_individual, answer2
    ):
        """Проверка, что неавторизованный пользователь не может
        изменить ответ"""
        response = client.put(
            f'{self.event_url}{event_individual.id}'
            f'{self.answers_url}{answer2.id}/',
            data=self.answer
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Response code is not 401'
        )

    def test_answer_patch_event_organizer(
            self, authenticated_client_event_organizer,
            event_individual, answer2, event_organizer
    ):
        """Проверка, что пользователь из модели организаторов
        может изменить ответ"""
        response = authenticated_client_event_organizer.patch(
            f'{self.event_url}{event_individual.id}'
            f'{self.answers_url}{answer2.id}/',
            data=self.answer
        )
        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200'
        )
        assert response.data['answer'] == self.answer['answer'], (
            'Response data is not correct'
        )

    def test_answer_patch_author_with_application(
            self, authenticated_client_5, event_individual, answer2,
            application_individual
    ):
        """Проверка, что автор может изменить ответ пока заявка
        не подтверждена"""
        response = authenticated_client_5.patch(
            f'{self.event_url}{event_individual.id}'
            f'{self.answers_url}{answer2.id}/',
            data=self.answer
        )
        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200'
        )
        assert response.data['answer'] == self.answer['answer'], (
            'Response data is not correct'
        )

    def test_answer_patch_author_without_application(
            self, authenticated_client_5, event_individual, answer2
    ):
        """Проверка, что автор не может изменить ответ когда заявка
        уже подтверждена"""
        response = authenticated_client_5.patch(
            f'{self.event_url}{event_individual.id}'
            f'{self.answers_url}{answer2.id}/',
            data=self.answer
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Response code is not 403'
        )

    def test_answer_patch_auth(
            self, free_authenticated_client, event_individual, answer2
    ):
        """Проверка, что авторизованный пользователь не может
        изменить ответ"""
        response = free_authenticated_client.patch(
            f'{self.event_url}{event_individual.id}'
            f'{self.answers_url}{answer2.id}/',
            data=self.answer
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Response code is not 403'
        )

    def test_answer_patch_not_auth(
            self, client, event_individual, answer2
    ):
        """Проверка, что неавторизованный пользователь не может
        изменить ответ"""
        response = client.patch(
            f'{self.event_url}{event_individual.id}'
            f'{self.answers_url}{answer2.id}/',
            data=self.answer
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Response code is not 401'
        )


@pytest.mark.django_db(transaction=True, reset_sequences=True)
class TestEventApplicationsViewSet:
    event_url = '/api/v1/events/'
    applications_url = '/applications/'

    short_user5 = {
        "id": 1,
        "username": "username5",
        "avatar": {"photo": None},
        "email": '',
        "first_name": "Имя5",
        "last_name": "Фамилия5",
        "patronymic_name": None,
        "date_of_birth": None,
        "membership_fee": False,
        "is_verified": False
    }
    short_event_individual = {
        "id": 1,
        "name": "Test Event",
        "banner": None
    }
    short_user5_id_4 = {
            "id": 4,
            "username": "username5",
            "avatar": {"photo": None},
            "email": '',
            "first_name": "Имя5",
            "last_name": "Фамилия5",
            "patronymic_name": None,
            "date_of_birth": None,
            "membership_fee": False,
            "is_verified": False
        }

    def test_list_applications_event_organizer(
            self, authenticated_client_event_organizer,
            event_individual, application_individual,
            event_organizer, application_individual2,
            user_4, user_5, answer
    ):
        """Проверка, что пользователь из модели организаторов
        может получить список заявок"""
        response = authenticated_client_event_organizer.get(
            f'{self.event_url}{event_individual.id}'
            f'{self.applications_url}'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200'
        )
        assert len(response.data) == 2, (
            'Response data is not correct'
        )
        application_data = response.data[0]
        application_data2 = response.data[1]
        assert 'id' in application_data, (
            'Not found id-key in response'
        )
        assert 'id' in application_data2, (
            'Not found id-key in response'
        )
        assert 'user' in application_data, (
            'Not found user-key in response'
        )
        assert 'user' in application_data2, (
            'Not found user-key in response'
        )
        assert 'event' in application_data, (
            'Not found event-key in response'
        )
        assert 'event' in application_data2, (
            'Not found event-key in response'
        )
        assert 'answers' in application_data, (
            'Not found answers-key in response'
        )
        assert 'answers' in application_data2, (
            'Not found answers-key in response'
        )
        assert 'documents' in application_data, (
            'Not found documents-key in response'
        )
        assert 'documents' in application_data2, (
            'Not found documents-key in response'
        )
        assert application_data['id'] == application_individual2.id, (
            'id is not correct'
        )
        assert application_data2['id'] == application_individual.id, (
            'id is not correct'
        )
        assert application_data2['user'] == self.short_user5_id_4
        assert application_data2['event'] == self.short_event_individual
        answer = AnswerSerializer(instance=answer).data
        assert answer in application_data2['answers']

    def test_list_applications_author(
            self, authenticated_client_5, event_individual,
            application_individual, application_individual2
    ):
        """Проверка, что автор заявки не может получить список заявок"""
        response = authenticated_client_5.get(
            f'{self.event_url}{event_individual.id}'
            f'{self.applications_url}'
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Response code is not 403'
        )

    def test_list_applications_auth(
            self, authenticated_client_5, event_individual,
            application_individual2
    ):
        """Проверка, что простой пользователь не может получить
        список заявок"""
        response = authenticated_client_5.get(
            f'{self.event_url}{event_individual.id}'
            f'{self.applications_url}'
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Response code is not 403'
        )

    def test_list_applications_not_auth(
            self, client, event_individual, application_individual
    ):
        """Проверка, что неавторизованный пользователь не может
        получить список заявок"""
        response = client.get(
            f'{self.event_url}{event_individual.id}'
            f'{self.applications_url}'
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Response code is not 401'
        )

    def test_create_application_auth_without_answers(
            self, authenticated_client_5, event_individual,
            issues
    ):
        """Проверка, что пока нет ответов на все вопросы мероприятия,
        пользователь не может создать заявку"""
        response = authenticated_client_5.post(
            f'{self.event_url}{event_individual.id}'
            f'{self.applications_url}'
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Response code is not 403'
        )

    def test_create_application_verif_auth_with_answers(
            self, authenticated_verifed_client_5, event_individual,
            issue, answer
    ):
        """Проверка, что верифицированный пользователь ответивший на
        все вопросы мероприятия может создать заявку"""
        response = authenticated_verifed_client_5.post(
            f'{self.event_url}{event_individual.id}'
            f'{self.applications_url}'
        )
        assert response.status_code == HTTPStatus.CREATED, (
            'Response code is not 201'
        )

    def test_create_application_verif_auth_without_answers(
            self, authenticated_verifed_client_5, event_individual,
            issue
    ):
        """Проверка, что пока нет ответов на все вопросы мероприятия,
        верифицированный пользователь не может создать заявку"""
        response = authenticated_verifed_client_5.post(
            f'{self.event_url}{event_individual.id}'
            f'{self.applications_url}'
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Response code is not 400'
        )

    def test_create_answer_not_auth(
            self, client, event_individual, issue
    ):
        """Проверка, что неавторизованный пользователь не может
        создать ответ на вопрос"""
        response = client.post(
            f'{self.event_url}{event_individual.id}'
            f'{self.applications_url}'
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Response code is not 401'
        )

    def test_create_application_verif_auth_duble(
            self, authenticated_verifed_client_5, event_individual,
            issue, answer, application_individual
    ):
        """Проверка, что верифицированный пользователь может подать
        повторную заявку"""
        response = authenticated_verifed_client_5.post(
            f'{self.event_url}{event_individual.id}'
            f'{self.applications_url}'
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Response code is not 400'
        )

    def test_create_application_verif_auth_with_participants(
            self, authenticated_verifed_client_5, event_individual,
            issue, answer, participant_individual_event
    ):
        """Проверка, что верифицированный пользователь не может подать
        заявку, если он уже участвует в эвенте"""
        response = authenticated_verifed_client_5.post(
            f'{self.event_url}{event_individual.id}'
            f'{self.applications_url}'
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Response code is not 400'
        )

    def test_applications_me_not_auth(
            self, client, event_individual, application_individual
    ):
        """Проверка, что неавторизованный пользователь не имеет
        доступа к me/ эндпоинту"""
        response = client.get(
            f'{self.event_url}{event_individual.id}'
            f'{self.applications_url}me/'
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Response code is not 401'
        )

    def test_applications_me_auth(
            self, authenticated_client, event_individual,
            application_individual
    ):
        """Проверка, что простой пользователь не имеет
        доступа к me/ эндпоинту если у него нет заявки на мероприятие"""
        response = authenticated_client.get(
            f'{self.event_url}{event_individual.id}'
            f'{self.applications_url}me/'
        )
        assert response.status_code == HTTPStatus.NOT_FOUND, (
            'Response code is not 404'
        )

    def test_applications_me_auth_with_application(
            self, authenticated_client_5, event_individual,
            application_individual, application_individual2,
            answer
    ):
        """Проверка, что пользователь с неподтвержденной заявкой имеет
        доступ к me/ эндпоинту"""
        response = authenticated_client_5.get(
            f'{self.event_url}{event_individual.id}'
            f'{self.applications_url}me/'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200'
        )
        application_data = response.data
        assert isinstance(application_data, dict), (
            'Not correct data type'
        )
        assert 'id' in application_data, (
            'Not found id-key in response'
        )
        assert 'user' in application_data, (
            'Not found user-key in response'
        )
        assert 'event' in application_data, (
            'Not found event-key in response'
        )
        assert 'answers' in application_data, (
            'Not found answers-key in response'
        )
        assert 'documents' in application_data, (
            'Not found documents-key in response'
        )
        assert application_data['id'] == application_individual.id, (
            'id is not correct'
        )
        assert application_data['user'] == self.short_user5
        assert application_data['event'] == self.short_event_individual
        answer = AnswerSerializer(instance=answer).data
        assert answer in application_data['answers']

    def test_retrieve_applications_not_auth(
            self, client, event_individual, application_individual
    ):
        """Проверка, что неавторизованный пользователь не имеет
        доступа заявке на мероприятие"""
        response = client.get(
            f'{self.event_url}{event_individual.id}'
            f'{self.applications_url}{application_individual.id}/'
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Response code is not 401'
        )

    def test_retrieve_applications_auth(
            self, authenticated_client_4, event_individual,
            application_individual, application_individual2
    ):
        """Проверка, что простой пользователь не имеет доступа
        к не своей заявке на мероприятие"""
        response = authenticated_client_4.get(
            f'{self.event_url}{event_individual.id}'
            f'{self.applications_url}{application_individual.id}/'
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Response code is not 403'
        )

    def test_retrieve_applications_auth_with_application(
            self, authenticated_client_5, event_individual,
            application_individual, application_individual2,
            answer
    ):
        """Проверка, что верифицированный пользователь может
        получить заявку на мероприятие"""
        response = authenticated_client_5.get(
            f'{self.event_url}{event_individual.id}'
            f'{self.applications_url}{application_individual.id}/'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200'
        )
        application_data = response.data
        assert isinstance(application_data, dict), (
            'Not correct data type'
        )
        assert 'id' in application_data, (
            'Not found id-key in response'
        )
        assert 'user' in application_data, (
            'Not found user-key in response'
        )
        assert 'event' in application_data, (
            'Not found event-key in response'
        )
        assert 'answers' in application_data, (
            'Not found answers-key in response'
        )
        assert 'documents' in application_data, (
            'Not found documents-key in response'
        )
        assert application_data['id'] == application_individual.id, (
            'id is not correct'
        )
        assert application_data['user'] == self.short_user5
        assert application_data['event'] == self.short_event_individual
        answer = AnswerSerializer(instance=answer).data
        assert answer in application_data['answers']

    def test_retrieve_applications_organizer(
            self, authenticated_client_event_organizer, event_individual,
            application_individual, application_individual2,
            answer, event_organizer
    ):
        """Проверка, что верифицированный пользователь может
        получить заявку на мероприятие"""
        response = authenticated_client_event_organizer.get(
            f'{self.event_url}{event_individual.id}'
            f'{self.applications_url}{application_individual.id}/'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200'
        )
        application_data = response.data
        assert isinstance(application_data, dict), (
            'Not correct data type'
        )
        assert 'id' in application_data, (
            'Not found id-key in response'
        )
        assert 'user' in application_data, (
            'Not found user-key in response'
        )
        assert 'event' in application_data, (
            'Not found event-key in response'
        )
        assert 'answers' in application_data, (
            'Not found answers-key in response'
        )
        assert 'documents' in application_data, (
            'Not found documents-key in response'
        )
        assert application_data['id'] == application_individual.id, (
            'id is not correct'
        )
        assert application_data['user'] == self.short_user5_id_4
        assert application_data['event'] == self.short_event_individual
        answer = AnswerSerializer(instance=answer).data
        assert answer in application_data['answers']

    def test_delete_application_not_auth(
            self, client, event_individual, application_individual
    ):
        """Проверка, что неавторизованный пользователь не может
        удалить заявку на мероприятие"""
        response = client.delete(
            f'{self.event_url}{event_individual.id}'
            f'{self.applications_url}{application_individual.id}/'
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Response code is not 401'
        )

    def test_delete_application_auth(
            self, authenticated_client_4, event_individual,
            application_individual
    ):
        """Проверка, что простой пользователь не может
        удалить заявку на мероприятие"""
        response = authenticated_client_4.delete(
            f'{self.event_url}{event_individual.id}'
            f'{self.applications_url}{application_individual.id}/'
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Response code is not 403'
        )

    def test_delete_applications_author_application(
            self, authenticated_client_5, event_individual,
            application_individual, application_individual2
    ):
        """Проверка, что автор заявки может
        удалить заявку на мероприятие"""
        response = authenticated_client_5.delete(
            f'{self.event_url}{event_individual.id}'
            f'{self.applications_url}{application_individual.id}/'
        )
        assert response.status_code == HTTPStatus.NO_CONTENT, (
            'Response code is not 204'
        )

    def test_delete_applications_event_organizer(
            self, authenticated_client_event_organizer,
            event_individual, application_individual,
            application_individual2, event_organizer
    ):
        """Проверка, что автор мероприятия может
        удалить заявку на мероприятие"""
        response = authenticated_client_event_organizer.delete(
            f'{self.event_url}{event_individual.id}'
            f'{self.applications_url}{application_individual.id}/'
        )
        assert response.status_code == HTTPStatus.NO_CONTENT, (
            'Response code is not 204'
        )

    def test_get_answer_applications_not_auth(
            self, client, event_individual, application_individual,
            answer
    ):
        """Проверка, что неавторизованный пользователь не может
        получить ответы из заявки на мероприятие"""
        response = client.get(
            f'{self.event_url}{event_individual.id}'
            f'{self.applications_url}{application_individual.id}/answers/'
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Response code is not 401'
        )

    def test_get_answer_applications_auth(
            self, free_authenticated_client, event_individual,
            application_individual, answer
    ):
        """Проверка, что неавторизованный пользователь не может
        получить ответы из заявки на мероприятие"""
        response = free_authenticated_client.get(
            f'{self.event_url}{event_individual.id}'
            f'{self.applications_url}{application_individual.id}/answers/'
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Response code is not 403'
        )

    def test_get_answer_applications_event_organizer(
            self, authenticated_client_event_organizer,
            event_individual, application_individual, answer,
            event_organizer, answer2
    ):
        """Проверка, что организатор мероприятия может
        получить ответы из заявки на мероприятие"""
        response = authenticated_client_event_organizer.get(
            f'{self.event_url}{event_individual.id}'
            f'{self.applications_url}{application_individual.id}/answers/'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200'
        )
        answer_data = AnswerSerializer(instance=answer).data
        assert answer_data in response.data

    def test_get_answer_applications_author(
            self, authenticated_client_5, event_individual,
            application_individual, answer
    ):
        """Проверка, что автор заявки не может
        получить ответы из заявки на мероприятие"""
        response = authenticated_client_5.get(
            f'{self.event_url}{event_individual.id}'
            f'{self.applications_url}{application_individual.id}/answers/'
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Response code is not 403'
        )

    def test_delete_answer_applications_not_auth(
            self, client, event_individual, application_individual,
            answer
    ):
        """Проверка, что неавторизованный пользователь не может
        удалить заявку на мероприятие"""
        response = client.delete(
            f'{self.event_url}{event_individual.id}'
            f'{self.applications_url}{application_individual.id}/answers/'
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Response code is not 401'
        )

    def test_delete_answer_applications_auth(
            self, free_authenticated_client, event_individual,
            application_individual, answer
    ):
        """Проверка, что неавторизованный пользователь не может
        удалить заявку на мероприятие"""
        response = free_authenticated_client.delete(
            f'{self.event_url}{event_individual.id}'
            f'{self.applications_url}{application_individual.id}/answers/'
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Response code is not 403'
        )

    def test_delete_answer_applications_event_organizer(
            self, authenticated_client_event_organizer,
            event_individual, application_individual, answer,
            event_organizer, answer2
    ):
        """Проверка, что организатор мероприятия может
        удалить заявку на мероприятие"""
        response = authenticated_client_event_organizer.delete(
            f'{self.event_url}{event_individual.id}'
            f'{self.applications_url}{application_individual.id}/answers/'
        )
        assert response.status_code == HTTPStatus.NO_CONTENT, (
            'Response code is not 204'
        )

    def test_delete_answer_applications_author(
            self, authenticated_client_5, event_individual,
            application_individual, answer
    ):
        """Проверка, что автор заявки не может
        удалить заявку на мероприятие"""
        response = authenticated_client_5.delete(
            f'{self.event_url}{event_individual.id}'
            f'{self.applications_url}{application_individual.id}/answers/'
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Response code is not 403'
        )

    def test_confirm_application_not_auth(
            self, client, event_individual, application_individual
    ):
        """Проверка, что неавторизованный пользователь не может
        подтвердить заявку на мероприятие"""
        response = client.post(
            f'{self.event_url}{event_individual.id}'
            f'{self.applications_url}{application_individual.id}/confirm/'
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Response code is not 401'
        )

    def test_confirm_application_auth(
            self, free_authenticated_client, event_individual,
            application_individual
    ):
        """Проверка, что простой авторизованный пользователь не может
        подтвердить заявку на мероприятие"""
        response = free_authenticated_client.post(
            f'{self.event_url}{event_individual.id}'
            f'{self.applications_url}{application_individual.id}/confirm/'
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Response code is not 403'
        )

    def test_confirm_application_author(
            self, free_authenticated_client, event_individual,
            application_individual
    ):
        """Проверка, что автор заявки не может
        подтвердить свою заявку на мероприятие"""
        response = free_authenticated_client.post(
            f'{self.event_url}{event_individual.id}'
            f'{self.applications_url}{application_individual.id}/confirm/'
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Response code is not 403'
        )

    def test_confirm_application_event_organizer(
            self, authenticated_client_event_organizer,
            event_individual, application_individual,
            event_organizer
    ):
        """Проверка, что организатор мероприятия может
        подтвердить заявку на мероприятие"""
        response = authenticated_client_event_organizer.post(
            f'{self.event_url}{event_individual.id}'
            f'{self.applications_url}{application_individual.id}/confirm/'
        )
        assert response.status_code == HTTPStatus.CREATED, (
            'Response code is not 201'
        )
        assert not EventApplications.objects.filter(
            id=application_individual.id
        ).exists(), 'Подтвержденная заявка не удалена'
        assert EventParticipants.objects.filter(
            event=event_individual, user=application_individual.user
        ).exists(), (
            'Не создались участники мероприятия после подтверждения заявки'
        )


@pytest.mark.django_db(transaction=True, reset_sequences=True)
class TestEventParticipantsViewSet:
    event_url = '/api/v1/events/'
    participants_url = '/participants/'

    participant_individual_event = {
        "id": 1,
        "user": TestEventApplicationsViewSet.short_user5,
        "event": TestEventApplicationsViewSet.short_event_individual,
        "answers": [
            {
                "id": 1,
                "event": 1,
                "user": 2,
                "answer": "Ответ на вопрос",
                "issue": 1
            }
        ],
        "documents": []
    }

    def test_get_participants_not_auth(
            self, client, event_individual, participant_individual_event
    ):
        """Проверка, что неавторизованный пользователь не может
        получить участников мероприятия"""
        response = client.get(
            f'{self.event_url}{event_individual.id}'
            f'{self.participants_url}'
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Response code is not 401'
        )

    def test_get_participants_auth(
            self, free_authenticated_client, event_individual,
            participant_individual_event
    ):
        """Проверка, что простой авторизованный пользователь не может
        получить участников мероприятия"""
        response = free_authenticated_client.get(
            f'{self.event_url}{event_individual.id}'
            f'{self.participants_url}'
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Response code is not 403'
        )

    def test_get_participants_event_organizer(
            self, authenticated_client_event_organizer,
            event_individual, participant_individual_event,
            event_organizer, answer
    ):
        """Проверка, что организатор мероприятия может
        получить участников мероприятия"""
        response = authenticated_client_event_organizer.get(
            f'{self.event_url}{event_individual.id}'
            f'{self.participants_url}'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200'
        )
        assert isinstance(response.data, list), (
            'Response data is not list'
        )
        assert len(response.data) == 1, 'Response data is not 1 object'
        data = response.data[0]
        assert 'id' in data, (
            'Not found id-key in response'
        )
        assert 'user' in data, (
            'Not found user-key in response'
        )
        assert 'event' in data, (
            'Not found event-key in response'
        )
        assert 'answers' in data, (
            'Not found answers-key in response'
        )
        assert 'documents' in data, (
            'Not found documents-key in response'
        )
        assert data['id'] == participant_individual_event.id, (
            'id is not correct'
        )
        assert data['user'] == TestEventApplicationsViewSet.short_user5_id_4
        assert data['event'] == (
            TestEventApplicationsViewSet.short_event_individual
        )
        answer = AnswerSerializer(instance=answer).data
        assert answer in data['answers']

    def test_get_participants_author(
            self, authenticated_client_5, event_individual,
            participant_individual_event
    ):
        """Проверка, что пользователь-участник не может
        получить всех участников мероприятия"""
        response = authenticated_client_5.get(
            f'{self.event_url}{event_individual.id}'
            f'{self.participants_url}'
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Response code is not 403'
        )

    def test_retrieve_participant_not_auth(
            self, client, event_individual, participant_individual_event
    ):
        """Проверка, что неавторизованный пользователь не может
        получить участника мероприятия"""
        response = client.get(
            f'{self.event_url}{event_individual.id}'
            f'{self.participants_url}{participant_individual_event.id}/'
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Response code is not 401'
        )

    def test_retrieve_participant_auth(
            self, free_authenticated_client, event_individual,
            participant_individual_event
    ):
        """Проверка, что простой авторизованный пользователь не может
        получить участника мероприятия"""
        response = free_authenticated_client.get(
            f'{self.event_url}{event_individual.id}'
            f'{self.participants_url}{participant_individual_event.id}/'
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Response code is not 403'
        )

    def test_retrieve_participant_event_organizer(
            self, authenticated_client_event_organizer,
            event_individual, participant_individual_event,
            event_organizer, answer
    ):
        """Проверка, что организатор мероприятия может
        получить участника мероприятия"""
        response = authenticated_client_event_organizer.get(
            f'{self.event_url}{event_individual.id}'
            f'{self.participants_url}{participant_individual_event.id}/'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200'
        )
        assert isinstance(response.data, dict), (
            'Response data is not dict'
        )
        data = response.data
        assert 'id' in data, (
            'Not found id-key in response'
        )
        assert 'user' in data, (
            'Not found user-key in response'
        )
        assert 'event' in data, (
            'Not found event-key in response'
        )
        assert 'answers' in data, (
            'Not found answers-key in response'
        )
        assert 'documents' in data, (
            'Not found documents-key in response'
        )
        assert data['id'] == participant_individual_event.id, (
            'id is not correct'
        )
        assert data['user'] == TestEventApplicationsViewSet.short_user5_id_4
        assert data['event'] == (
            TestEventApplicationsViewSet.short_event_individual
        )
        answer = AnswerSerializer(instance=answer).data
        assert answer in data['answers']

    def test_retrieve_participant_author(
            self, authenticated_client_5, event_individual,
            participant_individual_event
    ):
        """Проверка, что пользователь-участник не может
        получить свою информацию о участии в мероприятии"""
        response = authenticated_client_5.get(
            f'{self.event_url}{event_individual.id}'
            f'{self.participants_url}{participant_individual_event.id}/'
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Response code is not 403'
        )
    
    def test_delete_participant_not_auth(
            self, client, event_individual, participant_individual_event
    ):
        """Проверка, что неавторизованный пользователь не может
        удалить участника мероприятия"""
        response = client.delete(
            f'{self.event_url}{event_individual.id}'
            f'{self.participants_url}{participant_individual_event.id}/'
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Response code is not 401'
        )

    def test_delete_participant_auth(
            self, free_authenticated_client, event_individual,
            participant_individual_event
    ):
        """Проверка, что простой авторизованный пользователь не может
        удалить участника мероприятия"""
        response = free_authenticated_client.delete(
            f'{self.event_url}{event_individual.id}'
            f'{self.participants_url}{participant_individual_event.id}/'
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Response code is not 403'
        )

    def test_delete_participant_event_organizer(
            self, authenticated_client_event_organizer,
            event_individual, participant_individual_event,
            event_organizer, answer
    ):
        """Проверка, что организатор мероприятия может
        удалить участника мероприятия"""
        response = authenticated_client_event_organizer.delete(
            f'{self.event_url}{event_individual.id}'
            f'{self.participants_url}{participant_individual_event.id}/'
        )
        assert response.status_code == HTTPStatus.NO_CONTENT, (
            'Response code is not 204'
        )

    def test_delete_participant_author(
            self, authenticated_client_5, event_individual,
            participant_individual_event
    ):
        """Проверка, что пользователь-участник может
        удалить свою запись о участии в мероприятии"""
        response = authenticated_client_5.delete(
            f'{self.event_url}{event_individual.id}'
            f'{self.participants_url}{participant_individual_event.id}/'
        )
        assert response.status_code == HTTPStatus.NO_CONTENT, (
            'Response code is not 204'
        )

    def test_me_participant_author(
            self, authenticated_client_5,
            event_individual, participant_individual_event,
            answer
    ):
        """Проверка, что пользователь-участник имеет доступ к
        me/ эндпоинту"""
        response = authenticated_client_5.get(
            f'{self.event_url}{event_individual.id}'
            f'{self.participants_url}me/'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200'
        )
        assert isinstance(response.data, dict), (
            'Response data is not dict'
        )
        data = response.data
        assert 'id' in data, (
            'Not found id-key in response'
        )
        assert 'user' in data, (
            'Not found user-key in response'
        )
        assert 'event' in data, (
            'Not found event-key in response'
        )
        assert 'answers' in data, (
            'Not found answers-key in response'
        )
        assert 'documents' in data, (
            'Not found documents-key in response'
        )
        assert data['id'] == participant_individual_event.id, (
            'id is not correct'
        )
        assert data['user'] == TestEventApplicationsViewSet.short_user5
        assert data['event'] == (
            TestEventApplicationsViewSet.short_event_individual
        )
        answer = AnswerSerializer(instance=answer).data
        assert answer in data['answers']
    
    def test_me_participant_auth(
            self, free_authenticated_client,
            event_individual, participant_individual_event
    ):
        """Проверка, что простой пользователь не участник этого
        мероприятия не имеет доступа к me/ эндпоинту"""
        response = free_authenticated_client.get(
            f'{self.event_url}{event_individual.id}'
            f'{self.participants_url}me/'
        )
        assert response.status_code == HTTPStatus.NOT_FOUND, (
            'Response code is not 404'
        )
    
    def test_me_participant_event_organizer(
            self, authenticated_client_event_organizer,
            event_individual, participant_individual_event,
            event_organizer
    ):
        """Проверка, что организатор мероприятия не может
        получить доступ к me/ эндпоинту"""
        response = authenticated_client_event_organizer.get(
            f'{self.event_url}{event_individual.id}'
            f'{self.participants_url}me/'
        )
        assert response.status_code == HTTPStatus.NOT_FOUND, (
            'Response code is not 404'
        )

    def test_me_participant_not_auth(
            self, client, event_individual, participant_individual_event
    ):
        """Проверка, что неавторизованный пользователь не может
        получить доступ к me/ эндпоинту"""
        response = client.get(
            f'{self.event_url}{event_individual.id}'
            f'{self.participants_url}me/'
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Response code is not 401'
        )