from django_filters import rest_framework as filters

from events.models import Event


class EventFilter(filters.FilterSet):
    format = filters.CharFilter(
        field_name='format', lookup_expr='icontains', label='Формат'
    )
    direction = filters.CharFilter(
        field_name='direction', lookup_expr='icontains', label='Направление'
    )
    status = filters.CharFilter(
        field_name='status', lookup_expr='icontains', label='Статус'
    )
    scale = filters.CharFilter(
        field_name='scale',
        lookup_expr='icontains',
        label='Масштаб мероприятия'
    )

    class Meta:
        model = Event
        fields = ('format', 'direction', 'status', 'scale')
