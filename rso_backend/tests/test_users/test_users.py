from http import HTTPStatus

import pytest


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
