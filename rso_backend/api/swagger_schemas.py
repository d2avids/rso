from rest_framework import serializers

from events.models import Event


class EventSwaggerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = (
            'format',
            'direction',
            'status',
            'name',
            'banner',
            'conference_link',
            'address',
            'participants_number',
            'description',
            'application_type',
            'available_structural_units',
        )
