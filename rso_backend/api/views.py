from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.mixins import ListRetrieveUpdateViewSet, ListRetrieveViewSet
from api.serializers import (RegionSerializer, RSOUserSerializer,
                             UserDocumentsSerializer, UserEducationSerializer,
                             UserMediaSerializer,
                             UserPrivacySettingsSerializer,
                             UserRegionSerializer,
                             UserStatementDocumentsSerializer)
from users.models import (RSOUser, UserDocuments, UserEducation,
                          UserMedia, UserPrivacySettings, UserRegion,
                          UserStatementDocuments)
from headquarters.models import Region


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

    def perform_create(self, serializer):
        user_id = self.kwargs.get('user_pk', None)
        user = get_object_or_404(
            RSOUser, id=user_id
        ) if user_id else self.request.user
        serializer.save(user=user)


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
