import django_filters
from .models import CompetitionParticipants


class CompetitionParticipantsFilter(django_filters.FilterSet):
    is_tandem = django_filters.BooleanFilter(method='filter_by_group')

    class Meta:
        model = CompetitionParticipants
        fields = ['is_tandem']

    def filter_by_group(self, queryset, name, value):
        if value:
            return queryset.filter(detachment__isnull=False)
        else:
            return queryset.filter(detachment__isnull=True)
