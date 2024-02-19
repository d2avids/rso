from django_filters import rest_framework as filters

from users.models import RSOUser


class RSOUserFilter(filters.FilterSet):
    date_of_birth = filters.DateFilter()
    date_of_birth_gte = filters.DateFilter(
        field_name='date_of_birth', lookup_expr='gte'
    )
    date_of_birth_lte = filters.DateFilter(
        field_name='date_of_birth', lookup_expr='lte'
    )
    district_headquarter__name = filters.CharFilter(
        field_name='userdistrictheadquarterposition__headquarter__name',
        lookup_expr='icontains',
        label='Название окружного штаба'
    )
    regional_headquarter__name = filters.CharFilter(
        field_name='userregionalheadquarterposition__headquarter__name',
        lookup_expr='icontains',
        label='Название регионального штаба'
    )
    local_headquarter__name = filters.CharFilter(
        field_name='userlocalheadquarterposition__headquarter__name',
        lookup_expr='icontains',
        label='Название местного штаба'
    )
    educational_headquarter__name = filters.CharFilter(
        field_name='usereducationalheadquarterposition__headquarter__name',
        lookup_expr='icontains',
        label='Название образовательного штаба'
    )
    detachment__name = filters.CharFilter(
        field_name='userdetachmentposition__headquarter__name',
        lookup_expr='icontains',
        label='Название отряда'
    )
    region = filters.CharFilter(
        field_name='region__name',
        lookup_expr='icontains',
        label='Регион'
    )

    class Meta:
        model = RSOUser
        fields = (
            'date_of_birth',
            'date_of_birth_gte',
            'date_of_birth_lte',
            'district_headquarter__name',
            'regional_headquarter__name',
            'local_headquarter__name',
            'educational_headquarter__name',
            'detachment__name',
            'gender',
            'is_verified',
            'membership_fee',
            'region',
        )
