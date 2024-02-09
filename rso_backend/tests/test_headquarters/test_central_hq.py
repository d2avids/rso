import datetime

import pytest
from django.conf import settings
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
