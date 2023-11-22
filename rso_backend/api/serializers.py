from rest_framework import serializers
from users.models import RSOUser, UserEducation, UserDocuments, UserRegion, UserPrivacySettings, UserMedia, Region


class RSOUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = RSOUser
        fields = '__all__'


class UserEducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserEducation
        fields = '__all__'


class UserDocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDocuments
        fields = '__all__'


class UserRegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRegion
        fields = '__all__'


class UserPrivacySettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPrivacySettings
        fields = '__all__'


class UserMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserMedia
        fields = '__all__'


class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = '__all__'


class UserCreateSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = RSOUser
        fields = (
            'region',
            'last_name',
            'first_name',
            'patronymic',
            'date_of_birth',
            'phone_number',
            'email',
            'username',
            'password',
            'password_confirm',
        )

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Пароли не совпадают")
        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = RSOUser
        fields = (
            'last_name',
            'first_name',
            'patronymic',
            'position',
            'region',
            'social_vk',
            'social_tg',
            'phone_number',
            'email',
        )
