import io
import mimetypes
import os
import zipfile
from datetime import datetime

import pdfrw
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from pdfrw.buildxobj import pagexobj
from pdfrw.toreportlab import makerl
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from api.filters import EventFilter
from api.mixins import (CreateDeleteViewSet, ListRetrieveUpdateViewSet,
                        ListRetrieveViewSet)
from api.permissions import (IsAuthorPermission, IsDetachmentCommander,
                             IsDistrictCommander, IsEducationalCommander,
                             IsEventAuthor, IsLocalCommander,
                             IsRegionalCommander, IsRegionalCommanderForCert,
                             IsRegStuffOrDetCommander, IsStuffOrAuthor,
                             IsStuffOrCentralCommander,
                             MembershipFeePermission)
from api.serializers import (AreaSerializer, CentralHeadquarterSerializer,
                             CentralPositionSerializer,
                             DetachmentPositionSerializer,
                             DetachmentSerializer,
                             DistrictHeadquarterSerializer,
                             DistrictPositionSerializer,
                             EducationalHeadquarterSerializer,
                             EducationalInstitutionSerializer,
                             EducationalPositionSerializer,
                             EventAdditionalIssueSerializer,
                             EventDocumentDataSerializer,
                             EventOrganizerDataSerializer, EventSerializer,
                             EventTimeDataSerializer,
                             ForeignUserDocumentsSerializer,
                             LocalHeadquarterSerializer,
                             LocalPositionSerializer, MemberCertSerializer,
                             PositionSerializer,
                             ProfessionalEductionSerializer,
                             RegionalHeadquarterSerializer,
                             RegionalPositionSerializer, RegionSerializer,
                             RSOUserSerializer, ShortDetachmentSerializer,
                             ShortDistrictHeadquarterSerializer,
                             ShortEducationalHeadquarterSerializer,
                             ShortLocalHeadquarterSerializer,
                             ShortRegionalHeadquarterSerializer,
                             UserDetachmentApplicationSerializer,
                             UserDocumentsSerializer, UserEducationSerializer,
                             UserMediaSerializer,
                             UserPrivacySettingsSerializer,
                             UserProfessionalEducationSerializer,
                             UserRegionSerializer, UsersParentSerializer,
                             UserStatementDocumentsSerializer)
from api.swagger_schemas import EventSwaggerSerializer
from api.utils import (create_and_return_archive, download_file,
                       get_headquarter_users_positions_queryset, get_user,
                       get_user_by_id, text_to_lines)
from events.models import (Event, EventAdditionalIssue, EventDocumentData,
                           EventOrganizationData, EventTimeData)
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
from rso_backend.settings import BASE_DIR
from users.models import (MemberCert, RSOUser, UserDocuments, UserEducation,
                          UserForeignDocuments, UserMedia, UserMemberCertLogs,
                          UserMembershipLogs, UserParent, UserPrivacySettings,
                          UserProfessionalEducation, UserRegion,
                          UserStatementDocuments, UserVerificationRequest)


class RSOUserViewSet(ListRetrieveUpdateViewSet):
    """
    Представляет пользователей. Доступны операции чтения.
    Пользователь имеет возможность изменять собственные данные
    по id или по эндпоинту /users/me.
    Доступен поиск по username, first_name и last_name при передачи
    search query-параметра.
    """

    queryset = RSOUser.objects.all()
    serializer_class = RSOUserSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username', 'first_name', 'last_name')
    permission_classes = [permissions.AllowAny,]

    @action(
        detail=False,
        methods=['get', 'patch'],
        permission_classes=(permissions.IsAuthenticated, IsStuffOrAuthor),
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


class EducationalInstitutionViewSet(ListRetrieveViewSet):
    """Представляет учебные заведения. Доступны только операции чтения."""

    queryset = EducationalInstitution.objects.all()
    serializer_class = EducationalInstitutionSerializer


class RegionViewSet(ListRetrieveViewSet):
    """Представляет регионы. Доступны только операции чтения."""

    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    permission_classes = [IsStuffOrCentralCommander,]


class AreaViewSet(ListRetrieveViewSet):
    """Представляет направления для отрядов.

    Доступны только операции чтения.
    """

    queryset = Area.objects.all()
    serializer_class = AreaSerializer
    permission_classes = [IsStuffOrCentralCommander,]


class PositionViewSet(ListRetrieveViewSet):
    """Представляет должности для юзеров.

    Доступны только операции чтения.
    """

    queryset = Position.objects.all()
    serializer_class = PositionSerializer


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

    permission_classes = [permissions.IsAuthenticated,]

    def perform_create(self, serializer):
        user = get_user(self)
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
    permission_classes = [IsStuffOrAuthor,]

    def get_object(self):
        """Определяет instance для операций с объектом (get, upd, del)."""
        return get_object_or_404(UserEducation, user=self.request.user)


class UserProfessionalEducationViewSet(BaseUserViewSet):
    """Представляет профессиональную информацию пользователя.

    Дополнительные профобразования пользователя доступны по ключу
    'users_prof_educations'.
    """

    queryset = UserProfessionalEducation.objects.all()
    permission_classes = [IsStuffOrAuthor,]

    def get_object(self):
        return UserProfessionalEducation.objects.filter(
            user_id=self.request.user.id
        )

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return UserProfessionalEducationSerializer
        return ProfessionalEductionSerializer

    def destroy(self, request, *args, **kwargs):
        """Удаляет профессиональное образование пользователя."""

        queryset = self.get_queryset()
        if not queryset.filter(pk=kwargs['pk']).exists():
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={'detail': 'Нет записи с таким ID.'}
            )
        instance = self.get_queryset().get(pk=kwargs['pk'])
        if instance.user_id != self.request.user.id:
            return Response(
                status=status.HTTP_403_FORBIDDEN,
                data={'detail': 'У вас нет прав на удаление этой записи.'}
            )
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, *args, **kwargs):
        """Обновляет профессиональное образование пользователя."""

        queryset = self.get_queryset()
        if not queryset.filter(pk=kwargs['pk']).exists():
            return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={'detail': 'Нет записи с таким ID.'}
            )
        instance = self.get_queryset().get(pk=kwargs['pk'])
        if instance.user_id != self.request.user.id:
            return Response(
                status=status.HTTP_403_FORBIDDEN,
                data={'detail': 'У вас нет прав на изменение этой записи.'}
            )
        if self.action == 'partial_update':
            serializer = self.get_serializer(
                instance,
                data=request.data,
                partial=True
            )
        else:
            serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class UserDocumentsViewSet(BaseUserViewSet):
    """Представляет документы пользователя."""

    queryset = UserDocuments.objects.all()
    serializer_class = UserDocumentsSerializer
    permission_classes = (IsStuffOrAuthor,)

    def get_object(self):
        return get_object_or_404(UserDocuments, user=self.request.user)


class ForeignUserDocumentsViewSet(BaseUserViewSet):
    """Представляет документы иностранного пользователя."""

    queryset = UserForeignDocuments.objects.all()
    serializer_class = ForeignUserDocumentsSerializer
    permission_classes = (IsStuffOrAuthor,)

    def get_object(self):
        return get_object_or_404(UserForeignDocuments, user=self.request.user)


class UserRegionViewSet(BaseUserViewSet):
    """Представляет информацию о проживании пользователя."""

    queryset = UserRegion.objects.all()
    serializer_class = UserRegionSerializer
    permission_classes = (IsStuffOrAuthor,)

    def get_object(self):
        return get_object_or_404(UserRegion, user=self.request.user)


class UserPrivacySettingsViewSet(BaseUserViewSet):
    """Представляет настройки приватности пользователя."""

    queryset = UserPrivacySettings.objects.all()
    serializer_class = UserPrivacySettingsSerializer
    permission_classes = (IsStuffOrAuthor,)

    def get_object(self):
        return get_object_or_404(UserPrivacySettings, user=self.request.user)


class UserMediaViewSet(BaseUserViewSet):
    """Представляет медиа-данные пользователя."""

    queryset = UserMedia.objects.all()
    serializer_class = UserMediaSerializer
    permission_classes = (IsStuffOrAuthor,)

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

        filename = 'rso_membership_statement.docx'
        filepath = str(BASE_DIR) + '/templates/membership/' + filename
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

        filename = 'consent_to_the_processing_of_personal_data.docx'
        filepath = str(BASE_DIR) + '/templates/membership/' + filename
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

        filename = (
            'download_parent_consent_to_the_processing_of_personal_data.docx'
        )
        filepath = str(BASE_DIR) + '/templates/membership/' + filename
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

        filepath = str(BASE_DIR) + '\\templates\\membership\\'
        zip_filename = os.path.join(
            str(BASE_DIR) + '\\templates\\',
            'entry_forms.zip'
        )
        file_dir = os.listdir(filepath)
        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            for file in file_dir:
                zipf.write(os.path.join(filepath, file), file)
        zipf.close()
        filepath = str(BASE_DIR) + '\\templates\\' + 'entry_forms.zip'
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

    queryset = UserParent.objects.all()
    serializer_class = UsersParentSerializer
    permission_classes = (IsStuffOrAuthor,)

    def get_object(self):
        return get_object_or_404(UserParent, user=self.request.user)


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

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = (permissions.IsAdminUser,)
        else:
            permission_classes = (IsStuffOrCentralCommander,)
        return [permission() for permission in permission_classes]


class DistrictViewSet(viewsets.ModelViewSet):
    """Представляет окружные штабы.

    Привязывается к центральному штабу по ключу central_headquarter.
    При операции чтения доступно число количества участников в структурной
    единице по ключу members_count, а также список всех участников по ключу
    members.
    Доступен поиск по name при передаче ?search=<value> query-параметра.
    """

    queryset = DistrictHeadquarter.objects.all()
    serializer_class = DistrictHeadquarterSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = (IsStuffOrCentralCommander,)
        else:
            permission_classes = (IsDistrictCommander,)
        return [permission() for permission in permission_classes]


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
    """

    queryset = RegionalHeadquarter.objects.all()
    serializer_class = RegionalHeadquarterSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = (IsDistrictCommander,)
        else:
            permission_classes = (IsRegionalCommander,)
        return [permission() for permission in permission_classes]


class LocalViewSet(viewsets.ModelViewSet):
    """Представляет местные штабы.

    Привязывается к региональному штабу по ключу regional_headquarter (id).
    При операции чтения доступно число количества участников в структурной
    единице по ключу members_count, а также список всех участников по ключу
    members.
    Доступен поиск по name при передаче ?search=<value> query-параметра.
    """

    queryset = LocalHeadquarter.objects.all()
    serializer_class = LocalHeadquarterSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

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
    """

    queryset = EducationalHeadquarter.objects.all()
    serializer_class = EducationalHeadquarterSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

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
    единице по ключу members_count, а также список всех участников по ключу
    members.
    При операции чтения доступен список пользователей, подавших заявку на
    верификацию и относящихся к текущему отряду по
    ключу users_for_verification.
    При операции чтения доступен список пользователей, подавших заявку на
    вступление в отряд по ключу applications.
    Доступен поиск по name при передаче ?search=<value> query-параметра.
    """

    queryset = Detachment.objects.all()
    serializer_class = DetachmentSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = (IsEducationalCommander,)
        permission_classes = (IsDetachmentCommander, )
        return [permission() for permission in permission_classes]


class BasePositionViewSet(viewsets.ModelViewSet):
    """Базовый вьюсет для просмотра/изменения участников штабов.

    Необходимо переопределять метод get_queryset и атрибут serializer_class
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
        member_pk = self.kwargs.get('member_pk')
        obj = queryset.get(pk=member_pk)
        return obj


class CentralPositionViewSet(BasePositionViewSet):
    """Просмотреть участников и изменить уровень доверенности/позиции.

    Доступно только командиру.
    """

    serializer_class = CentralPositionSerializer
    permission_classes = (IsStuffOrCentralCommander,)

    def get_queryset(self):
        return get_headquarter_users_positions_queryset(
            self,
            CentralHeadquarter,
            UserCentralHeadquarterPosition
        )


class DistrictPositionViewSet(BasePositionViewSet):
    """Просмотреть участников и изменить уровень доверенности/позиции.

    Доступно только командиру.
    """

    serializer_class = DistrictPositionSerializer
    permission_classes = (IsDistrictCommander,)

    def get_queryset(self):
        return get_headquarter_users_positions_queryset(
            self,
            DistrictHeadquarter,
            UserDistrictHeadquarterPosition
        )


class RegionalPositionViewSet(BasePositionViewSet):
    """Просмотреть участников и изменить уровень доверенности/позиции.

    Доступно только командиру.
    """

    serializer_class = RegionalPositionSerializer
    permission_classes = (IsRegionalCommander,)

    def get_queryset(self):
        return get_headquarter_users_positions_queryset(
            self,
            RegionalHeadquarter,
            UserRegionalHeadquarterPosition
        )


class LocalPositionViewSet(BasePositionViewSet):
    """Просмотреть участников и изменить уровень доверенности/позиции.

    Доступно только командиру.
    """

    serializer_class = LocalPositionSerializer
    permission_classes = (IsLocalCommander,)

    def get_queryset(self):
        return get_headquarter_users_positions_queryset(
            self,
            LocalHeadquarter,
            UserLocalHeadquarterPosition
        )


class EducationalPositionViewSet(BasePositionViewSet):
    """Просмотреть участников и изменить уровень доверенности/позиции.

    Доступно только командиру.
    """

    serializer_class = EducationalPositionSerializer
    permission_classes = (IsEducationalCommander,)

    def get_queryset(self):
        return get_headquarter_users_positions_queryset(
            self,
            EducationalHeadquarter,
            UserEducationalHeadquarterPosition
        )


class DetachmentPositionViewSet(BasePositionViewSet):
    """Просмотреть участников и изменить уровень доверенности/позиции.

    Доступно только командиру.
    """

    serializer_class = DetachmentPositionSerializer
    permission_classes = (IsDetachmentCommander,)

    def get_queryset(self):
        return get_headquarter_users_positions_queryset(
            self,
            Detachment,
            UserDetachmentPosition
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


class EventViewSet(viewsets.ModelViewSet):
    """Представляет мероприятия."""

    queryset = Event.objects.all()
    serializer_class = EventSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_class = EventFilter
    search_fields = ('name', 'address', 'description',)

    PERMISSIONS_MAPPING = {
        'central': IsStuffOrCentralCommander,
        'districts': IsDistrictCommander,
        'regionals': IsRegionalCommander,
        'locals': IsLocalCommander,
        'educationals': IsEducationalCommander,
        'detachments': IsDetachmentCommander,
    }

    def get_permissions(self):
        """Применить пермишен в зависимости от действия."""
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        if self.action == 'create':
            event_unit = self.request.data.get('scale')
            permission_classes = [permissions.IsAuthenticated]
            permission_classes += [
                self.PERMISSIONS_MAPPING.get(
                    event_unit, permissions.IsAuthenticated
                )
            ]
        if self.action in (
                'update', 'update_time_data', 'update_document_data'
        ):
            permission_classes = [IsAuthorPermission]
        print(permission_classes)
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(request_body=EventSwaggerSerializer)
    def create(self, request, *args, **kwargs):
        author = request.user
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=EventTimeDataSerializer)
    @action(detail=True, methods=['put',], url_path='time_data')
    def update_time_data(self, request, pk=None):
        event = self.get_object()
        time_data_instance = EventTimeData.objects.get(event=event)

        serializer = EventTimeDataSerializer(
            time_data_instance, data=request.data
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(request_body=EventDocumentDataSerializer)
    @action(detail=True, methods=['put',], url_path='document_data')
    def update_document_data(self, request, pk=None):
        event = self.get_object()
        document_data_instance = EventDocumentData.objects.get(event=event)

        serializer = EventDocumentDataSerializer(
            document_data_instance, data=request.data
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EventOrganizationDataViewSet(viewsets.ModelViewSet):
    queryset = EventOrganizationData.objects.all()
    serializer_class = EventOrganizerDataSerializer
    permission_classes = (IsEventAuthor,)

    def get_queryset(self):
        queryset = super().get_queryset()
        event_pk = self.kwargs.get('event_pk')
        if event_pk is not None:
            queryset = queryset.filter(event__id=event_pk)
        return queryset

    def create(self, request, *args, **kwargs):
        event_pk = self.kwargs.get('event_pk')
        event = get_object_or_404(Event, pk=event_pk)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(event=event)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        data_pk = kwargs.get('pk')
        instance = get_object_or_404(
            EventOrganizationData,
            pk=data_pk,
            event__id=self.kwargs.get('event_pk')
        )
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EventAdditionalIssueViewSet(viewsets.ModelViewSet):
    queryset = EventAdditionalIssue.objects.all()
    serializer_class = EventAdditionalIssueSerializer
    permission_classes = (IsEventAuthor,)

    def get_queryset(self):
        queryset = super().get_queryset()
        event_pk = self.kwargs.get('event_pk')
        if event_pk is not None:
            queryset = queryset.filter(event__id=event_pk)
        return queryset

    def create(self, request, *args, **kwargs):
        event_pk = self.kwargs.get('event_pk')
        event = get_object_or_404(Event, pk=event_pk)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(event=event)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        data_pk = kwargs.get('pk')
        instance = get_object_or_404(
            EventAdditionalIssue,
            pk=data_pk,
            event__id=self.kwargs.get('event_pk')
        )
        serializer = self.get_serializer(instance, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def apply_for_verification(request):
    """Подать заявку на верификацию."""
    if request.method == 'POST':
        user = request.user
        try:
            UserVerificationRequest.objects.get(user=user)
            return Response(
                {'error': 'Вы уже подали заявку на верификацию'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except UserVerificationRequest.DoesNotExist:
            pass
        if user.is_verified:
            return Response(
                {'error': 'Пользователь уже верифицирован'},
                status=status.HTTP_400_BAD_REQUEST
            )
        UserVerificationRequest.objects.create(
            user=user
        )
        return Response(status=status.HTTP_201_CREATED)


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


@api_view(['POST', 'DELETE'])
@permission_classes([IsRegStuffOrDetCommander])
def verify_user(request, pk):
    """Принять/отклонить заявку пользователя на верификацию.

    Доступно только командирам и доверенным лицам региональных штабов
    (относящихся к тому же региону, что и юзер) и отрядов (в котором
    состоит юзер).
    """
    user = get_object_or_404(RSOUser, id=pk)
    if request.method == 'POST':
        application_for_verification = get_object_or_404(
            UserVerificationRequest, user=user
        )
        user.is_verified = True
        user.save()
        application_for_verification.delete()
        return Response(status=status.HTTP_202_ACCEPTED)
    application_for_verification = get_object_or_404(
        UserVerificationRequest, user=user
    )
    application_for_verification.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST', 'DELETE'])
@permission_classes([MembershipFeePermission])
def change_membership_fee_status(request, pk):
    """Изменить статус оплаты членского взноса пользователю.

    Доступно командирам и доверенным лицам РШ, в котором состоит
    пользователь.
    """
    user = get_object_or_404(RSOUser, id=pk)
    if request.method == 'POST':
        user.membership_fee = True
        user.save()
        UserMembershipLogs.objects.create(
            user=user,
            status_changed_by=request.user,
            status='Изменен на "оплачен"'
        )
        return Response(status=status.HTTP_202_ACCEPTED)
    user.membership_fee = False
    user.save()
    UserMembershipLogs.objects.create(
        user=user,
        status_changed_by=request.user,
        status='Изменен на "не оплачен"'
    )
    return Response(status=status.HTTP_204_NO_CONTENT)


class MemberCertViewSet(viewsets.ReadOnlyModelViewSet):

    TIMES_HEAD_SIZE = 15
    TIMES_TEXT_SIZE = 14
    ARIAL_TEXT_SIZE = 9
    HEAD_Y = 800
    VERTICAL_DISP = 155
    VERTICAL_RECIPIENT_DISP = 10
    VERTICAL_DISP_REQ = 160
    HORIZONTAL_DISP = 11
    HORIZONTAL_DISP_RECIPIENT = 12
    REQUISITES_X = 140
    REQUISITES_Y = 729
    LETTER_NUMBER_X = 50
    LETTER_NUMBER_Y = 650
    NAME_X = 135
    NAME_Y = 529
    BIRTHDAY_X = 126
    BIRTHDAY_Y = 496
    CERT_DATE_X = 160
    CERT_DATE_Y = 432
    REG_CASE_NAME_X = 29
    REG_CASE_NAME_Y = 385
    REG_NUMBER_X = 140
    REG_NUMBER_Y = 360
    INN_X = 380
    INN_Y = 309
    SNILS_X = 380
    SNILS_Y = 291
    RECIPIENT_X = 33
    RECIPIENT_Y = 230
    RECIPIENT_INTERNAL_X = 33
    RECIPIENT_INTERNAL_Y = 282
    RECIPIENT_LINE_X = 25
    RECIPIENT_LINE_Y = 240
    POSITION_PROC_PROP = 0.3
    POSITION_PROC_X = 25
    POSITION_PROC_Y = 99
    POSITION_PROC_LINE_Y = 110
    FIO = 3
    FI = 2
    SIGNATORY_X = 450
    SIGNATORY_Y = 85

    queryset = MemberCert.objects.all()
    serializer_class = MemberCertSerializer
    permission_classes = (IsRegionalCommanderForCert,)

    @classmethod
    def get_certificate(cls, user, request, cert_template='internal_cert.pdf'):
        """Метод собирает информацию о пользователе и его РШ.

        Работа метода представлена в комментариях к коду.
        """

        """Сбор данных из БД и запроса к эндпоинту."""
        data = request.data
        username = user.username
        first_name = user.first_name
        last_name = user.last_name
        patronymic_name = user.patronymic_name
        date_of_birth = user.date_of_birth
        try:
            user_docs = UserDocuments.objects.get(
                user=user
            )
            inn = user_docs.inn
            snils = user_docs.snils
        except UserDocuments.DoesNotExist:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={
                    'detail': 'Документы пользователя '
                    f'{username} не заполнены.'
                }
            )
        recipient = data.get('recipient', 'по месту требования')
        cert_start_date = datetime.strptime(
            data.get('cert_start_date'),
            '%Y-%m-%d'
        )
        cert_end_date = datetime.strptime(
            data.get('cert_end_date'),
            '%Y-%m-%d'
        )
        signatory = data.get('signatory', 'Фамилия Имя Отчество')
        position_procuration = data.get(
            'position_procuration', 'Руководитель регионального отделения'
        )
        try:
            regional_headquarter = UserRegionalHeadquarterPosition.objects.get(
                user=user
            ).headquarter
            commander = RSOUser.objects.get(
                id=regional_headquarter.commander.id
            )
            reg_case_name = regional_headquarter.case_name
            legal_address = str(regional_headquarter.legal_address)
            requisites = str(regional_headquarter.requisites)
            registry_number = str(regional_headquarter.registry_number)
            registry_date = regional_headquarter.registry_date
            commander_first_name = commander.first_name
            commander_last_name = commander.last_name
            commander_patronymic_name = commander.patronymic_name
        except (
            UserRegionalHeadquarterPosition.DoesNotExist,
            RegionalHeadquarter.DoesNotExist
        ):
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={
                    'detail': 'Не удалось определить региональный штаб '
                    f'пользователя {username}.'
                }
            )

        """Подготовка шаблона и шрифтов к выводу информации на лист."""
        template_path = os.path.join(
            str(BASE_DIR),
            'templates',
            'samples',
            cert_template
        )
        template = pdfrw.PdfReader(template_path, decompress=False).pages[0]
        template_obj = pagexobj(template)
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=A4, bottomup=1)
        xobj_name = makerl(c, template_obj)
        c.doForm(xobj_name)
        pdfmetrics.registerFont(
            TTFont(
                'Times_New_Roman',
                os.path.join(
                    str(BASE_DIR),
                    'templates',
                    'samples',
                    'fonts',
                    'times.ttf'
                )
            )
        )
        pdfmetrics.registerFont(
            TTFont(
                'Arial_Narrow',
                os.path.join(
                    str(BASE_DIR),
                    'templates',
                    'samples',
                    'fonts',
                    'arialnarrow.ttf'
                )
            )
        )

        """Блок вывода названия РШ в заголовок листа."""
        c.setFont('Times_New_Roman', cls.TIMES_HEAD_SIZE)
        page_width = c._pagesize[0]
        string_width = c.stringWidth(
            str(regional_headquarter),
            'Times_New_Roman',
            cls.TIMES_HEAD_SIZE
        )
        center_x = (page_width - string_width) / 2 + cls.VERTICAL_DISP
        c.drawCentredString(center_x, cls.HEAD_Y, str(regional_headquarter))

        """Блок вывода юр.адреса и реквизитов РШ под заголовком.

        В блоке опеределяется ширина поля на листе, куда будет выведен текст.
        Функция text_to_lines разбивает длину текста на строки. Длина строки
        определяется переменной proportion. Затем с помощью цикла
        производится перенос строк. Переменная line_break работает как ширина,
        на которую необходимо перенести строку.
        """
        c.setFont('Arial_Narrow', cls.ARIAL_TEXT_SIZE)
        text = legal_address + '.  ' + requisites
        string_width = c.stringWidth(
            text,
            'Arial_Narrow',
            cls.ARIAL_TEXT_SIZE
        )
        line_width = (page_width - cls.VERTICAL_DISP_REQ)
        proportion = line_width / string_width
        lines = text_to_lines(
            text=text,
            proportion=proportion
        )
        line_break = cls.HORIZONTAL_DISP
        for line in lines:
            c.drawString(
                cls.REQUISITES_X, cls.REQUISITES_Y - line_break, line
            )
            line_break += cls.HORIZONTAL_DISP
        c.drawString(
            cls.LETTER_NUMBER_X,
            cls. LETTER_NUMBER_Y,
            'б/н от ' + str(datetime.now().strftime('%d.%m.%Y'))
        )

        """Блок вывода информации о пользователе и РШ в тексте справки."""
        c.setFont('Times_New_Roman', cls.TIMES_TEXT_SIZE)
        if last_name and first_name and patronymic_name:
            c.drawString(
                cls.NAME_X,
                cls.NAME_Y,
                last_name + ' ' + first_name + ' ' + patronymic_name
            )
        if last_name and first_name and not patronymic_name:
            c.drawString(
                cls.NAME_X, cls.NAME_Y, last_name + ' ' + first_name
            )
        if date_of_birth:
            c.drawString(
                cls.BIRTHDAY_X,
                cls.BIRTHDAY_Y,
                str(date_of_birth.strftime('%d.%m.%Y')) + ' г.'
            )
        if (
            (not last_name and not first_name and not patronymic_name)
            or (not date_of_birth)
        ):
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={
                    'detail': f'Профиль пользователя {username} не заполнен.'
                }
            )
        c.drawString(
            cls.CERT_DATE_X,
            cls.CERT_DATE_Y,
            (
                'c '
                + str(cert_start_date.strftime('%d.%m.%Y'))
                + ' г. по '
                + str(cert_end_date.strftime('%d.%m.%Y') + ' г.')
            )
        )
        c.drawString(cls.REG_CASE_NAME_X, cls.REG_CASE_NAME_Y, reg_case_name)
        if registry_date:
            c.drawString(
                cls.REG_NUMBER_X,
                cls.REG_NUMBER_Y,
                (
                    registry_number
                    + ' от '
                    + registry_date.strftime('%d.%m.%Y')
                    + ' г.'
                )
            )
        else:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={
                    'detail': f'Данные РШ {regional_headquarter} не заполнены.'
                }
            )

        string_width = c.stringWidth(
            position_procuration,
            'Times_New_Roman',
            cls.TIMES_TEXT_SIZE
        )
        line_width = page_width
        proportion = cls.POSITION_PROC_PROP
        if proportion >= 1.0:
            c.drawString(
                cls.POSITION_PROC_X,
                cls.POSITION_PROC_Y,
                position_procuration
            )
        else:
            lines = text_to_lines(
                text=position_procuration,
                proportion=proportion
            )
            line_break = cls.HORIZONTAL_DISP
            for line in lines:
                c.drawString(
                    cls.POSITION_PROC_X,
                    cls.POSITION_PROC_LINE_Y - line_break,
                    line
                )
                line_break += cls.HORIZONTAL_DISP_RECIPIENT
        if cert_template == 'external_cert.pdf':
            c.drawString(cls.INN_X, cls.INN_Y, inn)
            c.drawString(cls.SNILS_X, cls.SNILS_Y, snils)
            string_width = c.stringWidth(
                recipient, 'Times_New_Roman', cls.TIMES_TEXT_SIZE
            )
            line_width = (page_width - cls.VERTICAL_RECIPIENT_DISP)
            start_line = line_width/2 - string_width/2
            proportion = line_width / string_width
            if proportion >= 1.0:
                c.drawString(start_line, cls.RECIPIENT_Y, recipient)
            else:
                lines = text_to_lines(
                    text=recipient,
                    proportion=proportion
                )
                line_break = cls.HORIZONTAL_DISP
                for line in lines:
                    c.drawString(
                        cls.RECIPIENT_X,
                        cls.RECIPIENT_Y - line_break,
                        line
                    )
                    line_break += cls.HORIZONTAL_DISP_RECIPIENT
            signatory_list = signatory.split()
            if len(signatory_list) == cls.FIO:
                c.drawString(
                    cls.SIGNATORY_X,
                    cls.SIGNATORY_Y,
                    (
                        signatory_list[0]
                        + ' '
                        + signatory_list[1][0]
                        + '.' + signatory_list[2][0]
                        + '.'
                    )
                )
            elif len(signatory_list) == cls.FI:
                c.drawString(
                    cls.SIGNATORY_X,
                    cls.SIGNATORY_Y,
                    signatory_list[0]
                    + ' '
                    + signatory_list[1][0]
                    + '.'
                )
        if cert_template == 'internal_cert.pdf':
            string_width = c.stringWidth(
                recipient, 'Times_New_Roman', cls.TIMES_TEXT_SIZE
            )
            line_width = (page_width - cls.VERTICAL_RECIPIENT_DISP)
            start_line = line_width/2 - string_width/2
            proportion = line_width / string_width
            if proportion >= 1.0:
                c.drawString(start_line, cls.RECIPIENT_INTERNAL_Y, recipient)
            else:
                lines = text_to_lines(
                    text=recipient,
                    proportion=proportion
                )
                line_break = cls.HORIZONTAL_DISP
                for line in lines:
                    c.drawString(
                        cls.RECIPIENT_INTERNAL_X,
                        cls.RECIPIENT_INTERNAL_Y - line_break,
                        line
                    )
                    line_break += cls.HORIZONTAL_DISP_RECIPIENT
            if (
                commander_first_name
                and commander_last_name
                and commander_patronymic_name
            ):
                c.drawString(
                    cls.SIGNATORY_X,
                    cls.SIGNATORY_Y,
                    str(commander_first_name)[0].upper()
                    + '.'
                    + str(commander_patronymic_name)[0].upper()
                    + '. '
                    + str(commander_last_name).capitalize()
                )
            elif (
                commander_first_name
                and commander_last_name
                and not commander_patronymic_name
            ):
                c.drawString(
                    cls.SIGNATORY_X,
                    cls.SIGNATORY_Y,
                    str(commander_first_name)[0].upper()
                    + '. '
                    + str(commander_last_name).capitalize()
                )
            c.showPage()
        c.save()
        return buf.getvalue()

    @action(
        detail=False,
        methods=['get', 'post'],
        permission_classes=(IsRegionalCommanderForCert,),
        serializer_class=MemberCertSerializer,
    )
    def external(self, request):

        if request.method == 'POST':
            user = get_user(self)
            serializer = self.get_serializer(
                data=request.data,
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user)
            ids = request.data.get('ids')
            external_certs = {}
            for user_id in ids:
                user = get_user_by_id(user_id)
                pdf_cert_or_response = self.get_certificate(
                    user=user,
                    request=request,
                    cert_template='external_cert.pdf'
                )
                if isinstance(pdf_cert_or_response, Response):
                    return pdf_cert_or_response
                filename = (
                    f'{user.username}.pdf'
                )
                external_certs[filename] = pdf_cert_or_response
                UserMemberCertLogs.objects.create(
                    user=user,
                    cert_type='external_cert',
                    cert_issued_by=request.user
                )
            response = create_and_return_archive(external_certs)
            return response

    @action(
        detail=False,
        methods=['get', 'post'],
        permission_classes=(IsRegionalCommanderForCert,),
        serializer_class=MemberCertSerializer,
    )
    def internal(self, request):

        if request.method == 'POST':
            user = get_user(self)
            serializer = self.get_serializer(
                data=request.data,
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(user=user)
            ids = request.data.get('ids')
            internal_certs = {}
            for user_id in ids:
                user = get_user_by_id(user_id)
                pdf_cert_or_response = self.get_certificate(
                    user=user,
                    request=request,
                    cert_template='internal_cert.pdf'
                )
                if isinstance(pdf_cert_or_response, Response):
                    return pdf_cert_or_response
                filename = (
                    f'{user.username}.pdf'
                )
                internal_certs[filename] = pdf_cert_or_response
                UserMemberCertLogs.objects.create(
                    user=user,
                    cert_type='internal_cert',
                    cert_issued_by=request.user
                )
            response = create_and_return_archive(internal_certs)
            return response
