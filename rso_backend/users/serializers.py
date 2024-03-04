from datetime import date

from django.db.models import Q
from django.http import Http404
from djoser.serializers import UserCreatePasswordRetypeSerializer
from rest_framework import serializers

from api.serializers import EducationalInstitutionSerializer, RegionSerializer
from api.utils import (create_first_or_exception, get_detachment_commander_num,
                       get_is_trusted, get_regional_headquarters_if_commander, get_regional_hq_commander_num)
from competitions.models import CompetitionApplications
from events.constants import EVENT_APPLICATIONS_MODEL
from events.models import EventOrganizationData
from headquarters.models import (CentralHeadquarter, Detachment,
                                 EducationalInstitution, Position, Region,
                                 RegionalHeadquarter,
                                 UserCentralHeadquarterPosition,
                                 UserDetachmentApplication,
                                 UserDetachmentPosition,
                                 UserDistrictHeadquarterPosition,
                                 UserEducationalHeadquarterPosition,
                                 UserLocalHeadquarterPosition,
                                 UserRegionalHeadquarterPosition)
from headquarters.serializers import (ShortDetachmentSerializer,
                                      ShortDistrictHeadquarterSerializer,
                                      ShortEducationalHeadquarterSerializer,
                                      ShortLocalHeadquarterSerializer,
                                      ShortRegionalHeadquarterSerializer)
from users.constants import (DOCUMENTS_RAW_EXISTS, EDUCATION_RAW_EXISTS,
                             MEDIA_RAW_EXISTS, PRIVACY_RAW_EXISTS,
                             REGION_RAW_EXISTS, STATEMENT_RAW_EXISTS,
                             TOO_MANY_EDUCATIONS)
from users.models import (RSOUser, UserDocuments, UserEducation,
                          UserForeignDocuments, UserMedia, UserParent,
                          UserPrivacySettings, UserProfessionalEducation,
                          UserRegion, UserStatementDocuments,
                          UserVerificationRequest)
from users.short_serializers import ShortUserSerializer


class EmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = RSOUser
        fields = ('email',)


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

    def to_representation(self, instance):
        """Изменяет вывод образовательной организации."""
        serialized_data = super().to_representation(instance)
        study_inst = instance.study_institution
        if study_inst:
            serialized_data['study_institution'] = (
                EducationalInstitutionSerializer(study_inst).data
            )
        return serialized_data

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

    study_institution = serializers.PrimaryKeyRelatedField(
        queryset=EducationalInstitution.objects.all(),
    )

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
            raise Http404(
                'У данного юзера не введено дополнительное'
                ' профессиональное образование.'
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


class UserAvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода аватарки из модели с Медиа юзера."""

    class Meta:
        ref_name = 'user_avatar'
        model = UserMedia
        fields = ('photo',)


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
            'is_rso_member',
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
            serialized_data['region'] = RegionSerializer(region).data

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
            central_headquarter = CentralHeadquarter.objects.first()
            central_headquarter_id = central_headquarter.id
        except CentralHeadquarter.DoesNotExist:
            central_headquarter_id = None
        return central_headquarter_id

    @staticmethod
    def get_district_headquarter_id(instance):
        try:
            district_headquarter = (
                UserDistrictHeadquarterPosition.objects.get(
                    user_id=instance.id
                )
            )
            district_headquarter_id = district_headquarter.headquarter_id
        except UserDistrictHeadquarterPosition.DoesNotExist:
            district_headquarter_id = None
        return district_headquarter_id

    @staticmethod
    def get_regional_headquarter_id(instance):
        try:
            regional_headquarter = (
                UserRegionalHeadquarterPosition.objects.get(
                    user_id=instance.id
                )
            )
            regional_headquarter_id = regional_headquarter.headquarter_id
        except UserRegionalHeadquarterPosition.DoesNotExist:
            regional_headquarter_id = None
        return regional_headquarter_id

    @staticmethod
    def get_local_headquarter_id(instance):
        try:
            local_headquarter = (
                UserLocalHeadquarterPosition.objects.get(
                    user_id=instance.id
                )
            )
            local_headquarter_id = local_headquarter.headquarter_id
        except UserLocalHeadquarterPosition.DoesNotExist:
            local_headquarter_id = None
        return local_headquarter_id

    @staticmethod
    def get_educational_headquarter_id(instance):
        try:
            educational_headquarter = (
                UserEducationalHeadquarterPosition.objects.get(
                    user_id=instance.id
                )
            )
            educational_headquarter_id = educational_headquarter.headquarter_id
        except UserEducationalHeadquarterPosition.DoesNotExist:
            educational_headquarter_id = None
        return educational_headquarter_id

    @staticmethod
    def get_detachment_id(instance):
        try:
            detachment = (
                UserDetachmentPosition.objects.get(
                    user_id=instance.id
                )
            )
            detachment_id = detachment.headquarter_id
        except UserDetachmentPosition.DoesNotExist:
            detachment_id = None
        return detachment_id

    @staticmethod
    def get_sent_verification(instance):
        verification_status = UserVerificationRequest.objects.filter(
            user_id=instance.id
        ).exists() or instance.is_verified
        return verification_status


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
        fields = BasePositionOnlySerializer.Meta.fields + ('headquarter',)


class DistrictPositionOnlySerializer(BasePositionOnlySerializer):
    headquarter = ShortDistrictHeadquarterSerializer()

    class Meta:
        model = UserDistrictHeadquarterPosition
        fields = BasePositionOnlySerializer.Meta.fields + ('headquarter',)


class RegionalPositionOnlySerializer(BasePositionOnlySerializer):
    headquarter = ShortRegionalHeadquarterSerializer()

    class Meta:
        model = UserRegionalHeadquarterPosition
        fields = BasePositionOnlySerializer.Meta.fields + ('headquarter',)


class LocalPositionOnlySerializer(BasePositionOnlySerializer):
    headquarter = ShortLocalHeadquarterSerializer()

    class Meta:
        model = UserLocalHeadquarterPosition
        fields = BasePositionOnlySerializer.Meta.fields + ('headquarter',)


class EducationalPositionOnlySerializer(BasePositionOnlySerializer):
    headquarter = ShortEducationalHeadquarterSerializer()

    class Meta:
        model = UserEducationalHeadquarterPosition
        fields = BasePositionOnlySerializer.Meta.fields + ('headquarter',)


class DetachmentPositionOnlySerializer(BasePositionOnlySerializer):
    headquarter = ShortDetachmentSerializer()

    class Meta:
        model = UserDetachmentPosition
        fields = BasePositionOnlySerializer.Meta.fields + ('headquarter',)


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


class UserCommanderSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода отрядов, где юзер коммандир."""

    centralheadquarter_commander = serializers.PrimaryKeyRelatedField(
        queryset=CentralHeadquarter.objects.all()
    )
    districtheadquarter_commander = ShortDistrictHeadquarterSerializer()
    regionalheadquarter_commander = ShortRegionalHeadquarterSerializer()
    localheadquarter_commander = ShortLocalHeadquarterSerializer()
    educationalheadquarter_commander = ShortEducationalHeadquarterSerializer()
    detachment_commander = ShortDetachmentSerializer()

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
                raise serializers.ValidationError({
                    'email': 'Пользователь с таким email уже существует.'
                })
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


class SafeUserSerializer(RSOUserSerializer):
    """Для сериализации безопасной части данных пользователя.

    Для использования в /safe_users/.
    """

    avatar = UserAvatarSerializer(source='media', read_only=True)

    class Meta:
        ref_name = 'safe_users'
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
            'is_rso_member',
            'education',
            'privacy',
            'central_headquarter_id',
            'district_headquarter_id',
            'regional_headquarter_id',
            'local_headquarter_id',
            'educational_headquarter_id',
            'detachment_id',
        )


class UserNotificationsCountSerializer(serializers.Serializer):
    """Считает количество активных заявок,
    доступных для рассмотрения пользователю.
    """

    count = serializers.SerializerMethodField()

    class Meta:
        model = RSOUser
        fields = ('count',)

    @staticmethod
    def get_count(instance):
        regional_hq_members_to_verify_count = 0
        detachment_members_to_verify_count = 0
        detachment_applications_count = 0
        event_applications_count = 0
        competition_applications_count = 0

        detachment_id = get_detachment_commander_num(user=instance)
        if detachment_id:
            detachment = Detachment.objects.get(pk=detachment_id)
            user_ids_in_verification_request = (
                UserVerificationRequest.objects.values_list(
                    'user_id', flat=True
                )
            )
            detachment_members_to_verify_count += detachment.members.filter(
                user__id__in=user_ids_in_verification_request
            ).count()
            detachment_applications_count += (
                UserDetachmentApplication.objects.filter(
                    detachment=detachment
                ).count()
            )

        regional_hq_id = get_regional_hq_commander_num(user=instance)
        if regional_hq_id:
            regional_hq = RegionalHeadquarter.objects.get(pk=regional_hq_id)
            regional_hq_members_to_verify_count += (
                UserVerificationRequest.objects.filter(
                    user__region=regional_hq.region,
                ).count()
            )

        events = instance.event_set.all()
        for event in events:
            event_application_type = event.application_type
            event_applications_count += (
                EVENT_APPLICATIONS_MODEL[
                    event_application_type
                ].objects.filter(event=event).count()
            )

        headquarter = get_regional_headquarters_if_commander(instance)
        if headquarter:
            competition_applications_count += (
                CompetitionApplications.objects.filter(
                    Q(junior_detachment__region=headquarter.region) &
                    Q(detachment__isnull=False) &
                    Q(is_confirmed_by_junior=True) |
                    Q(junior_detachment__region=headquarter.region) &
                    Q(detachment__isnull=True)
                ).count()
            )

        return (
                detachment_members_to_verify_count +
                regional_hq_members_to_verify_count +
                detachment_applications_count +
                event_applications_count +
                competition_applications_count
        )
