from djoser.serializers import UserCreateSerializer, UserSerializer
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


class CustomUserCreateSerializer(UserCreateSerializer):

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
        )


    def create(self, validated_data):
        user = RSOUser(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class CustomUserSerializer(UserSerializer):
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
