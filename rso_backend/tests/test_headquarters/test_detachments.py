import pytest

from http import HTTPStatus

from tests.conftest import user_uncommander_untrusted


@pytest.mark.django_db
def test_get_detachments_commander(authenticated_det_com_1a, detachment_1a, detachment_commander_1a):
    """Получение списка отрядов юзером-командиром одного из отрядов."""

    response = authenticated_det_com_1a.get('/api/v1/detachments/')

    assert response.status_code == HTTPStatus.OK, 'Response code is not 200'


@pytest.mark.django_db
def test_get_detachment_members_commander(
    client, detachment, authenticated_client
):
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
def test_delete_detachment_commander(
    client, detachment_2, authenticated_client_2
):
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
        'user': user_uncommander_untrusted,
        'position': 1,
        'is_trusted': True
    }
    # authenticated_client_7 = authenticated_client_7
    # authenticated_client_2 = authenticated_client_2
    # authenticated_client_9 = authenticated_client_9
    # authenticated_client = authenticated_client
    # educational_headquarter_2 = educational_headquarter_2
    # educational_headquarter = educational_headquarter
    # local_headquarter_2 = local_headquarter_2
    # local_headquarter = local_headquarter
    # regional_headquarter_2 = regional_headquarter_2
    # regional_headquarter = regional_headquarter
    # district_headquarter_2 = district_headquarter_2
    # district_headquarter = district_headquarter
    # central_headquarter_2 = central_headquarter_2
    # # admin_client = admin_client

    # roles_dict = {
    #     client: 'Анонимный юзер',
    #     authenticated_client_7: 'Невериф-й юзер некомандир, недоверенный',
    #     authenticated_client_2: 'Командир текущего отряда',
    #     authenticated_client_9: 'Командир другого отряда, свой ОбрШ',
    #     authenticated_client: 'Командир другого отряда, не свой ОбрШ',
    #     educational_headquarter_2: 'Командир своего ОбрШ',
    #     educational_headquarter: 'Командир другой ОбрШ',
    #     local_headquarter_2: 'Командир своего МШ',
    #     local_headquarter: 'Командир другой МШ',
    #     regional_headquarter_2: 'Командир своего РШ',
    #     regional_headquarter: 'Командир другой РШ',
    #     district_headquarter_2: 'Командир своего ОкрШ',
    #     district_headquarter: 'Командир другой ОкрШ',
    #     central_headquarter_2: 'Командир ЦШ',
    #     admin_client: 'Админ'
    # }

    @pytest.mark.parametrize(
            'client_name',
            [
              'client',
              'authenticated_client_7',
              'authenticated_client_2',
              'authenticated_client_9',
              'authenticated_client',
              'admin_client'
            ]
    )
    @pytest.mark.django_db
    def test_get_detachment_memberships(
        self, client, detachment_2, client_name,
        detachment_positions, request, educational_headquarter_2,
        educational_headquarter, local_headquarter_2, local_headquarter,
        regional_headquarter_2, regional_headquarter, district_headquarter_2,
        district_headquarter, central_headquarter_2
    ):
        """Получение списка участников отряда юзерами с разными ролями."""

        test_client = request.getfixturevalue(client_name)
        response = test_client.get(
            f'/api/v1/detachments/{detachment_2.pk}'
            f'/members/{detachment_positions.pk}/'
        )

        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200.'
        )

    # @pytest.mark.django_db
    # def test_get_detachment_memberships_anonymous(
    #     self, client, detachment_2, detachment_positions
    # ):
    #     """Получение списка участников отряда юзером-анонимом."""

    #     response = client.get(
    #         f'/api/v1/detachments/{detachment_2.pk}'
    #         f'/members/{detachment_positions.pk}/'
    #     )

    #     assert response.status_code == HTTPStatus.OK, (
    #         'Response code is not 200'
    #     )

    @pytest.mark.django_db
    def test_up_del_detachment_memberships(
        self, client, user_uncommander_untrusted, detachment_2,
        authenticated_client_2, detachment_positions, free_authenticated_client
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
