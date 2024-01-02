from rest_framework import serializers

from .models import (
    Event, EventAdditionalIssue, EventApplications, EventIssueAnswer
)


class EventApplicationsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventApplications
        fields = "__all__"
        read_only_fields = ('event',
                            'user',
                            'created_at',
                            'updated_at',
                            'is_approved')

    def validate(self, attrs):
        request = self.context.get('request')
        if request.method == 'POST':
            user = request.user
            event_id = request.parser_context.get('kwargs').get('event_pk')
            event = Event.objects.get(id=event_id)
            if EventApplications.objects.filter(
                event=event, user=user
            ).exists():
                raise serializers.ValidationError(
                    'Вы уже подали заявку на участие в этом мероприятии'
                )
        return attrs


class EventApplicationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventApplications
        fields = "__all__"
        read_only_fields = ('created_at',
                            'updated_at',
                            'event',
                            'user')


class AnswerSerializer(serializers.ModelSerializer):
    issue_id = serializers.PrimaryKeyRelatedField(
        queryset=EventAdditionalIssue.objects.all()  
    )
    application_id = serializers.PrimaryKeyRelatedField(
        queryset=EventApplications.objects.all()
    )

    class Meta:
        model = EventIssueAnswer
        fields = ('id',
                  'issue_id',
                  'application_id',
                  'answer')
