from django.shortcuts import get_object_or_404
from rest_framework import serializers

from .models import (
    Event, EventAdditionalIssue, EventApplications, EventIssueAnswer,
    EventParticipants
)


class EventApplicationsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventApplications
        fields = '__all__'
        read_only_fields = ('event', 'user', 'created_at')

    def validate(self, attrs):
        request = self.context.get('request')
        validation_error_messages = []
        if request.method == 'POST':
            user = request.user
            event_id = request.parser_context.get('kwargs').get('event_pk')
            event = get_object_or_404(Event, id=event_id)
            msg_apply_type_validation = self.validate_application_type(event)
            msg_answer_validation = self.validate_answered_questions(
                event, user
            )
            msg_duplicate_apply = self.validate_duplicate_application(
                event, user
            )
            if msg_apply_type_validation:
                validation_error_messages.append(msg_apply_type_validation)
            if msg_answer_validation:
                validation_error_messages.append(msg_answer_validation)
            if msg_duplicate_apply:
                validation_error_messages.append(msg_duplicate_apply)
            if validation_error_messages:
                raise serializers.ValidationError(validation_error_messages)
        return attrs

    def validate_application_type(self, event):
        if event.application_type != Event.EventApplicationType.PERSONAL:
            return ('Для данного мероприятия разрешена подача только '
                    'индивидуальных заявок')

    def validate_answered_questions(self, event, user):
        len_answers = EventIssueAnswer.objects.filter(
            application__event=event, application__user=user
        ).count()
        if event.additional_issues.count() != len_answers:
            return 'Вы не ответили на все вопросы'

    def validate_duplicate_application(self, event, user):
        if EventApplications.objects.filter(event=event, user=user).exists():
            return 'Вы уже подали заявку на участие в этом мероприятии'


class EventApplicationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventApplications
        fields = "__all__"
        read_only_fields = ('created_at',
                            'event',
                            'user')


class AnswerSerializer(serializers.ModelSerializer):
    # issue_id = serializers.PrimaryKeyRelatedField(
    #     queryset=EventAdditionalIssue.objects.all()
    # )

    class Meta:
        model = EventIssueAnswer
        fields = ('id',
                  'issue_id',
                  'application_id',
                  'answer') # all fields
        read_only_fields = ('id', 'application_id')

    def validate(self, attrs):
        request = self.context.get('request')
        if request.method == 'POST':
            application = self.context.get('application')
            len_questions = len(application.event.additional_issues.all())
            if len(request.data) != len_questions:
                raise serializers.ValidationError(
                    'Не на все вопросы даны ответы. '
                    'Всего вопросов: {}'.format(len_questions)
                )
            if EventIssueAnswer.objects.filter(
                application=application
            ).exists():
                raise serializers.ValidationError(
                    'Вы уже отвечали на вопросы данного мероприятия'
                )
        return attrs

    # # Перенесено во вью. Так как из за many=True передается один экземпляр
    # def create(self, validated_data):
    #     print(validated_data)
    #     application = self.context.get('application')
    #     questions = application.event.additional_issues.all()
    #     answers_to_create = []
    #     for answer_data in validated_data:
    #         issue_id = answer_data['issue_id']
    #         answer_text = answer_data['answer']
    #         issue_instance = questions.get(id=issue_id)
    #         answer_to_create = EventIssueAnswer(
    #             application=application,
    #             issue=issue_instance,
    #             answer=answer_text
    #         )
    #         answers_to_create.append(answer_to_create)

    #     return EventIssueAnswer.objects.bulk_create(answers_to_create)


class EventParticipantsSerializer(serializers.ModelSerializer):

    class Meta:
        model = EventParticipants
        fields = "__all__"
        read_only_fields = ('id',
                            'event',
                            'user')

    def validate(self, attrs):
        request = self.context.get('request')
        if request.method == 'POST':
            user = request.user
            event_id = request.parser_context.get('kwargs').get('event_pk')
            event = get_object_or_404(Event, id=event_id)
            if EventParticipants.objects.filter(
                event=event, user=user
            ).exists():
                raise serializers.ValidationError(
                    'Пользователь уже участвует в этом мероприятии. '
                    'Отклоните повторную заявку.'
                )
        return attrs
