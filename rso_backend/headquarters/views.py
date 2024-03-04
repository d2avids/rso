from dal import autocomplete
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.cache import cache
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from api.mixins import (CreateDeleteViewSet, ListRetrieveUpdateViewSet,
                        ListRetrieveViewSet)
from api.permissions import (IsDetachmentCommander, IsDistrictCommander,
                             IsEducationalCommander, IsLocalCommander,
                             IsRegionalCommander, IsStuffOrCentralCommander,
                             IsStuffOrCentralCommanderOrTrusted,
                             IsUserModelPositionCommander)
from api.utils import get_headquarter_users_positions_queryset
from headquarters.filters import (DetachmentFilter,
                                  EducationalHeadquarterFilter,
                                  LocalHeadquarterFilter,
                                  RegionalHeadquarterFilter)
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
                                 UserRegionalHeadquarterPosition)
from headquarters.serializers import (
    CentralHeadquarterSerializer, CentralPositionSerializer,
    DetachmentPositionSerializer, DetachmentSerializer,
    DistrictHeadquarterSerializer, DistrictPositionSerializer,
    EducationalHeadquarterSerializer, EducationalPositionSerializer,
    LocalHeadquarterSerializer, LocalPositionSerializer, PositionSerializer,
    RegionalHeadquarterSerializer, RegionalPositionSerializer,
    ShortDetachmentListSerializer, ShortDetachmentSerializer,
    ShortDistrictHeadquarterListSerializer, ShortDistrictHeadquarterSerializer,
    ShortEducationalHeadquarterListSerializer,
    ShortEducationalHeadquarterSerializer, ShortLocalHeadquarterListSerializer,
    ShortLocalHeadquarterSerializer, ShortRegionalHeadquarterListSerializer,
    ShortRegionalHeadquarterSerializer,
    UserDetachmentApplicationReadSerializer,
    UserDetachmentApplicationSerializer)
from headquarters.registry_serializers import (
    DistrictHeadquarterRegistrySerializer,
    RegionalHeadquarterRegistrySerializer, LocalHeadquarterRegistrySerializer,
    EducationalHeadquarterRegistrySerializer, DetachmentRegistrySerializer)
from headquarters.swagger_schemas import applications_response
from headquarters.utils import (get_detachment_members_to_verify,
                                get_regional_hq_members_to_verify)
from users.serializers import UserVerificationReadSerializer


class PositionViewSet(ListRetrieveViewSet):
    """Представляет должности для юзеров.

    Доступны только операции чтения.
    """

    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    ordering = ('name',)


class CentralViewSet(ListRetrieveUpdateViewSet):
    """Представляет центральные штабы.

    При операции чтения доступно число количества участников в структурной
    единице по ключу members_count, а также список всех участников по ключу
    members.
    Доступен поиск по name при передаче ?search=<value> query-параметра.
    """

    queryset = CentralHeadquarter.objects.all()
    serializer_class = CentralHeadquarterSerializer
    permission_classes = (IsStuffOrCentralCommander,)
    ordering = ('name',)

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = (permissions.IsAdminUser,)
        else:
            permission_classes = (IsStuffOrCentralCommanderOrTrusted,)
        return [permission() for permission in permission_classes]

    def get_object(self):
        obj_id = self.kwargs['pk']
        obj_cache_key = f'central-headquarter-{obj_id}'
        return cache.get_or_set(
            obj_cache_key,
            lambda: get_object_or_404(
                CentralHeadquarter, pk=obj_id
            ),
            timeout=settings.CENTRAL_OBJECT_CACHE_TTL
        )


class DistrictViewSet(viewsets.ModelViewSet):
    """Представляет окружные штабы.

    Привязывается к центральному штабу по ключу central_headquarter.
    При операции чтения доступно число количества участников в структурной
    единице по ключу members_count, а также список всех участников по ключу
    members.
    Доступен поиск по name при передаче ?search=<value> query-параметра.
    Сортировка по умолчанию - количество участников
    При указании registry=True в качестве query_param, выводит список объектов,
    адаптированный под блок "Реестр участников".
    """

    queryset = DistrictHeadquarter.objects.all()
    serializer_class = DistrictHeadquarterSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    ordering = ('name',)

    def get_serializer_class(self):
        if (
                self.request.query_params.get('registry') == 'true' and
                self.action == 'list'
        ):
            return DistrictHeadquarterRegistrySerializer
        if self.action == 'list':
            return ShortDistrictHeadquarterListSerializer
        return DistrictHeadquarterSerializer

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = (IsStuffOrCentralCommanderOrTrusted,)
        else:
            permission_classes = (IsDistrictCommander,)
        return [permission() for permission in permission_classes]

    def get_object(self):
        obj_id = self.kwargs['pk']
        obj_cache_key = f'district-headquarter-{obj_id}'

        return cache.get_or_set(
            obj_cache_key,
            lambda: get_object_or_404(
                DistrictHeadquarter, pk=obj_id
            ),
            timeout=settings.DISTR_OBJECT_CACHE_TTL
        )


class RegionalViewSet(viewsets.ModelViewSet):
    """Представляет региональные штабы.

    Привязывается к окружному штабу по ключу district_headquarter (id).
    Привязывается к региону по ключу region (id).
    При операции чтения доступно число количества участников в структурной
    единице по ключу members_count, а также список всех участников по ключу
    members.
    При операции чтения доступен список пользователей, подавших заявку на
    верификацию и относящихся к тому же региону, что и текущий региональный
    штаб, по ключу users_for_verification.
    Доступен поиск по name при передаче ?search=<value> query-параметра.
    Доступна сортировка по ключам name, founding_date, count_related.
    Сортировка по умолчанию - количество участников.
    Доступна фильтрация по Окружным Штабам. Ключ - district_headquarter__name.
    Доступна фильтрация по имени региона. Ключ - region.
    При указании registry=True в качестве query_param, выводит список объектов,
    адаптированный под блок "Реестр участников".
    """

    queryset = RegionalHeadquarter.objects.all()
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    search_fields = ('name', 'region__name',)
    ordering_fields = ('name', 'founding_date',)
    filterset_class = RegionalHeadquarterFilter

    def get_serializer_class(self):
        if (
                self.request.query_params.get('registry') == 'true' and
                self.action == 'list'
        ):
            return RegionalHeadquarterRegistrySerializer
        if self.action == 'list':
            return ShortRegionalHeadquarterListSerializer
        return RegionalHeadquarterSerializer

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = (IsDistrictCommander,)
        else:
            permission_classes = (IsRegionalCommander,)
        return [permission() for permission in permission_classes]

    def get_object(self):
        obj_id = self.kwargs['pk']
        obj_cache_key = f'regional-headquarter-{obj_id}'

        return cache.get_or_set(
            obj_cache_key,
            lambda: get_object_or_404(
                RegionalHeadquarter, pk=obj_id
            ),
            timeout=settings.REG_OBJECT_CACHE_TTL
        )

    @action(detail=True, methods=['get', ], url_path='verifications')
    def get_verifications(self, request, pk=None):
        """
        Получить список пользователей, подавших заявку на верификацию,
        у которых совпадает регион с регионом текущего РШ.
        """
        headquarter = self.get_object()
        members_to_verify = get_regional_hq_members_to_verify(headquarter)
        serializer = UserVerificationReadSerializer(
            instance=members_to_verify, many=True
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class LocalViewSet(viewsets.ModelViewSet):
    """Представляет местные штабы.

    Привязывается к региональному штабу по ключу regional_headquarter (id).
    При операции чтения доступно число количества участников в структурной
    единице по ключу members_count, а также список всех участников по ключу
    members.
    Доступен поиск по name при передаче ?search=<value> query-параметра.
    Доступна сортировка по ключам name, founding_date, count_related.
    Доступна фильтрация по РШ и ОШ. Ключи - regional_headquarter__name,
    district_headquarter__name.
    При указании registry=True в качестве query_param, выводит список объектов,
    адаптированный под блок "Реестр участников".
    """

    queryset = LocalHeadquarter.objects.all()
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    search_fields = ('name',)
    ordering_fields = ('name', 'founding_date',)
    filterset_class = LocalHeadquarterFilter

    def get_serializer_class(self):
        if (
                self.request.query_params.get('registry') == 'true' and
                self.action == 'list'
        ):
            return LocalHeadquarterRegistrySerializer
        if self.action == 'list':
            return ShortLocalHeadquarterListSerializer
        return LocalHeadquarterSerializer

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = (IsRegionalCommander,)
        else:
            permission_classes = (IsLocalCommander,)
        return [permission() for permission in permission_classes]


class EducationalViewSet(viewsets.ModelViewSet):
    """Представляет образовательные штабы.

    Может привязываться к местному штабу по ключу local_headquarter (id).
    Привязывается к региональному штабу по ключу regional_headquarter (id).
    Привязывается к образовательному институту по ключу educational_institution
    (id).
    Установлена валидация соответствия всех связанных штабов на наличие
    связи между собой.
    При операции чтения доступно число количества участников в структурной
    единице по ключу members_count, а также список всех участников по ключу
    members.
    Доступен поиск по name при передаче ?search=<value> query-параметра.
    Доступна сортировка по ключам name, founding_date, count_related.
    Доступна фильтрация по РШ, ОШ и ОИ. Ключи - regional_headquarter__name,
    district_headquarter__name, local_headquarter__name.
    При указании registry=True в качестве query_param, выводит список объектов,
    адаптированный под блок "Реестр участников".
    """

    queryset = EducationalHeadquarter.objects.all()
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    search_fields = ('name',)
    filterset_class = EducationalHeadquarterFilter
    ordering_fields = ('name', 'founding_date',)

    def get_serializer_class(self):
        if (
                self.request.query_params.get('registry') == 'true' and
                self.action == 'list'
        ):
            return EducationalHeadquarterRegistrySerializer
        if self.action == 'list':
            return ShortEducationalHeadquarterListSerializer
        return EducationalHeadquarterSerializer

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = (IsLocalCommander,)
        else:
            permission_classes = (IsEducationalCommander,)
        return [permission() for permission in permission_classes]


class DetachmentViewSet(viewsets.ModelViewSet):
    """Представляет информацию об отряде.

    Может привязываться к местному штабу по ключу local_headquarter (id).
    Может привязываться к образовательному штабу по ключу
    educational_headquarter (id).
    Привязывается к региональному штабу по ключу regional_headquarter (id).
    Привязывается к направлению по ключу area (id).
    Установлена валидация соответствия всех связанных штабов на наличие
    связи между собой.
    При операции чтения доступно число количества участников в структурной
    единице по ключу members_count, а также список всех участников по эндпоинту
    /members/.
    При операции чтения доступен список пользователей, подавших заявку на
    верификацию и относящихся к текущему отряду по
    эндпоинту /verifications/.
    При операции чтения доступен список пользователей, подавших заявку на
    вступление в отряд по эндпоинту /applications/.
    Доступен поиск по name при передаче ?search=<value> query-параметра.
    Доступна сортировка по ключам name, founding_date, count_related.
    Доступна фильтрация по ключам area__name, educational_institution__name.
    При указании registry=True в качестве query_param, выводит список объектов,
    адаптированный под блок "Реестр участников".
    """

    queryset = Detachment.objects.all()
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    search_fields = ('name',)
    filterset_class = DetachmentFilter
    ordering_fields = ('name', 'founding_date',)

    def get_serializer_class(self):
        if (
                self.request.query_params.get('registry') == 'true' and
                self.action == 'list'
        ):
            return DetachmentRegistrySerializer
        if self.action == 'list':
            return ShortDetachmentListSerializer
        return DetachmentSerializer

    def get_permissions(self):
        if self.action == 'create':
            #TODO: вернуть обратно после запрета юзерам создавать отряды
            # permission_classes = (IsEducationalCommander,)
            permission_classes = (permissions.IsAuthenticated,)
            return [permission() for permission in permission_classes]
        permission_classes = (IsDetachmentCommander, )
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['get', ], url_path='applications')
    @swagger_auto_schema(responses=applications_response)
    def get_applications(self, request, pk=None):
        """Получить список заявок на вступление в отряд."""
        detachment = self.get_object()
        applications = UserDetachmentApplication.objects.filter(
            detachment=detachment
        )
        serializer = UserDetachmentApplicationReadSerializer(
            instance=applications, many=True
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get', ], url_path='verifications')
    def get_verifications(self, request, pk=None):
        """Получить список членов отряда, подавших заявку на верификацию."""
        detachment = self.get_object()
        members_to_verify = get_detachment_members_to_verify(detachment)
        serializer = UserVerificationReadSerializer(
            instance=members_to_verify, many=True
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class BasePositionViewSet(viewsets.ModelViewSet):
    """Базовый вьюсет для просмотра/изменения участников штабов.

    Необходимо переопределять метод get_queryset и атрибут serializer_class.
    """

    serializer_class = None

    def filter_by_name(self, queryset):
        """Фильтрация участников структурной единицы по имени (first_name)."""
        search_by_name = self.request.query_params.get('search', None)
        if search_by_name:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search_by_name) |
                Q(user__last_name__icontains=search_by_name)
            )
        return queryset

    def get_queryset(self):
        pass

    def get_object(self):
        queryset = self.get_queryset()
        member_pk = self.kwargs.get('membership_pk')
        try:
            obj = queryset.get(pk=member_pk)
        # TODO: не лучшая практика, но пока не вижу более правильного решения
        # TODO: в действительности мы ловим DoesNotExist для дочерних классов
        # TODO: edit - можно добавить маппинг. Сделать позднее.
        except Exception:
            raise Http404('Не найден участник по заданному id членства.')
        return obj


class CentralPositionViewSet(BasePositionViewSet):
    """Просмотреть участников и изменить уровень доверенности/позиции.

    Доступно только командиру.

    Доступен поиск по username, first_name, last_name, patronymic_name
    """

    filter_backends = (filters.SearchFilter,)
    search_fields = (
        'user__username',
        'user__first_name',
        'user__last_name',
        'user__patronymic_name'
    )
    permission_classes = (IsStuffOrCentralCommander,)
    serializer_class = CentralPositionSerializer

    def get_queryset(self):
        queryset = get_headquarter_users_positions_queryset(
            self,
            CentralHeadquarter,
            UserCentralHeadquarterPosition
        )
        return cache.get_or_set(
            'central-members-list',
            queryset,
            timeout=settings.CENTRALHQ_MEMBERS_CACHE_TTL
        )


class DistrictPositionViewSet(BasePositionViewSet):
    """Просмотреть участников и изменить уровень доверенности/позиции.

    Доступно только командиру.

    Доступен поиск по username, first_name, last_name, patronymic_name
    """

    filter_backends = (filters.SearchFilter,)
    search_fields = (
        'user__username',
        'user__first_name',
        'user__last_name',
        'user__patronymic_name'
    )
    permission_classes = (IsUserModelPositionCommander,)
    serializer_class = DistrictPositionSerializer

    def get_queryset(self):
        queryset = get_headquarter_users_positions_queryset(
            self,
            DistrictHeadquarter,
            UserDistrictHeadquarterPosition
        )
        return cache.get_or_set(
            'district-members-list',
            queryset,
            timeout=settings.DISTRCICTHQ_MEMBERS_CACHE_TTL
        )


class RegionalPositionViewSet(BasePositionViewSet):
    """Просмотреть участников и изменить уровень доверенности/позиции.

    Доступно только командиру.

    Доступен поиск по username, first_name, last_name, patronymic_name
    """

    filter_backends = (filters.SearchFilter,)
    search_fields = (
        'user__username',
        'user__first_name',
        'user__last_name',
        'user__patronymic_name'
    )
    permission_classes = (IsUserModelPositionCommander,)
    serializer_class = RegionalPositionSerializer

    def get_queryset(self):
        queryset = get_headquarter_users_positions_queryset(
            self,
            RegionalHeadquarter,
            UserRegionalHeadquarterPosition
        )
        return cache.get_or_set(
            'regional-members-list',
            queryset,
            timeout=settings.REGIONALHQ_MEMBERS_CACHE_TTL
        )


class LocalPositionViewSet(BasePositionViewSet):
    """Просмотреть участников и изменить уровень доверенности/позиции.

    Доступно только командиру.

    Доступен поиск по username, first_name, last_name, patronymic_name
    """

    filter_backends = (filters.SearchFilter,)
    search_fields = (
        'user__username',
        'user__first_name',
        'user__last_name',
        'user__patronymic_name'
    )
    permission_classes = (IsUserModelPositionCommander,)
    serializer_class = LocalPositionSerializer

    def get_queryset(self):
        queryset = get_headquarter_users_positions_queryset(
            self,
            LocalHeadquarter,
            UserLocalHeadquarterPosition
        )
        return cache.get_or_set(
            'local-members-list',
            queryset,
            timeout=settings.LOCALHQ_MEMBERS_CACHE_TTL
        )


class EducationalPositionViewSet(BasePositionViewSet):
    """Просмотреть участников и изменить уровень доверенности/позиции.

    Доступно только командиру.

    Доступен поиск по username, first_name, last_name, patronymic_name
    """

    filter_backends = (filters.SearchFilter,)
    search_fields = (
        'user__username',
        'user__first_name',
        'user__last_name',
        'user__patronymic_name'
    )
    permission_classes = (IsUserModelPositionCommander,)
    serializer_class = EducationalPositionSerializer

    def get_queryset(self):
        queryset = get_headquarter_users_positions_queryset(
            self,
            EducationalHeadquarter,
            UserEducationalHeadquarterPosition
        )
        return cache.get_or_set(
            'edu-members-list',
            queryset,
            timeout=settings.EDUHQ_MEMBERS_CACHE_TTL
        )


class DetachmentPositionViewSet(BasePositionViewSet):
    """Просмотреть участников и изменить уровень доверенности/позиции.

    Доступно только командиру.

    Доступен поиск по username, first_name, last_name, patronymic_name
    """

    filter_backends = (filters.SearchFilter,)
    search_fields = (
        'user__username',
        'user__first_name',
        'user__last_name',
        'user__patronymic_name'
    )
    ordering_fields = ('last_name')
    permission_classes = (IsUserModelPositionCommander,)
    serializer_class = DetachmentPositionSerializer

    def get_queryset(self):
        queryset = get_headquarter_users_positions_queryset(
            self,
            Detachment,
            UserDetachmentPosition
        )
        return cache.get_or_set(
            'detachment-members-list',
            queryset,
            timeout=settings.DETACHMENT_MEMBERS_CACHE_TTL
        )


class DetachmentAcceptViewSet(CreateDeleteViewSet):
    """Принять/отклонить заявку участника в отряд по ID заявки.

    Можно дополнительно установить позицию и статус доверенности.
    Доступно командиру и доверенным лицам.
    """

    queryset = UserDetachmentPosition.objects.all()
    serializer_class = DetachmentPositionSerializer
    permission_classes = (IsDetachmentCommander,)

    def perform_create(self, serializer):
        """Получает user и detachment для сохранения."""
        headquarter_id = self.kwargs.get('pk')
        application_id = self.kwargs.get('application_pk')
        application = get_object_or_404(
            UserDetachmentApplication, id=application_id
        )
        user = application.user
        headquarter = get_object_or_404(Detachment, id=headquarter_id)
        application.delete()
        serializer.save(user=user, headquarter=headquarter)

    def create(self, request, *args, **kwargs):
        """Принимает (добавляет пользователя в отряд) юзера, удаляя заявку."""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(
                {'detail': e},
                status=status.HTTP_400_BAD_REQUEST
            )

    def destroy(self, request, *args, **kwargs):
        """Отклоняет (удаляет) заявку пользователя."""
        application_id = self.kwargs.get('application_pk')
        application = get_object_or_404(
            UserDetachmentApplication, id=application_id
        )
        application.delete()
        return Response(
            {'success': 'Заявка отклонена'},
            status=status.HTTP_204_NO_CONTENT
        )


class DetachmentApplicationViewSet(viewsets.ModelViewSet):
    """Подать/отменить заявку в отряд. URL-параметры обязательны.

    Доступно только авторизованному пользователю.
    """

    serializer_class = UserDetachmentApplicationSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        detachment_id = self.kwargs.get('pk')
        detachment = UserDetachmentApplication.objects.get(id=detachment_id)
        return UserDetachmentApplication.objects.filter(detachment=detachment)

    def perform_create(self, serializer):
        user = self.request.user
        detachment_id = self.kwargs.get('pk')
        detachment = get_object_or_404(Detachment, id=detachment_id)
        serializer.save(user=user, detachment=detachment)

    def create(self, request, *args, **kwargs):
        """Подает заявку на вступление в отряд, переданный URL-параметром."""
        if UserDetachmentPosition.objects.filter(user=request.user).exists():
            return Response(
                {'error': 'Вы уже являетесь членом одного из отрядов'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        """Отклоняет заявку на вступление в отряд."""
        detachment_id = self.kwargs.get('pk')
        try:
            application = UserDetachmentApplication.objects.get(
                user=self.request.user,
                detachment=Detachment.objects.get(id=detachment_id)
            )
            application.delete()
        except UserDetachmentApplication.DoesNotExist:
            return Response(
                {'error': 'Не найдена существующая заявка'},
                status=status.HTTP_404_NOT_FOUND
            )
        return Response(
            {'success': 'Заявка отклонена'},
            status=status.HTTP_204_NO_CONTENT
        )


@api_view(['GET'])
def get_structural_units(request):
    """
    Представление для агрегации и возврата списка всех
    структурных подразделений.

    Объединяет данные из различных типов штабов и отрядов,
    включая центральные, региональные, окружные, местные и
    образовательные штабы, а также отряды. Каждый тип подразделения
    сериализуется с использованием соответствующего сериализатора и
    возвращается в едином совокупном JSON-ответе.
    """
    central_headquarters = CentralHeadquarter.objects.all()
    regional_headquarters = RegionalHeadquarter.objects.all()
    district_headquarters = DistrictHeadquarter.objects.all()
    local_headquarters = LocalHeadquarter.objects.all()
    educational_headquarters = EducationalHeadquarter.objects.all()
    detachments = Detachment.objects.all()

    response = {
        'central_headquarters': CentralHeadquarterSerializer(
            central_headquarters, many=True
        ).data,
        'regional_headquarters': ShortRegionalHeadquarterSerializer(
            regional_headquarters, many=True
        ).data,
        'district_headquarters': ShortDistrictHeadquarterSerializer(
            district_headquarters, many=True
        ).data,
        'local_headquarters': ShortLocalHeadquarterSerializer(
            local_headquarters, many=True
        ).data,
        'educational_headquarters': ShortEducationalHeadquarterSerializer(
            educational_headquarters, many=True
        ).data,
        'detachments': ShortDetachmentSerializer(detachments, many=True).data
    }

    return Response(response)


class RegionAutoComplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Region.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs.order_by('name')


class EducationalAutoComplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = EducationalHeadquarter.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs.order_by('name')


class LocalAutoComplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = LocalHeadquarter.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs.order_by('name')


class RegionalAutoComplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = RegionalHeadquarter.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs.order_by('name')


class EducationalInstitutionAutoComplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = EducationalInstitution.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs.order_by('name')


class DetachmentAutoComplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Detachment.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs.order_by('name')


class PositionAutoComplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Position.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs.order_by('name')
