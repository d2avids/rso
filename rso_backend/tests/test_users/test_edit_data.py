from http import HTTPStatus

import pytest


@pytest.mark.django_db
def test_edit_education_data(authenticated_client,
                             central_headquarter,
                             educational_institution):
    payload = {
        'study_institution': 1,
        'study_faculty': 'string',
        'study_form': 'full_time',
        'study_year': 'string',
        'study_specialty': 'string'
    }
    response = authenticated_client.put(
        '/api/v1/rsousers/me/education/',
        payload
    )
    assert response.status_code == 200, 'Response status code is not 200'
    response = authenticated_client.get('/api/v1/rsousers/me/education/')
    assert response.data == payload


@pytest.mark.django_db
def test_edit_foreign_documents_data(authenticated_client,
                                     central_headquarter):
    payload = {
        'name': 'string',
        'foreign_pass_num': 'string',
        'foreign_pass_whom': 'string',
        'foreign_pass_date': '2024-02-08',
        'snils': 'string',
        'inn': 'string',
        'work_book_num': 'string'
    }
    response = authenticated_client.put(
        '/api/v1/rsousers/me/foreign_documents/',
        payload
    )
    assert response.status_code == 200, 'Response status code is not 200'
    response = authenticated_client.get(
        '/api/v1/rsousers/me/foreign_documents/'
    )
    assert response.data == payload


@pytest.mark.django_db
def test_edit_privacy_data(authenticated_client,
                           central_headquarter):
    payload = {
        'privacy_telephone': 'Все',
        'privacy_email': 'Все',
        'privacy_social': 'Все',
        'privacy_about': 'Все',
        'privacy_photo': 'Все'
    }
    response = authenticated_client.put(
        '/api/v1/rsousers/me/privacy/',
        payload
    )
    assert response.status_code == 200, 'Response status code is not 200'
    response = authenticated_client.get(
        '/api/v1/rsousers/me/privacy/'
    )
    assert response.data == payload


@pytest.mark.django_db
def test_edit_region_data(authenticated_client,
                          central_headquarter,
                          region):
    payload = {
        'reg_town': 'string',
        'reg_house': 'string',
        'reg_fact_same_address': True,
        'fact_town': 'string',
        'fact_house': 'string',
        'reg_region_id': 1,
        'fact_region_id': 1
    }
    response = authenticated_client.put(
        '/api/v1/rsousers/me/region/',
        payload
    )
    assert response.status_code == 200, 'Response status code is not 200'
    response = authenticated_client.get(
        '/api/v1/rsousers/me/region/'
    )
    response_payload = {
        'reg_region': 1,
        'reg_town': 'string',
        'reg_house': 'string',
        'reg_fact_same_address': True,
        'fact_region': 1,
        'fact_town': 'string',
        'fact_house': 'string',
        'reg_region_id': 1,
        'fact_region_id': 1
    }
    assert response.data == response_payload


@pytest.mark.django_db
def test_edit_statement_data(authenticated_client, central_headquarter):
    payload = {
        'rso_info_from': 'string',
        'personal_data_agreement': True
    }
    response = authenticated_client.patch(
        '/api/v1/rsousers/me/statement/',
        payload
    )
    assert response.status_code == 200, 'Response status code is not 200'
    response = authenticated_client.get(
        '/api/v1/rsousers/me/statement/'
    )
    response_payload = {
        'statement': None,
        'consent_personal_data': None,
        'consent_personal_data_representative': None,
        'passport': None,
        'passport_representative': None,
        'snils_file': None,
        'inn_file': None,
        'employment_document': None,
        'military_document': None,
        'international_passport': None,
        'additional_document': None,
        'rso_info_from': 'string',
        'personal_data_agreement': True
    }
    assert response.data == response_payload


@pytest.mark.django_db
def test_edit_documents_data(authenticated_client, central_headquarter):
    payload = {
        'snils': 'string',
        'russian_passport': True,
        'inn': 'string',
        'pass_ser_num': 'string',
        'pass_town': 'string',
        'pass_whom': 'string',
        'pass_date': '2024-02-08',
        'pass_code': 'string',
        'pass_address': 'string',
        'work_book_num': 'string',
        'international_pass': 'string',
        'mil_reg_doc_type': 'military_certificate',
        'mil_reg_doc_ser_num': 'string'
    }
    response = authenticated_client.put(
        '/api/v1/rsousers/me/documents/',
        payload
    )
    assert response.status_code == 200, 'Response status code is not 200'
    data = response.data
    assert data.get('snils') == 'string', 'Incorrect data'
    assert data.get('mil_reg_doc_type') == 'military_certificate', 'Data incor'
    response = authenticated_client.get('/api/v1/rsousers/me/documents/')
    assert response.data == payload


@pytest.mark.django_db
def test_edit_parent_data(authenticated_client,
                          central_headquarter,
                          region):
    payload = {
        "parent_last_name": "string",
        "parent_first_name": "string",
        "parent_patronymic_name": "string",
        "parent_date_of_birth": "2024-02-08",
        "relationship": "father",
        "parent_phone_number": "string",
        "russian_passport": True,
        "passport_number": "string",
        "passport_date": "2024-02-08",
        "passport_authority": "string",
        "region": 1,
        "city": "string",
        "address": "string"
    }
    response = authenticated_client.put(
        '/api/v1/rsousers/me/parent/',
        payload
    )
    assert response.status_code == 200, 'Response status code is not 200'
    response = authenticated_client.get(
        '/api/v1/rsousers/me/parent/'
    )
    assert response.data == payload


@pytest.mark.django_db(transaction=True)
def test_edit_me_professional_education(
    authenticated_client_8, authenticated_client_7, educational_institution,
    educational_institution_2
):
    """CRUD-тест для до проф образований + проверка удаления чужой записи"""

    payload = {
        'study_institution': educational_institution.pk,
        'years_of_study': '2010-2015',
        'exam_score': 'string',
        'qualification': 'string'
    }
    response = authenticated_client_8.post(
        '/api/v1/rsousers/me/professional_education/', payload, format="json"
    )
    assert response.status_code == HTTPStatus.CREATED, (
        'Response status code is not 201'
    )
    response = authenticated_client_8.get(
        '/api/v1/rsousers/me/professional_education/'
    )
    assert response.status_code == HTTPStatus.OK, (
        'Response status code is not 200'
    )
    payload = {
        'exam_score': 'very well',
        'study_institution': educational_institution_2.pk
    }
    response = authenticated_client_7.patch(
        '/api/v1/rsousers/me/professional_education/1/', payload
    )
    assert response.status_code == HTTPStatus.FORBIDDEN, (
        'Response status code is not 403'
    )
    response = authenticated_client_8.patch(
        '/api/v1/rsousers/me/professional_education/1/', payload
    )
    assert response.status_code == HTTPStatus.OK, (
        'Response status code is not 200'
    )
    response_2 = authenticated_client_7.delete(
        '/api/v1/rsousers/me/professional_education/1/'
    )
    assert response_2.status_code == HTTPStatus.FORBIDDEN, (
        'Response status code is not 403'
    )
    response = authenticated_client_8.delete(
        '/api/v1/rsousers/me/professional_education/1/'
    )
    assert response.status_code == HTTPStatus.NO_CONTENT, (
        'Response status code is not 204'
    )


@pytest.mark.django_db(transaction=True)
def test_edit_me_profedu_wrong_data(
            authenticated_client, authenticated_client_7, educational_institution
):
    """Проверка попытки записать проф образование с некорректными данными."""

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


@pytest.mark.django_db(transaction=True)
def test_get_me_five_professional_educations(
    authenticated_client, central_headquarter, educational_institution
):
    """Проверка попытки записать больше 5 профобразований."""

    payloads = [
            ('2010-2015', 'well done', 'professional'),
            ('2015-2016', 'medium rare', 'newby'),
            ('2017-2018', 'nice', 'welder'),
            ('2019-2020', 'good', 'doctor'),
            ('2021-2022', 'excellent', 'master'),
            ('2022-2023', 'unbelievable', 'wizard'),
        ]
    for years_of_study, exam_score, qualification in payloads:
        payload = {
            'study_institution': educational_institution.pk,
            'years_of_study': years_of_study,
            'exam_score': exam_score,
            'qualification': qualification
        }
        authenticated_client.post(
            '/api/v1/rsousers/me/professional_education/', payload, format="json"
        )
    response = authenticated_client.get(
        '/api/v1/rsousers/me/professional_education/'
    )
    assert len(response.data['users_prof_educations']) == 5, (
        'Wrong length of response data, expected 5'
    )
