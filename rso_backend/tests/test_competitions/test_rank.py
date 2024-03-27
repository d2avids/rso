from http import HTTPStatus
import pytest


@pytest.mark.django_db(transaction=True, reset_sequences=True)
class TestRankQ7:
    competition_url = '/api/v1/competitions/'
    question_url_7 = '/reports/q7/get_place/'

    def test_get_place_7_tandem(
            self, authenticated_client_3, q7_tandem_ranking, q7_ranking,
            competition
    ):
        """Тест получения места по 7 показателю."""
        response = authenticated_client_3.get(
            self.competition_url + str(competition.id) + self.question_url_7
        )
        assert response.status_code == HTTPStatus.OK
        assert response.data['place'] == 1

    def test_get_place_7_tandem_without_report(
            self, authenticated_client, q7_tandem_ranking, q7_ranking,
            competition
    ):
        """
        Тест получения места по 7 показателю если нет своего отчета,
        зато есть у второй команды-партнера.
        """
        response = authenticated_client.get(
            self.competition_url + str(competition.id) + self.question_url_7
        )
        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_get_place_7_tandem_without_rank(
            self, authenticated_client_3, q7_ranking, report_question7_verif,
            competition
    ):
        """
        Тест получения места по 7 показателю если рейтинг ещё не создан.
        """
        response = authenticated_client_3.get(
            self.competition_url + str(competition.id) + self.question_url_7
        )
        assert response.status_code == HTTPStatus.OK
        assert response.data['place'] == 'Показатель в обработке'

    def test_get_place_7_tandem_without_any_report(
            self, authenticated_client_4, q7_tandem_ranking, q7_ranking,
            competition
    ):
        """
        Тест получения места по 7 показателю если нет своего отчета совсем.
        """
        response = authenticated_client_4.get(
            self.competition_url + str(competition.id) + self.question_url_7
        )
        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_get_place_7_start(
            self, authenticated_client_5, q7_tandem_ranking, q7_ranking,
            competition
    ):
        """Тест получения места по 7 показателю."""
        response = authenticated_client_5.get(
            self.competition_url + str(competition.id) + self.question_url_7
        )
        assert response.status_code == HTTPStatus.OK
        assert response.data['place'] == 2

    def test_get_place_7_start_without_rank(
            self, authenticated_client_5, report_question7_verif2,
            competition
    ):
        """
        Тест получения места по 7 показателю если рейтинг ещё не создан.
        """
        response = authenticated_client_5.get(
            self.competition_url + str(competition.id) + self.question_url_7
        )
        assert response.status_code == HTTPStatus.OK
        assert response.data['place'] == 'Показатель в обработке'

    def test_get_place_7_start_without_any_report(
            self, authenticated_client_4, q7_tandem_ranking, q7_ranking,
            competition
    ):
        """
        Тест получения места по 7 показателю если нет своего отчета совсем.
        """
        response = authenticated_client_4.get(
            self.competition_url + str(competition.id) + self.question_url_7
        )
        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_get_place_7_not_auth(
            self, client, q7_tandem_ranking, q7_ranking,
            competition
    ):
        """
        Тест получения места по 7 показателю неавторизованного пользователя.
        """
        response = client.get(
            self.competition_url + str(competition.id) + self.question_url_7
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED



@pytest.mark.django_db(transaction=True, reset_sequences=True)
class TestRankQ8:
    competition_url = '/api/v1/competitions/'
    question_url_8 = '/reports/q8/get_place/'

    def test_get_place_8_tandem(
            self, authenticated_client_3, q8_tandem_ranking, q8_ranking,
            competition
    ):
        """Тест получения места по 8 показателю."""
        response = authenticated_client_3.get(
            self.competition_url + str(competition.id) + self.question_url_8
        )
        assert response.status_code == HTTPStatus.OK
        assert response.data['place'] == 1

    def test_get_place_8_tandem_without_report(
            self, authenticated_client, q8_tandem_ranking, q8_ranking,
            competition
    ):
        """
        Тест получения места по 8 показателю если нет своего отчета,
        зато есть у второй команды-партнера.
        """
        response = authenticated_client.get(
            self.competition_url + str(competition.id) + self.question_url_8
        )
        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_get_place_8_tandem_without_rank(
            self, authenticated_client_3, q8_ranking, report_question8_verif,
            competition
    ):
        """
        Тест получения места по 8 показателю если рейтинг ещё не создан.
        """
        response = authenticated_client_3.get(
            self.competition_url + str(competition.id) + self.question_url_8
        )
        assert response.status_code == HTTPStatus.OK
        assert response.data['place'] == 'Показатель в обработке'

    def test_get_place_8_tandem_without_any_report(
            self, authenticated_client_4, q8_tandem_ranking, q8_ranking,
            competition
    ):
        """
        Тест получения места по 8 показателю если нет своего отчета совсем.
        """
        response = authenticated_client_4.get(
            self.competition_url + str(competition.id) + self.question_url_8
        )
        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_get_place_8_start(
            self, authenticated_client_5, q8_tandem_ranking, q8_ranking,
            competition
    ):
        """Тест получения места по 8 показателю."""
        response = authenticated_client_5.get(
            self.competition_url + str(competition.id) + self.question_url_8
        )
        assert response.status_code == HTTPStatus.OK
        assert response.data['place'] == 2

    def test_get_place_8_start_without_rank(
            self, authenticated_client_5, report_question8_verif2,
            competition
    ):
        """
        Тест получения места по 8 показателю если рейтинг ещё не создан.
        """
        response = authenticated_client_5.get(
            self.competition_url + str(competition.id) + self.question_url_8
        )
        assert response.status_code == HTTPStatus.OK
        assert response.data['place'] == 'Показатель в обработке'

    def test_get_place_8_start_without_any_report(
            self, authenticated_client_4, q8_tandem_ranking, q8_ranking,
            competition
    ):
        """
        Тест получения места по 8 показателю если нет своего отчета совсем.
        """
        response = authenticated_client_4.get(
            self.competition_url + str(competition.id) + self.question_url_8
        )
        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_get_place_8_not_auth(
            self, client, q8_tandem_ranking, q8_ranking,
            competition
    ):
        """
        Тест получения места по 8 показателю неавторизованного пользователя.
        """
        response = client.get(
            self.competition_url + str(competition.id) + self.question_url_8
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.django_db(transaction=True, reset_sequences=True)
class TestRankQ9:
    competition_url = '/api/v1/competitions/'
    question_url_9 = '/reports/q9/get_place/'

    def test_get_place_9_tandem(
            self, authenticated_client_3, q9_tandem_ranking, q9_ranking,
            competition
    ):
        """Тест получения места по 9 показателю."""
        response = authenticated_client_3.get(
            self.competition_url + str(competition.id) + self.question_url_9
        )
        assert response.status_code == HTTPStatus.OK
        assert response.data['place'] == 1

    def test_get_place_9_tandem_without_report(
            self, authenticated_client, q9_tandem_ranking, q9_ranking,
            competition
    ):
        """
        Тест получения места по 9 показателю если нет своего отчета,
        зато есть у второй команды-партнера.
        """
        response = authenticated_client.get(
            self.competition_url + str(competition.id) + self.question_url_9
        )
        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_get_place_9_tandem_without_rank(
            self, authenticated_client_3, q9_ranking, report_question9_verif,
            competition
    ):
        """
        Тест получения места по 9 показателю если рейтинг ещё не создан.
        """
        response = authenticated_client_3.get(
            self.competition_url + str(competition.id) + self.question_url_9
        )
        assert response.status_code == HTTPStatus.OK
        assert response.data['place'] == 'Показатель в обработке'

    def test_get_place_9_tandem_without_any_report(
            self, authenticated_client_4, q9_tandem_ranking, q9_ranking,
            competition
    ):
        """
        Тест получения места по 9 показателю если нет своего отчета совсем.
        """
        response = authenticated_client_4.get(
            self.competition_url + str(competition.id) + self.question_url_9
        )
        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_get_place_9_start(
            self, authenticated_client_5, q9_tandem_ranking, q9_ranking,
            competition
    ):
        """Тест получения места по 9 показателю."""
        response = authenticated_client_5.get(
            self.competition_url + str(competition.id) + self.question_url_9
        )
        assert response.status_code == HTTPStatus.OK
        assert response.data['place'] == 2

    def test_get_place_9_start_without_rank(
            self, authenticated_client_5, report_question9_verif2,
            competition
    ):
        """
        Тест получения места по 9 показателю если рейтинг ещё не создан.
        """
        response = authenticated_client_5.get(
            self.competition_url + str(competition.id) + self.question_url_9
        )
        assert response.status_code == HTTPStatus.OK
        assert response.data['place'] == 'Показатель в обработке'

    def test_get_place_9_start_without_any_report(
            self, authenticated_client_4, q9_tandem_ranking, q9_ranking,
            competition
    ):
        """
        Тест получения места по 9 показателю если нет своего отчета совсем.
        """
        response = authenticated_client_4.get(
            self.competition_url + str(competition.id) + self.question_url_9
        )
        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_get_place_9_not_auth(
            self, client, q9_tandem_ranking, q9_ranking,
            competition
    ):
        """
        Тест получения места по 9 показателю неавторизованного пользователя.
        """
        response = client.get(
            self.competition_url + str(competition.id) + self.question_url_9
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.django_db(transaction=True, reset_sequences=True)
class TestRankQ19:
    competition_url = '/api/v1/competitions/'
    question_url_19 = '/reports/q19/get_place/'

    def test_get_place_19_tandem(
            self, authenticated_client_3, q19_tandem_ranking, q19_ranking,
            competition
    ):
        """Тест получения места по 19 показателю."""
        response = authenticated_client_3.get(
            self.competition_url + str(competition.id) + self.question_url_19
        )
        assert response.status_code == HTTPStatus.OK
        assert response.data['place'] == 1

    def test_get_place_19_tandem_without_report(
            self, authenticated_client, q19_tandem_ranking, q19_ranking,
            competition
    ):
        """
        Тест получения места по 19 показателю если нет своего отчета,
        зато есть у второй команды-партнера.
        """
        response = authenticated_client.get(
            self.competition_url + str(competition.id) + self.question_url_19
        )
        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_get_place_19_tandem_without_rank(
            self, authenticated_client_3, q19_ranking, report_question19_verif,
            competition
    ):
        """
        Тест получения места по 19 показателю если рейтинг ещё не создан.
        """
        response = authenticated_client_3.get(
            self.competition_url + str(competition.id) + self.question_url_19
        )
        assert response.status_code == HTTPStatus.OK
        assert response.data['place'] == 'Показатель в обработке'

    def test_get_place_19_tandem_without_any_report(
            self, authenticated_client_4, q19_tandem_ranking, q19_ranking,
            competition
    ):
        """
        Тест получения места по 19 показателю если нет своего отчета совсем.
        """
        response = authenticated_client_4.get(
            self.competition_url + str(competition.id) + self.question_url_19
        )
        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_get_place_19_start(
            self, authenticated_client_5, q19_tandem_ranking, q19_ranking,
            competition
    ):
        """Тест получения места по 19 показателю."""
        response = authenticated_client_5.get(
            self.competition_url + str(competition.id) + self.question_url_19
        )
        assert response.status_code == HTTPStatus.OK
        assert response.data['place'] == 2

    def test_get_place_19_start_without_rank(
            self, authenticated_client_5, report_question19_verif2,
            competition
    ):
        """
        Тест получения места по 19 показателю если рейтинг ещё не создан.
        """
        response = authenticated_client_5.get(
            self.competition_url + str(competition.id) + self.question_url_19
        )
        assert response.status_code == HTTPStatus.OK
        assert response.data['place'] == 'Показатель в обработке'

    def test_get_place_19_start_without_any_report(
            self, authenticated_client_4, q19_tandem_ranking, q19_ranking,
            competition
    ):
        """
        Тест получения места по 19 показателю если нет своего отчета совсем.
        """
        response = authenticated_client_4.get(
            self.competition_url + str(competition.id) + self.question_url_19
        )
        assert response.status_code == HTTPStatus.FORBIDDEN

    def test_get_place_19_not_auth(
            self, client, q19_tandem_ranking, q19_ranking,
            competition
    ):
        """
        Тест получения места по 19 показателю неавторизованного пользователя.
        """
        response = client.get(
            self.competition_url + str(competition.id) + self.question_url_19
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED