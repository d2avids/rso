from http import HTTPStatus

import pytest

from competitions.models import Q9, Q9Report


@pytest.mark.django_db(transaction=True, reset_sequences=True)
class TestQ9ViewSet:
    competition_url = '/api/v1/competitions/'
    question_url = '/reports/q9/'

    report = {
        "event_name": "Мероприятие New",
        "prize_place": 2
    }

    report_list = [
        {
            "event_name": "Мероприятие New",
            "prize_place": 2,
        }
    ]
    report_without_prize_place = [
        {
            "event_name": "Мероприятие 1"
        }
    ]
    report_with_prize_place_10 = [
        {
            "event_name": "Мероприятие 1",
            "prize_place": 10
        }
    ]
    report_without_event_name = [
        {
            "prize_place": 1
        }
    ]
    report_with_verif = {
            "event_name": "Мероприятие New",
            "prize_place": 1,
            "is_verified": True
        }

    def test_get_list_reg_commissar(
            self, authenticated_client_commissar_regional_headquarter,
            authenticated_client_commissar_regional_headquarter_2,
            competition, report_question9_not_verif, report_question9_verif2,
            report_question9_not_verif3
    ):
        """
        Проверка, что при запросе общего списка региональным командиром,
        выводятся все заявки этого региона, верифицированные и нет.
        """
        response = authenticated_client_commissar_regional_headquarter.get(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200'
        )
        data = response.data
        assert len(data) == 2, (
            'Количество отчетов не соответствует ожидаемому'
        )

        response = authenticated_client_commissar_regional_headquarter_2.get(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200'
        )
        assert len(response.data) == 1, (
            'Количество отчетов не соответствует ожидаемому'
        )

    def test_get_list_not_auth(
            self, client, competition, report_question9_not_verif,
    ):
        """
        Проверка, что неавторизованный пользователь не может
        получить список отчетов.
        """
        response = client.get(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}'
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Response code is not 401'
        )

    def test_get_list_auth(
            self, free_authenticated_client, competition,
            report_question9_not_verif
    ):
        """
        Проверка, что авторизованный пользователь не может
        получить список отчетов.
        """
        response = free_authenticated_client.get(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}'
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Response code is not 403'
        )

    def test_create_report_participant(
        self, authenticated_client, participants_competition_tandem,
        competition, detachment_competition, report_question9_not_verif2
    ):
        """
        Проверка, что пользователь - участник конкурса, может создать отчет.
        """
        response = authenticated_client.post(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}', data=self.report_list, format='json'
        )
        assert response.status_code == HTTPStatus.CREATED, (
            'Response code is not 201'
        )
        global_report = Q9Report.objects.filter(
            competition=competition,
            detachment=detachment_competition
        ).all()
        assert len(global_report) == 1, (
            'Количество отчетов не соответствует ожидаемому'
        )
        new_report = Q9.objects.filter(
            detachment_report=global_report[0]
        ).all()
        assert len(new_report) == 1, (
            'Количество отчетов не соответствует ожидаемому'
        )
        assert new_report[0].is_verified is False, (
            'Отчет ошибочно верифицирован при создании.'
        )
        assert new_report[0].prize_place == self.report['prize_place'], (
            'Отчет ошибочно создан с неверным призовым местом.'
        )

    def test_create_report_participant_without_event_name(
        self, authenticated_client, participants_competition_tandem,
        competition
    ):
        """
        Проверка, что пользователь - участник конкурса, не может создать отчет,
        если нет названия мероприятия.
        """
        response = authenticated_client.post(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}', self.report_without_event_name,
            format='json'
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Response code is not 400'
        )
        assert response.data == {
            "event_name": [
                "Обязательное поле."
            ]
        }

    def test_create_report_participant_without_prize_place(
        self, authenticated_client, participants_competition_tandem,
        competition
    ):
        """
        Проверка, что пользователь - участник конкурса, не может создать отчет,
        если не указано призовое место.
        """
        response = authenticated_client.post(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}', self.report_without_prize_place,
            format='json'
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Response code is not 400'
        )
        assert response.data == {
            'prize_place': [
                'Обязательное поле.'
            ]
        }

    def test_create_report_participant_with_incorrect_prize_place(
        self, authenticated_client, participants_competition_tandem,
        competition
    ):
        """
        Проверка, что пользователь - участник конкурса, не может создать отчет,
        если указано некорректное призовое место (10).
        """
        response = authenticated_client.post(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}', self.report_with_prize_place_10,
            format='json'
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Response code is not 400'
        )
        assert response.data == {
            'prize_place': [
                'Значения 10 нет среди допустимых вариантов.'
            ]
        }

    def test_create_report_not_auth(
        self, client, competition
    ):
        """
        Проверка, что неавторизованный пользователь не может
        создать отчет.
        """
        response = client.post(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}', data=self.report, format='json'
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Response code is not 401'
        )

    def test_create_report_auth(
        self, authenticated_client, competition
    ):
        """
        Проверка, что простой пользователь не может
        создать отчет.
        """
        response = authenticated_client.post(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}', data=self.report, format='json'
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Response code is not 403'
        )

    def test_get_report_id_not_auth(
        self, client, competition, report_question9_not_verif
    ):
        """
        Проверка, что неавторизованный пользователь не может
        получить отчет.
        """
        response = client.get(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}{report_question9_not_verif.id}/'
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Response code is not 401'
        )

    def test_get_report_id_auth(
        self, authenticated_client, competition, report_question9_not_verif
    ):
        """
        Проверка, что авторизованный пользователь не может
        получить отчет.
        """
        response = authenticated_client.get(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}{report_question9_not_verif.id}/'
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Response code is not 403'
        )

    def test_get_report_id_participant(
        self, authenticated_client, participants_competition_tandem,
        competition, report_question9_not_verif, report_question9_not_verif2
    ):
        """
        Проверка, что пользователь - участник конкурса, не может
        получить доступ к чужому отчету.
        """
        response = authenticated_client.get(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}{report_question9_not_verif2.id}/'
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Response code is not 403'
        )

    def test_get_report_id_author(
        self, authenticated_client_3, participants_competition_tandem,
        competition, report_question9_not_verif, report_question9_not_verif2
    ):
        """
        Проверка, что пользователь - участник конкурса, может
        получить доступ к своему отчету.
        """
        response = authenticated_client_3.get(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}{report_question9_not_verif.id}/'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200'
        )
        report = response.data
        assert report['event_name'] == (
            report_question9_not_verif.event_name
        ), 'Incorrect event_name'
        assert report['prize_place'] == (
            report_question9_not_verif.prize_place
        ), 'Incorrect prize_place'
        assert report['is_verified'] is False, 'Incorrect is_verified'

    def test_put_report_participant(
        self, authenticated_client_3, participants_competition_tandem,
        competition, report_question9_not_verif, report_question9_not_verif2
    ):
        """
        Проверка, что пользователь - участник конкурса, может
        изменить свой отчет, пока он не верифицирован.
        """
        response = authenticated_client_3.put(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}{report_question9_not_verif.id}/',
            data=self.report, format='json'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200'
        )
        report = response.data
        assert report['event_name'] == (
            report_question9_not_verif.event_name
        ), 'Incorrect event_name'
        assert report['prize_place'] == (
            report_question9_not_verif.prize_place
        ), 'Incorrect prize_place'
        assert report['is_verified'] is False, 'Incorrect is_verified'

    def test_put_report_participant_verif(
        self, authenticated_client_3, participants_competition_tandem,
        competition, report_question9_not_verif, report_question9_not_verif2
    ):
        """
        Проверка, что пользователь - участник конкурса, не может
        изменить в своем отчете поле is_verified.
        """
        response = authenticated_client_3.put(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}{report_question9_not_verif.id}/',
            data=self.report_with_verif, format='json'
        )
        data = response.data
        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200'
        )
        assert response.data['is_verified'] is False, (
            'Пользователь смог изменить поле is_verified'
        )

    def test_put_verif_report_participant(
        self, authenticated_client_3, participants_competition_tandem,
        competition, report_question9_verif, report_question9_not_verif2
    ):
        """
        Проверка, что автор отчета не может изменить его после того,
        как он верифицирован.
        """
        response = authenticated_client_3.put(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}{report_question9_verif.id}/',
            data=self.report, format='json'
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Response code is not 403'
        )

    def test_put_report_not_auth(
        self, client, participants_competition_tandem,
        competition, report_question9_not_verif
    ):
        """
        Проверка, что неавторизованный пользователь не может
        изменить отчет.
        """
        response = client.put(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}{report_question9_not_verif.id}/',
            data=self.report, format='json'
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Response code is not 401'
        )

    def test_put_report_auth(
        self, free_authenticated_client, participants_competition_tandem,
        competition, report_question9_not_verif
    ):
        """
        Проверка, что простой пользователь не может
        изменить отчет.
        """
        response = free_authenticated_client.put(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}{report_question9_not_verif.id}/',
            data=self.report, format='json'
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Response code is not 403'
        )

    def test_put_report_reg_commissar(
        self, authenticated_client_commissar_regional_headquarter,
        participants_competition_tandem,
        competition, report_question9_verif, report_question9_verif2
    ):
        """
        Проверка, что рег.комиссар может изменить верифицированный отчет, но
        не может изменить название мероприятия в отчете.
        """
        response = authenticated_client_commissar_regional_headquarter.put(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}{report_question9_verif.id}/',
            data=self.report, format='json'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200'
        )
        report = response.data
        assert report['certificate_scans'] is None, (
            'Incorrect certificate_scans'
        )
        assert report['event_name'] != (
            self.report['event_name']
        ), 'Изменилось название мероприятия.'
        assert report['prize_place'] == (
            self.report['prize_place']
        ), 'Incorrect prize_place'
        assert report['is_verified'] is True, 'Incorrect is_verified'

    def test_patch_report_participant(
        self, authenticated_client_3, participants_competition_tandem,
        competition, report_question9_not_verif, report_question9_not_verif2
    ):
        """
        Проверка, что пользователь - участник конкурса, может
        изменить свой отчет, пока он не верифицирован.
        """
        response = authenticated_client_3.patch(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}{report_question9_not_verif.id}/',
            data=self.report, format='json'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200'
        )
        report = response.data
        assert report['event_name'] == (
            report_question9_not_verif.event_name
        ), 'Incorrect event_name'
        assert report['prize_place'] == (
            report_question9_not_verif.prize_place
        ), 'Incorrect prize_place'
        assert report['is_verified'] is False, 'Incorrect is_verified'

    def test_patch_report_participant_verif(
        self, authenticated_client_3, participants_competition_tandem,
        competition, report_question9_not_verif, report_question9_not_verif2
    ):
        """
        Проверка, что пользователь - участник конкурса, не может
        изменить в своем отчете поле is_verified.
        """
        response = authenticated_client_3.patch(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}{report_question9_not_verif.id}/',
            data=self.report_with_verif, format='json'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200'
        )
        assert response.data['is_verified'] is False, (
            'Пользователь смог изменить поле is_verified'
        )

    def test_patch_verif_report_participant(
        self, authenticated_client_3, participants_competition_tandem,
        competition, report_question9_verif, report_question9_not_verif2
    ):
        """
        Проверка, что автор отчета не может изменить его после того,
        как он верифицирован.
        """
        response = authenticated_client_3.patch(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}{report_question9_verif.id}/',
            data=self.report, format='json'
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Response code is not 403'
        )

    def test_patch_report_not_auth(
        self, client, participants_competition_tandem,
        competition, report_question9_not_verif
    ):
        """
        Проверка, что неавторизованный пользователь не может
        изменить отчет.
        """
        response = client.patch(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}{report_question9_not_verif.id}/',
            data=self.report, format='json'
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Response code is not 401'
        )

    def test_patch_report_auth(
        self, free_authenticated_client, participants_competition_tandem,
        competition, report_question9_not_verif
    ):
        """
        Проверка, что простой пользователь не может
        изменить отчет.
        """
        response = free_authenticated_client.patch(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}{report_question9_not_verif.id}/',
            data=self.report, format='json'
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Response code is not 403'
        )

    def test_patch_report_reg_commissar(
        self, authenticated_client_commissar_regional_headquarter,
        participants_competition_tandem,
        competition, report_question9_verif, report_question9_verif2
    ):
        """
        Проверка, что рег.комиссар может изменить верифицированный отчет, но
        не может изменить название мероприятия в отчете.
        """
        response = authenticated_client_commissar_regional_headquarter.patch(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}{report_question9_verif.id}/',
            data=self.report, format='json'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200'
        )
        report = response.data
        assert report['certificate_scans'] is None, (
            'Incorrect certificate_scans'
        )
        assert report['event_name'] != (
            self.report['event_name']
        ), 'Изменилось название мероприятия.'
        assert report['prize_place'] == (
            self.report['prize_place']
        ), 'Incorrect prize_place'
        assert report['is_verified'] is True, 'Incorrect is_verified'

    @pytest.mark.parametrize(
        'client_name, expected_status', [
            ("free_authenticated_client", HTTPStatus.FORBIDDEN),
            ("client", HTTPStatus.UNAUTHORIZED),
            ("authenticated_client_3", HTTPStatus.NO_CONTENT),
            ("authenticated_client_commissar_regional_headquarter",
             HTTPStatus.NO_CONTENT),
        ]
    )
    def test_delete_report(
        self, client_name, expected_status,
        participants_competition_tandem, competition,
        report_question9_not_verif, report_question9_verif2,
        request
    ):
        """
        Проверка, прав удаления отчетов.
        """
        test_client = request.getfixturevalue(client_name)
        response = test_client.delete(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}{report_question9_not_verif.id}/'
        )
        assert response.status_code == expected_status, (
            'Response code is not ' + str(expected_status)
        )

    @pytest.mark.parametrize(
        'client_name, expected_status', [
            ("free_authenticated_client", HTTPStatus.FORBIDDEN),
            ("client", HTTPStatus.UNAUTHORIZED),
            ("authenticated_client_3", HTTPStatus.FORBIDDEN),
            ("authenticated_client_commissar_regional_headquarter",
             HTTPStatus.OK),
        ]
    )
    def test_accept_report(
        self, client_name, request, expected_status,
        participants_competition_tandem, competition,
        report_question9_not_verif, report_question9_verif2,
    ):
        """
        Проверка прав подтверждения отчетов.
        """
        test_client = request.getfixturevalue(client_name)
        response = test_client.post(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}{report_question9_not_verif.id}/accept/'
        )
        assert response.status_code == expected_status, (
            'Response code is not ' + str(expected_status)
        )
        if response.status_code == HTTPStatus.OK:
            verif_report = Q9.objects.get(
                id=report_question9_not_verif.id
            )
            assert verif_report.is_verified is True, 'Отчет не подтвержден'
            scores = Q9Report.objects.all()
            assert (
                scores[0].score ==
                verif_report.prize_place
            ), 'Среднее призовое место не соответствует ожидаемому'

    def test_put_number_participants_reg_commander(
            self, authenticated_client_commissar_regional_headquarter,
            participants_competition_tandem, competition,
            report_question9_verif, report_question9_verif_second
    ):
        """
        Проверка работы сигнала, который пересчитывает среднее призовое место,
        после изменения количества участников в
        верифицированной заявке рег.командиром.
        """
        response = authenticated_client_commissar_regional_headquarter.patch(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}{report_question9_verif_second.id}/',
            data=self.report,
            format='json'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200'
        )
        scores = Q9Report.objects.filter(
            competition=competition,
            detachment=report_question9_verif.detachment_report.detachment
        ).all()
        assert scores.count() == 1, (
            "Количество записей не соответствует ожидаемому"
        )
        assert (
            scores[0].score ==
            (self.report['prize_place'] +
             report_question9_verif.prize_place) / 2
        ), (
            "Среднее призовое место не пересчиталось, сигнал не отработал."
        )

    def test_me_with_report(
        self, authenticated_client_3, participants_competition_tandem,
        competition, report_question9_not_verif, report_question9_verif_second,
        report_question9_verif2
    ):
        """
        Проверка, что пользователь с подаными отчетами по запросу на
        /me/ может получить доступ к своим отчетам.
        """
        response = authenticated_client_3.get(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}me/'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200'
        )
        data = response.data
        assert isinstance(data, list), (
            'Response type is not list'
        )
        assert len(data) == 2, (
            'Количество отчетов не соответствует ожидаемому'
        )
        assert data[0]['id'] == report_question9_not_verif.id, (
            'Отчет не соответствует ожидаемому'
        )
        assert data[1]['id'] == report_question9_verif_second.id, (
            'Отчет не соответствует ожидаемому'
        )

    def test_me_without_report(
        self, authenticated_client_3, participants_competition_tandem,
        competition, report_question9_verif2
    ):
        """
        Проверка, что пользователь отряд которого не имеет
        поданых отчетов, получит пустой массив.
        """
        response = authenticated_client_3.get(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}me/'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200'
        )
        data = response.data
        assert isinstance(data, list), (
            'Response type is not list'
        )
        assert len(data) == 0, (
            'Количество отчетов не соответствует ожидаемому'
        )

    def test_me_not_auth(
        self, client, participants_competition_tandem,
        competition, report_question9_not_verif
    ):
        """
        Проверка, что неавторизованный пользователь не может
        получить доступ к эндпоинту.
        """
        response = client.get(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}me/'
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Response code is not 401'
        )

    def test_post_double_report(
        self, authenticated_client_3, participants_competition_tandem,
        competition, report_question9_verif
    ):
        """
        Проверка, что пользователь не может подать дубликат отчета.
        """
        response = authenticated_client_3.post(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}', data=[{
                "event_name": report_question9_verif.event_name,
                "prize_place": report_question9_verif.prize_place
            }],
            format='json'
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Response code is not 400'
        )
        assert response.data == {
            "event_name": [
                "Отчетность по этому мероприятию/конкурсу уже подана."
            ]
        }, 'Response data is not correct'
