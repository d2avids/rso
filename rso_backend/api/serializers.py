from djoser.serializers import UserCreatePasswordRetypeSerializer
from rest_framework import serializers

from api.constants import (DOCUMENTS_RAW_EXISTS, EDUCATION_RAW_EXISTS,
                           MEDIA_RAW_EXISTS, PRIVACY_RAW_EXISTS,
                           REGION_RAW_EXISTS, STATEMENT_RAW_EXISTS)
from api.utils import create_first_or_exception
from users.models import (Region, RSOUser, UserDocuments, UserEducation,
                          UserMedia, UserPrivacySettings, UserRegion,
                          UserStatementDocuments)


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ('name', 'branch')


class UserEducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserEducation
        fields = (
            'study_institution',
            'study_faculty',
            'study_group',
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


class RSOUserSerializer(serializers.ModelSerializer):
    """
    Выводит личные данные пользователя, а также все данные из всех
    связанных моделей.
    """
    user_region = UserRegionSerializer(read_only=True)
    documents = UserDocumentsSerializer(read_only=True)
    statement = UserStatementDocumentsSerializer(read_only=True)
    education = UserEducationSerializer(read_only=True)
    region = serializers.PrimaryKeyRelatedField(
        queryset=Region.objects.all(),
        allow_null=True,
        required=False,
    )
    media = serializers.SerializerMethodField()
    privacy = serializers.SerializerMethodField()

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
            'last_name_lat',
            'first_name_lat',
            'patronymic_lat',
            'phone_number',
            'gender',
            'region',
            'unit_type',
            'address',
            'bio',
            'social_vk',
            'social_tg',
            'membership_fee',
            'user_region',
            'documents',
            'statement',
            'media',
            'education',
            'privacy',
        )

    @staticmethod
    def get_media(obj):
        media = obj.media.first()
        return UserMediaSerializer(media).data if media else None

    @staticmethod
    def get_privacy(obj):
        privacy_settings = obj.privacy.first()
        return UserPrivacySettingsSerializer(
            privacy_settings
        ).data if privacy_settings else None


class UserCreateSerializer(UserCreatePasswordRetypeSerializer):
    region = serializers.PrimaryKeyRelatedField(
        queryset=Region.objects.all(),
        allow_null=True,
        required=False,
    )

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
