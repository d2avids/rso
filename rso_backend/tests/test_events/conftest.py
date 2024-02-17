import pytest
from events.models import Event


@pytest.fixture
def event_detachment(user_6, regional_headquarter):
    event = Event.objects.create(
        name='Test Event',
        format='Онлайн',
        status='Активный',
        scale='Отрядный',
        author=user_6,
        conference_link='https://example.com',
        address='address',
        participants_number=100,
        description='desc',
        available_structural_units='Отряды',
        org_regional_headquarter=regional_headquarter,

    )
    return event
