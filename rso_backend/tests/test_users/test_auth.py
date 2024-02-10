from http import HTTPStatus

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
def test_get_me(authenticated_client, central_headquarter):
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
def test_get_me_anonymous(client, central_headquarter):
    response = client.get('/api/v1/rsousers/me/')
    assert response.status_code == 401, 'Response status code is not 401'


@pytest.mark.django_db
def test_get_me_documents(authenticated_client, central_headquarter):
    response = authenticated_client.get('/api/v1/rsousers/me/documents/')
    assert response.status_code == 200, 'Response status code is not 200'


@pytest.mark.django_db
def test_get_me_documents_anonymous(client, central_headquarter):
    response = client.get('/api/v1/rsousers/me/documents/')
    assert response.status_code == 401, 'Response status code is not 401'


@pytest.mark.django_db
def test_get_me_statement(authenticated_client, central_headquarter):
    response = authenticated_client.get('/api/v1/rsousers/me/statement/')
    assert response.status_code == 200, 'Response status code is not 200'


@pytest.mark.django_db
def test_get_me_statement_anonymous(client, central_headquarter):
    response = client.get('/api/v1/rsousers/me/statement/')
    assert response.status_code == 401, 'Response status code is not 401'


@pytest.mark.django_db
def test_get_me_education(authenticated_client, central_headquarter):
    response = authenticated_client.get('/api/v1/rsousers/me/education/')
    assert response.status_code == 200, 'Response status code is not 200'


@pytest.mark.django_db
def test_get_me_education_anonymous(client, central_headquarter):
    response = client.get('/api/v1/rsousers/me/education/')
    assert response.status_code == 401, 'Response status code is not 401'


@pytest.mark.django_db
def test_get_me_foreign_documents(authenticated_client,
                                  central_headquarter):
    response = authenticated_client.get(
        '/api/v1/rsousers/me/foreign_documents/')
    assert response.status_code == 200, 'Response status code is not 200'


@pytest.mark.django_db
def test_get_me_foreign_documents_anonymous(client,
                                            central_headquarter):
    response = client.get('/api/v1/rsousers/me/foreign_documents/')
    assert response.status_code == 401, 'Response status code is not 401'


@pytest.mark.django_db
def test_get_me_media(authenticated_client, central_headquarter):
    response = authenticated_client.get('/api/v1/rsousers/me/media/')
    assert response.status_code == 200, 'Response status code is not 200'


@pytest.mark.django_db
def test_get_me_media_anonymous(client, central_headquarter):
    response = client.get('/api/v1/rsousers/me/media/')
    assert response.status_code == 401, 'Response status code is not 401'


@pytest.mark.django_db
def test_get_me_professional_education(
    authenticated_client, central_headquarter, educational_institution
):
    response = authenticated_client.get(
        '/api/v1/rsousers/me/professional_education/')
    assert response.status_code == HTTPStatus.NOT_FOUND, (
        'Response status code is not 404'
    )
    assert 'detail' in response.data, 'No detail key in response data'

    payload = {
        'study_institution': educational_institution.pk,
        'years_of_study': '2010-2015',
        'exam_score': 'string',
        'qualification': 'string'
    }
    print(payload)
    response = authenticated_client.post(
        '/api/v1/rsousers/me/professional_education/', payload, format="json"
    )
    assert response.status_code == HTTPStatus.CREATED, (
        'Response status code is not 201'
    )
    response = authenticated_client.get(
        '/api/v1/rsousers/me/professional_education/'
    )
    assert response.status_code == HTTPStatus.OK, (
        'Response status code is not 200'
    )
    response = authenticated_client.delete(
        '/api/v1/rsousers/me/professional_education/1/'
    )
    assert response.status_code == HTTPStatus.NO_CONTENT, (
        'Response status code is not 204'
    )
    payload = {
        'study_institution': educational_institution.pk,
        'years_of_study': '5',
        'exam_score': 'string',
        'qualification': 'string'
    }
    response = authenticated_client.post(
        '/api/v1/rsousers/me/professional_education/', payload
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST, (
        'Response status code is not 400'
    )

@pytest.mark.django_db
def test_get_me_five_professional_educations(
    authenticated_client, central_headquarter, educational_institution
):
    payloads = [
            ('2010-2015', 'well done', 'professional'),
            ('2015-2016', 'medium rare', 'newby'),
            ('2017-2018', 'nice', 'welder'),
            ('2019-2020', 'good', 'doctor'),
            ('2021-2022', 'excellent', 'master'),
            ('2022-2023', 'unbelivable', 'wizard'),
        ]
    for years_of_study, exam_score, qualification in payloads:
        payload = {
            'study_institution': educational_institution.pk,
            'years_of_study': years_of_study,
            'exam_score': exam_score,
            'qualification': qualification
        }
        response = authenticated_client.post(
            '/api/v1/rsousers/me/professional_education/', payload, format="json"
        )
    response = authenticated_client.get(
        '/api/v1/rsousers/me/professional_education/'
    )
    assert len(response.data['users_prof_educations']) == 5, (
        'Wrong length of response data, expected 5'
    )



@pytest.mark.django_db
def test_get_me_professional_education_anonymous(client,
                                                 central_headquarter):
    response = client.get('/api/v1/rsousers/me/professional_education/')
    assert response.status_code == 401, 'Response status code is not 401'
    assert 'detail' in response.data, 'No detail key in response data'


@pytest.mark.django_db
def test_get_me_privacy(authenticated_client, central_headquarter):
    response = authenticated_client.get('/api/v1/rsousers/me/privacy/')
    assert response.status_code == 200, 'Response status code is not 200'


@pytest.mark.django_db
def test_get_me_privacy_anonymous(client, central_headquarter):
    response = client.get('/api/v1/rsousers/me/privacy/')
    assert response.status_code == 401, 'Response status code is not 401'


@pytest.mark.django_db
def test_get_me_parent(authenticated_client, central_headquarter):
    response = authenticated_client.get('/api/v1/rsousers/me/parent/')
    assert response.status_code == 200, 'Response status code is not 200'


@pytest.mark.django_db
def test_get_me_parent_anonymous(client, central_headquarter):
    response = client.get('/api/v1/rsousers/me/parent/')
    assert response.status_code == 401, 'Response status code is not 401'


@pytest.mark.django_db
def test_get_me_region(authenticated_client, central_headquarter):
    response = authenticated_client.get('/api/v1/rsousers/me/region/')
    assert response.status_code == 200, 'Response status code is not 200'


@pytest.mark.django_db
def test_get_me_region_anonymous(client, central_headquarter):
    response = client.get('/api/v1/rsousers/me/region/')
    assert response.status_code == 401, 'Response status code is not 401'


@pytest.mark.django_db
def test_get_me_commander(authenticated_client, central_headquarter):
    response = authenticated_client.get('/api/v1/rsousers/me_commander/')
    assert response.status_code == 200, 'Response status code is not 200'


@pytest.mark.django_db
def test_get_me_commander_anonymous(client, central_headquarter):
    response = client.get('/api/v1/rsousers/me_commander/')
    assert response.status_code == 401, 'Response status code is not 401'


@pytest.mark.django_db
def test_get_me_trusted(authenticated_client, central_headquarter):
    response = authenticated_client.get('/api/v1/rsousers/me_trusted/')
    assert response.status_code == 200, 'Response status code is not 200'


@pytest.mark.django_db
def test_get_me_trusted_anonymous(client, central_headquarter):
    response = client.get('/api/v1/rsousers/me_trusted/')
    assert response.status_code == 401, 'Response status code is not 401'


@pytest.mark.django_db
def test_get_me_positions(authenticated_client, central_headquarter):
    response = authenticated_client.get('/api/v1/rsousers/me_positions/')
    assert response.status_code == 200, 'Response status code is not 200'


@pytest.mark.django_db
def test_get_me_positions_anonymous(client, central_headquarter):
    response = client.get('/api/v1/rsousers/me_positions/')
    assert response.status_code == 401, 'Response status code is not 401'


@pytest.mark.django_db
def test_logout_user(authenticated_client):
    response = authenticated_client.post('/api/v1/token/logout/')
    assert response.status_code == 204, 'Response status code is not 204'
