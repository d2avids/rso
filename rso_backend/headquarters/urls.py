from django.urls import path

from headquarters.views import (EducationalAutoComplete,
                                EducationalInstitutionAutoComplete,
                                LocalAutoComplete, RegionalAutoComplete,
                                RegionAutoComplete)

urlpatterns = [
    path(
        'autocomplete/region/',
        RegionAutoComplete.as_view(),
        name='region-autocomplete'
    ),
    path(
        'autocomplete/regional/',
        RegionalAutoComplete.as_view(),
        name='regional-autocomplete'
    ),
    path(
        'autocomplete/educational/',
        EducationalAutoComplete.as_view(),
         name='educational-autocomplete'
    ),
    path(
        'autocomplete/educational-institution/',
        EducationalInstitutionAutoComplete.as_view(),
        name='educational-institution-autocomplete'
    ),
    path(
        'autocomplete/local-autocomplete/',
        LocalAutoComplete.as_view(),
        name='local-autocomplete'
    )
]
