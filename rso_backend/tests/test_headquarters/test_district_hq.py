from http import HTTPStatus

import pytest
from tests.test_headquarters.conftest import user_with_position_in_district_hq


@pytest.mark.django_db
class TestDistrictHQPositions:
    payload = {
        'user': user_with_position_in_district_hq,
        'position': 1,
        'is_trusted': True
    }

    def test_get_district_hq_memberships_commander(
            self, client, district_hq_1a, user_with_position_in_district_hq,
            authenticated_distr_commander_1a, district_hq_positions,

    ):
        """Получение списка участников окружн. штаба командиром штаба.

        Тест выведен в отдельный для проверки ответа сериализатора,
        который не проверяется у остальных ролей.
        """

        response = authenticated_distr_commander_1a.get(
            f'/api/v1/districts/{district_hq_1a.pk}'
            f'/members/{district_hq_positions[0].pk}/',
        )

        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200.'
        )

        expected_keys = ['id', 'user', 'position', 'is_trusted']
        assert set(response.data.keys()) == set(expected_keys), (
            'Ответ сериализатора не содержит все необходимые поля.'
        )
        expected_keys = [
            'id',
            'username',
            'avatar',
            'email',
            'first_name',
            'last_name',
            'patronymic_name',
            'date_of_birth',
            'membership_fee',
            'is_verified'
        ]
        assert set(response.data['user'].keys()) == set(expected_keys), (
            'Ответ сериализатора поля user не содержит все необходимые поля.'
        )
        assert response.data['user']['username'] == (
            user_with_position_in_district_hq.username
        ), 'В ответе нет участника с должностью в штабе.'

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
    def test_get_district_hq_memberships(
            self, client, central_hq, district_hq_1a, district_hq_1b,
            regional_hq_1a, regional_hq_1b, local_hq_1a, local_hq_1b,
            edu_hq_1a, edu_hq_1b, detachment_1a, detachment_1b,
            client_name, request, district_hq_positions,
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
        Получение списка участников окружного штаба
        юзерами с разными ролями.
        """

        test_client = request.getfixturevalue(client_name)
        response = test_client.get(
            f'/api/v1/districts/{district_hq_1a.pk}'
            f'/members/{district_hq_positions[0].pk}/',
        )

        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200.'
        )
        expected_keys = ['id', 'user', 'position', 'is_trusted']
        assert set(response.data.keys()) == set(expected_keys), (
            'Ответ сериализатора не содержит все необходимые поля.'
        )
        assert response.data['user']['username'] == (
            user_with_position_in_district_hq.username
        ), 'В ответе нет участника с должностью в окружном штабе.'

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
            'authenticated_trusted_in_centr_hq',
            'authenticated_centr_commander',
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
            'authenticated_trusted_in_regional_hq',
            'authenticated_regional_commander_1a',
        ]
    )
    def test_bad_upd_del_district_hq_memberships(
        self, client, central_hq, district_hq_1a, district_hq_1b,
        regional_hq_1a, regional_hq_1b, local_hq_1a, local_hq_1b,
        edu_hq_1a, edu_hq_1b, detachment_1a, detachment_1b,
        client_name, request, district_hq_positions,
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
        """
        Плохая попытка изменения/удаления позиции участника Окр. штаба.

        В тесте принимают участие все роли юзеров, кроме:
        - командира окружного штаба 1а;
        - доверенного члена окружного штаба 1a;
        - анонима
        """

        self.payload['position'] = 2
        test_client = request.getfixturevalue(client_name)
        response = test_client.patch(
            f'/api/v1/districts/{district_hq_1a.pk}'
            f'/members/{district_hq_positions[0].pk}/',
            self.payload
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Response code is not 403.'
        )
        response = test_client.put(
            f'/api/v1/districts/{district_hq_1a.pk}'
            f'/members/{district_hq_positions[0].pk}/',
            self.payload
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Response code is not 403.'
        )

        response = test_client.delete(
            f'/api/v1/districts/{district_hq_1a.pk}'
            f'/members/{district_hq_positions[0].pk}/',
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Response code is not 403.'
        )

    def test_anon_upd_del_district_hq_memberships(
        self, client, district_hq_1a, district_hq_positions
    ):
        """Аноним пытается изменить/удалить позицию участника Окр. штаба."""

        self.payload['position'] = 2
        response = client.patch(
            f'/api/v1/districts/{district_hq_1a.pk}'
            f'/members/{district_hq_positions[0].pk}/',
            self.payload
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Response code is not 401.'
        )

        self.payload['position'] = 3
        response = client.put(
            f'/api/v1/districts/{district_hq_1a.pk}'
            f'/members/{district_hq_positions[0].pk}/',
            self.payload
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Response code is not 401.'
        )

        response = client.delete(
            f'/api/v1/districts/{district_hq_1a.pk}'
            f'/members/{district_hq_positions[0].pk}/',
            self.payload
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Response code is not 401.'
        )

    @pytest.mark.parametrize(
        'client_name', [
            'authenticated_trusted_in_district_hq',
            'authenticated_distr_commander_1a',
        ]
    )
    def test_good_upd_del_district_hq_memberships(
        self, client_name, request, district_hq_1a, district_hq_positions,
        positions_for_detachments, distr_commander_1a,
        user_trusted_in_district_hq, client
    ):
        """
        Проверка изменения/удаления позиции участника окружного штаба.

        Действующие лица, которым разрешен update:
        - командира  окружного штаба 1a;
        - доверенного члена окружного штаба 1a.
        DELETE запрещен и это тоже проверяем здесь.
        """

        test_client = request.getfixturevalue(client_name)
        self.payload['position'] = 2
        response = test_client.put(
            f'/api/v1/districts/{district_hq_1a.pk}'
            f'/members/{district_hq_positions[0].pk}/',
            self.payload
        )
        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200.'
        )
        assert response.data['position']['id'] == (
            self.payload['position']
        ), 'Position is not changed.'

        self.payload['position'] = 3
        response = test_client.patch(
            f'/api/v1/districts/{district_hq_1a.pk}'
            f'/members/{district_hq_positions[0].pk}/',
            self.payload
        )
        assert response.status_code == HTTPStatus.OK, (
            'Response code is not 200.'
        )
        assert response.data['position']['id'] == (
            self.payload['position']
        ), 'Position is not changed.'

        response = test_client.delete(
            f'/api/v1/districts/{district_hq_1a.pk}'
            f'/members/{district_hq_positions[0].pk}/',
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Response code is not 403.'
        )
