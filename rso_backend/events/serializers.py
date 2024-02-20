from django.shortcuts import get_object_or_404
from rest_framework import serializers

from api.utils import create_first_or_exception
from events.constants import (EVENT_DOCUMENT_DATA_RAW_EXISTS,
                              EVENT_TIME_DATA_RAW_EXISTS)
from events.models import (Event, EventAdditionalIssue, EventApplications,
                           EventDocument, EventDocumentData, EventIssueAnswer,
                           EventOrganizationData, EventParticipants,
                           EventTimeData, EventUserDocument,
                           MultiEventApplication)
from headquarters.models import (CentralHeadquarter, Detachment,
                                 DistrictHeadquarter, EducationalHeadquarter,
                                 LocalHeadquarter, RegionalHeadquarter)
from users.models import RSOUser
from users.serializers import ShortUserSerializer


class EventTimeDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventTimeData
        fields = (
            'event_duration_type',
            'start_date',
            'start_time',
            'end_date',
            'end_time',
            'registration_end_date',
            'registration_end_time',
        )

    def create(self, validated_data):
        return create_first_or_exception(
            self,
            validated_data,
            EventTimeData,
            EVENT_TIME_DATA_RAW_EXISTS
        )


class EventDocumentDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventDocumentData
        fields = (
            'passport',
            'snils',
            'inn',
            'work_book',
            'military_document',
            'consent_personal_data',
            'additional_info',
        )

    def create(self, validated_data):
        return create_first_or_exception(
            self,
            validated_data,
            EventDocumentData,
            EVENT_DOCUMENT_DATA_RAW_EXISTS
        )


class EventOrganizerDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventOrganizationData
        fields = (
            'id',
            'organizer',
            'organizer_phone_number',
            'organizer_email',
            'organization',
            'telegram',
            'is_contact_person',
        )


class EventDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventDocument
        fields = ('id', 'document',)


class EventAdditionalIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventAdditionalIssue
        fields = ('id', 'issue',)


class EventSerializer(serializers.ModelSerializer):
    time_data = EventTimeDataSerializer(read_only=True)
    document_data = EventDocumentDataSerializer(read_only=True)
    additional_issues = EventAdditionalIssueSerializer(
        read_only=True, many=True
    )
    organization_data = EventOrganizerDataSerializer(read_only=True, many=True)
    documents = EventDocumentSerializer(read_only=True, many=True)

    class Meta:
        model = Event
        fields = (
            'id',
            'author',
            'format',
            'direction',
            'status',
            'scale',
            'created_at',
            'name',
            'banner',
            'conference_link',
            'address',
            'participants_number',
            'description',
            'application_type',
            'available_structural_units',
            'time_data',
            'document_data',
            'documents',
            'organization_data',
            'additional_issues',
            'org_central_headquarter',
            'org_district_headquarter',
            'org_regional_headquarter',
            'org_local_headquarter',
            'org_educational_headquarter',
            'org_detachment',
        )
        read_only_fields = (
            'id',
            'author',
            'created_at',
            'documents',
            'organization_data',
            'time_data',
            'document_data',
        )

    def create(self, validated_data):
        instance = Event(**validated_data)
        try:
            instance.full_clean()
        except Exception as e:
            raise serializers.ValidationError({'error': str(e)})
        return super().create(validated_data)


class ShortEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = (
            'id',
            'name',
            'banner',
        )


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventIssueAnswer
        fields = (
            'id',
            'issue',
            'answer',
            'event',
            'user'
        )
        read_only_fields = (
            'id',
            'event',
            'user'
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        issue_id = representation['issue']
        issue = get_object_or_404(EventAdditionalIssue, id=issue_id)
        representation['issue'] = issue.issue
        return representation

    def validate(self, attrs):
        request = self.context.get('request')
        if request.method == 'POST':
            event = self.context.get('event')
            len_questions = len(event.additional_issues.all())
            if len(request.data) != len_questions:
                raise serializers.ValidationError(
                    'Не на все вопросы даны ответы. '
                    'Всего вопросов: {}'.format(len_questions)
                )
            if EventIssueAnswer.objects.filter(
                    event=event, user=request.user
            ).exists():
                raise serializers.ValidationError(
                    'Вы уже отвечали на вопросы данного мероприятия'
                )
            for answer in request.data:
                if not answer.get('answer'):
                    raise serializers.ValidationError(
                        'Ответ на вопрос не может быть пустым'
                    )
                if not answer.get('issue'):
                    raise serializers.ValidationError(
                        'Не выбран вопрос'
                    )
        return attrs


class EventApplicationsSerializer(serializers.ModelSerializer):
    answers = serializers.SerializerMethodField()
    documents = serializers.SerializerMethodField()
    user = ShortUserSerializer(read_only=True)
    event = ShortEventSerializer(read_only=True)

    class Meta:
        model = EventApplications
        fields = (
            'id',
            'user',
            'event',
            'answers',
            'documents',
            'created_at'
        )
        read_only_fields = (
            'created_at',
            'event',
            'user'
        )

    def get_answers(self, obj):
        return AnswerSerializer(
            EventIssueAnswer.objects.filter(event=obj.event, user=obj.user),
            many=True
        ).data

    def get_documents(self, obj):
        return EventUserDocumentSerializer(
            EventUserDocument.objects.filter(event=obj.event, user=obj.user),
            many=True
        ).data


class EventParticipantsSerializer(serializers.ModelSerializer):
    answers = serializers.SerializerMethodField()
    documents = serializers.SerializerMethodField()
    user = ShortUserSerializer(read_only=True)
    event = ShortEventSerializer(read_only=True)

    class Meta:
        model = EventParticipants
        fields = (
            'id',
            'user',
            'event',
            'answers',
            'documents'
        )
        read_only_fields = (
            'id',
            'event',
            'user'
        )

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

    def get_answers(self, obj):
        return AnswerSerializer(
            EventIssueAnswer.objects.filter(event=obj.event, user=obj.user),
            many=True
        ).data

    def get_documents(self, obj):
        return EventUserDocumentSerializer(
            EventUserDocument.objects.filter(event=obj.event, user=obj.user),
            many=True
        ).data


class EventUserDocumentSerializer(serializers.ModelSerializer):
    user = ShortUserSerializer(read_only=True)
    event = ShortEventSerializer(read_only=True)

    class Meta:
        model = EventUserDocument
        fields = '__all__'
        read_only_fields = (
            'id',
            'event',
            'user'
        )


class MultiEventApplicationSerializer(serializers.ModelSerializer):
    central_headquarter = serializers.PrimaryKeyRelatedField(
        queryset=CentralHeadquarter.objects.all(),
        required=False,
        allow_null=True,
        label='Центральный штаб'
    )
    district_headquarter = serializers.PrimaryKeyRelatedField(
        queryset=DistrictHeadquarter.objects.all(),
        required=False,
        allow_null=True,
        label='Окружной штаб'
    )
    regional_headquarter = serializers.PrimaryKeyRelatedField(
        queryset=RegionalHeadquarter.objects.all(),
        required=False,
        allow_null=True,
        label='Региональный штаб'
    )
    local_headquarter = serializers.PrimaryKeyRelatedField(
        queryset=LocalHeadquarter.objects.all(),
        required=False,
        allow_null=True,
        label='Местный штаб'
    )
    educational_headquarter = serializers.PrimaryKeyRelatedField(
        queryset=EducationalHeadquarter.objects.all(),
        required=False,
        allow_null=True,
        label='Образовательный штаб'
    )
    detachment = serializers.PrimaryKeyRelatedField(
        queryset=Detachment.objects.all(),
        required=False,
        allow_null=True,
        label='Отряд'
    )
    participants_count = serializers.IntegerField(
        min_value=1,
        label='Количество участников'
    )
    emblem = serializers.CharField(
        required=False,
        allow_null=True,
        label='Эмблема'
    )

    class Meta:
        model = MultiEventApplication
        fields = '__all__'
        read_only_fields = (
            'id',
            'event',
            'organizer_id',
            'created_at'
        )

    def validate(self, attrs):
        """
        Проверяет, что в одном элементе подана только одна структурная единица.
        Проверяет, наличие поля 'participants_count'.
        """
        structural_units = [
            attrs.get('central_headquarter'),
            attrs.get('district_headquarter'),
            attrs.get('regional_headquarter'),
            attrs.get('local_headquarter'),
            attrs.get('educational_headquarter'),
            attrs.get('detachment')
        ]
        count = sum(unit is not None for unit in structural_units)
        if count != 1:
            raise serializers.ValidationError(
                'В одном элементе можно подать только один тип '
                'структурной единицы.'
            )
        participants_count = attrs.get('participants_count')
        if not participants_count:
            raise serializers.ValidationError(
                'Необходимо указать количество участников.'
            )
        return attrs

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return {key: value for key, value in representation.items()
                if value is not None}


class ShortUnitSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для хранения общей логики штабов."""
    members_count = serializers.SerializerMethodField()

    class Meta:
        model = None
        fields = (
            'id',
            'name',
            'emblem',
            'members_count',
        )

    @staticmethod
    def get_members_count(obj):
        return obj.members.filter(user__is_verified=True).count()


class ShortDetachmentSerializerME(ShortUnitSerializer):
    class Meta:
        model = Detachment
        fields = ShortUnitSerializer.Meta.fields


class ShortEducationalHeadquarterSerializerME(ShortUnitSerializer):
    detachments = ShortDetachmentSerializerME(many=True)

    class Meta:
        model = EducationalHeadquarter
        fields = ShortUnitSerializer.Meta.fields + (
            'detachments',
        )


class ShortLocalHeadquarterSerializerME(ShortUnitSerializer):
    educational_headquarters = ShortEducationalHeadquarterSerializerME(
        many=True
    )
    detachments = ShortDetachmentSerializerME(many=True)

    class Meta:
        model = LocalHeadquarter
        fields = ShortUnitSerializer.Meta.fields + (
            'educational_headquarters',
            'detachments',
        )


class ShortRegionalHeadquarterSerializerME(ShortUnitSerializer):
    local_headquarters = ShortLocalHeadquarterSerializerME(many=True)
    educational_headquarters = ShortEducationalHeadquarterSerializerME(
        many=True
    )
    detachments = ShortDetachmentSerializerME(many=True)

    class Meta:
        model = RegionalHeadquarter
        fields = ShortUnitSerializer.Meta.fields + (
            'local_headquarters',
            'educational_headquarters',
            'detachments',
        )


class ShortDistrictHeadquarterSerializerME(ShortUnitSerializer):
    regionals_headquarters = ShortRegionalHeadquarterSerializerME(many=True)

    class Meta:
        model = DistrictHeadquarter
        fields = ShortUnitSerializer.Meta.fields + (
            'regionals_headquarters',
        )


class ShortCentralHeadquarterSerializerME(ShortUnitSerializer):
    districts_headquarters = ShortDistrictHeadquarterSerializerME(many=True)

    class Meta:
        model = CentralHeadquarter
        fields = ShortUnitSerializer.Meta.fields + (
            'districts_headquarters',
        )


class MultiEventParticipantsSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=RSOUser.objects.all()
    )

    class Meta:
        model = EventParticipants
        fields = (
            'id',
            'user',
            'event',
        )
        read_only_fields = (
            'id',
            'event',
        )

    def validate(self, attrs):
        user = attrs.get('user')
        if not user.is_verified:
            raise serializers.ValidationError(
                'Только верифицированных пользователей можно '
                'включать в списки.'
            )
        return attrs


class ShortMultiEventApplicationSerializer(serializers.ModelSerializer):
    headquarter_name = serializers.SerializerMethodField(
        label='Название штаба'
    )
    emblem = serializers.SerializerMethodField(
        label='Иконка штаба'
    )
    created_at = serializers.SerializerMethodField(
        label='Дата подачи заявки'
    )
    is_approved = serializers.SerializerMethodField(
        label='Подтверждена ли заявка'
    )

    class Meta:
        model = RSOUser
        fields = (
            'id',
            'headquarter_name',
            'emblem',
            'is_approved',
            'created_at',
        )

    def get_headquarter_name(self, instance):
        headquarter_instance = (
            self.context.get('headquarter_model').objects.filter(
                commander=instance
            ).first()
        )
        return headquarter_instance.name

    def get_emblem(self, instance):
        headquarter_instance = (
            self.context.get('headquarter_model').objects.filter(
                commander=instance
            ).first()
        )
        return (headquarter_instance.emblem.url
                if headquarter_instance.emblem
                else None)

    def get_created_at(self, instance):
        first_application = MultiEventApplication.objects.filter(
            organizer_id=instance.id
        ).first()
        return first_application.created_at

    def get_is_approved(self, instance):
        first_application = MultiEventApplication.objects.filter(
            organizer_id=instance.id
        ).first()
        return first_application.is_approved


class EventApplicationsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventApplications
        fields = '__all__'
        read_only_fields = ('event', 'user', 'created_at')

    def validate(self, attrs):
        request = self.context.get('request')
        validation_error_messages = []
        user = request.user
        event_id = request.parser_context.get('kwargs').get('event_pk')
        event = get_object_or_404(Event, id=event_id)
        msg_answer_validation = self.validate_answered_questions(
            event, user
        )
        msg_duplicate_apply = self.validate_duplicate_application(
            event, user
        )
        msg_user_is_participant = self.validate_user_is_participant(
            event, user
        )
        msg_all_documents_uploaded = self.validate_all_documents_uploaded(
            event, user
        )
        if msg_answer_validation:
            validation_error_messages.append(msg_answer_validation)
        if msg_duplicate_apply:
            validation_error_messages.append(msg_duplicate_apply)
        if msg_user_is_participant:
            validation_error_messages.append(msg_user_is_participant)
        if msg_all_documents_uploaded:
            validation_error_messages.append(msg_all_documents_uploaded)
        if validation_error_messages:
            raise serializers.ValidationError(validation_error_messages)
        return attrs

    def validate_answered_questions(self, event, user):
        len_answers = EventIssueAnswer.objects.filter(
            event=event, user=user
        ).count()
        if event.additional_issues.count() != len_answers:
            return 'Вы не ответили на все вопросы'

    def validate_duplicate_application(self, event, user):
        if EventApplications.objects.filter(event=event, user=user).exists():
            return 'Вы уже подали заявку на участие в этом мероприятии'

    def validate_user_is_participant(self, event, user):
        if EventParticipants.objects.filter(event=event, user=user).exists():
            return 'Вы уже участвуете в этом мероприятии'

    def validate_all_documents_uploaded(self, event, user):
        len_uploaded_documents = EventUserDocument.objects.filter(
            event=event, user=user
        ).count()
        len_documents = event.documents.count()
        if len_uploaded_documents < len_documents:
            return (
                'Вы загрузили не все документы. '
                'Всего необходимо {} документов'.format(len_documents)
            )

    def create(self, validated_data):
        instance = EventApplications(**validated_data)
        try:
            instance.full_clean()
        except Exception as e:
            raise serializers.ValidationError({'error': str(e)})
        return super().create(validated_data)
