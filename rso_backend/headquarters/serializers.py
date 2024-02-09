import datetime as dt

from api.serializers import (AreaSerializer, EducationalInstitutionSerializer,
                             RegionSerializer)
from competitions.models import CompetitionParticipants
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.db.models.query import QuerySet
from headquarters.models import (Area, CentralHeadquarter, Detachment,
                                 DistrictHeadquarter, EducationalHeadquarter,
                                 EducationalInstitution, LocalHeadquarter,
                                 Position, Region, RegionalHeadquarter,
                                 UserCentralHeadquarterPosition,
                                 UserDetachmentApplication,
                                 UserDetachmentPosition,
                                 UserDistrictHeadquarterPosition,
                                 UserEducationalHeadquarterPosition,
                                 UserLocalHeadquarterPosition,
                                 UserRegionalHeadquarterPosition)
from rest_framework import serializers
from users.models import RSOUser
from users.short_serializers import ShortUserSerializer


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ('id', 'name',)


class BasePositionSerializer(serializers.ModelSerializer):
    """
    Базовый класс для вывода участников и их должностей
    при получении структурных единиц.
    """

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

    def to_representation(self, instance):
        serialized_data = super().to_representation(instance)
        position = instance.position
        if position:
            serialized_data['position'] = PositionSerializer(position).data
        return serialized_data


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


class BaseShortUnitSerializer(serializers.ModelSerializer):
    """
    Базовый сериализатор для хранения общих полей штабов для короткого вывода.
    Хранит только поля id, name и banner.
    """

    class Meta:
        model = None
        fields = (
            'id',
            'name',
            'banner',
        )


class ShortDistrictHeadquarterSerializer(BaseShortUnitSerializer):
    class Meta:
        model = DistrictHeadquarter
        fields = BaseShortUnitSerializer.Meta.fields


class ShortRegionalHeadquarterSerializer(BaseShortUnitSerializer):
    class Meta:
        model = RegionalHeadquarter
        fields = BaseShortUnitSerializer.Meta.fields


class ShortLocalHeadquarterSerializer(BaseShortUnitSerializer):
    class Meta:
        model = LocalHeadquarter
        fields = BaseShortUnitSerializer.Meta.fields


class ShortEducationalHeadquarterSerializer(BaseShortUnitSerializer):
    class Meta:
        model = EducationalHeadquarter
        fields = BaseShortUnitSerializer.Meta.fields


class ShortDetachmentSerializer(BaseShortUnitSerializer):
    class Meta:
        model = Detachment
        fields = BaseShortUnitSerializer.Meta.fields


class BaseShortUnitListSerializer(serializers.ModelSerializer):
    """
    Базовый сериализатор для хранения общих полей штабов для короткого вывода
    при получении СПИСКА тех или иных структурных единиц.
    Хранит только поля id, name и banner.
    """

    members_count = serializers.SerializerMethodField(read_only=True)
    participants_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = None
        fields = (
            'id',
            'name',
            'emblem',
            'founding_date',
            'members_count',
            'participants_count',
        )

    @staticmethod
    def get_members_count(instance):
        if isinstance(instance, QuerySet):
            instance_type = type(instance.first())
        else:
            instance_type = type(instance)
        if issubclass(instance_type, CentralHeadquarter):
            return RSOUser.objects.filter(membership_fee=True).count()
        return instance.members.filter(user__membership_fee=True).count() + 1

    @staticmethod
    def get_participants_count(instance):
        if isinstance(instance, QuerySet):
            instance_type = type(instance.first())
        else:
            instance_type = type(instance)
        if issubclass(instance_type, CentralHeadquarter):
            return RSOUser.objects.count()
        return instance.members.count() + 1


class ShortDistrictHeadquarterListSerializer(BaseShortUnitListSerializer):
    class Meta:
        model = DistrictHeadquarter
        fields = BaseShortUnitListSerializer.Meta.fields


class ShortRegionalHeadquarterListSerializer(BaseShortUnitListSerializer):
    district_headquarter = serializers.PrimaryKeyRelatedField(
        queryset=DistrictHeadquarter.objects.all(),
    )

    class Meta:
        model = RegionalHeadquarter
        fields = BaseShortUnitListSerializer.Meta.fields + (
            'district_headquarter',
        )

    def to_representation(self, instance):
        serialized_data = super().to_representation(instance)
        region = instance.region
        if region:
            serialized_data['region'] = RegionSerializer(region).data
        return serialized_data



class ShortLocalHeadquarterListSerializer(BaseShortUnitListSerializer):
    regional_headquarter = serializers.PrimaryKeyRelatedField(
        queryset=RegionalHeadquarter.objects.all(),
    )

    class Meta:
        model = LocalHeadquarter
        fields = BaseShortUnitListSerializer.Meta.fields + (
            'regional_headquarter',
        )


class ShortEducationalHeadquarterListSerializer(BaseShortUnitListSerializer):
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

    class Meta:
        model = EducationalHeadquarter
        fields = BaseShortUnitListSerializer.Meta.fields + (
            'educational_institution',
            'local_headquarter',
            'regional_headquarter',
        )

    def to_representation(self, instance):
        serialized_data = super().to_representation(instance)
        educational_institution = instance.educational_institution
        serialized_data['educational_institution'] = (
            EducationalInstitutionSerializer(educational_institution).data
        )
        return serialized_data


class ShortDetachmentListSerializer(BaseShortUnitListSerializer):
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

    class Meta:
        model = Detachment
        fields = BaseShortUnitListSerializer.Meta.fields + (
            'educational_headquarter',
            'local_headquarter',
            'regional_headquarter',
            'region',
            'educational_institution',
            'area',
        )

    def to_representation(self, instance):
        serialized_data = super().to_representation(instance)
        educational_institution = instance.educational_institution
        area = instance.area
        region = instance.region
        serialized_data['educational_institution'] = (
            EducationalInstitutionSerializer(educational_institution).data
        )
        serialized_data['area'] = AreaSerializer(area).data
        serialized_data['region'] = RegionSerializer(region).data
        return serialized_data


class BaseUnitSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для хранения общей логики штабов.

    Предназначен для использования как родительский класс для всех
    сериализаторов штабов, обеспечивая наследование общих полей и методов.
    """

    _POSITIONS_MAPPING = {
        CentralHeadquarter: (
            UserCentralHeadquarterPosition, CentralPositionSerializer
        ),
        DistrictHeadquarter: (
            UserDistrictHeadquarterPosition, DistrictPositionSerializer
        ),
        RegionalHeadquarter: (
            UserRegionalHeadquarterPosition, RegionalPositionSerializer
        ),
        LocalHeadquarter: (
            UserLocalHeadquarterPosition, LocalPositionSerializer
        ),
        EducationalHeadquarter: (
            UserEducationalHeadquarterPosition, EducationalPositionSerializer
        ),
        Detachment: (UserDetachmentPosition, DetachmentPositionSerializer),
    }

    commander = serializers.PrimaryKeyRelatedField(
        queryset=RSOUser.objects.all(),
    )
    members_count = serializers.SerializerMethodField(read_only=True)
    participants_count = serializers.SerializerMethodField(read_only=True)
    leadership = serializers.SerializerMethodField(read_only=True)
    events_count = serializers.SerializerMethodField(read_only=True)

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
            'events_count',
            'leadership',
        )

    def to_representation(self, instance):
        """Переопределяем представление данных для полей commader."""
        serialized_data = super().to_representation(instance)
        commander = instance.commander
        if commander:
            serialized_data['commander'] = ShortUserSerializer(commander).data
        return serialized_data

    def _get_position_instance(self):
        if isinstance(self.instance, QuerySet):
            instance_type = type(self.instance.first())
        else:
            instance_type = type(self.instance)

        for model_class, (
                position_model, _
        ) in self._POSITIONS_MAPPING.items():
            if issubclass(instance_type, model_class):
                return position_model

    def _get_position_serializer(self):
        if isinstance(self.instance, QuerySet):
            instance_type = type(self.instance.first())
        else:
            instance_type = type(self.instance)

        for model_class, (
                _, serializer_class
        ) in self._POSITIONS_MAPPING.items():
            if issubclass(instance_type, model_class):
                return serializer_class

    def get_leadership(self, instance):
        """
        Вывод руководство отряда - всех, кроме указанных в настройках
        должностей.
        """
        serializer = self._get_position_serializer()
        position_instance = self._get_position_instance()
        leaders = position_instance.objects.exclude(
            Q(position__name__in=settings.NOT_LEADERSHIP_POSITIONS) |
            Q(position__isnull=True)
        )

        return serializer(leaders, many=True).data

    def get_events_count(self, instance):
        mapping_units = {
            'Detachment': 'Отрядное',
            'EducationalHeadquarter':
            ['Отрядное', 'Образовательное'],
            'LocalHeadquarter':
            ['Отрядное', 'Образовательное', 'Городское'],
            'RegionalHeadquarter':
            ['Отрядное', 'Образовательное', 'Городское', 'Региональное'],
            'DistrictHeadquarter':
            ['Отрядное', 'Образовательное', 'Городское', 'Региональное',
             'Окружное'],
            'CentralHeadquarter':
            ['Отрядное', 'Образовательное', 'Городское', 'Региональное',
             'Окружное', 'Всероссийское']
        }
        commander = instance.commander
        instance_unit_class_name = mapping_units.get(self.Meta.model.__name__)
        return commander.event_set.filter(
            scale__in=instance_unit_class_name
        ).count()

    @staticmethod
    def get_members_count(instance):
        if isinstance(instance, QuerySet):
            instance_type = type(instance.first())
        else:
            instance_type = type(instance)
        if issubclass(instance_type, CentralHeadquarter):
            return RSOUser.objects.filter(membership_fee=True).count()
        return instance.members.filter(user__membership_fee=True).count() + 1

    @staticmethod
    def get_participants_count(instance):
        if isinstance(instance, QuerySet):
            instance_type = type(instance.first())
        else:
            instance_type = type(instance)
        if issubclass(instance_type, CentralHeadquarter):
            return RSOUser.objects.count()
        return instance.members.count() + 1

    def validate(self, attrs):
        """
        Запрещает назначить пользователя командиром, если он уже им является.
        """
        commander_id = attrs.get('commander')
        print('валидириуем')
        print('командир айди:', commander_id)
        print(self.instance)
        if commander_id:
            instance_type = self.Meta.model
            print(f'INSTANCE TYPE: {instance_type}')
            for model_class in self._POSITIONS_MAPPING:
                if not issubclass(instance_type, model_class):
                    continue
                print(f'MODEL CLASS: {model_class}')
                existing_units = model_class.objects.exclude(
                    id=getattr(self.instance, 'id', None))

                if existing_units.filter(commander=commander_id).exists():
                    raise serializers.ValidationError(
                        f"Пользователь уже является командиром другого "
                        f"{model_class.__name__}."
                    )

        return attrs


class CentralHeadquarterSerializer(BaseUnitSerializer):
    """Сериализатор для центрального штаба.

    Наследует общую логику и поля от BaseUnitSerializer и связывает
    с моделью CentralHeadquarter.
    """
    working_years = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CentralHeadquarter
        fields = BaseUnitSerializer.Meta.fields + (
            'working_years',
            'detachments_appearance_year',
            'rso_founding_congress_date',
        )

    @staticmethod
    def get_working_years(instance):
        return (
            dt.datetime.now().year - settings.CENTRAL_HEADQUARTER_FOUNDING_DATE
        )


class DistrictHeadquarterSerializer(BaseUnitSerializer):
    """Сериализатор для окружного штаба.

    Дополнительно к полям из BaseUnitSerializer, добавляет поле
    central_headquarter для связи с центральным штабом.
    """

    central_headquarter = serializers.PrimaryKeyRelatedField(
        queryset=CentralHeadquarter.objects.all(),
        required=False
    )
    commander = serializers.PrimaryKeyRelatedField(
        queryset=RSOUser.objects.all(),
    )
    members = DistrictPositionSerializer(
        many=True,
        read_only=True
    )
    regional_headquarters = serializers.SerializerMethodField()
    local_headquarters = serializers.SerializerMethodField()
    educational_headquarters = serializers.SerializerMethodField()
    detachments = serializers.SerializerMethodField()

    class Meta:
        model = DistrictHeadquarter
        fields = BaseUnitSerializer.Meta.fields + (
            'central_headquarter',
            'founding_date',
            'members',
            'regional_headquarters',
            'local_headquarters',
            'educational_headquarters',
            'detachments',
        )
        read_only_fields = ('regional_headquarters',)

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

    def get_regional_headquarters(self, obj):
        hqs = RegionalHeadquarter.objects.filter(district_headquarter=obj)
        return ShortRegionalHeadquarterSerializer(hqs, many=True).data

    def get_educational_headquarters(self, obj):
        units = self._get_units(obj)
        educational_headquarters_serializer = (
            ShortEducationalHeadquarterSerializer(
                units['educational_headquarters'], many=True
            )
        ).data
        return educational_headquarters_serializer

    def get_local_headquarters(self, obj):
        units = self._get_units(obj)
        local_headquarters_serializer = ShortLocalHeadquarterSerializer(
            units['local_headquarters'], many=True
        ).data
        return local_headquarters_serializer

    def get_detachments(self, obj):
        units = self._get_units(obj)
        detachment_serializer = ShortDetachmentSerializer(
            units['detachments'], many=True
        ).data
        return detachment_serializer

    def to_representation(self, obj):
        """Для очищения кэша перед началом сериализации."""
        self._cached_units = None
        return super().to_representation(obj)


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
    detachments = serializers.SerializerMethodField(read_only=True)
    local_headquarters = serializers.SerializerMethodField(read_only=True)
    educational_headquarters = serializers.SerializerMethodField(
        read_only=True
    )

    class Meta:
        model = RegionalHeadquarter
        fields = BaseUnitSerializer.Meta.fields + (
            'region',
            'district_headquarter',
            'name_for_certificates',
            'conference_date',
            'registry_date',
            'registry_number',
            'case_name',
            'legal_address',
            'requisites',
            'founding_date',
            'detachments',
            'local_headquarters',
            'educational_headquarters',
        )
        read_only_fields = (
            'detachments',
            'local_headquarters',
            'educational_headquarters',
        )

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

    def get_detachments(self, obj):
        hqs = Detachment.objects.filter(regional_headquarter=obj)
        return ShortDetachmentSerializer(hqs, many=True).data

    def get_local_headquarters(self, obj):
        hqs = LocalHeadquarter.objects.filter(regional_headquarter=obj)
        return ShortLocalHeadquarterSerializer(hqs, many=True).data

    def get_educational_headquarters(self, obj):
        hqs = EducationalHeadquarter.objects.filter(regional_headquarter=obj)
        return ShortEducationalHeadquarterSerializer(hqs, many=True).data


class LocalHeadquarterSerializer(BaseUnitSerializer):
    """Сериализатор для местного штаба.

    Расширяет BaseUnitSerializer, добавляя поле regional_headquarter
    для связи с региональным штабом.
    """

    regional_headquarter = serializers.PrimaryKeyRelatedField(
        queryset=RegionalHeadquarter.objects.all(),
    )
    educational_headquarters = serializers.SerializerMethodField(
        read_only=True
    )
    detachments = serializers.SerializerMethodField(
        read_only=True
    )

    class Meta:
        model = LocalHeadquarter
        fields = BaseUnitSerializer.Meta.fields + (
            'regional_headquarter',
            'founding_date',
            'educational_headquarters',
            'detachments',
        )
        read_only_fields = ('educational_headquarters', 'detachments')

    def get_educational_headquarters(self, obj):
        hqs = EducationalHeadquarter.objects.filter(local_headquarter=obj)
        return ShortEducationalHeadquarterSerializer(hqs, many=True).data

    def get_detachments(self, obj):
        hqs = Detachment.objects.filter(local_headquarter=obj)
        return ShortDetachmentSerializer(hqs, many=True).data


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
    detachments = serializers.SerializerMethodField(
        read_only=True
    )

    class Meta:
        model = EducationalHeadquarter
        fields = BaseUnitSerializer.Meta.fields + (
            'educational_institution',
            'local_headquarter',
            'regional_headquarter',
            'founding_date',
            'detachments'
        )
        read_only_fields = ('detachments',)

    def validate(self, data):
        """
        Вызывает валидацию модели для проверки согласованности между местным
         и региональным штабами.
        """
        instance = EducationalHeadquarter(**data)
        try:
            instance.check_headquarters_relations()
            super().validate(data)
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)
        return data

    def to_representation(self, instance):
        """
        Вызывает родительский метод to_representation,
        а также изменяет вывод educational_institution.
        """
        serialized_data = super().to_representation(instance)
        educational_institution = instance.educational_institution
        serialized_data['educational_institution'] = (
            EducationalInstitutionSerializer(educational_institution).data
        )
        return serialized_data

    def get_detachments(self, obj):
        hqs = Detachment.objects.filter(educational_headquarter=obj)
        return ShortDetachmentSerializer(hqs, many=True).data


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


class UserDetachmentApplicationReadSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения заявок в отряд"""

    user = ShortUserSerializer(read_only=True)

    class Meta:
        model = UserDetachmentApplication
        fields = ('id', 'user')
        read_only_fields = ('user',)


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
    nomination = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    tandem_partner = serializers.SerializerMethodField()

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
            'founding_date',
            'nomination',
            'status',
            'tandem_partner',
        )

    def to_representation(self, instance):
        """
        Вызывает родительский метод to_representation,
        а также изменяет вывод educational_institution.
        """
        serialized_data = super().to_representation(instance)
        educational_institution = instance.educational_institution
        area = instance.area
        region = instance.region
        serialized_data['educational_institution'] = (
            EducationalInstitutionSerializer(educational_institution).data
        )
        serialized_data['area'] = AreaSerializer(area).data
        serialized_data['region'] = RegionSerializer(region).data
        return serialized_data

    def validate(self, data):
        """
        Вызывает валидацию модели для проверки согласованности между
        образовательным, местным и региональным штабами.
        """
        instance = Detachment(**data)
        try:
            instance.check_headquarters_relations()
            super().validate(data)
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)
        return data

    def get_leadership(self, instance):
        """
        Вывод руководства отряда (пользователи с должностями "Мастер
        (методист)" и "Комиссар", точные названия которых прописаны
        в настройках).
        """
        serializer = self._get_position_serializer()
        position_instance = self._get_position_instance()
        leaders = position_instance.objects.filter(
            Q(position__name=settings.MASTER_METHODIST_POSITION_NAME) |
            Q(position__name=settings.COMMISSIONER_POSITION_NAME)
        )
        return serializer(leaders, many=True).data

    def get_status(self, obj):
        if not CompetitionParticipants.objects.filter(
            Q(detachment=obj) & Q(junior_detachment__isnull=False) |
            Q(detachment__isnull=False) & Q(junior_detachment=obj)
        ).exists():
            return None
        if CompetitionParticipants.objects.filter(
            Q(detachment=obj) & Q(junior_detachment__isnull=False)
        ).exists():
            return 'Наставник'
        return 'Старт'

    def get_nomination(self, obj):
        if not CompetitionParticipants.objects.filter(
            Q(detachment=obj) & Q(junior_detachment__isnull=False) |
            Q(detachment__isnull=False) & Q(junior_detachment=obj) |
            Q(junior_detachment=obj)
        ).exists():
            return None
        if CompetitionParticipants.objects.filter(
            Q(detachment=obj) & Q(junior_detachment__isnull=False) |
            Q(detachment__isnull=False) & Q(junior_detachment=obj)
        ).exists():
            return 'Тандем'
        return 'Дебют'

    def get_tandem_partner(self, obj):
        participants = CompetitionParticipants.objects.filter(
            Q(detachment=obj) | Q(junior_detachment=obj)
        ).first()
        if participants:
            if participants.detachment == obj:
                return ShortDetachmentSerializer(
                    participants.junior_detachment
                ).data
            if participants.detachment:
                return ShortDetachmentSerializer(
                    participants.detachment
                ).data
