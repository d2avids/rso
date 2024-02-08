import pytest

from tests.conftest import REGION_MOJAISK, REGION_MOSCOW


@pytest.mark.django_db
def test_regions_list(client, region):
    response = client.get('/api/v1/regions/')
    assert response.status_code == 200, 'Response code is not 200'


@pytest.mark.django_db
def test_detailed_region(client, region):
    response = client.get('/api/v1/regions/1/')
    assert response.status_code == 200, 'Response code is not 200'
    data = response.data
    assert data['name'] == REGION_MOJAISK, 'Incorrect name'


@pytest.mark.django_db
def test_regions_search(client, region):
    response = client.get(f'/api/v1/regions/?search={REGION_MOSCOW}')
    assert response.status_code == 200, 'Response code is not 200'
    data = response.data
    assert len(data) == 1, 'Incorrect search result'
