import pytest

@pytest.mark.django_db
def test_educational_members(client, central_headquarter, educational_institutions):
    response = client.get('/api/v1/eduicational_institutions/')

    assert response.status_code == 200, 'Response code is not 200'

    assert len(response.data) > 1, 'Response data is 1 object or empty'

