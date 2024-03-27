import http
import json

import pytest

# TODO approve/reject different roles
# TODO GET and DELETE group_applications/me/
# TODO different levels of groupapplication events
# TODO applying by group application for not group event


@pytest.mark.django_db
class TestGroupApplicationsDetachment:

    def test_group_applications_detachment_commander(
            self,
            authenticated_det_com_1a,
            detachment_1a,
            detachment_positions,
            user_with_position_in_detachment,
            group_event_detachment
    ):
        response = authenticated_det_com_1a.get(
            '/api/v1/events/1/group_applications/'
        )
        assert response.status_code == http.HTTPStatus.OK, (
            'Response code is not 200'
        )
        assert response.data[0].get('username') is not None, (
            'Response data must contain user instances for '
            'detachment commander with users in the unit'
        )
        response = authenticated_det_com_1a.post(
            '/api/v1/events/1/group_applications/',
            json.dumps({'user_ids': [response.data[0].get('id')]}),
            content_type='application/json'
        )
        print(response.json())
        print(response.data)
        assert response.status_code == http.HTTPStatus.CREATED, (
            'Response code after post request is not 201'
        )

    def test_group_applications_anonymous(
        self,
        client,
        group_event_detachment
    ):
        response = client.get(
            '/api/v1/events/1/group_applications/'
        )
        assert response.status_code == http.HTTPStatus.UNAUTHORIZED, (
            'Response code is not 401 for anonymous user'
        )
        response = client.post(
            '/api/v1/events/1/group_applications/',
            json.dumps({'user_ids': [1]}),
            content_type='application/json'
        )
        assert response.status_code == http.HTTPStatus.UNAUTHORIZED, (
            'Response code after post request is not 401'
        )

    def test_group_applications_normal_user(
        self,
        authenticated_client_3,
        group_event_detachment
    ):
        response = authenticated_client_3.get(
            '/api/v1/events/1/group_applications/'
        )
        assert response.status_code == http.HTTPStatus.FORBIDDEN, (
            'Response code is not 403 for not commander'
        )
        response = authenticated_client_3.post(
            '/api/v1/events/1/group_applications/',
            json.dumps({'user_ids': [1]}),
            content_type='application/json'
        )
        assert response.status_code == http.HTTPStatus.FORBIDDEN, (
            'Response code after post request is not 403'
        )

    def test_group_applications_education_hq_commander(
        self,
        authenticated_edu_commander_1a,
        edu_hq_1a,
        group_event_detachment
    ):
        response = authenticated_edu_commander_1a.get(
            '/api/v1/events/1/group_applications/'
        )
        assert response.status_code == http.HTTPStatus.FORBIDDEN, (
            'Response code is not 403 for not detachment commader'
        )
        response = authenticated_edu_commander_1a.post(
            '/api/v1/events/1/group_applications/',
            json.dumps({'user_ids': [1]}),
            content_type='application/json'
        )
        assert response.status_code == http.HTTPStatus.FORBIDDEN, (
            'Response code after post request is not 403'
        )

    def test_group_applications_local_hq_commander(
        self,
        authenticated_local_commander_1a,
        local_hq_1a,
        group_event_detachment
    ):
        response = authenticated_local_commander_1a.get(
            '/api/v1/events/1/group_applications/'
        )
        assert response.status_code == http.HTTPStatus.FORBIDDEN, (
            'Response code is not 403 for not detachment commader'
        )
        response = authenticated_local_commander_1a.post(
            '/api/v1/events/1/group_applications/',
            json.dumps({'user_ids': [1]}),
            content_type='application/json'
        )
        assert response.status_code == http.HTTPStatus.FORBIDDEN, (
            'Response code after post request is not 403'
        )

    def test_group_applications_regional_hq_commander(
        self,
        authenticated_regional_commander_1a,
        regional_hq_1a,
        group_event_detachment
    ):
        response = authenticated_regional_commander_1a.get(
            '/api/v1/events/1/group_applications/'
        )
        assert response.status_code == http.HTTPStatus.FORBIDDEN, (
            'Response code is not 403 for not detachment commader'
        )
        response = authenticated_regional_commander_1a.post(
            '/api/v1/events/1/group_applications/',
            json.dumps({'user_ids': [1]}),
            content_type='application/json'
        )
        assert response.status_code == http.HTTPStatus.FORBIDDEN, (
            'Response code after post request is not 403'
        )

    def test_group_applications_district_hq_commander(
        self,
        authenticated_distr_commander_1a,
        district_hq_1a,
        group_event_detachment
    ):
        response = authenticated_distr_commander_1a.get(
            '/api/v1/events/1/group_applications/'
        )
        assert response.status_code == http.HTTPStatus.FORBIDDEN, (
            'Response code is not 403 for not detachment commader'
        )
        response = authenticated_distr_commander_1a.post(
            '/api/v1/events/1/group_applications/',
            json.dumps({'user_ids': [1]}),
            content_type='application/json'
        )
        assert response.status_code == http.HTTPStatus.FORBIDDEN, (
            'Response code after post request is not 403'
        )

    def test_group_applications_central_hq_commander(
        self,
        authenticated_centr_commander,
        central_hq,
        group_event_detachment
    ):
        response = authenticated_centr_commander.get(
            '/api/v1/events/1/group_applications/'
        )
        assert response.status_code == http.HTTPStatus.FORBIDDEN, (
            'Response code is not 403 for not detachment commader'
        )
        response = authenticated_centr_commander.post(
            '/api/v1/events/1/group_applications/',
            json.dumps({'user_ids': [1]}),
            content_type='application/json'
        )
        assert response.status_code == http.HTTPStatus.FORBIDDEN, (
            'Response code after post request is not 403'
        )
