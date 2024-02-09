import pytest


@pytest.mark.django_db(transaction=True)
class TestCompetitionViewSet:
    competition_url = '/api/v1/competitions/'

    def test_competition_list(self, client, competition, competition_2):
        response = client.get(self.competition_url)
        assert response.status_code == 200, 'Response code is not 200'
        assert isinstance(response.data, list), 'Response type is not list'
        assert isinstance(response.data[0], dict), 'Response type is not dict'
        assert 'name' in response.data[0], 'Not found name-key in response'
        assert response.data[0]['name'] == competition.name, 'Incorrect name'
        assert response.data[0]['id'] == competition.id, 'Incorrect id'

    def test_competition_detail(self, client, competition):
        response = client.get(f'{self.competition_url}{competition.id}/')
        assert response.status_code == 200, 'Response code is not 200'
        assert isinstance(response.data, dict), 'Response type is not dict'
        assert 'name' in response.data, 'Response type is not dict'
        assert response.data['name'] == competition.name, 'Incorrect name'
        assert response.data['id'] == competition.id, 'Incorrect id'

    def test_competition_detail_not_found(self, client):
        response = client.get(f'{self.competition_url}9999/')
        assert response.status_code == 404, 'Response code is not 404'

