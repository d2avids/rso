import pytest

from http import HTTPStatus,

from tests.conftest import authenticated_client_2, free_authenticated_client, user_6, client

@pytest.mark.django_db
def test_get_detachments_commander(client, detachment, authenticated_client):
    """Получение списка отрядов юзером-командиром одного из отрядов."""

    response = client.get('/api/v1/detachments/')

    assert response.status_code == HTTPStatus.OK, 'Response code is not 200'


@pytest.mark.django_db
def test_get_detachment_members_commander(client, detachment, authenticated_client):
    """Получение списка участников отряда юзером-командиром."""

    response = client.get(f'/api/v1/detachments/{detachment.pk}/members/')

    assert response.status_code == HTTPStatus.OK, 'Response code is not 200'


@pytest.mark.django_db
def test_get_detachments_commander_anonymous(client, detachment):
    """Получение списка отрядов юзером-анонимом."""

    response = client.get('/api/v1/detachments/')

    assert response.status_code == HTTPStatus.OK, 'Response code is not 200'


@pytest.mark.django_db
def test_get_detachment_members_anonymous(client, detachment):
    """Получение списка участников отряда юзером-анонимом."""

    response = client.get(f'/api/v1/detachments/{detachment.pk}/members/')

    assert response.status_code == HTTPStatus.OK, 'Response code is not 200'


@pytest.mark.django_db
def test_delete_detachment_commander(client, detachment_2, authenticated_client_2):
    """Удаление отряда юзером-командиром."""

    response = client.delete(f'/api/v1/detachments/{detachment_2.pk}/')

    assert response.status_code == HTTPStatus.NO_CONTENT, (
        'Response code is not 204'
    )


@pytest.mark.django_db
def test_delete_detachment_anonymous(client, detachment):
    """Удаление отряда юзером-анонимом."""

    response = client.delete(f'/api/v1/detachments/{detachment.pk}/')

    assert response.status_code == HTTPStatus.UNAUTHORIZED, (
        'Response code is not 401'
    )


class TestDetachmentsPositions:
    payload = {
        'user': user_6,
        'position': 1,
        'is_trusted': True
    }
    users_dict = {
        'Анонимный юзер': client,
        'Неверифицированный юзер': free_authenticated_client,
        'Верифицированный юзер': 'создать',
        'Командир текущего отряда': authenticated_client_2,
        'Командир другого отряда, свой ОбрШ': 'создать/найти',
        'Командир другого отряда, не свой ОбрШ': 'создать/найти',
        'Командир своего ОбрШ': 'создать/найти',
        'Командир другой ОбрШ': 'создать/найти',
        'Командир своего МШ': 'создать/найти',
        'Командир другой МШ': 'создать/найти',
        'Командир своего РШ': 'создать/найти',
        'Командир другой РШ': 'создать/найти',
        'Командир своего ОкрШ': 'создать/найти',
        'Командир другой ОкрШ': 'создать/найти',
        'Командир ЦШ': 'создать/найти',
    }

    @pytest.mark.django_db
    def test_get_detachment_memberships_commander(
        self, client, detachment_2, authenticated_client_2,
        detachment_positions
    ):
        """Получение списка участников отряда юзером-командиром."""

        response = authenticated_client_2.get(
            f'/api/v1/detachments/{detachment_2.pk}'
            f'/members/{detachment_positions.pk}/'
        )

        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200'
        )


    @pytest.mark.django_db
    def test_get_detachment_memberships_anonymous(
        self, client, detachment_2, detachment_positions
    ):
        """Получение списка участников отряда юзером-анонимом."""

        response = client.get(
            f'/api/v1/detachments/{detachment_2.pk}'
            f'/members/{detachment_positions.pk}/'
        )

        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200'
        )


    @pytest.mark.django_db
    def test_up_del_detachment_memberships(
        self, client, user_6, detachment_2, authenticated_client_2,
        detachment_positions, free_authenticated_client
    ):
        """Изменение позиции/должности участника отряда юзером-командиром."""

        response = free_authenticated_client.patch(
            f'/api/v1/detachments/{detachment_2.pk}'
            f'/members/{detachment_positions.pk}/',
            self.payload
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Response code is not 403'
        )
        response = authenticated_client_2.patch(
            f'/api/v1/detachments/{detachment_2.pk}'
            f'/members/{detachment_positions.pk}/',
            self.payload
        )

        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200'
        )
        response = authenticated_client_2.patch(
            f'/api/v1/detachments/{detachment_2.pk}/members/2/',
           self.payload
        )
        assert response.status_code == HTTPStatus.NOT_FOUND, (
            'Response code is not 404'
        )
