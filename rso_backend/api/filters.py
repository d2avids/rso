from django.db.models import Q
from django_filters import rest_framework as filters

from events.models import Event
from users.models import RSOUser
from headquarters.models import (Detachment, EducationalHeadquarter,
                                 LocalHeadquarter, RegionalHeadquarter)


class EventFilter(filters.FilterSet):
    format = filters.CharFilter(field_name='format', lookup_expr='iexact')
    direction = filters.CharFilter(
        field_name='direction', lookup_expr='iexact'
    )
    status = filters.CharFilter(
        field_name='status', lookup_expr='iexact'
    )
    scale = filters.CharFilter(
        field_name='scale', lookup_expr='iexact'
    )

    class Meta:
        model = Event
        fields = ('format', 'direction', 'status', 'scale')


class RSOUserFilter(filters.FilterSet):
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
        field_name='userdetachmentposition__detachment__name',
        lookup_expr='icontains',
        label='Название отряда'
    )
    region = filters.CharFilter(
        field_name='region__name',
        lookup_expr='iexact',
        label='Регион'
    )

    class Meta:
        model = RSOUser
        fields = (
            'district_headquarter__name',
            'regional_headquarter__name',
            'local_headquarter__name',
            'educational_headquarter__name',
            'detachment__name',
            'gender',
            'is_verified',
            'membership_fee',
            'date_of_birth',
            'region',
        )


class RegionalHeadquarterFilter(filters.FilterSet):
    district_headquarter__name = filters.CharFilter(
        field_name='district_headquarter__name',
        lookup_expr='icontains',
        label='Название окружного штаба'
    )

    class Meta:
        model = RegionalHeadquarter
        fields = ('district_headquarter__name', )


class LocalHeadquarterFilter(filters.FilterSet):
    district_headquarter__name = filters.CharFilter(
        field_name='regional_headquarter__district_headquarter__name',
        lookup_expr='icontains',
        label='Название окружного штаба'
    )
    regional_headquarter__name = filters.CharFilter(
        field_name='regional_headquarter__name',
        lookup_expr='icontains',
        label='Название регионального штаба'
    )

    class Meta:
        model = LocalHeadquarter
        fields = ('regional_headquarter__name', 'district_headquarter__name',)


class EducationalHeadquarterFilter(filters.FilterSet):

    district_headquarter__name = filters.CharFilter(
        method='filter_district_headquarter',
        label='Название окружного штаба'
    )
    regional_headquarter__name = filters.CharFilter(
        field_name='regional_headquarter__name',
        lookup_expr='icontains',
        label='Название регионального штаба'
    )
    local_headquarter__name = filters.CharFilter(
        field_name='local_headquarter__name',
        lookup_expr='icontains',
        label='Название местного штаба'
    )

    def filter_district_headquarter(self, queryset, name, value):
        return queryset.filter(
            Q(
                local_headquarter__regional_headquarter__district_headquarter__name__icontains=value
            ) |
            Q(
                regional_headquarter__district_headquarter__name__icontains=value
            )
        )

    class Meta:
        model = EducationalHeadquarter
        fields = (
            'local_headquarter__name',
            'regional_headquarter__name',
            'district_headquarter__name',
        )


class DetachmentFilter(filters.FilterSet):

    area__name = filters.CharFilter(
        field_name='area__name',
        lookup_expr='icontains',
        label='Название направления'
    )
    educational_institution__name = filters.CharFilter(
        field_name='educational_institution__name',
        lookup_expr='icontains',
        label='Название образовательной организации'
    )

    class Meta:
        model = Detachment
        fields = ('area__name', 'educational_institution__name')
