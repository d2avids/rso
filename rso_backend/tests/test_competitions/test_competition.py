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
        """Получение списка младших отрядов командиром отряда региона 1

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

    # def test_junior_detachments_commander_with_busy_detachment(
    #         self, authenticated_client, competition, detachment,
    #         junior_detachment, application     
    # ):
    #     """Получение списка младших отрядов командиром отряда региона 1

    #     У младшего отряда есть заявка на участие в конкурсе
        # TODO: Добавить второй старший и младший отряд с таким же регионом как и у отрядов в заявке
    #     """
