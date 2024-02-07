from django_filters import rest_framework as filters

from events.models import Event


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
