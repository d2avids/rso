import pytest

from http import HTTPStatus

from headquarters.models import Position
from tests.test_headquarters.conftest import user_with_position_in_detachment


class TestDetachmentsPositions:
    payload = {
        'user': user_with_position_in_detachment,
        'position': 1,
        'is_trusted': True
    }

    @pytest.mark.parametrize(
        'client_name',
        [
            'client',
            'authenticated_unverified',
            'authenticated_user_with_position_in_detachment',
            'authenticated_user_with_position_in_edu_hq',
            'authenticated_user_with_position_in_local_hq',
            'authenticated_user_with_position_in_regional_hq',
            'authenticated_user_with_position_in_distr_hq',
            'authenticated_user_with_position_in_centr_hq',
            'authenticated_trusted_in_detachment',
            'authenticated_trusted_in_edu_hq',
            'authenticated_trusted_in_local_hq',
            'authenticated_trusted_in_regional_hq',
            'authenticated_trusted_in_district_hq',
            'authenticated_trusted_in_centr_hq',
            'authenticated_centr_commander',
            'authenticated_distr_commander_1a',
            'authenticated_distr_commander_1b',
            'authenticated_regional_commander_1a',
            'authenticated_regional_commander_1b',
            'authenticated_local_commander_1a',
            'authenticated_local_commander_1b',
            'authenticated_edu_commander_1a',
            'authenticated_edu_commander_1b',
            'authenticated_det_com_1a',
            'authenticated_det_com_1b',
            'admin_client',
        ]
    )
    @pytest.mark.django_db
    def test_get_detachment_memberships(
            self, client, central_hq, district_hq_1a, district_hq_1b,
            regional_hq_1a, regional_hq_1b, local_hq_1a, local_hq_1b,
            edu_hq_1a, edu_hq_1b, detachment_1a, detachment_1b,
            client_name, request, detachment_positions,
            user_with_position_in_detachment, user_with_position_in_edu_hq,
            user_with_position_in_local_hq, user_with_position_in_regional_hq,
            user_with_position_in_district_hq, user_with_position_in_centr_hq,
            user_trusted_in_detachment, user_trusted_in_edu_hq,
            user_trusted_in_local_hq, user_trusted_in_regional_hq,
            user_trusted_in_district_hq, user_trusted_in_centr_hq,
            detachment_commander_1a, detachment_commander_1b,
            edu_commander_1a, edu_commander_1b, local_commander_1a,
            local_commander_1b, regional_commander_1a, regional_commander_1b,
            distr_commander_1a, distr_commander_1b, centr_commander
    ):
        """Получение списка участников отряда юзерами с разными ролями."""

        test_client = request.getfixturevalue(client_name)
        response = test_client.get(
            f'/api/v1/detachments/{detachment_1a.pk}'
            f'/members/{detachment_positions[0].pk}/'
        )

        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200.'
        )

        assert response.data['user']['username'] == (
            user_with_position_in_detachment.username
        ), 'В ответе нет участника с должностью в отряде.'

    @pytest.mark.parametrize(
        'client_name',
        [
            'authenticated_unverified',
            'authenticated_user_with_position_in_detachment',
            'authenticated_user_with_position_in_edu_hq',
            'authenticated_user_with_position_in_local_hq',
            'authenticated_user_with_position_in_regional_hq',
            'authenticated_user_with_position_in_distr_hq',
            'authenticated_user_with_position_in_centr_hq',
            'authenticated_trusted_in_edu_hq',
            'authenticated_trusted_in_local_hq',
            'authenticated_trusted_in_regional_hq',
            'authenticated_trusted_in_district_hq',
            'authenticated_trusted_in_centr_hq',
            'authenticated_centr_commander',
            'authenticated_distr_commander_1a',
            'authenticated_distr_commander_1b',
            'authenticated_regional_commander_1a',
            'authenticated_regional_commander_1b',
            'authenticated_local_commander_1a',
            'authenticated_local_commander_1b',
            'authenticated_edu_commander_1a',
            'authenticated_edu_commander_1b',
            'authenticated_det_com_1b',
            'admin_client',
        ]
    )
    @pytest.mark.django_db
    def test_bad_upd_del_detachment_memberships(
        self, client, central_hq, district_hq_1a, district_hq_1b,
        regional_hq_1a, regional_hq_1b, local_hq_1a, local_hq_1b,
        edu_hq_1a, edu_hq_1b, detachment_1a, detachment_1b,
        client_name, request, detachment_positions,
        user_with_position_in_detachment, user_with_position_in_edu_hq,
        user_with_position_in_local_hq, user_with_position_in_regional_hq,
        user_with_position_in_district_hq, user_with_position_in_centr_hq,
        user_trusted_in_edu_hq, user_trusted_in_centr_hq,
        user_trusted_in_local_hq, user_trusted_in_regional_hq,
        user_trusted_in_district_hq
    ):
        """Плохая попытка изменения/удаления позиции участника отряда.

        В тесте принимают участие все роли юзеров, кроме:
        - командира отряда 1а;
        - доверенного члена отряда 1a;
        - анонима
        """

        self.payload['position'] = 2
        test_client = request.getfixturevalue(client_name)
        response = test_client.patch(
            f'/api/v1/detachments/{detachment_1a.pk}'
            f'/members/{detachment_positions[0].pk}/',
            self.payload
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Response code is not 403.'
        )
        response = test_client.put(
            f'/api/v1/detachments/{detachment_1a.pk}'
            f'/members/{detachment_positions[0].pk}/',
            self.payload
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Response code is not 403.'
        )

        response = test_client.delete(
            f'/api/v1/detachments/{detachment_1a.pk}'
            f'/members/{detachment_positions[0].pk}/'
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Response code is not 403.'
        )


    @pytest.mark.django_db
    def test_anon_upd_del_detachment_memberships(
        self, client, detachment_1a, detachment_positions
    ):
        """Аноним пытается изменить/удалить позицию участника отряда."""

        self.payload['position'] = 2
        response = client.patch(
            f'/api/v1/detachments/{detachment_1a.pk}'
            f'/members/{detachment_positions[0].pk}/',
            self.payload
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Response code is not 401.'
        )

        self.payload['position'] = 2
        response = client.put(
            f'/api/v1/detachments/{detachment_1a.pk}'
            f'/members/{detachment_positions[0].pk}/',
            self.payload
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Response code is not 401.'
        )

        response = client.delete(
            f'/api/v1/detachments/{detachment_1a.pk}'
            f'/members/{detachment_positions[0].pk}/',
            self.payload
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Response code is not 401.'
        )

    @pytest.mark.parametrize(
        'client_name', [
            'authenticated_trusted_in_detachment',
            'authenticated_det_com_1a',
        ]
    )
    @pytest.mark.django_db
    def test_good_upd_del_detachment_memberships(
        self, client_name, request, detachment_1a, detachment_positions,
        positions_for_detachments, detachment_commander_1a,
        user_trusted_in_detachment, client
    ):
        """Проверка изменения/удаления позиции участника отряда.

        Действующие лица, которым разрешен update:
        - командира отряда 1a;
        - доверенного члена отряда 1a.
        DELETE запрещен и это тоже проверяем здесь.
        """

        test_client = request.getfixturevalue(client_name)
        self.payload['position'] = 2
        response = test_client.put(
            f'/api/v1/detachments/{detachment_1a.pk}'
            f'/members/{detachment_positions[0].pk}/',
            self.payload
        )
        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200.'
        )
        assert response.data['position']['name'] == (
            Position.objects.get(pk=2).name
        ), 'Position is not changed.'

        self.payload['position'] = 3
        response = test_client.patch(
            f'/api/v1/detachments/{detachment_1a.pk}'
            f'/members/{detachment_positions[0].pk}/',
            self.payload
        )
        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200.'
        )
        assert response.data['position']['name'] == (
            Position.objects.get(pk=3).name
        ), 'Position is not changed.'

        response = test_client.delete(
            f'/api/v1/detachments/{detachment_1a.pk}'
            f'/members/{detachment_positions[0].pk}/',
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Response code is not 403.'
        )
