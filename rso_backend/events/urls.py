from django.urls import path
from events.views import EventAutoComplete

urlpatterns = [
    path(
        'autocomplete/event/',
        EventAutoComplete.as_view(),
        name='event-autocomplete'
    ),
]
