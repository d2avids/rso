from http import HTTPStatus
import pytest


class TestEvents:
    event_creation_payload = {
        "format": "Онлайн",
        "direction": "Добровольческое",
        "status": "Активный",
        "name": "string",
        "scale": "Отрядное",
        "conference_link": "string",
        "address": "string",
        "participants_number": 2147483647,
        "description": "string",
        "application_type": "Персональная",
        "available_structural_units": "Отряды"
    }

    @pytest.mark.django_db
    def test_get_events(self, free_authenticated_client):
        response = free_authenticated_client.get('/api/v1/events/')
        assert response.status_code == HTTPStatus.OK, (
            'Should return 200 OK response'
        )

    @pytest.mark.django_db
    def test_post_events_free_client(self, free_authenticated_client):
        response = free_authenticated_client.post(
            '/api/v1/events/', data=self.event_creation_payload
        )
        assert response.status_code == HTTPStatus.FORBIDDEN, (
            'Should return 403 Forbidden response'
        )

    @pytest.mark.django_db
    def test_get_events_anonymous(self, client):
        response = client.get('/api/v1/events/')
        assert response.status_code == HTTPStatus.OK, (
            'Should return 200 OK response'
        )

    @pytest.mark.django_db
    def test_post_events_anonymous(self, client):
        response = client.post(
            '/api/v1/events/', data=self.event_creation_payload
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED, (
            'Should return 401 Unauthorized response'
        )


class TestEventsDetachmentScale:
    event_detachment_scale_payload = {
        "format": "Онлайн",
        "direction": "Добровольческое",
        "status": "Активный",
        "name": "string",
        "scale": "Отрядное",
        "conference_link": "string",
        "address": "string",
        "participants_number": 2147483647,
        "description": "string",
        "application_type": "Персональная",
        "available_structural_units": "Отряды"
    }

    event_edit_document_data_payload = {
        "passport": True,
        "snils": True,
        "inn": True,
        "work_book": True,
        "military_document": True,
        "consent_personal_data": True,
        "additional_info": "string"
    }

    event_edit_time_data_payload = {
        "event_duration_type": "Многодневное",
        "start_date": "2024-02-11",
        "start_time": "string",
        "end_date": "2024-02-11",
        "end_time": "string",
        "registration_end_date": "2024-02-11",
        "registration_end_time": "string"
    }

    @pytest.mark.django_db
    def test_detachment_scale_event_creation(
            self, authenticated_client_6, detachment_3
    ):
        response = authenticated_client_6.post(
            '/api/v1/events/', data=self.event_detachment_scale_payload
        )
        assert response.status_code == HTTPStatus.CREATED, (
            'Should return 201 Created response'
        )
        response = authenticated_client_6.get('/api/v1/events/1/')
        assert response.status_code == HTTPStatus.OK, (
            'Should return 200 OK response'
        )
        data = response.data
        assert 'time_data' in data and isinstance(data['time_data'], dict), (
            'Should return dict with time_data'
        )
        assert 'document_data' in data and isinstance(
            data['time_data'], dict
        ), 'Should return dict with time_data'
        assert 'documents' in data and isinstance(
            data['documents'], list
        ), 'Should return list with documents'
        assert 'organization_data' in data and isinstance(
            data['organization_data'], list
        ), 'Should return list with organization_data'
        assert 'additional_issues' in data and isinstance(
            data['additional_issues'], list
        ), 'Should return list with additional_issues'

    @pytest.mark.django_db
    def test_detachment_scale_edit_time_data(
            self, authenticated_client_6, event_detachment
    ):
        response = authenticated_client_6.put(
            '/api/v1/events/1/time_data/',
            data=self.event_edit_time_data_payload
        )
        assert response.status_code == HTTPStatus.OK, (
            'Should return 200 response'
        )
        data = response.data
        assert data == self.event_edit_time_data_payload

    @pytest.mark.django_db
    def test_detachment_scale_edit_document_data(
            self, authenticated_client_6, event_detachment, user_6
    ):
        response = authenticated_client_6.put(
            '/api/v1/events/1/document_data/',
            data=self.event_edit_document_data_payload
        )
        assert response.status_code == HTTPStatus.OK, (
            'Should return 200 response'
        )
        data = response.data
        assert data == self.event_edit_time_data_payload

    @pytest.mark.django_db
    def test_detachment_scale_event_edit(
            self, authenticated_client_6, event_detachment, user_6
    ):
        response = authenticated_client_6.put(
            '/api/v1/events/1/', data=self.event_detachment_scale_payload
        )
        assert response.status_code == HTTPStatus.OK, (
            'Should return 200 OK response'
        )
        response = authenticated_client_6.get('/api/v1/events/1/')
        assert response.status_code == HTTPStatus.OK, (
            'Should return 200 OK response'
        )

    @pytest.mark.django_db
    def test_event_creation_wrong_scale(
            self, authenticated_client_6, detachment_3
    ):
        wrong_scale_payload = self.event_detachment_scale_payload.copy()
        wrong_scale_payload['scale'] = 'wrong_scale'
        response = authenticated_client_6.post(
            '/api/v1/events/', data=wrong_scale_payload
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Should return 400 Bad Request response'
        )
        response = authenticated_client_6.get('/api/v1/events/1/')
        assert response.status_code == HTTPStatus.NOT_FOUND, (
            'Should return 404 Not Found response'
        )

    @pytest.mark.django_db
    def test_event_creation_wrong_status(
            self, authenticated_client_6, detachment_3
    ):
        wrong_status_payload = self.event_detachment_scale_payload.copy()
        wrong_status_payload['status'] = 'wrong_status'
        response = authenticated_client_6.post(
            '/api/v1/events/', data=wrong_status_payload
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Should return 400 Bad Request response'
        )
        response = authenticated_client_6.get('/api/v1/events/1/')
        assert response.status_code == HTTPStatus.NOT_FOUND, (
            'Should return 404 Not Found response'
        )

    @pytest.mark.django_db
    def test_event_creation_wrong_format(
            self, authenticated_client_6, detachment_3
    ):
        wrong_format_payload = self.event_detachment_scale_payload.copy()
        wrong_format_payload['format'] = 'wrong_format'
        response = authenticated_client_6.post(
            '/api/v1/events/', data=wrong_format_payload
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Should return 400 Bad Request response'
        )
        response = authenticated_client_6.get('/api/v1/events/1/')
        assert response.status_code == HTTPStatus.NOT_FOUND, (
            'Should return 404 Not Found response'
        )

    @pytest.mark.django_db
    def test_event_creation_wrong_direction(
            self, authenticated_client_6, detachment_3
    ):
        wrong_direction_payload = self.event_detachment_scale_payload.copy()
        wrong_direction_payload['direction'] = 'wrong_direction'
        response = authenticated_client_6.post(
            '/api/v1/events/', data=wrong_direction_payload
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Should return 400 Bad Request response'
        )
        response = authenticated_client_6.get('/api/v1/events/1/')
        assert response.status_code == HTTPStatus.NOT_FOUND, (
            'Should return 404 Not Found response'
        )

    @pytest.mark.django_db
    def test_event_creation_wrong_available_units(
            self, authenticated_client_6, detachment_3
    ):
        wrong_available_units_payload = self.event_detachment_scale_payload.copy()
        wrong_available_units_payload[
            'available_structural_units'
        ] = 'wrong_available_structural_units'
        response = authenticated_client_6.post(
            '/api/v1/events/', data=wrong_available_units_payload
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST, (
            'Should return 400 Bad Request response'
        )
        response = authenticated_client_6.get('/api/v1/events/1/')
        assert response.status_code == HTTPStatus.NOT_FOUND, (
            'Should return 404 Not Found response'
        )
