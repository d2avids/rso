from django.urls import path

from users.views import UserAutocomplete

urlpatterns = [
    path(
        'autocomplete/user/',
        UserAutocomplete.as_view(),
        name='user-autocomplete'
    ),
]
