from django_filters import rest_framework as filters

from headquarters.models import EducationalInstitution


class EducationalInstitutionFilter(filters.FilterSet):

    region__name = filters.CharFilter(
        field_name='region__name',
        lookup_expr='icontains',
        label='Название региона'
    )

    class Meta:
        model = EducationalInstitution
        fields = ('region__name',)