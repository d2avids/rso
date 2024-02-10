import datetime
from http import HTTPStatus

import pytest

from rso_backend import settings


@pytest.mark.django_db(transaction=True)
class TestCompetitionViewSet:
    competition_url = '/api/v1/competitions/'

    def test_competition_list(self, client, competition, competition_2):
        """Получение списка конкурсов"""
        response = client.get(self.competition_url)
        assert response.status_code == HTTPStatus.OK, 'Response code is not 200'
        assert isinstance(response.data, list), 'Response type is not list'
        assert isinstance(response.data[0], dict), 'Response type is not dict'
        assert 'name' in response.data[0], 'Not found name-key in response'
        assert response.data[0]['name'] == competition.name, 'Incorrect name'
        assert response.data[0]['id'] == competition.id, 'Incorrect id'

    def test_competition_detail(self, client, competition):
        """Получение конкурса"""
        response = client.get(f'{self.competition_url}{competition.id}/')
        assert response.status_code == HTTPStatus.OK, 'Response code is not 200'
        assert isinstance(response.data, dict), 'Response type is not dict'
        assert 'name' in response.data, 'Not found name-key in response'
        assert 'id' in response.data, 'Not found id-key in response'
        assert response.data['name'] == competition.name, 'Incorrect name'
        assert response.data['id'] == competition.id, 'Incorrect id'

    def test_competition_detail_not_found(self, client):
        """Получение конкурса по несуществующему id"""
        response = client.get(f'{self.competition_url}99999/')
        assert response.status_code == HTTPStatus.NOT_FOUND, (
            'Response code is not 404'
        )

    def test_create_competition_not_auth(self, client):
        """Создание конкурса неавторизованным пользователем"""
        response = client.post(self.competition_url, {'name': 'test'})
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Response code is not 401'
        )

    def test_create_competition_auth(self, authenticated_client):
        """Создание конкурса авторизованным пользователем"""
        response = authenticated_client.post(
            self.competition_url, {'name': 'test'}
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Response code is not 403'
        )

    def test_create_competition_admin(self, admin_client):
        """Создание конкурса администратором"""
        response = admin_client.post(self.competition_url, {'name': 'test'})
        assert response.status_code == HTTPStatus.CREATED, (
            'Response code is not 201'
        )

    def test_junior_detachments_not_auth(self, client, competition):
        """Получение списка младших отрядов неавторизованным пользователем"""
        response = client.get(
            f'{self.competition_url}{competition.id}/junour_detachments/'
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Response code is not 401'
        )

    def test_junior_detachments_auth(self, authenticated_client, competition):
        """Получение списка младших отрядов авторизованным пользователем"""
        response = authenticated_client.get(
            f'{self.competition_url}{competition.id}/junour_detachments/'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200'
        )
        assert response.data == [], 'Incorrect permissions'

    def test_junior_detachments_commander_with_true_region(
            self, authenticated_client, detachment, competition,
            junior_detachment, junior_detachment_2
    ):
        """Получение списка младших отрядов командиром отряда региона 1

        Есть свободные младшие отряды в регионе 1
        """
        response = authenticated_client.get(
            f'{self.competition_url}{competition.id}/junour_detachments/'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200'
        )
        data = response.data
        assert len(data) == 1, 'Incorrect count of junior detachments'
        assert 'id' in data[0], 'Not found id-key in response'
        assert 'name' in data[0], 'Not found name-key in response'
        assert 'banner' in data[0], 'Not found banner-key in response'
        assert 'area' in data[0], 'Not found area-key in response'
        assert data[0]['id'] == junior_detachment.id, 'Incorrect id'
        assert data[0]['name'] == junior_detachment.name, 'Incorrect name'
        assert data[0]['banner'] == f'{settings.MEDIA_URL}{junior_detachment.banner}', (
            'Incorrect banner'
        )
        assert data[0]['area'] == str(junior_detachment.area), 'Incorrect area'

    def test_junior_detachments_commander_with_false_region(
            self, authenticated_client, competition, detachment,
            junior_detachment_2
    ):
        """Получение списка младших отрядов командиром старшего отряда региона 1

        Нет младших отрядов в регионе 1, есть в регионе 2
        """
        response = authenticated_client.get(
            f'{self.competition_url}{competition.id}/junour_detachments/'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200'
        )
        data = response.data
        assert len(data) == 0, 'Incorrect count of junior detachments'

    def test_junior_detachments_commander_with_busy_detachment_in_region(
        self, authenticated_client, competition, detachment, junior_detachment,
        application_competition_start,
    ):
        """Получение списка младших отрядов командиром старшего отряда региона 1

        У одного младшего отряда есть заявка старт на участие в конкурсе.
        """
        response = authenticated_client.get(
            f'{self.competition_url}{competition.id}/junour_detachments/'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200'
        )
        assert len(response.data) == 0, 'Incorrect count of junior detachments'

    def test_junior_detachments_commander_with_busy_and_free_detachment(
            self, authenticated_client_6, competition, detachment,
            junior_detachment, application_competition_tandem,
            detachment_3, junior_detachment_3
    ):
        """Получение списка младших отрядов командиром старшего отряда региона 1

        У одного младшего отряда есть тандем заявка на участие в конкурсе.
        Есть свободный младший отряд в регионе 1
        """
        response = authenticated_client_6.get(
            f'{self.competition_url}{competition.id}/junour_detachments/'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200'
        )
        data = response.data
        assert len(data) == 1, 'Incorrect count of junior detachments'
        assert 'id' in data[0], 'Not found id-key in response'
        assert 'name' in data[0], 'Not found name-key in response'
        assert 'banner' in data[0], 'Not found banner-key in response'
        assert 'area' in data[0], 'Not found area-key in response'
        assert data[0]['id'] == junior_detachment_3.id, 'Incorrect id'
        assert data[0]['name'] == junior_detachment_3.name, 'Incorrect name'
        assert data[0]['banner'] == f'{settings.MEDIA_URL}{junior_detachment_3.banner}', (
            'Incorrect banner'
        )
        assert data[0]['area'] == str(junior_detachment_3.area), 'Incorrect area'

    def test_junior_detachments_commander_junior_detachment(
        self, authenticated_client_3, competition, detachment,
        junior_detachment, junior_detachment_3
    ):
        """Получение списка младших отрядов командиром младшего отряда
        региона 1

        Проверка, что возвращается пустой список (нет доступа), при том,
        что есть свободные младшие и старшие отряды в регионе 1
        """
        response = authenticated_client_3.get(
            f'{self.competition_url}{competition.id}/junour_detachments/'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200'
        )
        data = response.data
        assert len(data) == 0, 'Incorrect count of junior detachments'
        assert data == [], 'Incorrect list of junior detachments'

    def test_applications_get_list_regional_headquarter_commander(
            self, authenticated_client, competition,
            application_competition_start,
            regional_headquarter, junior_detachment
        ):
        """Проверка, что командир рег. штаба может получить список заявок"""
        response = authenticated_client.get(
            f'{self.competition_url}{competition.id}/applications/'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200'
        )
        data = response.data
        assert len(data) == 1, 'Incorrect count of applications'
        assert 'id' in data[0], 'Not found id-key in response'
        assert 'competition' in data[0], (
            'Not found competition-key in response'
        )
        assert 'junior_detachment' in data[0], (
            'Not found junior_detachment-key in response'
        )
        assert 'detachment' in data[0], 'Not found detachment-key in response'
        assert 'is_confirmed_by_junior' in data[0], (
            'Not found is_confirmed_by_junior-key in response'
        )
        assert data[0]['id'] == application_competition_start.id, 'Incorrect id'
        assert data[0]['competition']['id'] == competition.id, 'Incorrect id'
        assert data[0]['competition']['name'] == competition.name, 'Incorrect name'
        assert data[0]['junior_detachment'] == {
            'id': junior_detachment.id,
            'name': junior_detachment.name,
            'banner': f'http://testserver{settings.MEDIA_URL}{junior_detachment.banner}',
            'area': str(junior_detachment.area),
        }
        assert data[0]['detachment'] is None, 'Incorrect detachment'
        assert data[0]['is_confirmed_by_junior'] is False, 'Incorrect status'

    def test_applications_get_list_auth(
            self, authenticated_client, competition,
    ):
        """Проверка, что не региональный командир не может получить список заявок"""
        response = authenticated_client.get(
            f'{self.competition_url}{competition.id}/applications/'
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Response code is not 403'
        )

    def test_create_applications_not_auth(
        self, client, competition
    ):
        """Проверка, что неавторизованный пользователь не может
        получить список заявок"""
        response = client.get(
            f'{self.competition_url}{competition.id}/applications/'
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Response code is not 401'
        )

    def test_create_applications_auth_tandem(
        self, authenticated_client, competition, junior_detachment
    ):
        """Проверка, что не командир не может подать заявку тандем"""
        response = authenticated_client.post(
            f'{self.competition_url}{competition.id}/applications/',
            {'junior_detachment': junior_detachment.id}
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Response code is not 400'
        )

    def test_create_applications_auth_start(
        self, authenticated_client, competition
    ):
        """Проверка, что не командир не может подать заявку старт"""
        response = authenticated_client.post(
            f'{self.competition_url}{competition.id}/applications/',
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Response code is not 400'
        )

    def test_create_applications_commander(
            self, authenticated_client, competition, detachment,
            junior_detachment
    ):
        """Проверка, что командир старшего отряда может подать
        тандем заявку с свободным младшим отрядом
        """
        response = authenticated_client.post(
            f'{self.competition_url}{competition.id}/applications/',
            {'junior_detachment': junior_detachment.id}
        )
        assert response.status_code == HTTPStatus.CREATED, (
            'Response code is not 201'
        )

    def test_create_applications_junior_commander(
            self, authenticated_client_3, competition, junior_detachment
    ):
        """Проверка, что командир младшего отряда может подать старт заявку"""
        response = authenticated_client_3.post(
            f'{self.competition_url}{competition.id}/applications/',
        )
        assert response.status_code == HTTPStatus.CREATED, (
            'Response code is not 201'
        )

    def test_create_applications_start_commander(
            self, authenticated_client, competition, detachment
    ):
        """Проверка, что командир старшего отряда не может подать старт заявку"""
        response = authenticated_client.post(
            f'{self.competition_url}{competition.id}/applications/',
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Response code is not 400'
        )
    
    def test_create_applications_busy_detachment(
        self, authenticated_client_3, competition, junior_detachment,
        application_competition_start
    ):
        """Проверка, что занятой отряд не может подать еще одну заявку"""
        response = authenticated_client_3.post(
            f'{self.competition_url}{competition.id}/applications/',
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Response code is not 400'
        )

    def test_create_applications_busy_detachment_tandem(
        self, authenticated_client, competition, detachment,
        application_competition_tandem, junior_detachment_3
    ):
        """Проверка, что занятой старший отряд не может подать
        заявку с свободным младшим отрядом"""
        response = authenticated_client.post(
            f'{self.competition_url}{competition.id}/applications/',
            {'junior_detachment': junior_detachment_3.id}
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Response code is not 400'
        )

    def test_create_applications_detachment_tandem_with_busy_junior(
            self, authenticated_client, competition,
            application_competition_start,
            junior_detachment
    ):
        """Проверка, что свободный старший отряд не может подать
        в заявку занятой младший отряд"""
        response = authenticated_client.post(
            f'{self.competition_url}{competition.id}/applications/',
            {'junior_detachment': junior_detachment.id}
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Response code is not 400'
        )

    def test_download_regulation_file_auth(
        self, authenticated_client, competition
    ):
        """Проверка, что положение конкурса можно скачать
        авторизованному пользователю"""
        response = authenticated_client.get(
            f'{self.competition_url}download_regulation_file/'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200'
        )
        assert (response.get('Content-Disposition') ==
                'attachment; filename="Regulation_on_the_best_LSO_2024.pdf"')

    def test_download_regulation_file_not_auth(
        self, client, competition
    ):
        """Проверка, что положение конкурса можно скачать
        не авторизованному пользователю"""
        response = client.get(
            f'{self.competition_url}download_regulation_file/'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200'
        )
        assert (response.get('Content-Disposition') ==
                'attachment; filename="Regulation_on_the_best_LSO_2024.pdf"')

    def test_applications_all_auth(
        self, authenticated_client, competition, application_competition_start,
        junior_detachment
    ):
        """Проверка, что все заявки на конкурс можно просмотреть
        авторизованному пользователю"""
        response = authenticated_client.get(
            f'{self.competition_url}{competition.id}/applications/all/'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200'
        )
        data = response.data
        # assert type(data) == list
        assert len(data) == 1
        assert data[0]['id'] == application_competition_start.id
        assert len(data) == 1, 'Incorrect count of applications'
        assert 'id' in data[0], 'Not found id-key in response'
        assert 'competition' in data[0], (
            'Not found competition-key in response'
        )
        assert 'junior_detachment' in data[0], (
            'Not found junior_detachment-key in response'
        )
        assert 'detachment' in data[0], 'Not found detachment-key in response'
        assert 'is_confirmed_by_junior' in data[0], (
            'Not found is_confirmed_by_junior-key in response'
        )
        assert data[0]['id'] == application_competition_start.id, 'Incorrect id'
        assert data[0]['competition']['id'] == competition.id, 'Incorrect id'
        assert data[0]['competition']['name'] == competition.name, 'Incorrect name'
        assert data[0]['junior_detachment'] == {
            'id': junior_detachment.id,
            'name': junior_detachment.name,
            'banner': f'http://testserver{settings.MEDIA_URL}{junior_detachment.banner}',
            'area': str(junior_detachment.area),
        }
        assert data[0]['detachment'] is None, 'Incorrect detachment'
        assert data[0]['is_confirmed_by_junior'] is False, 'Incorrect status'

    def test_applications_all_not_auth(
        self, client, competition, application_competition_tandem,
        junior_detachment, detachment
    ):
        """Проверка, что все заявки на конкурс можно просмотреть
        не авторизованному пользователю"""
        response = client.get(
            f'{self.competition_url}{competition.id}/applications/all/'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200'
        )
        data = response.data
        assert len(data) == 1, 'Incorrect count of applications'
        assert 'id' in data[0], 'Not found id-key in response'
        assert 'competition' in data[0], (
            'Not found competition-key in response'
        )
        assert 'junior_detachment' in data[0], (
            'Not found junior_detachment-key in response'
        )
        assert 'detachment' in data[0], 'Not found detachment-key in response'
        assert 'is_confirmed_by_junior' in data[0], (
            'Not found is_confirmed_by_junior-key in response'
        )
        assert data[0]['id'] == application_competition_tandem.id, 'Incorrect id'
        assert data[0]['competition']['id'] == competition.id, 'Incorrect id'
        assert data[0]['competition']['name'] == competition.name, 'Incorrect name'
        assert data[0]['junior_detachment'] == {
            'id': junior_detachment.id,
            'name': junior_detachment.name,
            'banner': f'http://testserver{settings.MEDIA_URL}{junior_detachment.banner}',
            'area': str(junior_detachment.area),
        }
        assert data[0]['detachment'] == {
            'id': detachment.id,
            'name': detachment.name,
            'banner': f'http://testserver{settings.MEDIA_URL}{detachment.banner}',
            'area': str(detachment.area),
        }
        assert data[0]['is_confirmed_by_junior'] is False, 'Incorrect status'

    def test_applications_me_with_applications(
            self, authenticated_client, competition,
            application_competition_tandem, application_competition_start_2,
            junior_detachment, detachment
    ):
        """Проверка, что командир старшего отряда может получить заявку,
        если его отряд в заявке

        Есть еще не подтвержденные заявки, которые ему не отобразятся.
        """
        response = authenticated_client.get(
            f'{self.competition_url}{competition.id}/applications/me/'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200'
        )
        data = response.data
        assert isinstance(data, dict), 'Incorrect type of response'
        assert 'id' in data, 'Not found id-key in response'
        assert 'competition' in data, (
            'Not found competition-key in response'
        )
        assert 'junior_detachment' in data, (
            'Not found junior_detachment-key in response'
        )
        assert 'detachment' in data, 'Not found detachment-key in response'
        assert 'is_confirmed_by_junior' in data, (
            'Not found is_confirmed_by_junior-key in response'
        )
        assert data['id'] == application_competition_tandem.id, 'Incorrect id'
        assert data['competition']['id'] == competition.id, 'Incorrect id'
        assert data['competition']['name'] == competition.name, 'Incorrect name'
        assert data['junior_detachment'] == {
            'id': junior_detachment.id,
            'name': junior_detachment.name,
            'banner': f'http://testserver{settings.MEDIA_URL}{junior_detachment.banner}',
            'area': str(junior_detachment.area),
        }
        assert data['detachment'] == {
            'id': detachment.id,
            'name': detachment.name,
            'banner': f'http://testserver{settings.MEDIA_URL}{detachment.banner}',
            'area': str(detachment.area),
        }
        assert data['is_confirmed_by_junior'] is False, 'Incorrect status'

    def test_applications_me_without_applications(
            self, authenticated_client, competition,
            application_competition_start_2
    ):
        """Проверка, что если у пользователя нет заявки на конкурс,
        то ответ будет 404"""
        response = authenticated_client.get(
            f'{self.competition_url}{competition.id}/applications/me/'
        )
        assert response.status_code == HTTPStatus.NOT_FOUND, (
            'Response code is not 404'
        )

    def test_applications_me_without_applications_commander(
            self, authenticated_client, competition, detachment,
            application_competition_start_2
    ):
        """Проверка, что если у пользователя-коммандира отряда нет заявки на конкурс,
        то ответ будет 404"""
        response = authenticated_client.get(
            f'{self.competition_url}{competition.id}/applications/me/'
        )
        assert response.status_code == HTTPStatus.NOT_FOUND, (
            'Response code is not 404'
        )
    
    def test_applications_me_not_auth(self, client, competition):
        """Проверка, что нельзя получить заявки неавторизованному пользователю"""
        response = client.get(
            f'{self.competition_url}{competition.id}/applications/me/'
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Response code is not 401'
        )

    def test_applications_id_reg_commander(
            self, authenticated_client, competition,
            application_competition_start_2, regional_headquarter,
            junior_detachment_3
    ):
        """Проверка, что командир регионального штаба может получить
        заявку по id"""
        response = authenticated_client.get(
            f'{self.competition_url}{competition.id}/applications/'
            f'{application_competition_start_2.id}/'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200'
        )
        data = response.data
        assert isinstance(data, dict), 'Incorrect type of response'
        assert 'id' in data, 'Not found id-key in response'
        assert 'competition' in data, (
            'Not found competition-key in response'
        )
        assert 'junior_detachment' in data, (
            'Not found junior_detachment-key in response'
        )
        assert 'detachment' in data, 'Not found detachment-key in response'
        assert 'is_confirmed_by_junior' in data, (
            'Not found is_confirmed_by_junior-key in response'
        )
        assert data['id'] == application_competition_start_2.id, 'Incorrect id'
        assert data['competition']['id'] == competition.id, 'Incorrect id'
        assert data['competition']['name'] == competition.name, 'Incorrect name'
        assert data['junior_detachment'] == {
            'id': junior_detachment_3.id,
            'name': junior_detachment_3.name,
            'banner': f'http://testserver{settings.MEDIA_URL}{junior_detachment_3.banner}',
            'area': str(junior_detachment_3.area),
        }
        assert data['detachment'] is None, 'Incorrect status'

    # def test_applications_id_auth(
    #         self, authenticated_client, competition,
    #         application_competition_start
    # ):
    #     """Проверка, что простой пользователь не может получить заявку по id"""
    #     response = authenticated_client.get(
    #         f'{self.competition_url}{competition.id}/applications/'
    #         f'{application_competition_start.id}/'
    #     )
    #     assert response.status_code == HTTPStatus.FORBIDDEN, (
    #         'Response code is not 403'
    #     )

    def test_applications_id_not_auth(
            self, client, competition, application_competition_tandem
    ):
        """Проверка, что нельзя получить заявку неавторизованному пользователю"""
        response = client.get(
            f'{self.competition_url}{competition.id}/applications/'
            f'{application_competition_tandem.id}/'
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Response code is not 401'
        )

    def test_applications_id_put_junior_detachment(
            self, authenticated_client_3, competition, junior_detachment,
            application_competition_start
    ):
        """Проверка, что командир младшего отряда может изменить поле
        is_confirmed_by_junior"""
        response = authenticated_client_3.put(
            f'{self.competition_url}{competition.id}/applications/'
            f'{application_competition_start.id}/',
            {'is_confirmed_by_junior': True}
        )
        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200'
        )
        assert response.data['is_confirmed_by_junior'] is True, (
            'Incorrect is_confirmed_by_junior'
        )

    def test_applications_id_put_detachment(
            self, authenticated_client, competition, junior_detachment,
            application_competition_tandem, detachment
    ):
        """Проверка, что командир старшего отряда не может изменить поле
        is_confirmed_by_junior"""
        response = authenticated_client.put(
            f'{self.competition_url}{competition.id}/applications/'
            f'{application_competition_tandem.id}/',
            {'is_confirmed_by_junior': True}
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Response code is not 403'
        )

    def test_applications_id_put_auth(
            self, authenticated_client, competition,
            application_competition_tandem
    ):
        """Проверка, что простой пользователь не может изменить поле
        is_confirmed_by_junior"""
        response = authenticated_client.put(
            f'{self.competition_url}{competition.id}/applications/'
            f'{application_competition_tandem.id}/',
            {'is_confirmed_by_junior': True}
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Response code is not 403'
        )

    def test_applications_id_put_not_auth(
            self, client, competition,
            application_competition_tandem
    ):
        """Проверка, что не авторизованный пользователь не может изменить поле
        is_confirmed_by_junior"""
        response = client.put(
            f'{self.competition_url}{competition.id}/applications/'
            f'{application_competition_tandem.id}/',
            {'is_confirmed_by_junior': True}
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Response code is not 401'
        )