import pytest

from http import HTTPStatus

from headquarters.models import Position
from tests.test_headquarters.conftest import user_with_position_in_regional_hq


class TestRegionalHQPositions:
    payload = {
        'user': user_with_position_in_regional_hq,
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
    def test_get_regional_hq_memberships(
            self, client, central_hq, district_hq_1a, district_hq_1b,
            regional_hq_1a, regional_hq_1b, local_hq_1a, local_hq_1b,
            edu_hq_1a, edu_hq_1b, detachment_1a, detachment_1b,
            client_name, request, regional_hq_positions,
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
        """
        Получение списка участников регионального штаба
        юзерами с разными ролями.
        """

        test_client = request.getfixturevalue(client_name)
        response = test_client.get(
            f'/api/v1/regionals/{regional_hq_1a.pk}'
            f'/members/{regional_hq_positions[0].pk}/',
        )

        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200.'
        )

        assert response.data['user']['username'] == (
            user_with_position_in_regional_hq.username
        ), 'В ответе нет участника с должностью в региональном штабе.'

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
            'authenticated_trusted_in_detachment',
            'authenticated_trusted_in_edu_hq',
            'authenticated_trusted_in_district_hq',
            'authenticated_trusted_in_centr_hq',
            'authenticated_centr_commander',
            'authenticated_distr_commander_1a',
            'authenticated_distr_commander_1b',
            'authenticated_regional_commander_1b',
            'authenticated_edu_commander_1a',
            'authenticated_local_commander_1b',
            'authenticated_det_com_1a',
            'authenticated_edu_commander_1b',
            'authenticated_det_com_1b',
            'admin_client',
            'authenticated_trusted_in_local_hq',
            'authenticated_local_commander_1a',
        ]
    )
    @pytest.mark.django_db
    def test_bad_upd_del_regional_hq_memberships(
        self, client, central_hq, district_hq_1a, district_hq_1b,
        regional_hq_1a, regional_hq_1b, local_hq_1a, local_hq_1b,
        edu_hq_1a, edu_hq_1b, detachment_1a, detachment_1b,
        client_name, request, regional_hq_positions,
        user_with_position_in_detachment, user_with_position_in_edu_hq,
        user_with_position_in_local_hq, user_with_position_in_regional_hq,
        user_with_position_in_district_hq, user_with_position_in_centr_hq,
        user_trusted_in_detachment, user_trusted_in_centr_hq,
        user_trusted_in_local_hq, user_trusted_in_regional_hq,
        user_trusted_in_district_hq, centr_commander,
        detachment_commander_1a, detachment_commander_1b,
        edu_commander_1b, local_commander_1a, distr_commander_1b,
        local_commander_1b, regional_commander_1a, regional_commander_1b,
        distr_commander_1a,
    ):
        """Плохая попытка изменения/удаления позиции участника Рег. штаба.

        В тесте принимают участие все роли юзеров, кроме:
        - командира региональногоштаба 1а;
        - доверенного члена регионального штаба 1a;
        - анонима
        """

        self.payload['position'] = 2
        test_client = request.getfixturevalue(client_name)
        response = test_client.patch(
            f'/api/v1/regionals/{regional_hq_1a.pk}'
            f'/members/{regional_hq_positions[0].pk}/',
            self.payload
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Response code is not 403.'
        )
        response = test_client.put(
            f'/api/v1/regionals/{regional_hq_1a.pk}'
            f'/members/{regional_hq_positions[0].pk}/',
            self.payload
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Response code is not 403.'
        )

        response = test_client.delete(
            f'/api/v1/regionals/{regional_hq_1a.pk}'
            f'/members/{regional_hq_positions[0].pk}/',
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Response code is not 403.'
        )

    @pytest.mark.django_db
    def test_anon_upd_del_regional_hq_memberships(
        self, client, regional_hq_1a, regional_hq_positions
    ):
        """Аноним пытается изменить/удалить позицию участника рег. штаба."""

        self.payload['position'] = 2
        response = client.patch(
            f'/api/v1/regionals/{regional_hq_1a.pk}'
            f'/members/{regional_hq_positions[0].pk}/',
            self.payload
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Response code is not 401.'
        )

        self.payload['position'] = 3
        response = client.put(
            f'/api/v1/regionals/{regional_hq_1a.pk}'
            f'/members/{regional_hq_positions[0].pk}/',
            self.payload
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Response code is not 401.'
        )

        response = client.delete(
            f'/api/v1/regionals/{regional_hq_1a.pk}'
            f'/members/{regional_hq_positions[0].pk}/',
            self.payload
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Response code is not 401.'
        )

    @pytest.mark.parametrize(
        'client_name', [
            'authenticated_trusted_in_regional_hq',
            'authenticated_regional_commander_1a',
        ]
    )
    @pytest.mark.django_db
    def test_good_upd_del_regional_hq_memberships(
        self, client_name, request, regional_hq_1a, regional_hq_positions,
        positions_for_detachments, regional_commander_1a,
        user_trusted_in_regional_hq, client
    ):
        """Проверка изменения/удаления позиции участника регионального штаба.

        Действующие лица, которым разрешен update:
        - командира  регионального штаба 1a;
        - доверенного члена регионального штаба 1a.
        DELETE запрещен и это тоже проверяем здесь.
        """

        test_client = request.getfixturevalue(client_name)
        self.payload['position'] = 2
        response = test_client.put(
            f'/api/v1/regionals/{regional_hq_1a.pk}'
            f'/members/{regional_hq_positions[0].pk}/',
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
            f'/api/v1/regionals/{regional_hq_1a.pk}'
            f'/members/{regional_hq_positions[0].pk}/',
            self.payload
        )
        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200.'
        )
        assert response.data['position']['name'] == (
            Position.objects.get(pk=3).name
        ), 'Position is not changed.'

        response = test_client.delete(
            f'/api/v1/regionals/{regional_hq_1a.pk}'
            f'/members/{regional_hq_positions[0].pk}/',
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Response code is not 403.'
        )
