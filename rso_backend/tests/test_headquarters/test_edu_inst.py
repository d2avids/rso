import pytest
from tests.conftest import (EDUCATIONAL_INSTITUTION_NAME,
                            EDUCATIONAL_INSTITUTION_SHORT_NAME, REGION_MOJAISK)


@pytest.mark.django_db
def test_edu_inst_list(client, central_headquarter, educational_institution):
    response = client.get('/api/v1/eduicational_institutions/')

    assert response.status_code == 200, 'Response code is not 200'

    assert len(response.data) > 1, 'Response data is 1 object or empty'


@pytest.mark.django_db
def test_detailed_inst(client, central_headquarter, educational_institution):
    response = client.get('/api/v1/eduicational_institutions/1/')

    assert response.status_code == 200, 'Response code is not 200'

    data = response.data
    assert data['name'] == EDUCATIONAL_INSTITUTION_NAME, 'Incorrect data'
    assert data['short_name'] == EDUCATIONAL_INSTITUTION_SHORT_NAME, (
        'Incorrect data'
    )
    assert isinstance(data['region'], dict), 'Incorrect data'


@pytest.mark.django_db
def test_edu_inst_search(client, central_headquarter, educational_institution):
    response = client.get(
        f'/api/v1/eduicational_institutions/'
        f'?search={EDUCATIONAL_INSTITUTION_SHORT_NAME}'
    )

    assert response.status_code == 200, 'Response code is not 200'
    assert response.data is not None, 'Response data is not empty'


@pytest.mark.django_db
def test_edu_inst_region_filter(client,
                                central_headquarter,
                                educational_institution):
    response = client.get(
        f'/api/v1/eduicational_institutions/'
        f'?region__name={REGION_MOJAISK}'
    )

    assert response.status_code == 200, 'Response code is not 200'
    assert response.data is not None, 'Response data is not empty'
