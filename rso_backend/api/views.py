import os
import mimetypes
import zipfile

from django.shortcuts import get_object_or_404
from django.http.response import HttpResponse
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.mixins import ListRetrieveUpdateViewSet, ListRetrieveViewSet, \
    CreateViewSet
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
                             UsersParentSerializer)
from api.utils import download_file
from headquarters.models import (CentralHeadquarter, Detachment,
                                 DistrictHeadquarter, EducationalHeadquarter,
                                 LocalHeadquarter, Region, RegionalHeadquarter,
                                 UserDetachmentPosition)
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

    @action(
            detail=False,
            methods=('get',),
            permission_classes=(permissions.IsAuthenticated,)
    )
    def download_membership_file(self, request):
        """Скачивание бланка заявления на вступление в РСО.

        Эндпоинт для скачивания
        /users/me/statement/download_membership_statement_file/
        """

        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filename = 'rso_membership_statement.docx'
        filepath = BASE_DIR + '/templates/membership/' + filename
        return download_file(filepath, filename)

    @action(
            detail=False,
            methods=('get',),
            permission_classes=(permissions.IsAuthenticated,)
    )
    def download_consent_personal_data(self, request):
        """Скачивание бланка согласия на обработку персональных данных.

        Эндпоинт для скачивания
        /users/me/statement/download_consent_to_the_processing_of_personal_data/
        """

        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filename = 'consent_to_the_processing_of_personal_data.docx'
        filepath = BASE_DIR + '/templates/membership/' + filename
        return download_file(filepath, filename)

    @action(
            detail=False,
            methods=('get',),
            permission_classes=(permissions.IsAuthenticated,)
    )
    def download_parent_consent_personal_data(self, request):
        """
        Скачивание бланка согласия законного представителя
        на обработку персональных данных несовершеннолетнего.
        Эндпоинт для скачивания
        /users/me/statement/download_parent_consent_to_the_processing_of_personal_data/
        """

        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filename = (
            'download_parent_consent_to_the_processing_of_personal_data.docx'
        )
        filepath = BASE_DIR + '/templates/membership/' + filename
        return download_file(filepath, filename)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(permissions.IsAuthenticated,)
    )
    def download_all_forms(self, _):
        """Скачивание архива с бланками.

        В архиве все три бланка для подачи заявления на вступление в РСО.
        Архив доступен по эндпоинту /users/me/statement/download_all_forms/
        """

        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = BASE_DIR + '\\templates\\membership\\'
        zip_filename = os.path.join(
            BASE_DIR + '\\templates\\',
            'entry_forms.zip'
        )
        file_dir = os.listdir(filepath)
        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            for file in file_dir:
                zipf.write(os.path.join(filepath, file), file)
        zipf.close()
        filepath = BASE_DIR + '\\templates\\' + 'entry_forms.zip'
        path = open(filepath, 'rb')
        mime_type, _ = mimetypes.guess_type(filepath)
        response = HttpResponse(path, content_type=mime_type)
        response['Content-Disposition'] = (
            'attachment; filename=%s' % 'entry_forms.zip'
        )
        os.remove(filepath)
        return response


class UsersParentViewSet(BaseUserViewSet):
    """Представляет законного представителя пользователя."""
    queryset = UsersParent.objects.all()
    serializer_class = UsersParentSerializer


class CentralViewSet(ListRetrieveUpdateViewSet):
    queryset = CentralHeadquarter.objects.all()
    serializer_class = CentralHeadquarterSerializer


class DistrictViewSet(viewsets.ModelViewSet):
    queryset = DistrictHeadquarter.objects.all()
    serializer_class = DistrictHeadquarterSerializer


class RegionalViewSet(viewsets.ModelViewSet):
    queryset = RegionalHeadquarter.objects.all()
    serializer_class = RegionalHeadquarterSerializer


class LocalViewSet(viewsets.ModelViewSet):
    queryset = LocalHeadquarter.objects.all()
    serializer_class = LocalHeadquarterSerializer


class EducationalViewSet(viewsets.ModelViewSet):
    queryset = EducationalHeadquarter.objects.all()
    serializer_class = EducationalHeadquarterSerializer


class DetachmentViewSet(viewsets.ModelViewSet):
    queryset = Detachment.objects.all()
    serializer_class = DetachmentSerializer


class DetachmentPositionViewSet(CreateViewSet):
    queryset = UserDetachmentPosition.objects.all()
    serializer_class = DetachmentPositionSerializer
