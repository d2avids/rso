# from http import HTTPStatus
# import pytest

# from competitions.models import ParticipationInAllRussianEvents, ParticipationInDistrAndInterregEvents, PrizePlacesInAllRussianEvents, PrizePlacesInAllRussianLaborProjects, PrizePlacesInDistrAndInterregEvents, PrizePlacesInDistrAndInterregLaborProjects, Score


# @pytest.mark.django_db(transaction=True, reset_sequences=True)
# class TestThrough:
#     """Сквозное тестирование, + тест таблицы Score."""

#     report_7_to_8 = {
#         "event_name": "Мероприятие New",
#         "number_of_participants": 10,
#         "links": [
#             {
#                 "link": "http://127.0.0.1:8000/swagger/"
#             },
#             {
#                 "link": "http://127.0.0.1:8000/api/v1/competitions/"
#             }
#         ]
#     }
#     competition_url = '/api/v1/competitions/'
#     question_url = [
#         '/reports/participation_in_distr_and_interreg_events/',
#         '/reports/participation_in_all_russian_events/',
#         '/reports/prize_places_in_distr_and_interreg_events/',
#         '/reports/prize_places_in_all_russian_events/',
#         '/reports/prize_places_in_distr_and_interreg_labor_projects/',
#         '/reports/prize_places_in_all_russian_labor_projects/'
#     ]
#     report_9_to_12 = {
#         "event_name": "Мероприятие New",
#         "prize_place": 2
#     }

#     def test_through_7_to_12_create(
#         self, authenticated_client_5, participants_competition_start,
#         competition, junior_detachment_3, report_question7_verif2,
#         report_question8_verif2, report_question9_verif2,
#         report_question10_verif2, report_question11_verif2,
#         report_question12_verif2,
#         authenticated_client_commissar_regional_headquarter
#     ):
#         """
#         Сквозной тест, последовательное создание отчетов по параметрам
#         от 7 по 12 включительно и проверка их наличие в БД.
#         Проверяет, что ничего не наслаивается и не сохраняется туда, куда
#         не нужно.
#         Также проверяет, что сигнал корректно отрабатывает и очки корректно
#         пересчитываются.
#         Исходные: у отряда-участника есть верифицированные заявки по
#         каждому вопросу.
#         Действия в тесте: отряд создает новые заявки, эти заявки верифицирует
#         рег комиссар.
#         Проверяем: заявка создалась, статус ее верификации отрицательный,
#         проверяем что в таблице очков нет записи,  подтверждаем отчеты,
#         проверяем, что очки пересчитались.
#         """
#         response = authenticated_client_5.post(
#                 f'{self.competition_url}{competition.id}'
#                 f'{self.question_url[0]}', data=self.report_7_to_8,
#                 format='json'
#             )
#         assert response.status_code == HTTPStatus.CREATED, (
#             'Response code is not 201'
#         )
#         reports_7 = ParticipationInDistrAndInterregEvents.objects.filter(
#             competition=competition,
#             detachment=junior_detachment_3
#         ).all()
#         assert len(reports_7) == 2, (
#             'В question 9 количество отчетов не соответствует ожидаемому'
#         )
#         assert reports_7[1].is_verified is False, (
#             'В question 9 отчет ошибочно верифицирован при создании.'
#         )
#         assert reports_7[0].is_verified is True, (
#             'В question 9 отчет ошибочно верифицирован при создании.'
#         )

#         response = authenticated_client_5.post(
#             f'{self.competition_url}{competition.id}'
#             f'{self.question_url[1]}', data=self.report_7_to_8, format='json'
#         )
#         assert response.status_code == HTTPStatus.CREATED, (
#             'Response code is not 201'
#         )
#         reports_8 = ParticipationInAllRussianEvents.objects.filter(
#             competition=competition,
#             detachment=junior_detachment_3
#         ).all()
#         assert len(reports_8) == 2, (
#             'В question 9 количество отчетов не соответствует ожидаемому'
#         )
#         assert reports_8[1].is_verified is False, (
#             'В question 9 отчет ошибочно верифицирован при создании.'
#         )

#         response = authenticated_client_5.post(
#             f'{self.competition_url}{competition.id}'
#             f'{self.question_url[2]}', data=self.report_9_to_12, format='json'
#         )
#         assert response.status_code == HTTPStatus.CREATED, (
#             'Response code is not 201'
#         )
#         reports_9 = PrizePlacesInDistrAndInterregEvents.objects.filter(
#             competition=competition,
#             detachment=junior_detachment_3
#         ).all()
#         assert len(reports_9) == 2, (
#             'В question 9 количество отчетов не соответствует ожидаемому'
#         )
#         assert reports_9[1].is_verified is False, (
#             'В question 9 отчет ошибочно верифицирован при создании.'
#         )

#         response = authenticated_client_5.post(
#             f'{self.competition_url}{competition.id}'
#             f'{self.question_url[3]}', data=self.report_9_to_12, format='json'
#         )
#         assert response.status_code == HTTPStatus.CREATED, (
#             'Response code is not 201'
#         )
#         reports_10 = PrizePlacesInAllRussianEvents.objects.filter(
#             competition=competition,
#             detachment=junior_detachment_3
#         ).all()
#         assert len(reports_10) == 2, (
#             'В question 10 количество отчетов не соответствует ожидаемому'
#         )
#         assert reports_10[1].is_verified is False, (
#             'В question 10 отчет ошибочно верифицирован при создании.'
#         )

#         response = authenticated_client_5.post(
#             f'{self.competition_url}{competition.id}'
#             f'{self.question_url[4]}', data=self.report_9_to_12, format='json'
#         )
#         assert response.status_code == HTTPStatus.CREATED, (
#             'Response code is not 201'
#         )
#         reports_11 = PrizePlacesInDistrAndInterregLaborProjects.objects.filter(
#             competition=competition,
#             detachment=junior_detachment_3
#         ).all()
#         assert len(reports_11) == 2, (
#             'В question 11 количество отчетов не соответствует ожидаемому'
#         )
#         assert reports_11[1].is_verified is False, (
#             'В question 11 отчет ошибочно верифицирован при создании.'
#         )

#         response = authenticated_client_5.post(
#             f'{self.competition_url}{competition.id}'
#             f'{self.question_url[5]}', data=self.report_9_to_12, format='json'
#         )
#         assert response.status_code == HTTPStatus.CREATED, (
#             'Response code is not 201'
#         )
#         reports_12 = PrizePlacesInAllRussianLaborProjects.objects.filter(
#             competition=competition,
#             detachment=junior_detachment_3
#         ).all()
#         assert len(reports_12) == 2, (
#             'В question 12 количество отчетов не соответствует ожидаемому'
#         )
#         assert reports_12[1].is_verified is False, (
#             'В question 12 отчет ошибочно верифицирован при создании.'
#         )

#         score = Score.objects.filter(
#             competition=competition,
#             detachment=junior_detachment_3
#         ).all()
#         # сигнал не срабатывает при первичном сохранении с is_verified=True,
#         # поэтому тут ноль при наличии уже верифицированных отчетах(фикстура)
#         assert len(score) == 0, (
#             'В таблице Score создались записи без согласования рег.коммиссара'
#         )
#         # Подтверждение рег.командиром.
#         for i in range(6):
#             response = authenticated_client_commissar_regional_headquarter.post(
#                 f'{self.competition_url}{competition.id}'
#                 f'{self.question_url[i]}2/accept/'
#             )
#         score = Score.objects.filter(
#             competition=competition,
#             detachment=junior_detachment_3
#         ).all()
#         assert len(score) == 1, (
#             'В таблице Score создалось несколько строк по одному отряду'
#         )
#         score = score[0]
#         assert (score.participation_in_distr_and_interreg_events ==
#                 reports_7[1].number_of_participants +
#                 reports_7[0].number_of_participants), (
#             'В таблице Score по вопросу 7 сумма участников отличается '
#             'от ожидаемого'
#         )
#         assert (score.participation_in_all_russian_events ==
#                 reports_8[1].number_of_participants +
#                 reports_8[0].number_of_participants), (
#             'В таблице Score по вопросу 8 сумма участников отличается '
#             'от ожидаемого'
#         )
#         assert (score.prize_places_in_distr_and_interreg_events ==
#                 (reports_9[1].prize_place +
#                  reports_9[0].prize_place)/2), (
#             'В таблице Score по вопросу 9 среднее очков отличается '
#             'от ожидаемого'
#         )
#         assert (score.prize_places_in_all_russian_events ==
#                 (reports_10[1].prize_place +
#                  reports_10[0].prize_place)/2), (
#             'В таблице Score по вопросу 10 среднее очков отличается '
#             'от ожидаемого'
#         )
#         assert (score.prize_places_in_distr_and_interreg_labor_projects ==
#                 (reports_11[1].prize_place +
#                  reports_11[0].prize_place)/2), (
#             'В таблице Score по вопросу 11 среднее очков отличается '
#             'от ожидаемого'
#         )
#         assert (score.prize_places_in_all_russian_labor_projects ==
#                 (reports_12[1].prize_place +
#                  reports_12[0].prize_place)/2), (
#             'В таблице Score по вопросу 12 среднее очков отличается '
#             'от ожидаемого'
#         )
