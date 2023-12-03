from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.mixins import ListRetrieveUpdateViewSet, ListRetrieveViewSet, \
    CreateViewSet, CreateDeleteViewSet
from api.serializers import (CentralHeadquarterSerializer,
                             DetachmentSerializer,
                             DistrictHeadquarterSerializer,
                             EducationalHeadquarterSerializer,
                             LocalHeadquarterSerializer,
                             RegionalHeadquarterSerializer, RegionSerializer,
                             RSOUserSerializer, UserDocumentsSerializer,
                             UserEducationSerializer, UserMediaSerializer,
                             UserPrivacySettingsSerializer,
                             UserRegionSerializer,
                             UserStatementDocumentsSerializer,
                             DetachmentPositionSerializer,
                             UsersParentSerializer,
                             UserDetachmentApplicationSerializer,
                             EducationalPositionSerializer,
                             LocalPositionSerializer,
                             RegionalPositionSerializer,
                             DistrictPositionSerializer,
                             CentralPositionSerializer)
from headquarters.models import (CentralHeadquarter, Detachment,
                                 DistrictHeadquarter, EducationalHeadquarter,
                                 LocalHeadquarter, Region, RegionalHeadquarter,
                                 UserDetachmentPosition,
                                 UserDetachmentApplication, UserEducationalHeadquarterPosition, UserCentralHeadquarterPosition, UserLocalHeadquarterPosition, UserRegionalHeadquarterPosition, UserDistrictHeadquarterPosition)
from users.models import (RSOUser, UserDocuments, UserEducation, UserMedia,
                          UserPrivacySettings, UserRegion, UsersParent,
                          UserStatementDocuments)


class RSOUserViewSet(ListRetrieveUpdateViewSet):
    """
    Представляет пользователей. Доступны операции чтения.
    Пользователь имеет возможность изменять собственные данные
    по id или по эндпоинту /users/me.
    """

    queryset = RSOUser.objects.all()
    serializer_class = RSOUserSerializer

    @action(
        detail=False,
        methods=['get', 'patch'],
        permission_classes=(permissions.IsAuthenticated,),
        serializer_class=RSOUserSerializer,
    )
    def me(self, request, pk=None):
        """Представляет текущего авторизованного пользователя."""
        if request.method == 'PATCH':
            serializer = self.get_serializer(
                request.user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

        return Response(self.get_serializer(request.user).data)


class RegionViewSet(ListRetrieveViewSet):
    """Представляет регионы. Доступны только операции чтения."""

    queryset = Region.objects.all()
    serializer_class = RegionSerializer


class BaseUserViewSet(viewsets.ModelViewSet):
    """
    Базовый класс ViewSet для работы с моделями,
    связанными с пользователем (RSOUser).

    Этот класс предназначен для расширения и создания специализированных
    ViewSets для различных пользовательских моделей. Он обеспечивает полный
    набор CRUD-операций (создание, чтение, обновление, удаление) для моделей,
    связанных с пользователем.

    Атрибуты:
    - permission_classes: используется permissions.IsAuthenticated для
    проверки, что пользователь аутентифицирован.

    Методы:
    - create(request, *args, **kwargs): Обрабатывает POST-запросы для создания
    новой записи. Вызывает описанный ниже perform_create метод.

    - perform_create(serializer): Позволяет связать создаваемую запись с
    текущим (авторизованным) пользователем.

    - retrieve(request, *args, **kwargs): Обрабатывает GET-запросы
    для получения записи текущего пользователя без явного указания ID в урле

    - update(request, *args, **kwargs): Обрабатывает PUT/PATCH-запросы для
    обновления существующей записи текущего пользователя без
    явного указания ID в урле

    - destroy(request, *args, **kwargs): Обрабатывает DELETE-запросы для
    удаления существующей записи текущего пользователя без
    явного указания ID в урле

    Параметры:
    - request: Объект HttpRequest, содержащий данные запроса.
    - args, kwargs: Дополнительные аргументы и ключевые аргументы, переданные
    в метод.

    Возвращаемое значение:
    - Ответ HttpResponse или Response, содержащий данные записи
    (для create, retrieve, update) или пустой ответ (для destroy).
    """

    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        user_id = self.kwargs.get('user_pk', None)
        user = get_object_or_404(
            RSOUser, id=user_id
        ) if user_id else self.request.user
        serializer.save(user=user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserEducationViewSet(BaseUserViewSet):
    """Представляет образовательную информацию пользователя."""

    queryset = UserEducation.objects.all()
    serializer_class = UserEducationSerializer

    def get_object(self):
        """Определяет instance для операций с объектом (get, upd, del)."""
        return get_object_or_404(UserEducation, user=self.request.user)


class UserDocumentsViewSet(BaseUserViewSet):
    """Представляет документы пользователя."""

    queryset = UserDocuments.objects.all()
    serializer_class = UserDocumentsSerializer

    def get_object(self):
        return get_object_or_404(UserDocuments, user=self.request.user)


class UserRegionViewSet(BaseUserViewSet):
    """Представляет информацию о проживании пользователя."""

    queryset = UserRegion.objects.all()
    serializer_class = UserRegionSerializer

    def get_object(self):
        return get_object_or_404(UserRegion, user=self.request.user)


class UserPrivacySettingsViewSet(BaseUserViewSet):
    """Представляет настройки приватности пользователя."""

    queryset = UserPrivacySettings.objects.all()
    serializer_class = UserPrivacySettingsSerializer

    def get_object(self):
        return get_object_or_404(UserPrivacySettings, user=self.request.user)


class UserMediaViewSet(BaseUserViewSet):
    """Представляет медиа-данные пользователя."""

    queryset = UserMedia.objects.all()
    serializer_class = UserMediaSerializer

    def get_object(self):
        return get_object_or_404(UserMedia, user=self.request.user)


class UserStatementDocumentsViewSet(BaseUserViewSet):
    """Представляет заявление на вступление в РСО пользователя."""

    queryset = UserStatementDocuments.objects.all()
    serializer_class = UserStatementDocumentsSerializer

    def get_object(self):
        return get_object_or_404(
            UserStatementDocuments,
            user=self.request.user
        )


class UsersParentViewSet(BaseUserViewSet):
    """Представляет законного представителя пользователя."""

    queryset = UsersParent.objects.all()
    serializer_class = UsersParentSerializer


class CentralViewSet(ListRetrieveUpdateViewSet):
    """Представляет центральные штабы.

    При операции чтения доступно число количества участников в структурной
    единице по ключу members_count, а также список всех участников по ключу
    members.
    """

    queryset = CentralHeadquarter.objects.all()
    serializer_class = CentralHeadquarterSerializer


class DistrictViewSet(viewsets.ModelViewSet):
    """Представляет окружные штабы.

    Привязывается к центральному штабу по ключу central_headquarter.
    При операции чтения доступно число количества участников в структурной
    единице по ключу members_count, а также список всех участников по ключу
    members.
    """

    queryset = DistrictHeadquarter.objects.all()
    serializer_class = DistrictHeadquarterSerializer


class RegionalViewSet(viewsets.ModelViewSet):
    """Представляет региональные штабы.

    Привязывается к окружному штабу по ключу district_headquarter (id).
    Привязывается к региону по ключу region (id).
    При операции чтения доступно число количества участников в структурной
    единице по ключу members_count, а также список всех участников по ключу
    members.
    """

    queryset = RegionalHeadquarter.objects.all()
    serializer_class = RegionalHeadquarterSerializer


class LocalViewSet(viewsets.ModelViewSet):
    """Представляет локальные штабы.

    Привязывается к региональному штабу по ключу regional_headquarter (id).
    При операции чтения доступно число количества участников в структурной
    единице по ключу members_count, а также список всех участников по ключу
    members.
    """

    queryset = LocalHeadquarter.objects.all()
    serializer_class = LocalHeadquarterSerializer


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
    """

    queryset = EducationalHeadquarter.objects.all()
    serializer_class = EducationalHeadquarterSerializer


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
    единице по ключу members_count, а также список всех участников по ключу
    members.
    """

    queryset = Detachment.objects.all()
    serializer_class = DetachmentSerializer


class BasePositionViewSet(viewsets.ModelViewSet):
    """Базовый вьюсет для просмотра/изменения участников штабов.

    Необходимо переопределять метод get_queryset и атрибут serializer_class
    """

    serializer_class = None

    def get_queryset(self):
        pass

    def get_object(self):
        queryset = self.get_queryset()
        member_pk = self.kwargs.get('member_pk')
        obj = queryset.get(pk=member_pk)
        return obj


class CentralPositionViewSet(BasePositionViewSet):
    """Просмотреть участников и изменить уровень доверенности/позиции.

    Доступно только командиру.
    """

    serializer_class = CentralPositionSerializer

    def get_queryset(self):
        headquarter_id = self.kwargs.get('pk')
        headquarter = RegionalHeadquarter.objects.get(id=headquarter_id)
        return UserCentralHeadquarterPosition.objects.filter(
            headquarter=headquarter
        )


class DistrictPositionViewSet(BasePositionViewSet):
    """Просмотреть участников и изменить уровень доверенности/позиции.

    Доступно только командиру.
    """

    serializer_class = DistrictPositionSerializer

    def get_queryset(self):
        headquarter_id = self.kwargs.get('pk')
        headquarter = RegionalHeadquarter.objects.get(id=headquarter_id)
        return UserDistrictHeadquarterPosition.objects.filter(
            headquarter=headquarter
        )


class RegionalPositionViewSet(BasePositionViewSet):
    """Просмотреть участников и изменить уровень доверенности/позиции.

    Доступно только командиру.
    """

    serializer_class = RegionalPositionSerializer

    def get_queryset(self):
        headquarter_id = self.kwargs.get('pk')
        headquarter = RegionalHeadquarter.objects.get(id=headquarter_id)
        return UserRegionalHeadquarterPosition.objects.filter(
            headquarter=headquarter
        )


class LocalPositionViewSet(BasePositionViewSet):
    """Просмотреть участников и изменить уровень доверенности/позиции.

    Доступно только командиру.
    """

    serializer_class = LocalPositionSerializer

    def get_queryset(self):
        headquarter_id = self.kwargs.get('pk')
        headquarter = LocalHeadquarter.objects.get(id=headquarter_id)
        return UserLocalHeadquarterPosition.objects.filter(
            headquarter=headquarter
        )


class EducationalPositionViewSet(BasePositionViewSet):
    """Просмотреть участников и изменить уровень доверенности/позиции.

    Доступно только командиру.
    """

    serializer_class = EducationalPositionSerializer

    def get_queryset(self):
        headquarter_id = self.kwargs.get('pk')
        headquarter = EducationalHeadquarter.objects.get(id=headquarter_id)
        return UserEducationalHeadquarterPosition.objects.filter(
            headquarter=headquarter
        )


class DetachmentPositionViewSet(BasePositionViewSet):
    """Просмотреть участников и изменить уровень доверенности/позиции.

    Доступно только командиру.
    """

    serializer_class = DetachmentPositionSerializer

    def get_queryset(self):
        detachment_id = self.kwargs.get('pk')
        detachment = Detachment.objects.get(id=detachment_id)
        return UserDetachmentPosition.objects.filter(headquarter=detachment)


class DetachmentAcceptViewSet(CreateDeleteViewSet):
    """Принять/отклонить заявку участника в отряд по ID заявки.

    Можно дополнительно установить позицию и статус доверенности.
    Доступно командиру и доверенным лицам.
    """

    queryset = UserDetachmentPosition.objects.all()
    serializer_class = DetachmentPositionSerializer

    def perform_create(self, serializer):
        """Получает user и detachment для сохранения."""
        headquarter_id = self.kwargs.get('pk')
        application_id = self.kwargs.get('application_pk')
        application = UserDetachmentApplication.objects.get(id=application_id)
        user = application.user
        headquarter = get_object_or_404(Detachment, id=headquarter_id)
        application.delete()
        serializer.save(user=user, headquarter=headquarter)

    def create(self, request, *args, **kwargs):
        """Принимает (добавляет пользователя в отряд) юзера, удаляя заявку."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        """Отклоняет (удаляет) заявку пользователя."""
        application_id = self.kwargs.get('application_pk')
        application = UserDetachmentApplication.objects.get(id=application_id)
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
        detachment = Detachment.objects.get(id=detachment_id)
        serializer.save(user=user, detachment=detachment)

    def create(self, request, *args, **kwargs):
        """Подает заявку на вступление в отряд, переданный URL-параметром."""
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
