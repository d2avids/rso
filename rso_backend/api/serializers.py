import datetime as dt
from datetime import date

from django.core.exceptions import ValidationError
from djoser.serializers import UserCreatePasswordRetypeSerializer
from rest_framework import serializers

from api.constants import (DOCUMENTS_RAW_EXISTS, EDUCATION_RAW_EXISTS,
                           MEDIA_RAW_EXISTS, PRIVACY_RAW_EXISTS,
                           REGION_RAW_EXISTS, STATEMENT_RAW_EXISTS,
                           TOO_MANY_EDUCATIONS)
from api.utils import create_first_or_exception
from headquarters.models import (CentralHeadquarter, Detachment,
                                 DistrictHeadquarter, EducationalHeadquarter,
                                 EducationalInstitution, LocalHeadquarter,
                                 Position, Region, RegionalHeadquarter,
                                 UserCentralHeadquarterPosition,
                                 UserDetachmentApplication,
                                 UserDetachmentPosition,
                                 UserDistrictHeadquarterPosition,
                                 UserEducationalHeadquarterPosition,
                                 UserLocalHeadquarterPosition,
                                 UserRegionalHeadquarterPosition, Area,)
from users.models import (ProfessionalEduction, RSOUser, UserDocuments,
                          UserEducation, UserMedia, UserPrivacySettings,
                          UserRegion, UsersParent, UserStatementDocuments,
                          UserVerificationRequest, ForeignUserDocuments,
                          MemberCert)


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
        model = ProfessionalEduction
        fields = (
            'study_institution',
            'years_of_study',
            'exam_score',
            'qualification'
        )


class ProfessionalEductionSerializerID(ProfessionalEductionSerializer):
    """Сериализатор дополнительного проф образования всех юзеров c ID."""

    class Meta:
        model = ProfessionalEduction
        fields = ('id',) + ProfessionalEductionSerializer.Meta.fields

    def create(self, validated_data):
        """Сохраенение в БД допрофобразования.

        В методе реализована проверка количества записей.
        """

        manager = ProfessionalEduction.objects
        if manager.count() < 5:
            return manager.create(**validated_data)
        raise serializers.ValidationError(TOO_MANY_EDUCATIONS)


class UserProfessionalEducationSerializer(serializers.ModelSerializer):
    """Сериализатор дополнительного профобразования."""

    users_prof_educations = serializers.SerializerMethodField()

    class Meta:
        model = ProfessionalEduction
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
            users_data = ProfessionalEduction.objects.filter(
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
        model = ForeignUserDocuments
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
            ForeignUserDocuments,
            DOCUMENTS_RAW_EXISTS
        )


class UserPrivacySettingsSerializer(serializers.ModelSerializer):
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
        model = UsersParent
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
        )
        read_only_fields = ('membership_fee', 'is_verified')

    def get_professional_education(self, obj):
        return UserProfessionalEducationSerializer(
            ProfessionalEduction.objects.filter(user=obj),
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

    class Meta:
        model = DistrictHeadquarter
        fields = BaseUnitSerializer.Meta.fields + (
            'central_headquarter',
            'founding_date',
            'members',
        )


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

    class Meta:
        model = LocalHeadquarter
        fields = BaseUnitSerializer.Meta.fields + (
            'regional_headquarter',
            'members',
            'founding_date',
        )


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

    class Meta:
        model = EducationalHeadquarter
        fields = BaseUnitSerializer.Meta.fields + (
            'educational_institution',
            'local_headquarter',
            'regional_headquarter',
            'members',
            'founding_date',
        )

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
