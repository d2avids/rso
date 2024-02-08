from django.urls import path

from headquarters.views import (EducationalAutoComplete,
                                EducationalInstitutionAutoComplete,
                                LocalAutoComplete, RegionalAutoComplete,
                                RegionAutoComplete)

urlpatterns = [
    path(
        'region-userautocomplete/',
        RegionAutoComplete.as_view(),
        name='region-autocomplete'
    ),
    path(
        'regional-autocomplete/',
        RegionalAutoComplete.as_view(),
        name='regional-autocomplete'
    ),
    path(
        'educational-autocomplete/',
        EducationalAutoComplete.as_view(),
         name='educational-autocomplete'
    ),
    path(
        'educational-institutionautocomplete/',
        EducationalInstitutionAutoComplete.as_view(),
        name='educational-institution-autocomplete'
    ),
    path(
        'local-autocomplete/',
        LocalAutoComplete.as_view(),
        name='local-autocomplete'
    )
]
