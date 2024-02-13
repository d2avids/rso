import pytest

from http import HTTPStatus


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


# @pytest.mark.django_db
# def test_delete_detachment_commander(client, detachment, authenticated_client):
#     """Удаление отряда юзером-командиром."""

#     response = client.delete(f'/api/v1/detachments/{detachment.pk}/')

#     assert response.status_code == HTTPStatus.NO_CONTENT, 'Response code is not 204'


@pytest.mark.django_db
def test_delete_detachment_anonymous(client, detachment):
    """Удаление отряда юзером-анонимом."""

    response = client.delete(f'/api/v1/detachments/{detachment.pk}/')

    assert response.status_code == HTTPStatus.UNAUTHORIZED, 'Response code is not 401'


# @pytest.mark.django_db
# def test_get_detachment_memberships_commander(client, detachment, authenticated_client, detachment_positions):
#     """Получение списка участников отряда юзером-командиром."""

#     response = client.get(f'/api/v1/detachments/{detachment.pk}/members/{detachment_positions.pk}/')

#     print(response.data, 'test_get_detachment_memberships_commander')
#     assert response.status_code == HTTPStatus.OK, 'Response code is not 200'


# @pytest.mark.django_db
# def test_get_detachment_memberships_anonymous(client, detachment, detachment_positions):
#     """Получение списка участников отряда юзером-анонимом."""

#     response = client.get(f'/api/v1/detachments/{detachment.pk}/members/{detachment_positions.pk}/')

#     assert response.status_code == HTTPStatus.OK, 'Response code is not 200'


# @pytest.mark.django_db
# def test_up_del_detachment_memberships(
#     client, user_6, detachment, authenticated_client,
#     detachment_positions, free_authenticated_client
# ):
#     """Изменение позиции/должности участника отряда юзером-командиром."""

#     payload = {
#         'user': user_6,
#         'position': 1,
#         'is_trusted': True
#     }
#     response = free_authenticated_client.patch(
#         f'/api/v1/detachments/{detachment.pk}/members/{detachment_positions.pk}/',
#         payload
#     )
#     assert response.status_code == HTTPStatus.FORBIDDEN, 'Response code is not 403'
#     response = authenticated_client.patch(
#         f'/api/v1/detachments/{detachment.pk}/members/{detachment_positions.pk}/',
#         payload
#     )
#     print(response.data)
#     assert response.status_code == HTTPStatus.OK, 'Response code is not 200'
#     response = authenticated_client.patch(
#         f'/api/v1/detachments/{detachment.pk}/members/2/',
#         payload
#     )
#     assert response.status_code == HTTPStatus.NOT_FOUND, 'Response code is not 404'
