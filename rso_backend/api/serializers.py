import datetime as dt
from datetime import date

from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from djoser.serializers import UserCreatePasswordRetypeSerializer
from rest_framework import serializers

from api.constants import (DOCUMENTS_RAW_EXISTS, EDUCATION_RAW_EXISTS,
                           EVENT_DOCUMENT_DATA_RAW_EXISTS,
                           EVENT_TIME_DATA_RAW_EXISTS, MEDIA_RAW_EXISTS,
                           PRIVACY_RAW_EXISTS, REGION_RAW_EXISTS,
                           STATEMENT_RAW_EXISTS, TOO_MANY_EDUCATIONS)
from api.utils import create_first_or_exception
from events.models import (Event, EventAdditionalIssue, EventApplications,
                           EventDocument, EventDocumentData, EventIssueAnswer,
                           EventOrganizationData, EventParticipants,
                           EventTimeData, EventUserDocument)
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
        fields = ('id', 'name', )


class EducationalInstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationalInstitution
        fields = (
            'id', 'short_name', 'name', 'rector', 'rector_email', 'region'
        )


class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ('id', 'name', )


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ('id', 'name',)


class EventTimeDataSerializer(serializers.ModelSerializer):
    event_duration_type = serializers.CharField(
        source='get_event_duration_type_display'
    )

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
    available_structural_units = serializers.CharField(
        source='get_available_structural_units_display'
    )
    application_type = serializers.CharField(
        source='get_application_type_display'
    )
    direction = serializers.CharField(source='get_direction_display')
    format = serializers.CharField(source='get_format_display')
    status = serializers.CharField(source='get_status_display')
    scale = serializers.CharField(source='get_scale_display')

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
            'scale',
            'created_at',
            'documents',
            'organization_data',
            'time_data',
            'document_data',
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
    privacy_telephone = serializers.CharField(
        source='get_privacy_telephone_display'
    )
    privacy_email = serializers.CharField(source='get_privacy_email_display')
    privacy_social = serializers.CharField(source='get_privacy_social_display')
    privacy_about = serializers.CharField(source='get_privacy_about_display')
    privacy_photo = serializers.CharField(source='get_privacy_photo_display')

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
        )
        read_only_fields = ('membership_fee', 'is_verified')

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
            central_headquarter_id = CentralHeadquarter.objects.get(
                id=instance.id
            ).id
        except CentralHeadquarter.DoesNotExist:
            central_headquarter_id = None
        return central_headquarter_id

    @staticmethod
    def get_district_headquarter_id(instance):
        try:
            district_headquarter_id = DistrictHeadquarter.objects.get(
                id=instance.id
            ).id
        except DistrictHeadquarter.DoesNotExist:
            district_headquarter_id = None
        return district_headquarter_id

    @staticmethod
    def get_regional_headquarter_id(instance):
        try:
            regional_headquarter_id = RegionalHeadquarter.objects.get(
                id=instance.id
            ).id
        except RegionalHeadquarter.DoesNotExist:
            regional_headquarter_id = None
        return regional_headquarter_id

    @staticmethod
    def get_local_headquarter_id(instance):
        try:
            local_headquarter_id = LocalHeadquarter.objects.get(
                id=instance.id
            ).id
        except LocalHeadquarter.DoesNotExist:
            local_headquarter_id = None
        return local_headquarter_id

    @staticmethod
    def get_educational_headquarter_id(instance):
        try:
            eduicational_headquarter_id = EducationalHeadquarter.objects.get(
                id=instance.id
            ).id
        except EducationalHeadquarter.DoesNotExist:
            eduicational_headquarter_id = None
        return eduicational_headquarter_id

    @staticmethod
    def get_detachment_id(instance):
        try:
            detachment_id = Detachment.objects.get(id=instance.id).id
        except Detachment.DoesNotExist:
            detachment_id = None
        return detachment_id


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
        )


class UserVerificationSerializer(serializers.ModelSerializer):
    """Для сериализации заявок на верификацию."""

    user = ShortUserSerializer()

    class Meta:
        model = UserVerificationRequest
        fields = ('user',)


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
    """Для вывода участников при получении штаба."""

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

    commander = serializers.PrimaryKeyRelatedField(
        queryset=RSOUser.objects.all(),
    )
    members_count = serializers.SerializerMethodField(read_only=True)
    participants_count = serializers.SerializerMethodField(read_only=True)

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
        )

    @staticmethod
    def get_members_count(instance):
        return instance.members.filter(user__membership_fee=True).count()

    @staticmethod
    def get_participants_count(instance):
        return instance.members.count()


class DistrictHeadquarterSerializer(BaseUnitSerializer):
    """Сериализатор для окружного штаба.

    Дополнительно к полям из BaseUnitSerializer, добавляет поле
    central_headquarter для связи с центральным штабом.
    """

    central_headquarter = serializers.PrimaryKeyRelatedField(
        queryset=CentralHeadquarter.objects.all()
    )
    commander = serializers.PrimaryKeyRelatedField(
        queryset=RSOUser.objects.all(),
    )
    members = DistrictPositionSerializer(
        many=True,
        read_only=True
    )
    regional_headquarters = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = DistrictHeadquarter
        fields = BaseUnitSerializer.Meta.fields + (
            'central_headquarter',
            'founding_date',
            'members',
            'regional_headquarters',
        )
        read_only_fields = ('regional_headquarters', )

    def get_regional_headquarters(self, obj):
        hqs = RegionalHeadquarter.objects.filter(district_headquarter=obj)
        return ShortRegionalHeadquarterSerializer(hqs, many=True).data


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
    members = RegionalPositionSerializer(
        many=True,
        read_only=True
    )
    users_for_verification = serializers.SerializerMethodField(read_only=True)
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
            'members',
            'users_for_verification',
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

    @staticmethod
    def get_users_for_verification(obj):
        verification_requests = UserVerificationRequest.objects.filter(
            user__region=obj.region,
            user__is_verified=False
        ).select_related('user')
        return [{
            'id': request.user.id,
            'name': f'{request.user.first_name} {request.user.last_name}',
            'email': request.user.email
        } for request in verification_requests]

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
    members = LocalPositionSerializer(
        many=True,
        read_only=True
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
            'members',
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
    members = EducationalPositionSerializer(
        many=True,
        read_only=True
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
            'members',
            'founding_date',
            'detachments'
        )
        read_only_fields = ('detachments', )

    def validate(self, data):
        """
        Вызывает валидацию модели для проверки согласованности между местным
         и региональным штабами.
        """
        instance = EducationalHeadquarter(**data)
        try:
            instance.full_clean()
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)
        return data

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
    applications = UserDetachmentApplicationSerializer(
        many=True,
        read_only=True
    )
    members = DetachmentPositionSerializer(
        many=True,
        read_only=True
    )
    users_for_verification = serializers.SerializerMethodField(read_only=True)

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
            'applications',
            'members',
            'users_for_verification',
            'founding_date',
        )

    def validate(self, data):
        """
        Вызывает валидацию модели для проверки согласованности между
        образовательным, местным и региональным штабами.
        """
        instance = Detachment(**data)
        try:
            instance.full_clean()
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)
        return data

    @staticmethod
    def get_users_for_verification(obj):
        users_positions = obj.members.filter(
            user__is_verified=False).select_related('user')

        return [{
            'id': position.user.id,
            'name': f'{position.user.first_name} {position.user.last_name}',
            'email': position.user.email
        } for position in users_positions]


class CentralHeadquarterSerializer(BaseUnitSerializer):
    """Сериализатор для центрального штаба.

    Наследует общую логику и поля от BaseUnitSerializer и связывает
    с моделью CentralHeadquarter.
    """
    members = CentralPositionSerializer(
        many=True,
        read_only=True
    )
    working_years = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CentralHeadquarter
        fields = BaseUnitSerializer.Meta.fields + (
            'members',
            'working_years',
        )

    @staticmethod
    def get_working_years(instance):
        return dt.datetime.now().year - 1958


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
        if len_uploaded_documents != len_documents:
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
    class Meta:
        model = EventUserDocument
        fields = '__all__'
        read_only_fields = (
            'id',
            'event',
            'user'
        )
