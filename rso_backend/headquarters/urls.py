from django.urls import path

from headquarters.views import (DetachmentAutoComplete,
                                EducationalAutoComplete,
                                EducationalInstitutionAutoComplete,
                                LocalAutoComplete, PositionAutoComplete,
                                RegionalAutoComplete, RegionAutoComplete)

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
        'autocomplete/local/',
        LocalAutoComplete.as_view(),
        name='local-autocomplete'
    ),
    path(
        'autocomplete/detachment/',
        DetachmentAutoComplete.as_view(),
        name='detachment-autocomplete',
    ),
    path(
        'autocomplete/position/',
        PositionAutoComplete.as_view(),
        name='position-autocomplete'
    )
]
