from django.urls import path

from .views import (CompetitionDetachmentAutoComplete,
                    CompetitionJuniorDetachmentAutoComplete)

urlpatterns = [
    path(
        'autocomplete/competition_detachments/',
        CompetitionDetachmentAutoComplete.as_view(),
        name='competition-detachment-autocomplete'
    ),
    path(
        'autocomplete/competition_junior_detachments/',
        CompetitionJuniorDetachmentAutoComplete.as_view(),
        name='competition-junior-detachment-autocomplete'
    )
]
