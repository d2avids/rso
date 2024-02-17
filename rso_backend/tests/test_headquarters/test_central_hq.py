import datetime

from http import HTTPStatus

import pytest
from django.conf import settings

from headquarters.models import Position
from tests.test_headquarters.conftest import user_with_position_in_centr_hq
from tests.conftest import (CENTRAL_HEADQUARTER_NAME,
                            DETACHMENTS_APPEARANCE_YEAR,
                            RSO_FOUNDING_CONGRESS_DATE)


@pytest.mark.django_db
def test_central_hq(client, central_headquarter):
    response = client.get('/api/v1/centrals/')
    assert response.status_code == 200, 'Central HQs are not available'


@pytest.mark.django_db
def test_detailed_central_hq(client, central_headquarter):
    response = client.get('/api/v1/centrals/1/')
    assert response.status_code == 200, 'Central HQ is not available'
    data = response.data
    assert data.get(
        'name'
    ) == CENTRAL_HEADQUARTER_NAME, 'Central HQ name is not correct'
    assert data.get(
        'detachments_appearance_year'
    ) == DETACHMENTS_APPEARANCE_YEAR, (
        'Detachments appearance year is not correct'
    )
    assert data.get(
        'rso_founding_congress_date'
    ) == RSO_FOUNDING_CONGRESS_DATE, 'Founding congress date is not correct'
    assert data.get(
        'working_years'
    ) == (
        datetime.date.today().year -
        settings.CENTRAL_HEADQUARTER_FOUNDING_DATE
    ), 'Working years value is not correct'
    assert 'members_count' in data, 'Members count is missing'
    assert 'participants_count' in data, 'Participants count is missing'


@pytest.mark.django_db
def test_central_hq_members(client, central_headquarter):
    response = client.get('/api/v1/centrals/1/members/')
    assert response.status_code == 200, '/members/ is not available'

##TODO: запись должности не создается. Разобраться с созданием
## и затем раскомментировать класс с тестами.

# class TestCentralHQPositions:
#     payload = {
#         'user': user_with_position_in_centr_hq,
#         'position': 1,
#         'is_trusted': True
#     }

#     @pytest.mark.parametrize(
#         'client_name',
#         [
#             'client',
#             'authenticated_unverified',
#             'authenticated_user_with_position_in_detachment',
#             'authenticated_user_with_position_in_edu_hq',
#             'authenticated_user_with_position_in_local_hq',
#             'authenticated_user_with_position_in_regional_hq',
#             'authenticated_user_with_position_in_distr_hq',
#             'authenticated_user_with_position_in_centr_hq',
#             'authenticated_trusted_in_detachment',
#             'authenticated_trusted_in_edu_hq',
#             'authenticated_trusted_in_local_hq',
#             'authenticated_trusted_in_regional_hq',
#             'authenticated_trusted_in_district_hq',
#             'authenticated_trusted_in_centr_hq',
#             'authenticated_centr_commander',
#             'authenticated_distr_commander_1a',
#             'authenticated_distr_commander_1b',
#             'authenticated_regional_commander_1a',
#             'authenticated_regional_commander_1b',
#             'authenticated_local_commander_1a',
#             'authenticated_local_commander_1b',
#             'authenticated_edu_commander_1a',
#             'authenticated_edu_commander_1b',
#             'authenticated_det_com_1a',
#             'authenticated_det_com_1b',
#             'admin_client',
#         ]
#     )
#     @pytest.mark.django_db
#     def test_get_central_hq_memberships(
#             self, client, central_hq, district_hq_1a, district_hq_1b,
#             regional_hq_1a, regional_hq_1b, local_hq_1a, local_hq_1b,
#             edu_hq_1a, edu_hq_1b, detachment_1a, detachment_1b,
#             client_name, request, central_hq_positions,
#             user_with_position_in_detachment, user_with_position_in_edu_hq,
#             user_with_position_in_local_hq, user_with_position_in_regional_hq,
#             user_with_position_in_district_hq, user_with_position_in_centr_hq,
#             user_trusted_in_detachment, user_trusted_in_edu_hq,
#             user_trusted_in_local_hq, user_trusted_in_regional_hq,
#             user_trusted_in_district_hq, user_trusted_in_centr_hq,
#             detachment_commander_1a, detachment_commander_1b,
#             edu_commander_1a, edu_commander_1b, local_commander_1a,
#             local_commander_1b, regional_commander_1a, regional_commander_1b,
#             distr_commander_1a, distr_commander_1b, centr_commander
#     ):
#         """
#         Получение списка участников центрального штаба
#         юзерами с разными ролями.
#         """

#         test_client = request.getfixturevalue(client_name)
#         print(central_hq_positions[0], central_hq_positions[0].pk)
#         response = test_client.get(
#             f'/api/v1/centrals/{central_hq.pk}'
#             f'/members/{central_hq_positions[0].pk}/',
#         )

#         assert response.status_code == HTTPStatus.OK, (
#             'Response code is not 200.'
#         )

#         assert response.data['user']['username'] == (
#             user_with_position_in_centr_hq.username
#         ), 'В ответе нет участника с должностью в окружном штабе.'

#     @pytest.mark.parametrize(
#         'client_name',
#         [
#             'authenticated_unverified',
#             'authenticated_user_with_position_in_detachment',
#             'authenticated_user_with_position_in_edu_hq',
#             'authenticated_user_with_position_in_local_hq',
#             'authenticated_user_with_position_in_regional_hq',
#             'authenticated_user_with_position_in_distr_hq',
#             'authenticated_user_with_position_in_centr_hq',
#             'authenticated_trusted_in_detachment',
#             'authenticated_trusted_in_edu_hq',
#             'authenticated_distr_commander_1b',
#             'authenticated_regional_commander_1b',
#             'authenticated_edu_commander_1a',
#             'authenticated_local_commander_1b',
#             'authenticated_det_com_1a',
#             'authenticated_edu_commander_1b',
#             'authenticated_det_com_1b',
#             'admin_client',
#             'authenticated_trusted_in_local_hq',
#             'authenticated_local_commander_1a',
#             'authenticated_trusted_in_regional_hq',
#             'authenticated_regional_commander_1a',
#             'authenticated_trusted_in_district_hq',
#             'authenticated_distr_commander_1a',
#         ]
#     )
#     @pytest.mark.django_db
#     def test_bad_upd_del_central_hq_memberships(
#         self, client, central_hq, district_hq_1a, district_hq_1b,
#         regional_hq_1a, regional_hq_1b, local_hq_1a, local_hq_1b,
#         edu_hq_1a, edu_hq_1b, detachment_1a, detachment_1b,
#         client_name, request, central_hq_positions,
#         user_with_position_in_detachment, user_with_position_in_edu_hq,
#         user_with_position_in_local_hq, user_with_position_in_regional_hq,
#         user_with_position_in_district_hq, user_with_position_in_centr_hq,
#         user_trusted_in_detachment, user_trusted_in_centr_hq,
#         user_trusted_in_local_hq, user_trusted_in_regional_hq,
#         user_trusted_in_district_hq, centr_commander,
#         detachment_commander_1a, detachment_commander_1b,
#         edu_commander_1b, local_commander_1a, distr_commander_1b,
#         local_commander_1b, regional_commander_1a, regional_commander_1b,
#         distr_commander_1a,
#     ):
#         """Плохая попытка изменения/удаления позиции участника ЦШ.

#         В тесте принимают участие все роли юзеров, кроме:
#         - командира центрального штаба 1а;
#         - доверенного члена центрального штаба 1a;
#         - анонима
#         """

#         self.payload['position'] = 2
#         test_client = request.getfixturevalue(client_name)
#         response = test_client.patch(
#             f'/api/v1/centrals/{central_hq.pk}'
#             f'/members/{central_hq_positions[0].pk}/',
#             self.payload
#         )
#         assert response.status_code == HTTPStatus.FORBIDDEN, (
#             'Response code is not 403.'
#         )
#         response = test_client.put(
#             f'/api/v1/centrals/{central_hq.pk}'
#             f'/members/{central_hq_positions[0].pk}/',
#             self.payload
#         )
#         assert response.status_code == HTTPStatus.FORBIDDEN, (
#             'Response code is not 403.'
#         )

#         response = test_client.delete(
#             f'/api/v1/centrals/{central_hq.pk}'
#             f'/members/{central_hq_positions[0].pk}/',
#         )
#         assert response.status_code == HTTPStatus.FORBIDDEN, (
#             'Response code is not 403.'
#         )

#     @pytest.mark.django_db
#     def test_anon_upd_del_central_hq_memberships(
#         self, client, central_hq, central_hq_positions
#     ):
#         """Аноним пытается изменить/удалить позицию участника ЦШ."""

#         self.payload['position'] = 2
#         response = client.patch(
#             f'/api/v1/centrals/{central_hq.pk}'
#             f'/members/{central_hq_positions[0].pk}/',
#             self.payload
#         )
#         assert response.status_code == HTTPStatus.UNAUTHORIZED, (
#             'Response code is not 401.'
#         )

#         self.payload['position'] = 3
#         response = client.put(
#             f'/api/v1/centrals/{central_hq.pk}'
#             f'/members/{central_hq_positions[0].pk}/',
#             self.payload
#         )
#         assert response.status_code == HTTPStatus.UNAUTHORIZED, (
#             'Response code is not 401.'
#         )

#         response = client.delete(
#             f'/api/v1/centrals/{central_hq.pk}'
#             f'/members/{central_hq_positions[0].pk}/',
#             self.payload
#         )
#         assert response.status_code == HTTPStatus.UNAUTHORIZED, (
#             'Response code is not 401.'
#         )

#     @pytest.mark.parametrize(
#         'client_name', [
#             'authenticated_trusted_in_centr_hq',
#             'authenticated_centr_commander',
#         ]
#     )
#     @pytest.mark.django_db
#     def test_good_upd_del_central_hq_memberships(
#         self, client_name, request, central_hq, central_hq_positions,
#         positions_for_detachments, centr_commander,
#         user_trusted_in_centr_hq, client
#     ):
#         """Проверка изменения/удаления позиции участника центрального штаба.

#         Действующие лица, которым разрешен update:
#         - командира  центрального штаба 1a;
#         - доверенного члена центрального штаба 1a.
#         DELETE запрещен и это тоже проверяем здесь.
#         """

#         test_client = request.getfixturevalue(client_name)
#         self.payload['position'] = 2
#         response = test_client.put(
#             f'/api/v1/centrals/{central_hq.pk}'
#             f'/members/{central_hq_positions[0].pk}/',
#             self.payload
#         )
#         assert response.status_code == HTTPStatus.OK, (
#             'Response code is not 200.'
#         )
#         assert response.data['position']['name'] == (
#             Position.objects.get(pk=2).name
#         ), 'Position is not changed.'

#         self.payload['position'] = 3
#         response = test_client.patch(
#             f'/api/v1/centrals/{central_hq.pk}'
#             f'/members/{central_hq_positions[0].pk}/',
#             self.payload
#         )
#         assert response.status_code == HTTPStatus.OK, (
#             'Response code is not 200.'
#         )
#         assert response.data['position']['name'] == (
#             Position.objects.get(pk=3).name
#         ), 'Position is not changed.'

#         response = test_client.delete(
#             f'/api/v1/centrals/{central_hq.pk}'
#             f'/members/{central_hq_positions[0].pk}/',
#         )
#         assert response.status_code == HTTPStatus.FORBIDDEN, (
#             'Response code is not 403.'
#         )
