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
