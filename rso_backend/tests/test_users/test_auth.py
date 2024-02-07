import pytest

from tests.conftest import USER_FIRST_NAME, USER_LAST_NAME, USERNAME


@pytest.mark.django_db
def test_register_user(client):
    payload = {
        'last_name': 'Peter',
        'first_name': 'Ivanov',
        'username': 'peterivanov',
        'password': 'XksakAZVfl',
        're_password': 'XksakAZVfl'
    }
    response = client.post('/api/v1/register/', payload)
    assert response.status_code == 201, 'Response status code is not 201'
    data = response.data

    assert data.get('last_name') == payload[
        'last_name'
    ], 'Invalid data returned'
    assert data.get('first_name') == payload[
        'first_name'
    ], 'Invalid data returned'
    assert data.get('username') == payload['username'], 'Invalid data returned'
    assert 'region' in data and data.get(
        'region'
    ) is None, 'Invalid data returned'
    assert 'password' not in data, 'Password is shown in the response'


@pytest.mark.django_db
def test_login_user(client, user):
    payload = {
        'username': 'dimka',
        'password': 'Ddmi36VRN'
    }
    response = client.post('/api/v1/token/login/', payload)
    assert response.status_code == 200, 'Response status code is not 200'
    data = response.data

    assert 'auth_token' in data, 'auth_token is missing in the response'


@pytest.mark.django_db
def test_get_me(authenticated_client, region, central_headquarter):
    response = authenticated_client.get('/api/v1/rsousers/me/')
    assert response.status_code == 200, 'Response status code is not 200'
    data = response.data
    assert data.get(
        'is_verified'
    ) is False, 'User should not be verified after registration'
    assert data.get(
        'membership_fee'
    ) is False, 'Membership_fee should be False after registration'
    assert data.get(
        'sent_verification'
    ) is False, 'Sent_verification should be False after registration'
    assert data.get('first_name') == USER_FIRST_NAME, 'Invalid first name'
    assert data.get('last_name') == USER_LAST_NAME, 'Invalid last name'
    assert data.get('username') == USERNAME, 'Invalid username'
    assert 'central_headquarter_id' in data and data.get(
        'central_headquarter_id'
    ) == 1, 'Invalid central headquarter_id'
    assert 'district_headquarter_id' in data and data.get(
        'district_headquarter_id'
    ) is None, 'Invalid district headquarter_id'
    assert 'regional_headquarter_id' in data and data.get(
        'regional_headquarter_id'
    ) is None, 'Invalid regional headquarter_id'
    assert 'local_headquarter_id' in data and data.get(
        'local_headquarter_id'
    ) is None, 'Invalid local headquarter_id'
    assert 'educational_headquarter_id' in data and data.get(
        'educational_headquarter_id'
    ) is None, 'Invalid educational headquarter_id'
    assert 'detachment_id' in data and data.get(
        'detachment_id'
    ) is None, 'Invalid detachment_id'


@pytest.mark.django_db
def test_get_me_anonymous(client, region, central_headquarter):
    response = client.get('/api/v1/rsousers/me/')
    assert response.status_code == 401, 'Response status code is not 401'


@pytest.mark.django_db
def test_get_me_documents(authenticated_client, region, central_headquarter):
    response = authenticated_client.get('/api/v1/rsousers/me/documents/')
    assert response.status_code == 200, 'Response status code is not 200'


@pytest.mark.django_db
def test_get_me_documents_anonymous(client, region, central_headquarter):
    response = client.get('/api/v1/rsousers/me/documents/')
    assert response.status_code == 401, 'Response status code is not 401'


@pytest.mark.django_db
def test_get_me_education(authenticated_client, region, central_headquarter):
    response = authenticated_client.get('/api/v1/rsousers/me/education/')
    assert response.status_code == 200, 'Response status code is not 200'


@pytest.mark.django_db
def test_get_me_education_anonymous(client, region, central_headquarter):
    response = client.get('/api/v1/rsousers/me/education/')
    assert response.status_code == 401, 'Response status code is not 401'


@pytest.mark.django_db
def test_get_me_foreign_documents(authenticated_client, region,
                                  central_headquarter):
    response = authenticated_client.get(
        '/api/v1/rsousers/me/foreign_documents/')
    assert response.status_code == 200, 'Response status code is not 200'


@pytest.mark.django_db
def test_get_me_foreign_documents_anonymous(client, region,
                                            central_headquarter):
    response = client.get('/api/v1/rsousers/me/foreign_documents/')
    assert response.status_code == 401, 'Response status code is not 401'


@pytest.mark.django_db
def test_get_me_media(authenticated_client, region, central_headquarter):
    response = authenticated_client.get('/api/v1/rsousers/me/media/')
    assert response.status_code == 200, 'Response status code is not 200'


@pytest.mark.django_db
def test_get_me_media_anonymous(client, region, central_headquarter):
    response = client.get('/api/v1/rsousers/me/media/')
    assert response.status_code == 401, 'Response status code is not 401'


@pytest.mark.django_db
def test_get_me_professional_education(authenticated_client, region,
                                       central_headquarter):
    response = authenticated_client.get(
        '/api/v1/rsousers/me/professional_education/')
    assert response.status_code == 404, 'Response status code is not 404'
    assert 'detail' in response.data, 'No detail key in response data'


@pytest.mark.django_db
def test_get_me_professional_education_anonymous(client, region,
                                                 central_headquarter):
    response = client.get('/api/v1/rsousers/me/professional_education/')
    assert response.status_code == 404, 'Response status code is not 404'
    assert 'detail' in response.data, 'No detail key in response data'


@pytest.mark.django_db
def test_get_me_privacy(authenticated_client, region, central_headquarter):
    response = authenticated_client.get('/api/v1/rsousers/me/privacy/')
    assert response.status_code == 200, 'Response status code is not 200'


@pytest.mark.django_db
def test_get_me_privacy_anonymous(client, region, central_headquarter):
    response = client.get('/api/v1/rsousers/me/privacy/')
    assert response.status_code == 401, 'Response status code is not 401'


@pytest.mark.django_db
def test_get_me_parent(authenticated_client, region, central_headquarter):
    response = authenticated_client.get('/api/v1/rsousers/me/parent/')
    assert response.status_code == 200, 'Response status code is not 200'


@pytest.mark.django_db
def test_get_me_parent_anonymous(client, region, central_headquarter):
    response = client.get('/api/v1/rsousers/me/parent/')
    assert response.status_code == 401, 'Response status code is not 401'


@pytest.mark.django_db
def test_get_me_region(authenticated_client, region, central_headquarter):
    response = authenticated_client.get('/api/v1/rsousers/me/region/')
    assert response.status_code == 200, 'Response status code is not 200'


@pytest.mark.django_db
def test_get_me_region_anonymous(client, region, central_headquarter):
    response = client.get('/api/v1/rsousers/me/region/')
    assert response.status_code == 401, 'Response status code is not 401'


@pytest.mark.django_db
def test_get_me_commander(authenticated_client, region, central_headquarter):
    response = authenticated_client.get('/api/v1/rsousers/me_commander/')
    assert response.status_code == 200, 'Response status code is not 200'


@pytest.mark.django_db
def test_get_me_commander_anonymous(client, region, central_headquarter):
    response = client.get('/api/v1/rsousers/me_commander/')
    assert response.status_code == 401, 'Response status code is not 401'


@pytest.mark.django_db
def test_get_me_trusted(authenticated_client, region, central_headquarter):
    response = authenticated_client.get('/api/v1/rsousers/me_trusted/')
    assert response.status_code == 200, 'Response status code is not 200'


@pytest.mark.django_db
def test_get_me_trusted_anonymous(client, region, central_headquarter):
    response = client.get('/api/v1/rsousers/me_trusted/')
    assert response.status_code == 401, 'Response status code is not 401'


@pytest.mark.django_db
def test_get_me_positions(authenticated_client, region, central_headquarter):
    response = authenticated_client.get('/api/v1/rsousers/me_positions/')
    assert response.status_code == 200, 'Response status code is not 200'


@pytest.mark.django_db
def test_get_me_positions_anonymous(client, region, central_headquarter):
    response = client.get('/api/v1/rsousers/me_positions/')
    assert response.status_code == 401, 'Response status code is not 401'


@pytest.mark.django_db
def test_logout_user(authenticated_client):
    response = authenticated_client.post('/api/v1/token/logout/')
    assert response.status_code == 204, 'Response status code is not 204'
