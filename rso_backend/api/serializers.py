import datetime as dt
from drf_yasg import openapi
from datetime import date
from drf_yasg.utils import swagger_serializer_method
from django.conf import settings
from django.db.models import Q
from django.db.models.query import QuerySet
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreatePasswordRetypeSerializer
from rest_framework import serializers

from api.constants import (DOCUMENTS_RAW_EXISTS, EDUCATION_RAW_EXISTS,
                           EVENT_DOCUMENT_DATA_RAW_EXISTS,
                           EVENT_TIME_DATA_RAW_EXISTS, MEDIA_RAW_EXISTS,
                           PRIVACY_RAW_EXISTS, REGION_RAW_EXISTS,
                           STATEMENT_RAW_EXISTS, TOO_MANY_EDUCATIONS)
from api.utils import create_first_or_exception, get_is_trusted
from events.models import (Сompetition, СompetitionApplications,
                           СompetitionParticipants, Event,
                           EventAdditionalIssue, EventApplications,
                           EventDocument, EventDocumentData, EventIssueAnswer,
                           EventOrganizationData, EventParticipants,
                           EventTimeData, EventUserDocument,
                           MultiEventApplication)
from headquarters.models import (Area, CentralHeadquarter, Detachment,
                                 DistrictHeadquarter, EducationalHeadquarter,
                                 EducationalInstitution, LocalHeadquarter,
                                 Position, Region, RegionalHeadquarter,
                                 UserCentralHeadquarterPosition,
                                 UserDetachmentApplication,
                                 UserDetachmentPosition,
                                 UserDistrictHeadquarterPosition,
                                 UserEducationalHeadquarterPosition,
                                 UserLocalHeadquarterPosition,
                                 UserRegionalHeadquarterPosition)
from users.models import (MemberCert, RSOUser, UserDocuments, UserEducation,
                          UserForeignDocuments, UserMedia, UserParent,
                          UserPrivacySettings, UserProfessionalEducation,
                          UserRegion, UserStatementDocuments,
                          UserVerificationRequest)


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ('id', 'name',)


class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ('id', 'name',)


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ('id', 'name', 'code')


class EducationalInstitutionSerializer(serializers.ModelSerializer):
    region = RegionSerializer()

    class Meta:
        model = EducationalInstitution
        fields = (
            'id', 'short_name', 'name', 'rector', 'rector_email', 'region'
        )


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


class ShortEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = (
            'id',
            'name',
            'banner',
        )


class UserEducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserEducation
        fields = (
            'study_institution',
            'study_faculty',
            'study_form',
            'study_year',
            'study_specialty',
        )

    def create(self, validated_data):
        return create_first_or_exception(
            self,
            validated_data,
            UserEducation,
            EDUCATION_RAW_EXISTS
        )


class ProfessionalEductionSerializer(serializers.ModelSerializer):
    """Сериализатор дополнительного проф образования всех юзеров.

    Используется в сериализаторе UserProfessionalEducationSerializer,
    который будет сериализован в поле users_prof_educations одного пользователя
    по эндпоинту /users/me/prof_education.
    """

    class Meta:
        model = UserProfessionalEducation
        fields = (
            'study_institution',
            'years_of_study',
            'exam_score',
            'qualification'
        )


class ProfessionalEductionSerializerID(ProfessionalEductionSerializer):
    """Сериализатор дополнительного проф образования всех юзеров c ID."""

    class Meta:
        model = UserProfessionalEducation
        fields = ('id',) + ProfessionalEductionSerializer.Meta.fields

    def create(self, validated_data):
        """Сохраенение в БД допрофобразования.

        В методе реализована проверка количества записей.
        """

        manager = UserProfessionalEducation.objects
        if manager.count() < 5:
            return manager.create(**validated_data)
        raise serializers.ValidationError(TOO_MANY_EDUCATIONS)


class UserProfessionalEducationSerializer(serializers.ModelSerializer):
    """Сериализатор дополнительного профобразования."""

    users_prof_educations = serializers.SerializerMethodField()

    class Meta:
        model = UserProfessionalEducation
        fields = (
            'users_prof_educations',
        )

    @staticmethod
    def get_users_prof_educations(obj):
        """Возвращает список проф образования юзера.

        Декоратор @staticmethod позволяет определить метод как статический
        без создания экземпляра. Из obj получаем queryset и сериализуем его.
        При отсутвии проф образования возвращаем исключение с сообщением.
        """
        try:
            users_data = UserProfessionalEducation.objects.filter(
                user_id=obj.first().user_id
            )
        except AttributeError:
            raise serializers.ValidationError(
                'У данного юзера не введено дополнительное'
                ' профессиональное образование.',
            )
        serializer = ProfessionalEductionSerializerID(users_data, many=True)
        return serializer.data


class UserDocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDocuments
        fields = (
            'snils',
            'russian_passport',
            'inn',
            'pass_ser_num',
            'pass_town',
            'pass_whom',
            'pass_date',
            'pass_code',
            'pass_address',
            'work_book_num',
            'international_pass',
            'mil_reg_doc_type',
            'mil_reg_doc_ser_num',
        )

    def create(self, validated_data):
        return create_first_or_exception(
            self,
            validated_data,
            UserDocuments,
            DOCUMENTS_RAW_EXISTS
        )


class ForeignUserDocumentsSerializer(serializers.ModelSerializer):
    """Сериализатор документом иностранного гражданина."""

    class Meta:
        model = UserForeignDocuments
        fields = (
            'name',
            'foreign_pass_num',
            'foreign_pass_whom',
            'foreign_pass_date',
            'snils',
            'inn',
            'work_book_num',
        )

    def create(self, validated_data):
        return create_first_or_exception(
            self,
            validated_data,
            UserForeignDocuments,
            DOCUMENTS_RAW_EXISTS
        )


class PrivacyOptionField(serializers.ChoiceField):
    def to_representation(self, value):
        if value in self.choices:
            return self.choices[value][1]
        return value


class UserPrivacySettingsSerializer(serializers.ModelSerializer):
    privacy_telephone = serializers.CharField()
    privacy_email = serializers.CharField()
    privacy_social = serializers.CharField()
    privacy_about = serializers.CharField()
    privacy_photo = serializers.CharField()

    class Meta:
        model = UserPrivacySettings
        fields = (
            'privacy_telephone',
            'privacy_email',
            'privacy_social',
            'privacy_about',
            'privacy_photo',
        )

    def create(self, validated_data):
        return create_first_or_exception(
            self,
            validated_data,
            UserPrivacySettings,
            PRIVACY_RAW_EXISTS
        )


class UserMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserMedia
        fields = (
            'banner',
            'photo',
            'photo1',
            'photo2',
            'photo3',
            'photo4',
        )

    def create(self, validated_data):
        return create_first_or_exception(
            self,
            validated_data,
            UserMedia,
            MEDIA_RAW_EXISTS
        )


class UserStatementDocumentsSerializer(serializers.ModelSerializer):
    """Эндпоинт для подачи заявления на вступление в РСО."""

    class Meta:
        model = UserStatementDocuments
        fields = (
            'statement',
            'consent_personal_data',
            'consent_personal_data_representative',
            'passport',
            'passport_representative',
            'snils_file',
            'inn_file',
            'employment_document',
            'military_document',
            'international_passport',
            'additional_document',
            'rso_info_from',
            'personal_data_agreement',
        )

    def create(self, validated_data):
        return create_first_or_exception(
            self,
            validated_data,
            UserStatementDocuments,
            STATEMENT_RAW_EXISTS
        )


class UserRegionSerializer(serializers.ModelSerializer):
    reg_region_id = serializers.PrimaryKeyRelatedField(
        queryset=Region.objects.all(),
        source='reg_region',
        allow_null=True,
        required=False,
    )
    fact_region_id = serializers.PrimaryKeyRelatedField(
        queryset=Region.objects.all(),
        source='fact_region',
        allow_null=True,
        required=False,
    )

    class Meta:
        model = UserRegion
        fields = (
            'reg_region',
            'reg_town',
            'reg_house',
            'reg_fact_same_address',
            'fact_region',
            'fact_town',
            'fact_house',
            'reg_region_id',
            'fact_region_id',
        )
        read_only_fields = ('reg_region', 'fact_region')

    def create(self, validated_data):
        return create_first_or_exception(
            self,
            validated_data,
            UserRegion,
            REGION_RAW_EXISTS
        )


class UsersParentSerializer(serializers.ModelSerializer):
    """Сериализатор законного представителя."""

    class Meta:
        model = UserParent
        fields = (
            'parent_last_name',
            'parent_first_name',
            'parent_patronymic_name',
            'parent_date_of_birth',
            'relationship',
            'parent_phone_number',
            'russian_passport',
            'passport_number',
            'passport_date',
            'passport_authority',
            'region',
            'city',
            'address',
        )


class RSOUserSerializer(serializers.ModelSerializer):
    """
    Выводит личные данные пользователя, а также все данные из всех
    связанных моделей.
    """

    is_adult = serializers.SerializerMethodField(read_only=True)
    user_region = UserRegionSerializer(read_only=True)
    documents = UserDocumentsSerializer(read_only=True)
    statement = UserStatementDocumentsSerializer(read_only=True)
    education = UserEducationSerializer(read_only=True)
    region = serializers.PrimaryKeyRelatedField(
        queryset=Region.objects.all(),
        allow_null=True,
        required=False,
    )
    media = UserMediaSerializer(read_only=True)
    privacy = UserPrivacySettingsSerializer(read_only=True)
    parent = UsersParentSerializer(read_only=True)
    professional_education = serializers.SerializerMethodField()
    central_headquarter_id = serializers.SerializerMethodField(read_only=True)
    district_headquarter_id = serializers.SerializerMethodField(read_only=True)
    regional_headquarter_id = serializers.SerializerMethodField(read_only=True)
    local_headquarter_id = serializers.SerializerMethodField(read_only=True)
    educational_headquarter_id = serializers.SerializerMethodField(
        read_only=True
    )
    detachment_id = serializers.SerializerMethodField(read_only=True)
    sent_verification = serializers.SerializerMethodField()

    class Meta:
        model = RSOUser
        fields = (
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'patronymic_name',
            'date_of_birth',
            'is_adult',
            'last_name_lat',
            'first_name_lat',
            'patronymic_lat',
            'phone_number',
            'gender',
            'region',
            'address',
            'bio',
            'social_vk',
            'social_tg',
            'membership_fee',
            'is_verified',
            'user_region',
            'documents',
            'statement',
            'media',
            'education',
            'privacy',
            'parent',
            'professional_education',
            'central_headquarter_id',
            'district_headquarter_id',
            'regional_headquarter_id',
            'local_headquarter_id',
            'educational_headquarter_id',
            'detachment_id',
            'sent_verification',
        )
        read_only_fields = ('membership_fee', 'is_verified')

    def to_representation(self, instance):
        """
        Вызывает родительский метод to_representation,
        а также изменяем вывод region.
        """
        serialized_data = super().to_representation(instance)
        region = instance.region
        if region:
            serialized_data['region'] = region.name

        return serialized_data

    def get_professional_education(self, obj):
        return UserProfessionalEducationSerializer(
            UserProfessionalEducation.objects.filter(user=obj),
            many=True,
            context={'request': self.context.get('request')},
        ).data

    def get_is_adult(self, obj):
        """Метод определения совершеннолетия.

        Проверяем возраст пользователя.
        Если он несовершеннолетний (меньше 18 лет), то возвращаем False
        """
        if obj.date_of_birth:
            today = date.today()
            age = (today.year - obj.date_of_birth.year
                   - (
                           (today.month, today.day) < (
                       obj.date_of_birth.month, obj.date_of_birth.day
                   )
                   ))
            return age >= 18

    @staticmethod
    def get_central_headquarter_id(instance):
        try:
            central_headquarter_id = CentralHeadquarter.objects.first().id
        except CentralHeadquarter.DoesNotExist:
            central_headquarter_id = None
        return central_headquarter_id

    @staticmethod
    def get_district_headquarter_id(instance):
        try:
            district_headquarter_id = (
                UserDistrictHeadquarterPosition.objects.get(
                    user_id=instance.id
                ).headquarter_id
            )
        except UserDistrictHeadquarterPosition.DoesNotExist:
            district_headquarter_id = None
        return district_headquarter_id

    @staticmethod
    def get_regional_headquarter_id(instance):
        try:
            regional_headquarter_id = (
                UserRegionalHeadquarterPosition.objects.get(
                    user_id=instance.id
                ).headquarter_id
            )
        except UserRegionalHeadquarterPosition.DoesNotExist:
            regional_headquarter_id = None
        return regional_headquarter_id

    @staticmethod
    def get_local_headquarter_id(instance):
        try:
            local_headquarter_id = (
                UserLocalHeadquarterPosition.objects.get(
                    user_id=instance.id
                ).headquarter_id
            )
        except UserLocalHeadquarterPosition.DoesNotExist:
            local_headquarter_id = None
        return local_headquarter_id

    @staticmethod
    def get_educational_headquarter_id(instance):
        try:
            educational_headquarter_id = (
                UserEducationalHeadquarterPosition.objects.get(
                    user_id=instance.id
                ).headquarter_id
            )
        except UserEducationalHeadquarterPosition.DoesNotExist:
            educational_headquarter_id = None
        return educational_headquarter_id

    @staticmethod
    def get_detachment_id(instance):
        try:
            detachment_id = (
                UserDetachmentPosition.objects.get(
                    user_id=instance.id
                ).headquarter_id
            )
        except UserDetachmentPosition.DoesNotExist:
            detachment_id = None
        return detachment_id

    @staticmethod
    def get_sent_verification(instance):
        verification_status = UserVerificationRequest.objects.filter(user_id=instance.id).exists() or instance.is_verified
        return verification_status


class UserCommanderSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода отрядов где юзер коммандир."""

    centralheadquarter_commander = serializers.PrimaryKeyRelatedField(
        queryset=CentralHeadquarter.objects.all()
    )
    districtheadquarter_commander = serializers.PrimaryKeyRelatedField(
        queryset=DistrictHeadquarter.objects.all()
    )
    regionalheadquarter_commander = serializers.PrimaryKeyRelatedField(
        queryset=RegionalHeadquarter.objects.all()
    )
    localheadquarter_commander = serializers.PrimaryKeyRelatedField(
        queryset=LocalHeadquarter.objects.all()
    )
    educationalheadquarter_commander = serializers.PrimaryKeyRelatedField(
        queryset=EducationalHeadquarter.objects.all()
    )
    detachment_commander = serializers.PrimaryKeyRelatedField(
        queryset=Detachment.objects.all()
    )

    class Meta:
        model = RSOUser
        fields = (
            'centralheadquarter_commander',
            'districtheadquarter_commander',
            'regionalheadquarter_commander',
            'localheadquarter_commander',
            'educationalheadquarter_commander',
            'detachment_commander'
        )


class UserTrustedSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода отрядов где юзер доверенный."""

    centralheadquarter_trusted = serializers.SerializerMethodField()
    districtheadquarter_trusted = serializers.SerializerMethodField()
    regionalheadquarter_trusted = serializers.SerializerMethodField()
    localheadquarter_trusted = serializers.SerializerMethodField()
    educationalheadquarter_trusted = serializers.SerializerMethodField()
    detachment_trusted = serializers.SerializerMethodField()

    class Meta:
        model = RSOUser
        fields = (
            'centralheadquarter_trusted',
            'districtheadquarter_trusted',
            'regionalheadquarter_trusted',
            'localheadquarter_trusted',
            'educationalheadquarter_trusted',
            'detachment_trusted'
        )

    def get_centralheadquarter_trusted(self, obj):
        return get_is_trusted(
            obj=obj,
            model=UserCentralHeadquarterPosition
        )

    def get_districtheadquarter_trusted(self, obj):
        return get_is_trusted(
            obj=obj,
            model=UserDistrictHeadquarterPosition
        )

    def get_regionalheadquarter_trusted(self, obj):
        return get_is_trusted(
            obj=obj,
            model=UserRegionalHeadquarterPosition
        )

    def get_localheadquarter_trusted(self, obj):
        return get_is_trusted(
            obj=obj,
            model=UserLocalHeadquarterPosition
        )

    def get_educationalheadquarter_trusted(self, obj):
        return get_is_trusted(
            obj=obj,
            model=UserEducationalHeadquarterPosition
        )

    def get_detachment_trusted(self, obj):
        return get_is_trusted(
            obj=obj,
            model=UserDetachmentPosition
        )


class UserAvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода аватарки из модели с Медиа юзера."""

    class Meta:
        model = UserMedia
        fields = ('photo',)


class ShortUserSerializer(serializers.ModelSerializer):
    """Для сериализации небольшой части данных пользователя."""

    avatar = UserAvatarSerializer(source='media', read_only=True)

    class Meta:
        model = RSOUser
        fields = (
            'id',
            'username',
            'avatar',
            'email',
            'first_name',
            'last_name',
            'patronymic_name',
            'date_of_birth',
            'membership_fee',
            'is_verified',
        )


class UserVerificationReadSerializer(serializers.ModelSerializer):
    """Для чтения заявок на верификацию."""

    user = ShortUserSerializer(read_only=True)

    class Meta:
        model = UserVerificationRequest
        fields = ('user',)
        read_only_fields = ('user',)


class UserCreateSerializer(UserCreatePasswordRetypeSerializer):
    """Сериализатор создания пользователя.

    Подключается к Djoser в settings.py -> DJOSER -> SERIALIZERS.
    """

    region = serializers.PrimaryKeyRelatedField(
        queryset=Region.objects.all(),
        allow_null=True,
        required=False,
    )

    def create(self, validated_data):
        """Приводим ФИО к корректному формату: с большой буквы."""

        if 'last_name' in validated_data:
            validated_data['last_name'] = (
                validated_data['last_name'].capitalize()
            )
        if 'first_name' in validated_data:
            validated_data['first_name'] = (
                validated_data['first_name'].capitalize()
            )
        if 'patronymic_name' in validated_data:
            validated_data['patronymic_name'] = (
                validated_data['patronymic_name'].capitalize()
            )

        return super().create(validated_data)

    def validate(self, attrs):
        if self.context.get('request').method == 'POST':
            if RSOUser.objects.filter(
                email=attrs.get('email'),
            ).exists():
                raise serializers.ValidationError(
                    'Пользователь с таким email уже существует.'
                )
        return super().validate(attrs)

    class Meta:
        model = RSOUser
        fields = (
            'region',
            'last_name',
            'first_name',
            'patronymic_name',
            'date_of_birth',
            'phone_number',
            'email',
            'username',
            'password',
        )


class BasePositionSerializer(serializers.ModelSerializer):
    """
    Базовый класс для вывода участников и их должностей
    при получении структурных единиц.
    """

    position = serializers.PrimaryKeyRelatedField(
        queryset=Position.objects.all(),
        required=False,
    )
    user = ShortUserSerializer(read_only=True)

    class Meta:
        model = UserCentralHeadquarterPosition
        fields = (
            'id',
            'user',
            'position',
            'is_trusted',
        )
        read_only_fields = ('user',)

    def to_representation(self, instance):
        serialized_data = super().to_representation(instance)
        position = instance.position
        if position:
            serialized_data['position'] = position.name
        return serialized_data


class CentralPositionSerializer(BasePositionSerializer):
    """Для вывода участников при получении центрального штаба."""

    class Meta:
        model = UserCentralHeadquarterPosition
        fields = BasePositionSerializer.Meta.fields
        read_only_fields = BasePositionSerializer.Meta.read_only_fields


class DistrictPositionSerializer(BasePositionSerializer):
    """Для вывода участников при получении окружного штаба."""

    class Meta:
        model = UserDistrictHeadquarterPosition
        fields = BasePositionSerializer.Meta.fields
        read_only_fields = BasePositionSerializer.Meta.read_only_fields


class RegionalPositionSerializer(BasePositionSerializer):
    """Для вывода участников при получении регионального штаба."""

    class Meta:
        model = UserRegionalHeadquarterPosition
        fields = BasePositionSerializer.Meta.fields
        read_only_fields = BasePositionSerializer.Meta.read_only_fields


class LocalPositionSerializer(BasePositionSerializer):
    """Для вывода участников при получении местного штаба."""

    class Meta:
        model = UserLocalHeadquarterPosition
        fields = BasePositionSerializer.Meta.fields
        read_only_fields = BasePositionSerializer.Meta.read_only_fields


class EducationalPositionSerializer(BasePositionSerializer):
    """Для вывода участников при получении образовательного штаба."""

    class Meta:
        model = UserEducationalHeadquarterPosition
        fields = BasePositionSerializer.Meta.fields
        read_only_fields = BasePositionSerializer.Meta.read_only_fields


class DetachmentPositionSerializer(BasePositionSerializer):
    """Сериализаатор для добавления пользователя в отряд."""

    class Meta:
        model = UserDetachmentPosition
        fields = BasePositionSerializer.Meta.fields
        read_only_fields = BasePositionSerializer.Meta.read_only_fields


class BasePositionOnlySerializer(serializers.ModelSerializer):
    """
    Базовый класс для вывода должностей
    пользователя в /rsousers/{id}/positions/
    """

    position = serializers.SlugRelatedField(
        queryset=Position.objects.all(),
        slug_field='name'
    )

    class Meta:
        model = None
        fields = ('id', 'position', 'is_trusted')


class CentralPositionOnlySerializer(BasePositionOnlySerializer):
    headquarter = serializers.PrimaryKeyRelatedField(
        queryset=CentralHeadquarter.objects.all(),
    )

    class Meta:
        model = UserCentralHeadquarterPosition
        fields = BasePositionSerializer.Meta.fields + ('headquarter',)


class DistrictPositionOnlySerializer(BasePositionOnlySerializer):
    headquarter = serializers.PrimaryKeyRelatedField(
        queryset=DistrictHeadquarter.objects.all(),
    )

    class Meta:
        model = UserDistrictHeadquarterPosition
        fields = BasePositionSerializer.Meta.fields + ('headquarter',)


class RegionalPositionOnlySerializer(BasePositionOnlySerializer):
    headquarter = serializers.PrimaryKeyRelatedField(
        queryset=RegionalHeadquarter.objects.all(),
    )

    class Meta:
        model = UserRegionalHeadquarterPosition
        fields = BasePositionSerializer.Meta.fields + ('headquarter',)


class LocalPositionOnlySerializer(BasePositionOnlySerializer):
    headquarter = serializers.PrimaryKeyRelatedField(
        queryset=LocalHeadquarter.objects.all(),
    )

    class Meta:
        model = UserLocalHeadquarterPosition
        fields = BasePositionSerializer.Meta.fields + ('headquarter',)


class EducationalPositionOnlySerializer(BasePositionOnlySerializer):
    headquarter = serializers.PrimaryKeyRelatedField(
        queryset=EducationalHeadquarter.objects.all(),
    )

    class Meta:
        model = UserEducationalHeadquarterPosition
        fields = BasePositionSerializer.Meta.fields + ('headquarter',)


class DetachmentPositionOnlySerializer(BasePositionOnlySerializer):
    headquarter = serializers.PrimaryKeyRelatedField(
        queryset=Detachment.objects.all(),
    )

    class Meta:
        model = UserDetachmentPosition
        fields = BasePositionSerializer.Meta.fields + ('headquarter',)


class UserHeadquarterPositionSerializer(serializers.ModelSerializer):
    """
    Сериализатор для вывода объектов должностей в структурных
    единицах, в которых состоит юзер.
    """

    usercentralheadquarterposition = CentralPositionOnlySerializer()
    userdistrictheadquarterposition = DistrictPositionOnlySerializer()
    userregionalheadquarterposition = RegionalPositionOnlySerializer()
    userlocalheadquarterposition = LocalPositionOnlySerializer()
    usereducationalheadquarterposition = EducationalPositionOnlySerializer()
    userdetachmentposition = DetachmentPositionOnlySerializer()

    class Meta:
        model = RSOUser
        fields = (
            'usercentralheadquarterposition',
            'userdistrictheadquarterposition',
            'userregionalheadquarterposition',
            'userlocalheadquarterposition',
            'usereducationalheadquarterposition',
            'userdetachmentposition'
        )


class BaseShortUnitSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для хранения общей логики штабов.

    Хранит только поля id, name и banner.
    """

    class Meta:
        model = None
        fields = (
            'id',
            'name',
            'banner',
        )


class ShortDistrictHeadquarterSerializer(BaseShortUnitSerializer):
    class Meta:
        model = DistrictHeadquarter
        fields = BaseShortUnitSerializer.Meta.fields


class ShortRegionalHeadquarterSerializer(BaseShortUnitSerializer):
    class Meta:
        model = RegionalHeadquarter
        fields = BaseShortUnitSerializer.Meta.fields


class ShortLocalHeadquarterSerializer(BaseShortUnitSerializer):
    class Meta:
        model = LocalHeadquarter
        fields = BaseShortUnitSerializer.Meta.fields


class ShortEducationalHeadquarterSerializer(BaseShortUnitSerializer):
    class Meta:
        model = EducationalHeadquarter
        fields = BaseShortUnitSerializer.Meta.fields


class ShortDetachmentSerializer(BaseShortUnitSerializer):
    class Meta:
        model = Detachment
        fields = BaseShortUnitSerializer.Meta.fields


class BaseUnitSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для хранения общей логики штабов.

    Предназначен для использования как родительский класс для всех
    сериализаторов штабов, обеспечивая наследование общих полей и методов.
    """

    _POSITIONS_MAPPING = {
        CentralHeadquarter: (
            UserCentralHeadquarterPosition, CentralPositionSerializer
        ),
        DistrictHeadquarter: (
            UserDistrictHeadquarterPosition, DistrictPositionSerializer
        ),
        RegionalHeadquarter: (
            UserRegionalHeadquarterPosition, RegionalPositionSerializer
        ),
        LocalHeadquarter: (
            UserLocalHeadquarterPosition, LocalPositionSerializer
        ),
        EducationalHeadquarter: (
            UserEducationalHeadquarterPosition, EducationalPositionSerializer
        ),
        Detachment: (UserDetachmentPosition, DetachmentPositionSerializer),
    }

    commander = serializers.PrimaryKeyRelatedField(
        queryset=RSOUser.objects.all(),
    )
    members_count = serializers.SerializerMethodField(read_only=True)
    participants_count = serializers.SerializerMethodField(read_only=True)
    leadership = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = None
        fields = (
            'id',
            'name',
            'commander',
            'about',
            'emblem',
            'social_vk',
            'social_tg',
            'banner',
            'slogan',
            'city',
            'members_count',
            'participants_count',
            'leadership',
        )

    def to_representation(self, instance):
        """Переопределяем представление данных для полей commader."""
        serialized_data = super().to_representation(instance)
        commander = instance.commander
        if commander:
            serialized_data['commander'] = ShortUserSerializer(commander).data
        return serialized_data

    def _get_position_instance(self):
        if isinstance(self.instance, QuerySet):
            print('УСЛОВИЕ СРАБОТАЛО')
            instance_type = type(self.instance.first())
        else:
            print('УСЛОВИЕ НЕ СРАБОТАЛО')
            instance_type = type(self.instance)
        print(instance_type)

        for model_class, (
                position_model, _
        ) in self._POSITIONS_MAPPING.items():
            if issubclass(instance_type, model_class):
                return position_model

    def _get_position_serializer(self):
        if isinstance(self.instance, QuerySet):
            print('УСЛОВИЕ СРАБОТАЛО')
            instance_type = type(self.instance.first())
        else:
            print('УСЛОВИЕ НЕ СРАБОТАЛО')
            instance_type = type(self.instance)
        print(instance_type)

        for model_class, (
                _, serializer_class
        ) in self._POSITIONS_MAPPING.items():
            if issubclass(instance_type, model_class):
                return serializer_class

    def get_leadership(self, instance):
        """
        Вывод руководства отряда (пользователи с должностями "Мастер
        (методист)" и "Комиссар", точные названия которых прописаны
        в настройках).
        """
        serializer = self._get_position_serializer()
        position_instance = self._get_position_instance()
        leaders = position_instance.objects.filter(
            Q(position__name=settings.MASTER_METHODIST_POSITION_NAME) |
            Q(position__name=settings.COMMISSIONER_POSITION_NAME)
        )
        return serializer(leaders, many=True).data

    @staticmethod
    def get_members_count(instance):
        return instance.members.filter(user__membership_fee=True).count()

    @staticmethod
    def get_participants_count(instance):
        return instance.members.count()

    def validate(self, attrs):
        """
        Запрещает назначить пользователя командиром, если он уже им является.
        """
        commander_id = attrs.get('commander')
        print('валидириуем')
        print('командир айди:', commander_id)
        print(self.instance)
        if commander_id:
            instance_type = self.Meta.model
            print(f'INSTANCE TYPE: {instance_type}')
            for model_class in self._POSITIONS_MAPPING:
                if not issubclass(instance_type, model_class):
                    continue
                print(f'MODEL CLASS: {model_class}')
                existing_units = model_class.objects.exclude(
                    id=getattr(self.instance, 'id', None))

                if existing_units.filter(commander=commander_id).exists():
                    raise serializers.ValidationError(
                        f"Пользователь уже является командиром другого "
                        f"{model_class.__name__}."
                    )

        return attrs


class CentralHeadquarterSerializer(BaseUnitSerializer):
    """Сериализатор для центрального штаба.

    Наследует общую логику и поля от BaseUnitSerializer и связывает
    с моделью CentralHeadquarter.
    """
    working_years = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CentralHeadquarter
        fields = BaseUnitSerializer.Meta.fields + (
            'working_years',
            'detachments_appearance_year',
            'rso_founding_congress_date',
        )

    @staticmethod
    def get_working_years(instance):
        return dt.datetime.now().year - 1958


class DistrictHeadquarterSerializer(BaseUnitSerializer):
    """Сериализатор для окружного штаба.

    Дополнительно к полям из BaseUnitSerializer, добавляет поле
    central_headquarter для связи с центральным штабом.
    """

    central_headquarter = serializers.PrimaryKeyRelatedField(
        queryset=CentralHeadquarter.objects.all(),
        required=False
    )
    commander = serializers.PrimaryKeyRelatedField(
        queryset=RSOUser.objects.all(),
    )
    members = DistrictPositionSerializer(
        many=True,
        read_only=True
    )
    regional_headquarters = serializers.SerializerMethodField(read_only=True)
    local_headquarters = serializers.SerializerMethodField(read_only=True)
    educational_headquarters = serializers.SerializerMethodField(read_only=True)
    detachments = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = DistrictHeadquarter
        fields = BaseUnitSerializer.Meta.fields + (
            'central_headquarter',
            'founding_date',
            'members',
            'regional_headquarters',
            'local_headquarters',
            'educational_headquarters',
            'detachments',
        )
        read_only_fields = ('regional_headquarters',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cached_units = None

    def _get_units(self, obj):
        """
        Сохраняем юниты в кэш и отдаем их. Если есть в кэше, берем оттуда.
        """
        if self._cached_units is None:
            self._cached_units = obj.get_related_units()
        return self._cached_units

    def get_regional_headquarters(self, obj):
        hqs = RegionalHeadquarter.objects.filter(district_headquarter=obj)
        return ShortRegionalHeadquarterSerializer(hqs, many=True).data

    def get_educational_headquarters(self, obj):
        units = self._get_units(obj)
        educational_headquarters_serializer = (
            ShortEducationalHeadquarterSerializer(
                units['educational_headquarters'], many=True
            )
        ).data
        return educational_headquarters_serializer

    def get_local_headquarters(self, obj):
        units = self._get_units(obj)
        local_headquarters_serializer = ShortLocalHeadquarterSerializer(
            units['local_headquarters'], many=True
        ).data
        return local_headquarters_serializer

    def get_detachments(self, obj):
        units = self._get_units(obj)
        detachment_serializer = ShortDetachmentSerializer(
            units['detachments'], many=True
        ).data
        return detachment_serializer

    def to_representation(self, obj):
        """Для очищения кэша перед началом сериализации."""
        self._cached_units = None
        return super().to_representation(obj)


class RegionalHeadquarterSerializer(BaseUnitSerializer):
    """Сериализатор для регионального штаба.

    Включает в себя поля из BaseUnitSerializer, а также поля region и
    district_headquarter для указания региона и привязки к окружному штабу.
    Выводит пользователей для верификации.
    """

    region = serializers.PrimaryKeyRelatedField(
        queryset=Region.objects.all()
    )
    district_headquarter = serializers.PrimaryKeyRelatedField(
        queryset=DistrictHeadquarter.objects.all(),
    )
    detachments = serializers.SerializerMethodField(read_only=True)
    local_headquarters = serializers.SerializerMethodField(read_only=True)
    educational_headquarters = serializers.SerializerMethodField(
        read_only=True
    )

    class Meta:
        model = RegionalHeadquarter
        fields = BaseUnitSerializer.Meta.fields + (
            'region',
            'district_headquarter',
            'name_for_certificates',
            'conference_date',
            'registry_date',
            'registry_number',
            'case_name',
            'legal_address',
            'requisites',
            'founding_date',
            'detachments',
            'local_headquarters',
            'educational_headquarters',
        )
        read_only_fields = (
            'detachments',
            'local_headquarters',
            'educational_headquarters',
        )

    def to_representation(self, instance):
        """
        Вызывает родительский метод to_representation,
        а также изменяем вывод region.
        """
        serialized_data = super().to_representation(instance)
        region = instance.region
        if region:
            serialized_data['region'] = region.name
        return serialized_data

    def get_detachments(self, obj):
        hqs = Detachment.objects.filter(regional_headquarter=obj)
        return ShortDetachmentSerializer(hqs, many=True).data

    def get_local_headquarters(self, obj):
        hqs = LocalHeadquarter.objects.filter(regional_headquarter=obj)
        return ShortLocalHeadquarterSerializer(hqs, many=True).data

    def get_educational_headquarters(self, obj):
        hqs = EducationalHeadquarter.objects.filter(regional_headquarter=obj)
        return ShortEducationalHeadquarterSerializer(hqs, many=True).data


class LocalHeadquarterSerializer(BaseUnitSerializer):
    """Сериализатор для местного штаба.

    Расширяет BaseUnitSerializer, добавляя поле regional_headquarter
    для связи с региональным штабом.
    """

    regional_headquarter = serializers.PrimaryKeyRelatedField(
        queryset=RegionalHeadquarter.objects.all(),
    )
    educational_headquarters = serializers.SerializerMethodField(
        read_only=True
    )
    detachments = serializers.SerializerMethodField(
        read_only=True
    )

    class Meta:
        model = LocalHeadquarter
        fields = BaseUnitSerializer.Meta.fields + (
            'regional_headquarter',
            'founding_date',
            'educational_headquarters',
            'detachments',
        )
        read_only_fields = ('educational_headquarters', 'detachments')

    def get_educational_headquarters(self, obj):
        hqs = EducationalHeadquarter.objects.filter(local_headquarter=obj)
        return ShortEducationalHeadquarterSerializer(hqs, many=True).data

    def get_detachments(self, obj):
        hqs = Detachment.objects.filter(local_headquarter=obj)
        return ShortDetachmentSerializer(hqs, many=True).data


class EducationalHeadquarterSerializer(BaseUnitSerializer):
    """Сериализатор для образовательного штаба.

    Содержит ссылки на образовательное учреждение и связанные
    местный и региональный штабы. Включает в себя валидацию для
    проверки согласованности связей между штабами.
    """

    educational_institution = serializers.PrimaryKeyRelatedField(
        queryset=EducationalInstitution.objects.all(),
    )
    regional_headquarter = serializers.PrimaryKeyRelatedField(
        queryset=RegionalHeadquarter.objects.all(),
    )
    local_headquarter = serializers.PrimaryKeyRelatedField(
        queryset=LocalHeadquarter.objects.all(),
        required=False,
    )
    detachments = serializers.SerializerMethodField(
        read_only=True
    )

    class Meta:
        model = EducationalHeadquarter
        fields = BaseUnitSerializer.Meta.fields + (
            'educational_institution',
            'local_headquarter',
            'regional_headquarter',
            'founding_date',
            'detachments'
        )
        read_only_fields = ('detachments',)

    def validate(self, data):
        """
        Вызывает валидацию модели для проверки согласованности между местным
         и региональным штабами.
        """
        instance = EducationalHeadquarter(**data)
        try:
            instance.check_headquarters_relations()
            super().validate(data)
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)
        return data

    def to_representation(self, instance):
        """
        Вызывает родительский метод to_representation,
        а также изменяет вывод educational_institution.
        """
        serialized_data = super().to_representation(instance)
        educational_institution = instance.educational_institution
        serialized_data['educational_institution'] = (
            EducationalInstitutionSerializer(educational_institution).data
        )
        return serialized_data

    def get_detachments(self, obj):
        hqs = Detachment.objects.filter(educational_headquarter=obj)
        return ShortDetachmentSerializer(hqs, many=True).data


class UserDetachmentApplicationSerializer(serializers.ModelSerializer):
    """Сериализатор для подачи заявок в отряд"""

    class Meta:
        model = UserDetachmentApplication
        fields = ('id', 'user',)
        read_only_fields = ('user',)

    def validate(self, attrs):
        """
        Запрещает подачу заявки пользователем в отряд, относящемуся к
        региональному штабу, который не привязан к региону пользователя.
        Запрещает повторную подачу заявки в тот же или другие отряды.
        """
        user = self.context['request'].user
        detachment = Detachment.objects.get(
            id=self.context['view'].kwargs.get('pk')
        )
        if UserDetachmentApplication.objects.filter(user=user).exists():
            raise ValidationError(
                'Вы уже подали заявку в один из отрядов'
            )
        if detachment.regional_headquarter.region != user.region:
            raise ValidationError(
                'Нельзя подать заявку на вступление в отряд вне своего региона'
            )
        return attrs


class UserDetachmentApplicationReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения заявок в отряд"""

    user = ShortUserSerializer(read_only=True)

    class Meta:
        model = UserDetachmentApplication
        fields = ('id', 'user')
        read_only_fields = ('user',)


class DetachmentSerializer(BaseUnitSerializer):
    """Сериализатор для отряда.

    Наследует общие поля из BaseUnitSerializer и добавляет специфические поля
    для отряда, включая связи с образовательным, местным и региональным
    штабами, а также поле для указания области деятельности (area).
    Включает в себя валидацию для
    проверки согласованности связей между штабами.
    """

    educational_headquarter = serializers.PrimaryKeyRelatedField(
        queryset=EducationalHeadquarter.objects.all(),
        required=False,
    )
    local_headquarter = serializers.PrimaryKeyRelatedField(
        queryset=LocalHeadquarter.objects.all(),
        required=False
    )
    regional_headquarter = serializers.PrimaryKeyRelatedField(
        queryset=RegionalHeadquarter.objects.all(),
        required=False
    )
    area = serializers.PrimaryKeyRelatedField(
        queryset=Area.objects.all()
    )
    nomination = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    tandem_partner = serializers.SerializerMethodField()

    class Meta:
        model = Detachment
        fields = BaseUnitSerializer.Meta.fields + (
            'educational_headquarter',
            'local_headquarter',
            'regional_headquarter',
            'region',
            'educational_institution',
            'city',
            'area',
            'photo1',
            'photo2',
            'photo3',
            'photo4',
            'city',
            'founding_date',
            'nomination',
            'status',
            'tandem_partner',
        )

    def to_representation(self, instance):
        """
        Вызывает родительский метод to_representation,
        а также изменяет вывод area, educational_institution и region.
        """
        serialized_data = super().to_representation(instance)
        area = instance.area
        educational_institution = instance.educational_institution
        region = instance.region
        serialized_data['area'] = area.name
        serialized_data['educational_institution'] = (
            EducationalInstitutionSerializer(educational_institution).data
        )
        serialized_data['region'] = region.name
        return serialized_data

    def validate(self, data):
        """
        Вызывает валидацию модели для проверки согласованности между
        образовательным, местным и региональным штабами.
        """
        instance = Detachment(**data)
        try:
            instance.check_headquarters_relations()
            super().validate(data)
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)
        return data

    def get_status(self, obj):
        if not СompetitionParticipants.objects.filter(
            Q(detachment=obj) & Q(junior_detachment__isnull=False) |
            Q(detachment__isnull=False) & Q(junior_detachment=obj)
        ).exists():
            return None
        if СompetitionParticipants.objects.filter(
            Q(detachment=obj) & Q(junior_detachment__isnull=False)
        ).exists():
            return 'Наставник'
        return 'Старт'

    def get_nomination(self, obj):
        if not СompetitionParticipants.objects.filter(
            Q(detachment=obj) & Q(junior_detachment__isnull=False) |
            Q(detachment__isnull=False) & Q(junior_detachment=obj) |
            Q(junior_detachment=obj)
        ).exists():
            return None
        if СompetitionParticipants.objects.filter(
            Q(detachment=obj) & Q(junior_detachment__isnull=False) |
            Q(detachment__isnull=False) & Q(junior_detachment=obj)
        ).exists():
            return 'Тандем'
        return 'Дебют'

    def get_tandem_partner(self, obj):
        participants = СompetitionParticipants.objects.filter(
            Q(detachment=obj) | Q(junior_detachment=obj)
        ).first()
        if participants:
            if participants.detachment == obj:
                return ShortDetachmentSerializer(
                    participants.junior_detachment
                ).data
            if participants.detachment:
                return ShortDetachmentSerializer(
                    participants.detachment
                ).data


class MemberCertSerializer(serializers.ModelSerializer):
    users = ShortUserSerializer(
        many=True,
        read_only=True
    )
    ids = serializers.ListField(
        child=serializers.IntegerField(), read_only=True
    )

    class Meta:
        model = MemberCert
        fields = (
            'id',
            'users',
            'cert_start_date',
            'cert_end_date',
            'recipient',
            'issue_date',
            'number',
            'ids',
            'signatory',
            'position_procuration'
        )


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


class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = RSOUser
        fields = ('email',)


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
    detachments = ShortDetachmentSerializerME(many=True)

    class Meta:
        model = RegionalHeadquarter
        fields = ShortUnitSerializer.Meta.fields + (
            'local_headquarters',
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


class DjoserUserSerializer(RSOUserSerializer):
    """Для сериализации безопасной части данных пользователя.

    Для использования в дефолтном джосеровском /users/.
    """

    avatar = UserAvatarSerializer(source='media', read_only=True)

    class Meta:
        model = RSOUser
        fields = (
            'id',
            'username',
            'avatar',
            'email',
            'first_name',
            'last_name',
            'patronymic_name',
            'date_of_birth',
            'is_adult',
            'last_name_lat',
            'first_name_lat',
            'patronymic_lat',
            'phone_number',
            'gender',
            'region',
            'address',
            'bio',
            'social_vk',
            'social_tg',
            'membership_fee',
            'is_verified',
            'media',
            'education',
            'privacy',
            'central_headquarter_id',
            'district_headquarter_id',
            'regional_headquarter_id',
            'local_headquarter_id',
            'educational_headquarter_id',
            'detachment_id',
        )


class ShortDetachmentCompititionSerializer(BaseShortUnitSerializer):
    area = serializers.CharField(source='area.name')

    class Meta:
        model = Detachment
        fields = BaseShortUnitSerializer.Meta.fields + (
            'area',
        )


class СompetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Сompetition
        fields = '__all__'


class СompetitionApplicationsObjectSerializer(serializers.ModelSerializer):
    competition = СompetitionSerializer()
    junior_detachment = ShortDetachmentCompititionSerializer()
    detachment = ShortDetachmentCompititionSerializer()

    class Meta:
        model = СompetitionApplications
        fields = (
            'id',
            'competition',
            'junior_detachment',
            'detachment',
            'created_at',
            'is_confirmed_by_junior'
        )


class СompetitionApplicationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = СompetitionApplications
        fields = (
            'id',
            'competition',
            'junior_detachment',
            'detachment',
            'created_at',
            'is_confirmed_by_junior'
        )
        read_only_fields = (
            'id',
            'created_at',
            'competition',
            'junior_detachment',
        )

    def validate(self, attrs):
        request = self.context.get('request')
        applications = СompetitionApplications.objects.all()
        participants = СompetitionParticipants.objects.all()
        if request.method == 'POST':
            MIN_DATE = (f'{settings.DATE_JUNIOR_SQUAD[2]}'
                        f'.{settings.DATE_JUNIOR_SQUAD[1]}.'
                        f'{settings.DATE_JUNIOR_SQUAD[0]} года')
            competition = self.context.get('competition')
            detachment = self.context.get('detachment')
            junior_detachment = self.context.get('junior_detachment')

            if detachment:
                if not request.data.get('junior_detachment'):
                    raise serializers.ValidationError(
                        f'- дата основания основания отряда ранее {MIN_DATE}'
                    )
                if detachment.founding_date >= date(
                    *settings.DATE_JUNIOR_SQUAD
                ):
                    raise serializers.ValidationError(
                        f'- отряд-наставник должен быть основан до {MIN_DATE}'
                    )
                if applications.filter(
                    competition=competition,
                    detachment=detachment
                ).exists() or participants.filter(
                    competition=competition,
                    detachment=detachment
                ).exists():
                    raise serializers.ValidationError(
                        'Вы уже подали заявку или участвуете в этом конкурсе'
                    )

            if junior_detachment.founding_date < date(
                *settings.DATE_JUNIOR_SQUAD
            ):
                raise serializers.ValidationError(
                    f'- дата основания отряда ранее {MIN_DATE}'
                )
            if applications.filter(
                competition=competition,
                junior_detachment=junior_detachment
                ).exists() or participants.filter(
                    competition=competition,
                    junior_detachment=junior_detachment
                    ).exists():
                raise serializers.ValidationError(
                    '- отряд уже подал заявку или участвует '
                    'в этом конкурсе'
                )
        return attrs


class СompetitionParticipantsObjectSerializer(serializers.ModelSerializer):
    detachment = ShortDetachmentCompititionSerializer()
    junior_detachment = ShortDetachmentCompititionSerializer()

    class Meta:
        model = СompetitionParticipants
        fields = (
            'id',
            'competition',
            'detachment',
            'junior_detachment',
            'created_at'
        )


class СompetitionParticipantsSerializer(serializers.ModelSerializer):
    class Meta:
        model = СompetitionParticipants
        fields = (
            'id',
            'competition',
            'detachment',
            'junior_detachment',
            'created_at'
        )
        read_only_fields = (
            'id',
            'competition',
            'detachment',
            'junior_detachment',
            'created_at'
        )

    def validate(self, attrs):
        request = self.context.get('request')
        if request.method == 'POST':
            application = self.context.get('application')
            if (application.detachment and not
                    application.is_confirmed_by_junior):
                raise serializers.ValidationError(
                    'Заявка еще не подтверждена младшим отрядом.'
                )
        return attrs
