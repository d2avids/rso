from http import HTTPStatus
import pytest

from competitions.models import Q8, Q8Report


@pytest.mark.django_db(transaction=True, reset_sequences=True)
class TestParticipationInDistrictAndInterregionalEventsViewSet:
    competition_url = '/api/v1/competitions/'
    question_url = '/reports/q8/'

    report = {
        "event_name": "Мероприятие New",
        "number_of_participants": 10,
        "links": [
            {
                "link": "http://128.0.0.1:8000/swagger/"
            },
            {
                "link": "http://128.0.0.1:8000/api/v1/competitions/"
            }
        ]
    }
    report_list = [
        {
            "event_name": "Мероприятие New",
            "number_of_participants": 10,
            "links": [
                {
                    "link": "http://128.0.0.1:8000/swagger/"
                },
                {
                    "link": "http://128.0.0.1:8000/api/v1/competitions/"
                }
            ]
        }
    ]
    report_with_verif = [
        {
            "event_name": "Мероприятие New",
            "number_of_participants": 10,
            "links": [
                {
                    "link": "http://128.0.0.1:8000/swagger/"
                }
            ],
            "is_verified": True
        }
    ]
    report_without_link = [
        {
            "event_name": "Мероприятие 1",
            "number_of_participants": 10,
        }
    ]
    report_with_link_0 = [
        {
            "event_name": "Мероприятие 1",
            "number_of_participants": 10,
            "links": []
        }
    ]
    report_without_event_name = [
        {
            "number_of_participants": 10,
            "links": [
                {
                    "link": "http://128.0.0.1:8000/swagger/"
                }
            ]
        }
    ]
    report_without_number_of_participants = [
        {
            "event_name": "Мероприятие 1",
            "links": [
                {
                    "link": "http://128.0.0.1:8000/swagger/"
                }
            ]
        }
    ]

    def test_get_list_reg_commissar(
            self, authenticated_client_commissar_regional_headquarter,
            authenticated_client_commissar_regional_headquarter_2,
            competition, report_question8_not_verif, report_question8_verif2,
            report_question8_not_verif3
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
            self, client, competition, report_question8_not_verif,
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
            report_question8_not_verif
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
        competition, detachment_competition, report_question8_not_verif2
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
        global_report = Q8Report.objects.filter(
            competition=competition,
            detachment=detachment_competition
        ).all()
        assert len(global_report) == 1, (
            'Количество отчетов не соответствует ожидаемому'
        )
        new_report = Q8.objects.filter(
            detachment_report=global_report[0]
        ).all()
        assert len(new_report) == 1, (
            'Количество отчетов не соответствует ожидаемому'
        )
        assert new_report[0].links.count() == 2, (
            'Количество ссылок на отчет не соответствует ожидаемому'
        )
        assert (
            new_report[0].links.all()[1].link == self.report['links'][0]['link']
        ), (
            'Ссылки на отчет не соответствуют ожидаемым'
        )
        assert (
            new_report[0].links.all()[0].link == self.report['links'][1]['link']
        ), (
            'Ссылки на отчет не соответствуют ожидаемым'
        )
        assert new_report[0].is_verified is False, (
            'Отчет ошибочно верифицирован при создании.'
        )

    def test_create_report_participant_without_link(
        self, authenticated_client, participants_competition_tandem,
        competition
    ):
        """
        Проверка, что пользователь - участник конкурса, не может создать отчет,
        если нет ни одной ссылки.
        """
        response = authenticated_client.post(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}', self.report_without_link, format='json'
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Response code is not 400'
        )
        assert response.data == {
            "links": [
                "Обязательное поле."
            ]
        }, 'Response data is not correct'

    def test_create_report_participant_with_link_0(
        self, authenticated_client, participants_competition_tandem,
        competition
    ):
        """
        Проверка, что пользователь - участник конкурса, не может создать отчет,
        если нет ни одной ссылки.
        """
        response = authenticated_client.post(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}', self.report_with_link_0, format='json'
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Response code is not 400'
        )
        assert response.data == {
            "links": [
                "Добавьте хотя бы одну ссылку на фотоотчет"
            ]
        }, 'Response data is not correct'

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

    def test_create_report_participant_without_number_of_participants(
        self, authenticated_client, participants_competition_tandem,
        competition
    ):
        """
        Проверка, что пользователь - участник конкурса, не может создать отчет,
        если нет количества участников.
        """
        response = authenticated_client.post(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}', self.report_without_number_of_participants,
            format='json'
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Response code is not 400'
        )
        assert response.data == {
            "number_of_participants": [
                "Укажите количество участников."
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
            f'{self.question_url}', data=list(self.report), format='json'
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
            f'{self.question_url}', data=list(self.report), format='json'
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Response code is not 403'
        )

    def test_get_report_id_not_auth(
        self, client, competition, report_question8_not_verif
    ):
        """
        Проверка, что неавторизованный пользователь не может
        получить отчет.
        """
        response = client.get(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}{report_question8_not_verif.id}/'
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Response code is not 401'
        )

    def test_get_report_id_auth(
        self, authenticated_client, competition, report_question8_not_verif
    ):
        """
        Проверка, что авторизованный пользователь не может
        получить отчет.
        """
        response = authenticated_client.get(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}{report_question8_not_verif.id}/'
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Response code is not 403'
        )

    def test_get_report_id_participant(
        self, authenticated_client, participants_competition_tandem,
        competition, report_question8_not_verif, report_question8_not_verif2
    ):
        """
        Проверка, что пользователь - участник конкурса, не может
        получить доступ к чужому отчету.
        """
        response = authenticated_client.get(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}{report_question8_not_verif2.id}/'
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Response code is not 403'
        )

    def test_get_report_id_author(
        self, authenticated_client_3, participants_competition_tandem,
        competition, report_question8_not_verif, report_question8_not_verif2
    ):
        """
        Проверка, что пользователь - участник конкурса, может
        получить доступ к своему отчету.
        """
        response = authenticated_client_3.get(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}{report_question8_not_verif.id}/'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200'
        )
        report = response.data
        assert report['event_name'] == (
            report_question8_not_verif.event_name
        ), 'Incorrect event_name'
        assert report['number_of_participants'] == (
            report_question8_not_verif.number_of_participants
        ), 'Incorrect number_of_participants'
        assert report['is_verified'] is False, 'Incorrect is_verified'
        assert (
            report['links'][0]['link'] == report_question8_not_verif.links.all()[0].link
        ), (
            'Ссылки на отчет не соответствуют ожидаемым'
        )

    def test_put_report_participant(
        self, authenticated_client_3, participants_competition_tandem,
        competition, report_question8_not_verif, report_question8_not_verif2
    ):
        """
        Проверка, что пользователь - участник конкурса, может
        изменить свой отчет, пока он не верифицирован.
        """
        response = authenticated_client_3.put(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}{report_question8_not_verif.id}/',
            data=self.report, format='json'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200'
        )
        report = response.data
        assert report['event_name'] == (
            report_question8_not_verif.event_name
        ), 'Incorrect event_name'
        assert report['number_of_participants'] == (
            report_question8_not_verif.number_of_participants
        ), 'Incorrect number_of_participants'
        assert report['is_verified'] is False, 'Incorrect is_verified'
        assert (
            report['links'][0]['link'] == report_question8_not_verif.links.all()[0].link
        ), (
            'Ссылки на отчет не соответствуют ожидаемым'
        )

    def test_put_report_participant_verif(
        self, authenticated_client_3, participants_competition_tandem,
        competition, report_question8_not_verif, report_question8_not_verif2
    ):
        """
        Проверка, что пользователь - участник конкурса, не может
        изменить в своем отчете поле is_verified.
        """
        response = authenticated_client_3.put(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}{report_question8_not_verif.id}/',
            data=self.report_with_verif[0], format='json'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200'
        )
        assert response.data['is_verified'] is False, (
            'Простой пользователь смог изменить поле is_verified'
        )

    def test_put_verif_report_participant(
        self, authenticated_client_3, participants_competition_tandem,
        competition, report_question8_verif, report_question8_not_verif2
    ):
        """
        Проверка, что автор отчета не может изменить его после того,
        как он верифицирован.
        """
        response = authenticated_client_3.put(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}{report_question8_verif.id}/',
            data=self.report, format='json'
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Response code is not 403'
        )

    def test_put_report_not_auth(
        self, client, participants_competition_tandem,
        competition, report_question8_not_verif
    ):
        """
        Проверка, что неавторизованный пользователь не может
        изменить отчет.
        """
        response = client.put(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}{report_question8_not_verif.id}/',
            data=self.report, format='json'
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Response code is not 401'
        )

    def test_put_report_auth(
        self, free_authenticated_client, participants_competition_tandem,
        competition, report_question8_not_verif
    ):
        """
        Проверка, что простой пользователь не может
        изменить отчет.
        """
        response = free_authenticated_client.put(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}{report_question8_not_verif.id}/',
            data=self.report, format='json'
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Response code is not 403'
        )

    def test_put_report_reg_commissar(
        self, authenticated_client_commissar_regional_headquarter,
        participants_competition_tandem,
        competition, report_question8_verif, report_question8_verif2
    ):
        """
        Проверка, что рег.комиссар может изменить верифицированный отчет, но
        не может изменить название мероприятия в отчете.
        """
        response = authenticated_client_commissar_regional_headquarter.put(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}{report_question8_verif.id}/',
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
        assert report['number_of_participants'] == (
            self.report['number_of_participants']
        ), 'Incorrect number_of_participants'
        assert report['is_verified'] is True, 'Incorrect is_verified'
        assert len(report['links']) == 2, (
            'Количество ссылок на отчет не соответствует ожидаемому'
        )
        assert (
            report['links'][0]['link'] == self.report['links'][1]['link']
        ), (
            'Ссылки на отчет не соответствуют ожидаемым'
        )
        assert (
            report['links'][1]['link'] == self.report['links'][0]['link']
        ), (
            'Ссылки на отчет не соответствуют ожидаемым'
        )

    def test_patch_report_participant(
        self, authenticated_client_3, participants_competition_tandem,
        competition, report_question8_not_verif, report_question8_not_verif2
    ):
        """
        Проверка, что пользователь - участник конкурса, может
        изменить свой отчет, пока он не верифицирован.
        """
        response = authenticated_client_3.patch(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}{report_question8_not_verif.id}/',
            data=self.report, format='json'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200'
        )
        report = response.data
        assert report['event_name'] == (
            report_question8_not_verif.event_name
        ), 'Incorrect event_name'
        assert report['number_of_participants'] == (
            report_question8_not_verif.number_of_participants
        ), 'Incorrect number_of_participants'
        assert report['is_verified'] is False, 'Incorrect is_verified'
        assert (
            report['links'][0]['link'] == report_question8_not_verif.links.all()[0].link
        ), (
            'Ссылки на отчет не соответствуют ожидаемым'
        )

    def test_patch_report_participant_verif(
        self, authenticated_client_3, participants_competition_tandem,
        competition, report_question8_not_verif, report_question8_not_verif2
    ):
        """
        Проверка, что пользователь - участник конкурса, не может
        изменить в своем отчете поле is_verified.
        """
        response = authenticated_client_3.patch(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}{report_question8_not_verif.id}/',
            data=self.report_with_verif[0], format='json'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200'
        )
        assert response.data['is_verified'] is False, (
            'Простой пользователь смог изменить поле is_verified'
        )

    def test_patch_verif_report_participant(
        self, authenticated_client_3, participants_competition_tandem,
        competition, report_question8_verif, report_question8_not_verif2
    ):
        """
        Проверка, что автор отчета не может изменить его после того,
        как он верифицирован.
        """
        response = authenticated_client_3.patch(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}{report_question8_verif.id}/',
            data=self.report, format='json'
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Response code is not 403'
        )

    def test_patch_report_not_auth(
        self, client, participants_competition_tandem,
        competition, report_question8_not_verif
    ):
        """
        Проверка, что неавторизованный пользователь не может
        изменить отчет.
        """
        response = client.patch(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}{report_question8_not_verif.id}/',
            data=self.report, format='json'
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Response code is not 401'
        )

    def test_patch_report_auth(
        self, free_authenticated_client, participants_competition_tandem,
        competition, report_question8_not_verif
    ):
        """
        Проверка, что простой пользователь не может
        изменить отчет.
        """
        response = free_authenticated_client.patch(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}{report_question8_not_verif.id}/',
            data=self.report, format='json'
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Response code is not 403'
        )

    def test_patch_report_reg_commissar(
        self, authenticated_client_commissar_regional_headquarter,
        participants_competition_tandem,
        competition, report_question8_verif, report_question8_verif2
    ):
        """
        Проверка, что рег.комиссар может изменить верифицированный отчет, но
        не может изменить название мероприятия в отчете.
        """
        response = authenticated_client_commissar_regional_headquarter.patch(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}{report_question8_verif.id}/',
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
        assert report['number_of_participants'] == (
            self.report['number_of_participants']
        ), 'Incorrect number_of_participants'
        assert report['is_verified'] is True, 'Incorrect is_verified'
        assert len(report['links']) == 2, (
            'Количество ссылок на отчет не соответствует ожидаемому'
        )
        assert (
            report['links'][0]['link'] == self.report['links'][1]['link']
        ), (
            'Ссылки на отчет не соответствуют ожидаемым'
        )
        assert (
            report['links'][1]['link'] == self.report['links'][0]['link']
        ), (
            'Ссылки на отчет не соответствуют ожидаемым'
        )

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
        report_question8_not_verif, report_question8_verif2,
        request
    ):
        """
        Проверка, прав удаления отчетов.
        """
        test_client = request.getfixturevalue(client_name)
        response = test_client.delete(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}{report_question8_not_verif.id}/'
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
        report_question8_not_verif, report_question8_verif2,
    ):
        """
        Проверка прав подтверждения отчетов.
        """
        test_client = request.getfixturevalue(client_name)
        response = test_client.post(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}{report_question8_not_verif.id}/accept/'
        )
        assert response.status_code == expected_status, (
            'Response code is not ' + str(expected_status)
        )
        if response.status_code == HTTPStatus.OK:
            verif_report = Q8.objects.get(
                id=report_question8_not_verif.id
            )
            assert verif_report.is_verified is True, 'Отчет не подтвержден'
            scores = Q8Report.objects.all()
            assert (
                scores[0].score ==
                verif_report.number_of_participants
            ), 'Оценка не соответствует ожидаемому'

    def test_put_number_participants_reg_commander(
            self, authenticated_client_commissar_regional_headquarter,
            participants_competition_tandem, competition,
            report_question8_verif, report_question8_verif_second
    ):
        """
        Проверка работы сигнала, который пересчитывает общее количество
        очков, после изменения количества участников в
        верифицированной заявке рег.командиром.
        """
        response = authenticated_client_commissar_regional_headquarter.patch(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}{report_question8_verif_second.id}/',
            data=self.report,
            format='json'
        )
        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200'
        )
        scores = Q8Report.objects.filter(
            competition=competition,
            detachment=report_question8_verif_second.detachment_report.detachment
        ).all()
        assert scores.count() == 1, (
            "Количество записей не соответствует ожидаемому"
        )
        assert (
            scores[0].score ==
            self.report['number_of_participants'] +
            report_question8_verif.number_of_participants
        ), (
            "Количество участников не пересчиталось, сигнал не отработал."
        )

    def test_me_with_report(
        self, authenticated_client_3, participants_competition_tandem,
        competition, report_question8_not_verif, report_question8_verif_second,
        report_question8_verif2
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
        assert data[0]['id'] == report_question8_not_verif.id, (
            'Отчет не соответствует ожидаемому'
        )
        assert data[1]['id'] == report_question8_verif_second.id, (
            'Отчет не соответствует ожидаемому'
        )

    def test_me_without_report(
        self, authenticated_client_3, participants_competition_tandem,
        competition, report_question8_verif2
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
        competition, report_question8_not_verif
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
        competition, report_question8_verif
    ):
        """
        Проверка, что пользователь не может подать дубликат отчета.
        """
        response = authenticated_client_3.post(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}', data=[{
                "event_name": report_question8_verif.event_name,
                "number_of_participants": report_question8_verif.number_of_participants,
                "links": [{"link": report_question8_verif.links.all()[0].link}]
            }],
            format='json'
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Response code is not 400'
        )
        assert response.data == {
            "event_name": [
                "Отчетность по этому мероприятию уже подана."
            ]
        }, 'Response data is not correct'

    def test_post_double_links(
        self, authenticated_client_3, participants_competition_tandem,
        competition, report_question8_verif
    ):
        """
        Проверка, что пользователь не может подать отчет с
        одинаковыми ссылками.
        """
        response = authenticated_client_3.post(
            f'{self.competition_url}{competition.id}'
            f'{self.question_url}', data=[{
                "event_name": self.report['event_name'],
                "number_of_participants": self.report['number_of_participants'],
                "links": [
                    {"link": report_question8_verif.links.all()[0].link},
                    {"link": report_question8_verif.links.all()[0].link}
                ]
            }],
            format='json'
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Response code is not 400'
        )
        assert response.data == {
            "links": [
                "Указаны одинаковые ссылки."
            ]
        }, 'Response data is not correct'
