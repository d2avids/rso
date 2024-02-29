from http import HTTPStatus

import pytest

from tests.test_headquarters import conftest

@pytest.mark.django_db
def test_rsouser_filters(
        authenticated_client, district_headquarter,
        regional_headquarter, local_headquarter, educational_headquarter,
        detachment, user
):
    """Проверка работы фильтров для эндпоинта списка юзеров.

    Каждое поле проверяется по отдельности,
    затем сразу все в одном запросе.
    """

    response = authenticated_client.get(
        f'/api/v1/rsousers?search={user.username}'
    )
    assert response.status_code == HTTPStatus.OK, (
        'Response status code is not 200'
    )
    assert response.data[0]['username'] == user.username
    headquarters = [
        district_headquarter, regional_headquarter, local_headquarter,
        educational_headquarter, detachment
    ]
    for headquarter in headquarters:
        response = authenticated_client.get(
            f'/api/v1/rsousers?{headquarter}__name={headquarter.name}'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Response status code is not 200'
        )
    response = authenticated_client.get(
        f'/api/v1/rsousers?gender=male'
    )
    assert response.status_code == HTTPStatus.OK, (
        'Response status code is not 200'
    )
    response = authenticated_client.get(
        f'/api/v1/rsousers?is_verified=False'
    )
    assert response.status_code == HTTPStatus.OK, (
        'Response status code is not 200'
    )
    response = authenticated_client.get(
        f'/api/v1/rsousers?membership_fee=False'
    )
    assert response.status_code == HTTPStatus.OK, (
        'Response status code is not 200'
    )
    response = authenticated_client.get(
        f'/api/v1/rsousers?date_of_birth=2020-01-01'
    )
    assert response.status_code == HTTPStatus.OK, (
        'Response status code is not 200'
    )
    response = authenticated_client.get(
        f'/api/v1/rsousers?region=1'
    )
    assert response.status_code == HTTPStatus.OK, (
        'Response status code is not 200'
    )
    response = authenticated_client.get(
        '/api/v1/rsousers?'
        f'search={user.username}&'
        f'district_headquarter__name={district_headquarter.name}&'
        f'regional_headquarter__name={regional_headquarter.name}&'
        f'local_headquarter__name={local_headquarter.name}&'
        f'educational_headquarter__name={educational_headquarter.name}&'
        f'detachment__name={detachment.name}&'
        'gender=male&'
        'is_verified=False&'
        'membership_fee=False&'
        'date_of_birth=2020-01-01&'
        'region=1'
    )
    assert response.status_code == HTTPStatus.OK, (
        'Response status code is not 200'
    )


# @pytest.mark.django_db
# class TestRSOUsers:

    # @pytest.mark.parametrize(
    #     'client_name', 'expected_status',
    #     [
    #         ('client', HTTPStatus.UNAUTHORIZED),
    #         ('authenticated_unverified', HTTPStatus.FORBIDDEN),
    #         ('authenticated_user_with_position_in_detachment', HTTPStatus.FORBIDDEN),
    #         ('authenticated_user_with_position_in_edu_hq', HTTPStatus.FORBIDDEN),
    #         ('authenticated_user_with_position_in_local_hq', HTTPStatus.FORBIDDEN),
    #         ('authenticated_user_with_position_in_regional_hq', HTTPStatus.FORBIDDEN),
    #         ('authenticated_user_with_position_in_distr_hq', HTTPStatus.FORBIDDEN),
    #         ('authenticated_user_with_position_in_centr_hq', HTTPStatus.FORBIDDEN),
    #         ('authenticated_trusted_in_detachment', HTTPStatus.FORBIDDEN),
    #         ('authenticated_trusted_in_edu_hq', HTTPStatus.FORBIDDEN),
    #         ('authenticated_trusted_in_local_hq', HTTPStatus.FORBIDDEN),
    #         ('authenticated_trusted_in_regional_hq', HTTPStatus.FORBIDDEN),
    #         ('authenticated_trusted_in_district_hq', HTTPStatus.FORBIDDEN),
    #         ('authenticated_trusted_in_centr_hq', HTTPStatus.FORBIDDEN),
    #         ('authenticated_centr_commander', HTTPStatus.FORBIDDEN),
    #         ('authenticated_distr_commander_1a', HTTPStatus.FORBIDDEN),
    #         ('authenticated_distr_commander_1b', HTTPStatus.FORBIDDEN),
    #         ('authenticated_regional_commander_1a', HTTPStatus.OK),
    #         ('authenticated_regional_commander_1b', HTTPStatus.FORBIDDEN),
    #         ('authenticated_local_commander_1a', HTTPStatus.FORBIDDEN),
    #         ('authenticated_local_commander_1b', HTTPStatus.FORBIDDEN),
    #         ('authenticated_edu_commander_1a', HTTPStatus.FORBIDDEN),
    #         ('authenticated_edu_commander_1b', HTTPStatus.FORBIDDEN),
    #         ('authenticated_det_com_1b', HTTPStatus.FORBIDDEN),
    #         ('admin_client', HTTPStatus.FORBIDDEN),
    #         ('authenticated_detachment_commander_1a', HTTPStatus.OK),
    #     ]
    # )
    # def test_retrieve_user_object(
    #         self, client, central_hq, district_hq_1a, district_hq_1b,
    #         regional_hq_1a, regional_hq_1b, local_hq_1a, local_hq_1b,
    #         edu_hq_1a, edu_hq_1b, detachment_1a, detachment_1b,
    #         client_name, request, detachment_positions,
    #         user_with_position_in_detachment, user_with_position_in_edu_hq,
    #         user_with_position_in_local_hq, user_with_position_in_regional_hq,
    #         user_with_position_in_district_hq, user_with_position_in_centr_hq,
    #         user_trusted_in_detachment, user_trusted_in_edu_hq,
    #         user_trusted_in_local_hq, user_trusted_in_regional_hq,
    #         user_trusted_in_district_hq, user_trusted_in_centr_hq,
    #         detachment_commander_1a, detachment_commander_1b,
    #         edu_commander_1a, edu_commander_1b, local_commander_1a,
    #         local_commander_1b, regional_commander_1a, regional_commander_1b,
    #         distr_commander_1a, distr_commander_1b, centr_commander,
    #         expected_status
    # ):
    #     """Получение пользователя  по id юзерами с разными ролями."""

    #     test_client = request.getfixturevalue(client_name)
    #     response = test_client.get(
    #         f'/api/v1/rsousers/{user_with_position_in_detachment.pk}/'
    #     )
    #     assert response.status_code == expected_status, (
    #         'Response code is not ' + str(expected_status)
    #     )
