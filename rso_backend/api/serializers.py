from django.db import IntegrityError
from rest_framework import serializers

from users.models import (Region, RSOUser, UserDocuments, UserEducation,
                          UserMedia, UserPrivacySettings, UserRegion,
                          UserStatementDocuments)


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = '__all__'


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
        try:
            return UserEducation.objects.create(**validated_data)
        except IntegrityError:
            raise serializers.ValidationError(
                {'detail': 'Образовательная информация для '
                           'данного пользователя уже существует'}
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
        try:
            return UserDocuments.objects.create(**validated_data)
        except IntegrityError:
            raise serializers.ValidationError(
                {'detail': 'Документы для данного пользователя уже существуют'}
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
        try:
            return UserPrivacySettings.objects.create(**validated_data)
        except IntegrityError:
            raise serializers.ValidationError(
                {
                    'detail': 'Настройки приватности для данного '
                              'пользователя уже существуют'}
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
        try:
            return UserMedia.objects.create(**validated_data)
        except IntegrityError:
            raise serializers.ValidationError(
                {
                    'detail': 'Медиа-данные для данного '
                              'пользователя уже существуют'}
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
        try:
            return UserStatementDocuments.objects.create(**validated_data)
        except IntegrityError:
            raise serializers.ValidationError(
                {
                    'detail': 'Документы пользователя для вступления в РСО '
                              'уже существуют для данного пользователя'}
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
        try:
            return UserRegion.objects.create(**validated_data)
        except IntegrityError:
            raise serializers.ValidationError(
                {'detail': 'Данные региона для данного пользователя '
                           'уже существуют'}
            )


class RSOUserSerializer(serializers.ModelSerializer):
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
