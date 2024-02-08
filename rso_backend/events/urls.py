from django.urls import path

from events.views import EventAutoComplete

urlpatterns = [
    path(
        'event-autocomplete/',
        EventAutoComplete.as_view(),
        name='event-autocomplete'
    ),
]
