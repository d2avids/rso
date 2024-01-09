from django.shortcuts import get_object_or_404
from rest_framework import serializers
from events.models import Event, EventParticipants, MultiEventApplication

from headquarters.models import (
    CentralHeadquarter, DistrictHeadquarter, RegionalHeadquarter,
    LocalHeadquarter, EducationalHeadquarter, Detachment
)
from users.models import RSOUser


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
        max_value=100,
        label='Количество участников'
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
        return obj.members.count()


class ShortDetachmentSerializer(ShortUnitSerializer):
    class Meta:
        model = Detachment
        fields = ShortUnitSerializer.Meta.fields


class ShortEducationalHeadquarterSerializer(ShortUnitSerializer):
    detachments = ShortDetachmentSerializer(many=True)

    class Meta:
        model = EducationalHeadquarter
        fields = ShortUnitSerializer.Meta.fields + (
            'detachments',
        )


class ShortLocalHeadquarterSerializer(ShortUnitSerializer):
    educational_headquarters = ShortEducationalHeadquarterSerializer(many=True)
    detachments = ShortDetachmentSerializer(many=True)

    class Meta:
        model = LocalHeadquarter
        fields = ShortUnitSerializer.Meta.fields + (
            'educational_headquarters',
            'detachments',
        )


class ShortRegionalHeadquarterSerializer(ShortUnitSerializer):
    local_headquarters = ShortLocalHeadquarterSerializer(many=True)
    detachments = ShortDetachmentSerializer(many=True)

    class Meta:
        model = RegionalHeadquarter
        fields = ShortUnitSerializer.Meta.fields + (
            'local_headquarters',
            'detachments',
        )


class ShortDistrictHeadquarterSerializer(ShortUnitSerializer):
    regionals_headquarters = ShortRegionalHeadquarterSerializer(many=True)

    class Meta:
        model = DistrictHeadquarter
        fields = ShortUnitSerializer.Meta.fields + (
            'regionals_headquarters',
        )


class ShortCentralHeadquarterSerializer(ShortUnitSerializer):
    districts_headquarters = ShortDistrictHeadquarterSerializer(many=True)

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
