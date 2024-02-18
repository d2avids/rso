from rest_framework import serializers

from events.models import Event
from headquarters.models import (Detachment, DistrictHeadquarter,
                                 EducationalHeadquarter, LocalHeadquarter,
                                 RegionalHeadquarter)
from headquarters.serializers import BaseShortUnitListSerializer


class BaseRegistrySerializer(BaseShortUnitListSerializer):
    """
    Базовый класс для сериализаторов, используемых в эндпоинтах
    штабов при указании query-параметра registry как true.
    """

    events_count = serializers.SerializerMethodField()

    class Meta:
        model = None
        fields = BaseShortUnitListSerializer.Meta.fields + ('event_count',)


class DistrictHeadquarterRegistrySerializer(BaseRegistrySerializer):
    regional_headquarters_count = serializers.SerializerMethodField()
    local_headquarters_count = serializers.SerializerMethodField()
    educational_headquarters_count = serializers.SerializerMethodField()
    detachments_count = serializers.SerializerMethodField()

    class Meta:
        model = DistrictHeadquarter
        fields = BaseRegistrySerializer.Meta.fields + (
            'regional_headquarters_count',
            'local_headquarters_count',
            'educational_headquarters_count',
            'detachments_count',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cached_units = None

    def _get_units(self, obj):
        """
        Сохраняем юниты в кэш и отдаем их. Если есть в кэше, берем оттуда.
        """
        if self._cached_units is None:
            self._cached_units = obj.get_related_units()
        return self._cached_units

    def get_regional_headquarters_count(self, obj):
        return self._get_units(obj)['regional_headquarters'].count()

    def get_educational_headquarters_count(self, obj):
        return self._get_units(obj)['educational_headquarters'].count()

    def get_local_headquarters_count(self, obj):
        return self._get_units(obj)['local_headquarters'].count()

    def get_detachments_count(self, obj):
        return self._get_units(obj)['detachments'].count()

    def to_representation(self, obj):
        """Для очищения кэша перед началом сериализации."""
        self._cached_units = None
        return super().to_representation(obj)

    @staticmethod
    def get_event_count(instance):
        return Event.objects.filter(org_district_headquarter=instance).count()


class RegionalHeadquarterRegistrySerializer(BaseRegistrySerializer):
    local_headquarters_count = serializers.SerializerMethodField()
    educational_headquarters_count = serializers.SerializerMethodField()
    detachments_count = serializers.SerializerMethodField()

    class Meta:
        model = RegionalHeadquarter
        fields = BaseRegistrySerializer.Meta.fields + (
            'local_headquarters_count',
            'educational_headquarters_count',
            'detachments_count',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cached_units = None

    def _get_units(self, obj):
        """
        Сохраняем юниты в кэш и отдаем их. Если есть в кэше, берем оттуда.
        """
        if self._cached_units is None:
            self._cached_units = obj.get_related_units()
        return self._cached_units

    def get_educational_headquarters_count(self, obj):
        return self._get_units(obj)['educational_headquarters'].count()

    def get_local_headquarters_count(self, obj):
        return self._get_units(obj)['local_headquarters'].count()

    def get_detachments_count(self, obj):
        return self._get_units(obj)['detachments'].count()

    def to_representation(self, obj):
        """Для очищения кэша перед началом сериализации."""
        self._cached_units = None
        return super().to_representation(obj)

    @staticmethod
    def get_event_count(instance):
        return Event.objects.filter(org_regional_headquarter=instance).count()


class LocalHeadquarterRegistrySerializer(BaseRegistrySerializer):
    educational_headquarters_count = serializers.SerializerMethodField()
    detachments_count = serializers.SerializerMethodField()

    class Meta:
        model = LocalHeadquarter
        fields = BaseRegistrySerializer.Meta.fields + (
            'educational_headquarters_count',
            'detachments_count',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._cached_units = None

    @staticmethod
    def get_event_count(instance):
        return Event.objects.filter(org_local_headquarter=instance).count()

    def _get_units(self, obj):
        """
        Сохраняем юниты в кэш и отдаем их. Если есть в кэше, берем оттуда.
        """
        if self._cached_units is None:
            self._cached_units = obj.get_related_units()
        return self._cached_units

    def get_educational_headquarters_count(self, obj):
        return self._get_units(obj)['educational_headquarters'].count()

    def get_detachments_count(self, obj):
        return self._get_units(obj)['detachments'].count()

    def to_representation(self, obj):
        """Для очищения кэша перед началом сериализации."""
        self._cached_units = None
        return super().to_representation(obj)


class EducationalHeadquarterRegistrySerializer(BaseRegistrySerializer):
    detachments_count = serializers.SerializerMethodField()

    class Meta:
        model = EducationalHeadquarter
        fields = BaseRegistrySerializer.Meta.fields + ('detachments_count',)

    @staticmethod
    def _get_units(obj):
        """Получаем связанные юниты (отряды)."""
        return obj.get_related_units()

    def get_detachments_count(self, obj):
        return self._get_units(obj)['detachments'].count()

    @staticmethod
    def get_event_count(instance):
        return Event.objects.filter(
            org_educational_headquarter=instance
        ).count()


class DetachmentRegistrySerializer(BaseRegistrySerializer):
    class Meta:
        model = Detachment
        fields = BaseRegistrySerializer.Meta.fields

    @staticmethod
    def get_event_count(instance):
        return Event.objects.filter(
            org_detachment=instance
        ).count()
