from headquarters.models import Area, EducationalInstitution, Region
from rest_framework import serializers
from users.models import MemberCert
from users.short_serializers import ShortUserSerializer


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
