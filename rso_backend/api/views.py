import io
import itertools
import mimetypes
import os
import zipfile
from datetime import date, datetime

import pdfrw
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q, Count
from django.conf import settings
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from pdfrw.buildxobj import pagexobj
from pdfrw.toreportlab import makerl
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import filters, permissions, serializers, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from api import constants
from api.filters import (EducationalHeadquarterFilter, EventFilter,
                         LocalHeadquarterFilter, RSOUserFilter,
                         DetachmentFilter, RegionalHeadquarterFilter)
from api.mixins import (CreateDeleteViewSet, CreateListRetrieveDestroyViewSet,
                        CreateRetrieveUpdateViewSet,
                        ListRetrieveDestroyViewSet, ListRetrieveUpdateViewSet,
                        ListRetrieveViewSet, RetrieveUpdateViewSet,
                        RetrieveViewSet)
from api.permissions import (IsApplicantOrOrganizer,
                             IsAuthorMultiEventApplication,
                             IsAuthorPermission, IsCommander,
                             IsDetachmentCommander, IsDistrictCommander,
                             IsEducationalCommander, IsEventAuthor,
                             IsEventOrganizer, IsLocalCommander,
                             IsRegionalCommander, IsRegionalCommanderForCert,
                             IsRegionalCommanderOrAdmin,
                             IsRegionalCommanderOrAdminOrAuthor,
                             IsRegStuffOrDetCommander, IsStuffOrAuthor,
                             IsStuffOrCentralCommander,
                             IsStuffOrCentralCommanderOrTrusted,
                             IsVerifiedPermission, MembershipFeePermission,
                             IsUserModelPositionCommander,
                             IsCommanderOrTrustedAnywhere)
from api.serializers import (AnswerSerializer, AreaSerializer,
                             CentralHeadquarterSerializer,
                             CentralPositionSerializer,
                             CompetitionSerializer,
                             CompetitionApplicationsSerializer,
                             CompetitionApplicationsObjectSerializer,
                             CompetitionParticipantsSerializer,
                             CompetitionParticipantsObjectSerializer,
                             DetachmentPositionSerializer,
                             DetachmentSerializer,
                             DistrictHeadquarterSerializer,
                             DistrictPositionSerializer,
                             EducationalHeadquarterSerializer,
                             EducationalInstitutionSerializer,
                             EducationalPositionSerializer, EmailSerializer,
                             EventAdditionalIssueSerializer,
                             EventApplicationsSerializer,
                             EventApplicationsCreateSerializer,
                             EventDocumentDataSerializer,
                             EventOrganizerDataSerializer,
                             EventParticipantsSerializer, EventSerializer,
                             EventTimeDataSerializer,
                             EventUserDocumentSerializer,
                             ForeignUserDocumentsSerializer,
                             LocalHeadquarterSerializer,
                             LocalPositionSerializer, MemberCertSerializer,
                             MultiEventApplicationSerializer,
                             MultiEventParticipantsSerializer,
                             PositionSerializer,
                             ProfessionalEductionSerializer,
                             RegionalHeadquarterSerializer,
                             RegionalPositionSerializer, RegionSerializer,
                             RSOUserSerializer,
                             ShortCentralHeadquarterSerializerME,
                             ShortDetachmentSerializer,
                             ShortDetachmentSerializerME,
                             ShortDistrictHeadquarterSerializer,
                             ShortDistrictHeadquarterSerializerME,
                             ShortEducationalHeadquarterSerializer,
                             ShortEducationalHeadquarterSerializerME,
                             ShortLocalHeadquarterSerializer,
                             ShortLocalHeadquarterSerializerME,
                             ShortMultiEventApplicationSerializer,
                             ShortRegionalHeadquarterSerializer,
                             ShortRegionalHeadquarterSerializerME,
                             ShortUserSerializer,
                             UserDetachmentApplicationSerializer,
                             UserDocumentsSerializer, UserEducationSerializer,
                             UserMediaSerializer,
                             UserPrivacySettingsSerializer,
                             UserProfessionalEducationSerializer,
                             UserRegionSerializer, UserTrustedSerializer,
                             UsersParentSerializer,
                             UserStatementDocumentsSerializer,
                             UserDetachmentApplicationReadSerializer,
                             UserVerificationReadSerializer,
                             UserCommanderSerializer,
                             UserHeadquarterPositionSerializer)
from api.swagger_schemas import (EventSwaggerSerializer, applications_response,
                                 application_me_response, answer_response,
                                 participant_me_response,
                                 request_update_application,
                                 response_competitions_applications,
                                 response_competitions_participants,
                                 response_create_application,
                                 response_junior_detachments)
from api.utils import (create_and_return_archive, download_file,
                       get_headquarter_users_positions_queryset, get_user,
                       get_user_by_id, text_to_lines)
from competitions.models import CompetitionParticipants, CompetitionApplications, Competitions
from events.models import (Event, EventAdditionalIssue, EventApplications,
                           EventDocumentData, EventIssueAnswer,
                           EventOrganizationData, EventParticipants,
                           EventTimeData, EventUserDocument,
                           MultiEventApplication)
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
from api.tasks import send_reset_password_email_without_user
from rso_backend.settings import BASE_DIR
from users.models import (MemberCert, RSOUser, UserDocuments, UserEducation,
                          UserForeignDocuments, UserMedia, UserMemberCertLogs,
                          UserMembershipLogs, UserParent, UserPrivacySettings,
                          UserProfessionalEducation, UserRegion,
                          UserStatementDocuments, UserVerificationLogs, UserVerificationRequest)


class CustomUserViewSet(UserViewSet):
    """Кастомный вьюсет юзера.
    Доступно изменение метода сброса пароля reset_password
    на новом эндпоинте api/v1/reset_password/.
    Эндпоинт списка юзеров /api/v1/rsousers.
    Доступен поиск по username, first_name, last_name, patronymic_name
    при передаче search query-параметра.
    По умолчанию сортируются по last_name.
    Доступна фильтрация по полям:
    - district_headquarter__name,
    - regional_headquarter__name,
    - local_headquarter__name,
    - educational_headquarter__name,
    - detachment__name,
    - gender,
    - is_verified,
    - membership_fee,
    - date_of_birth.
    """

    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    search_fields = ('username', 'first_name', 'last_name', 'patronymic_name')
    filterset_class = RSOUserFilter
    ordering_fields = ('last_name')

    @action(
            methods=['post'],
            detail=False,
            permission_classes=(permissions.IsAuthenticated,),
            serializer_class=EmailSerializer,
    )
    def reset_password(self, request, *args, **kwargs):
        """
        POST-запрос с адресом почты в json`е
        высылает ссылку на почту на подтвеждение смены пароля.
        Вид ссылки в почте:
        'https://лк.трудкрут.рф/password/reset/confirm/{uid}/{token}'
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        try:
            RSOUser.objects.get(email__iexact=data.get('email'))
            send_reset_password_email_without_user.delay(data=data)
            return Response(status=status.HTTP_200_OK)
        except (RSOUser.DoesNotExist, AttributeError):
            return Response(
                {'detail': (
                    'Нет пользователя с введенным email или опечатка в адресе.'
                )},
                status=status.HTTP_204_NO_CONTENT
            )
        except RSOUser.MultipleObjectsReturned:
            return Response(
                {'detail': (
                    'В БД несколько юзеров с одним адресом почты.'
                    ' Отредактируйте дубликаты и повторите попытку.'
                )},
                status=status.HTTP_409_CONFLICT
            )


class RSOUserViewSet(RetrieveViewSet):
    """
    Представляет пользователей. Доступны операции чтения.
    Пользователь имеет возможность изменять собственные данные
    по id или по эндпоинту /users/me.
    Доступен поиск по username, first_name, last_name, patronymic_name
    при передаче search query-параметра.
    По умолчанию сортируются по last_name.
    Доступна фильтрация по полям:
    - district_headquarter__name,
    - regional_headquarter__name,
    - local_headquarter__name,
    - educational_headquarter__name,
    - detachment__name,
    - gender,
    - is_verified,
    - membership_fee,
    - date_of_birth.
    """

    queryset = RSOUser.objects.all()
    serializer_class = RSOUserSerializer
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    search_fields = ('username', 'first_name', 'last_name', 'patronymic_name')
    filterset_class = RSOUserFilter
    ordering_fields = ('last_name')
    # TODO: переписать пермишены, чтобы получить данные можно было
    # TODO: только тех пользователей, что состоят в той же стр. ед., где
    # TODO: запрашивающий пользователь и является командиром/доверенным
    permission_classes = (
        permissions.IsAuthenticated, IsCommanderOrTrustedAnywhere,
    )

    @action(
        detail=False,
        methods=['get', 'patch'],
        permission_classes=(permissions.IsAuthenticated, IsStuffOrAuthor,),
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

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(permissions.IsAuthenticated, IsStuffOrAuthor,),
        serializer_class=UserCommanderSerializer
    )
    def me_commander(self, request, pk=None):
        """
        Представляет айди структурных единиц, в которых пользователь
        является командиром.
        """
        if request.method == 'GET':
            serializer = UserCommanderSerializer(request.user)
            return Response(serializer.data)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(permissions.IsAuthenticated, IsStuffOrAuthor,),
        serializer_class=UserCommanderSerializer
    )
    def me_trusted(self, request, pk=None):
        """
        Представляет айди структурных единиц, в которых пользователь
        является доверенным.
        """
        if request.method == 'GET':
            serializer = UserTrustedSerializer(request.user)
            return Response(serializer.data)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(permissions.IsAuthenticated, IsStuffOrAuthor,),
        serializer_class=UserCommanderSerializer
    )
    def me_positions(self, request, pk=None):
        """
        Представляет должности текущего юзера на каждом структурном уровне.
        """
        if request.method == 'GET':
            serializer = UserHeadquarterPositionSerializer(request.user)
            return Response(serializer.data)

    @action(
        detail=True,
        methods=['get'],
        permission_classes=(permissions.AllowAny,),
        serializer_class=UserCommanderSerializer
    )
    def positions(self, request, pk=None):
        """
        Представляет должности юзера по pk на каждом структурном уровне.
        """
        if request.method == 'GET':
            user = get_object_or_404(RSOUser, id=pk)
            serializer = UserHeadquarterPositionSerializer(user)
            return Response(serializer.data)


class EducationalInstitutionViewSet(ListRetrieveViewSet):
    """Представляет учебные заведения. Доступны только операции чтения."""

    queryset = EducationalInstitution.objects.all()
    serializer_class = EducationalInstitutionSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

    ordering = ('name',)


class RegionViewSet(ListRetrieveViewSet):
    """Представляет регионы. Доступны только операции чтения."""

    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', 'code')
    permission_classes = [IsStuffOrCentralCommander,]
    ordering = ('name',)


class AreaViewSet(ListRetrieveViewSet):
    """Представляет направления для отрядов.

    Доступны только операции чтения.
    """

    queryset = Area.objects.all()
    serializer_class = AreaSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    permission_classes = [IsStuffOrCentralCommander,]
    ordering_fields = ('name',)


class PositionViewSet(ListRetrieveViewSet):
    """Представляет должности для юзеров.

    Доступны только операции чтения.
    """

    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    ordering = ('name',)


class BaseUserViewSet(viewsets.ModelViewSet):
    """
    Базовый класс ViewSet для работы с моделями,
    связанными с пользователем (RSOUser).

    Этот класс предназначен для расширения и создания специализированных
    ViewSets для различных пользовательских моделей. Он обеспечивает полный
    набор CRUD-операций (создание, чтение, обновление, удаление) для моделей,
    связанных с пользователем.

    Атрибуты:
    - permission_classes: используется permissions. IsAuthenticated для
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
    ordering_fields = ('study_specialty',)

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
    ordering = ('qualification',)

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

        filename = 'rso_membership_statement.rtf'
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

        filename = 'consent_to_the_processing_of_personal_data.rtf'
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
            'download_parent_consent_to_the_processing_of_personal_data.rtf'
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
            permission_classes = (IsStuffOrCentralCommanderOrTrusted,)
        return [permission() for permission in permission_classes]


class DistrictViewSet(viewsets.ModelViewSet):
    """Представляет окружные штабы.

    Привязывается к центральному штабу по ключу central_headquarter.
    При операции чтения доступно число количества участников в структурной
    единице по ключу members_count, а также список всех участников по ключу
    members.
    Доступен поиск по name при передаче ?search=<value> query-параметра.
    Сортировка по умолчанию - количество участников
    """

    queryset = DistrictHeadquarter.objects.annotate(
        count_related=Count('members')
    )
    serializer_class = DistrictHeadquarterSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    ordering = ('count_related',)

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = (IsStuffOrCentralCommanderOrTrusted,)
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
    Доступна сортировка по ключам name, founding_date, count_related.
    Сортировка по умолчанию - количество участников.
    Доступна фильтрация по Окружным Штабам. Ключ - district_headquarter__name.
    """

    queryset = RegionalHeadquarter.objects.annotate(
        count_related=Count('members')
    )
    serializer_class = RegionalHeadquarterSerializer
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    search_fields = ('name', 'region__name',)
    ordering_fields = ('name', 'founding_date', 'count_related')
    ordering = ('count_related', )
    filterset_class = RegionalHeadquarterFilter

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = (IsDistrictCommander,)
        else:
            permission_classes = (IsRegionalCommander,)
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['get', ], url_path='verifications')
    def get_verifications(self, request, pk=None):
        """
        Получить список пользователей, подавших заявку на верификацию,
        у которых совпадает регион с регионом текущего РШ.
        """
        headquarter = self.get_object()
        verifications = UserVerificationRequest.objects.filter(
            user__region=headquarter.region,
        ).select_related('user')
        serializer = UserVerificationReadSerializer(
            instance=verifications, many=True
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
    """

    queryset = LocalHeadquarter.objects.annotate(
        count_related=Count('members')
    )
    serializer_class = LocalHeadquarterSerializer
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    search_fields = ('name',)
    ordering_fields = ('name', 'founding_date', 'count_related')
    ordering = ('count_related', )
    filterset_class = LocalHeadquarterFilter

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
    """

    queryset = EducationalHeadquarter.objects.annotate(
        count_related=Count('members')
    )
    serializer_class = EducationalHeadquarterSerializer
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    search_fields = ('name',)
    filterset_class = EducationalHeadquarterFilter
    ordering_fields = ('name', 'founding_date', 'count_related')
    ordering = ('count_related', )

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
    Доступна фильтрация по ключам area__name, educational_institution__name,
    """

    queryset = Detachment.objects.annotate(
        count_related=Count('members')
    )
    serializer_class = DetachmentSerializer
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    search_fields = ('name',)
    filterset_class = DetachmentFilter
    ordering_fields = ('name', 'founding_date', 'count_related')
    ordering = ('count_related', )

    def get_permissions(self):
        if self.action == 'create':
            permission_classes = (IsEducationalCommander,)
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
        user_ids_in_verification_request = (
            UserVerificationRequest.objects.values_list(
                'user_id', flat=True
            )
        )
        members_to_verify = detachment.members.filter(
            user__id__in=user_ids_in_verification_request
        ).select_related('user')
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
        # TODO: в действительности мы отлавливаем DoesNotExist для дочерних классов
        # TODO: edit - можно добавить маппинг. Сделать позднее.
        except Exception:
            return Response(
                {'detail': 'Не найден участник по заданному айди членства.'},
                status=status.HTTP_404_NOT_FOUND
            )
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
    permission_classes = (IsUserModelPositionCommander,)

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
    permission_classes = (IsUserModelPositionCommander,)

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
    permission_classes = (IsUserModelPositionCommander,)

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
    permission_classes = (IsUserModelPositionCommander,)

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
    permission_classes = (IsUserModelPositionCommander,)

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

    _PERMISSIONS_MAPPING = {
        'Всероссийское': IsStuffOrCentralCommander,
        'Окружное': IsDistrictCommander,
        'Региональное': IsRegionalCommander,
        'Городское': IsLocalCommander,
        'Образовательное': IsEducationalCommander,
        'Отрядное': IsDetachmentCommander,
    }

    def get_permissions(self):
        """
        Применить пермишен в зависимости от действия и масштаба мероприятия.
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        if self.action == 'create':
            event_unit = self.request.data.get('scale')
            permission_classes = [permissions.IsAuthenticated]
            permission_classes += [
                self._PERMISSIONS_MAPPING.get(
                    event_unit, permissions.IsAuthenticated
                )
            ]
        if self.action in (
                'update', 'update_time_data', 'update_document_data'
        ):
            permission_classes = [IsAuthorPermission, IsEventOrganizer]
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
        """Заполнить информацию о времени проведения мероприятия."""
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
        """
        Указать необходимые к заполнению документы
        для участия в мероприятии.
        """
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
    """Представляет информацию об организаторах мероприятия.

    Добавленные пользователь могу иметь доступ к редактированию информации о
    мероприятии, а также рассмотрение и принятие/отклонение заявок на участие.
    """
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
    """
    Представляет дополнительные вопросы к мероприятию, необходимые
    для заполнения при подаче индивидуальной заявки.
    """
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
@permission_classes([permissions.IsAuthenticated, IsRegStuffOrDetCommander])
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
        UserVerificationLogs.objects.create(
            user=user,
            date=datetime.now(),
            verification_by=request.user,
            description='Верификация пользователем'
        )
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

        if data.get('cert_start_date') is not None:
            cert_start_date = datetime.strptime(
                data.get('cert_start_date'),
                '%Y-%m-%d'
            )
        else:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={
                    'detail': 'Не указана дата начала действия сертификата.'
                }
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
            else:
                c.drawString(cls.SIGNATORY_X, cls.SIGNATORY_Y, signatory)
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

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties=constants.properties | constants.properties_external,
            required=['cert_start_date', 'cert_end_date', 'recipient', 'ids'],
        ),
        method='post',
    )
    @action(
        detail=False,
        methods=['post',],
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
            if ids is None:
                return Response(
                    {'detail': 'Поле ids не может быть пустым.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            external_certs = {}
            for user_id in ids:
                if user_id == 0:
                    return Response(
                        {'detail': 'Поле ids не может содержать 0.'},
                    )
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
                    cert_type='Для работодателя',
                    cert_issued_by=request.user
                )
            response = create_and_return_archive(external_certs)
            return response

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties=constants.properties,
            required=['cert_start_date', 'cert_end_date', 'recipient', 'ids'],
        ),
        method='post',
    )
    @action(
        detail=False,
        methods=['post',],
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
            if ids is None:
                return Response(
                    {'detail': 'Поле ids не может быть пустым.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            internal_certs = {}
            for user_id in ids:
                if user_id == 0:
                    return Response(
                        {'detail': 'Поле ids не может содержать 0.'},
                    )
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
                    cert_type='Внутренняя справка',
                    cert_issued_by=request.user
                )
            response = create_and_return_archive(internal_certs)
            return response


class EventApplicationsViewSet(CreateListRetrieveDestroyViewSet):
    """Представление заявок на участие в мероприятии.

    Доступ:
        - создание - авторизованные пользователи;
        - чтение и удаление - авторы заявок либо пользователи
          из модели организаторов;
    """
    queryset = EventApplications.objects.all()
    serializer_class = EventApplicationsSerializer
    permission_classes = (permissions.IsAuthenticated, IsEventOrganizer)

    def get_queryset(self):
        """ Получение заявок конкретного мероприятия. """
        queryset = super().get_queryset()
        event_pk = self.kwargs.get('event_pk')
        if event_pk is not None:
            queryset = queryset.filter(event__id=event_pk)
        return queryset

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return EventApplicationsCreateSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated(), IsVerifiedPermission()]
        elif self.action in ['retrieve', 'destroy']:
            return [permissions.IsAuthenticated(), IsApplicantOrOrganizer()]
        else:
            return super().get_permissions()

    def create(self, request, *args, **kwargs):
        """Создание заявки на участие в мероприятии."""
        user = request.user
        event_pk = self.kwargs.get('event_pk')
        event = get_object_or_404(Event, pk=event_pk)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(event=event, user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """
        Реализует функционал отклонения заявки на участие в мероприятии.
        При отклонении заявки удаляются все документы и ответы на вопросы.
        """
        instance = self.get_object()
        # очень дорого, нужно оптимизировать.
        answers = EventIssueAnswer.objects.filter(
            event=instance.event, user=instance.user
        )
        documents = EventUserDocument.objects.filter(
            event=instance.event, user=instance.user
        )
        try:
            with transaction.atomic():
                instance.delete()
                documents.delete()  # и тут подумать над оптимизацией...
                answers.delete()
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True,
            methods=['post'],
            url_path='confirm',
            serializer_class=EventParticipantsSerializer,
            permission_classes=(permissions.IsAuthenticated,
                                IsEventOrganizer,))
    def confirm(self, request, *args, **kwargs):
        """Подтверждение заявки на участие в мероприятии и создание участника.

        После подтверждения заявка удаляется.
        Доступен только для организаторов мероприятия.
        Если пользователь уже участвует в мероприятии,
        выводится предупреждение.
        """
        instance = self.get_object()
        serializer = EventParticipantsSerializer(data=request.data,
                                                 context={'request': request})
        serializer.is_valid(raise_exception=True)
        try:
            with transaction.atomic():
                serializer.save(user=instance.user, event=instance.event)
                instance.delete()
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True,
            methods=['get', 'delete'],
            url_path='answers',
            serializer_class=AnswerSerializer,
            permission_classes=(permissions.IsAuthenticated,
                                IsEventOrganizer,))
    @swagger_auto_schema(responses=answer_response)
    def answers(self, request, event_pk, pk):
        """Action для получения (GET) или удаления ответов (DELETE)
        на вопросы мероприятия по данной заявке.

        Доступен только для пользователей из модели организаторов.
        """
        answers = EventIssueAnswer.objects.filter(user=request.user,
                                                  event__id=event_pk)
        if request.method == 'GET':
            serializer = AnswerSerializer(answers,
                                          many=True,
                                          context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        try:
            answers.delete()
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            methods=['get'],
            url_path='me',
            serializer_class=EventApplicationsSerializer,
            permission_classes=(permissions.IsAuthenticated,))
    @swagger_auto_schema(responses=application_me_response)
    def me(self, request, event_pk):
        """Action для получения всей информации по поданной текущим
        пользователем заявке на участие в мероприятии.

        Доступен всем авторизованным пользователям.

        Если у этого пользователя заявки по данному мероприятию нет -
        выводится HTTP_404_NOT_FOUND.
        """
        application = EventApplications.objects.filter(
            user=request.user, event__id=event_pk
        ).first()
        if application is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = EventApplicationsSerializer(application,
                                                 context={'request': request})
        return Response(serializer.data)


class EventParticipantsViewSet(ListRetrieveDestroyViewSet):
    """Представление участников мероприятия.

    Доступ:
        - удаление: фигурирующий в записи пользователь или
                    юзер из модели организаторов мероприятий;
        - чтение: только для пользователей из модели
                  организаторов мероприятий.
    """
    queryset = EventParticipants.objects.all()
    serializer_class = EventParticipantsSerializer
    permission_classes = (permissions.IsAuthenticated, IsEventOrganizer)

    def get_queryset(self):
        queryset = super().get_queryset()
        event_pk = self.kwargs.get('event_pk')
        if event_pk is not None:
            queryset = queryset.filter(event__id=event_pk)
        return queryset

    def get_permissions(self):
        if self.action == 'destroy':
            return [permissions.IsAuthenticated(), IsApplicantOrOrganizer()]
        return super().get_permissions()

    @action(detail=False,
            methods=['get'],
            url_path='me',
            serializer_class=EventParticipantsSerializer,
            permission_classes=(permissions.IsAuthenticated,))
    @swagger_auto_schema(responses=participant_me_response)
    def me(self, request, event_pk):
        """Action для получения всей информации по профилю участника
        мероприятия.

        Доступен всем авторизованным пользователям.

        Если текущий пользователь не участвует в мероприятии -
        выводится HTTP_404_NOT_FOUND.
        """
        user_profile = EventParticipants.objects.filter(
            user=request.user, event__id=event_pk
        ).first()
        if user_profile is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = EventParticipantsSerializer(user_profile)
        return Response(serializer.data)


@swagger_auto_schema(method='POST', request_body=AnswerSerializer(many=True))
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_answers(request, event_pk):
    """Сохранение ответов на вопросы мероприятия.

    Доступ - все авторизованные.
    """
    event = get_object_or_404(Event, pk=event_pk)
    user = request.user
    questions = event.additional_issues.all()
    serializer = AnswerSerializer(data=request.data,
                                  many=True,
                                  context={'event': event,
                                           'request': request})
    serializer.is_valid(raise_exception=True)
    answers_to_create = []
    for answer_data in request.data:
        issue_id = answer_data.get('issue')
        answer_text = answer_data.get('answer')
        issue_instance = questions.get(id=issue_id)
        answer_to_create = EventIssueAnswer(
            event=event,
            user=user,
            issue=issue_instance,
            answer=answer_text
        )
        answers_to_create.append(answer_to_create)

    EventIssueAnswer.objects.bulk_create(answers_to_create)

    return Response(status=status.HTTP_201_CREATED)


class AnswerDetailViewSet(RetrieveUpdateViewSet):
    """Поштучное получение, изменение и удаление ответов
    в индивидуальных заявках на мероприятие.

    Доступ:
        - удаление - только пользователи из модели организаторов;
        - редактирование - автор записи (только если заявка еще не принята)
          либо пользователи из модели организаторов.
        - чтение - автор заявки, либо пользователи из модели организаторов.
    """
    queryset = EventIssueAnswer.objects.all()
    serializer_class = AnswerSerializer
    permission_classes = (permissions.IsAuthenticated, IsApplicantOrOrganizer)

    def get_permissions(self):
        if self.action == 'destroy':
            return [permissions.IsAuthenticated(), IsEventOrganizer()]
        if (self.action in ['update', 'partial_update'] and
                self.request.user.is_authenticated):
            if not EventApplications.objects.filter(
                event_id=self.kwargs.get('event_pk'),
                user=self.request.user
            ).exists():
                return [permissions.IsAuthenticated(), IsEventOrganizer()]
        return super().get_permissions()

    @swagger_auto_schema(responses=answer_response)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @action(detail=False,
            methods=['get'],
            url_path='me',
            serializer_class=AnswerSerializer,
            permission_classes=(permissions.IsAuthenticated,))
    @swagger_auto_schema(responses=answer_response)
    def me(self, request, event_pk):
        """Action для получения сохраненных ответов пользователя по
        текущему мероприятию.

        Доступен всем авторизованным пользователям.

        Если текущий пользователь не имеет сохраненных ответов -
        возвращается пустой массив.
        """
        user_documents = EventIssueAnswer.objects.filter(
            user=request.user, event__id=event_pk
        ).all()
        serializer = AnswerSerializer(user_documents,
                                      many=True,
                                      context={'request': request})
        return Response(serializer.data)


class EventUserDocumentViewSet(CreateRetrieveUpdateViewSet):
    """Представление сохраненных документов пользователя (сканов).

    Доступ:
        - создание(загрузка) только авторизованные пользователи;
        - чтение/редактирование/удаление только пользователи
          из модели организаторов мероприятий.
    """
    queryset = EventUserDocument.objects.all()
    serializer_class = EventUserDocumentSerializer
    permission_classes = (permissions.IsAuthenticated, IsEventOrganizer)

    def get_queryset(self):
        queryset = super().get_queryset()
        event_pk = self.kwargs.get('event_pk')
        if event_pk is not None:
            queryset = queryset.filter(event__id=event_pk)
        return queryset

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated()]
        if (self.action in ['update', 'partial_update'] and
                self.request.user.is_authenticated):
            if EventApplications.objects.filter(
                event_id=self.kwargs.get('event_pk'),
                user=self.request.user
            ).exists():
                return [permissions.IsAuthenticated(),
                        IsApplicantOrOrganizer()]
        if self.action == 'retrieve':
            return [permissions.IsAuthenticated(), IsApplicantOrOrganizer()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        """Сохранение скана документа пользователя.

        Доступ - только авторизованные пользователи.
        Принимает только файл.
        """
        event_pk = self.kwargs.get('event_pk')
        user = request.user
        event = get_object_or_404(Event, pk=event_pk)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(event=event, user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False,
            methods=['get'],
            url_path='me',
            serializer_class=EventUserDocumentSerializer,
            permission_classes=(permissions.IsAuthenticated,))
    def me(self, request, event_pk):
        """Action для получения загруженных документов пользователя
        текущего мероприятия.

        Доступен всем авторизованным пользователям.

        Если текущий пользователь не загружал документы -
        возвращается пустой массив.
        """
        user_documents = EventUserDocument.objects.filter(
            user=request.user, event__id=event_pk
        ).all()
        serializer = EventUserDocumentSerializer(user_documents, many=True)
        return Response(serializer.data)


class MultiEventViewSet(CreateListRetrieveDestroyViewSet):
    """Вьюсет для многоэтапной заявки на мероприятие.

    GET(list): Выводит список подвластных структурных единиц
               доступных к подаче в заявке.
    GET(retrieve): Выводит одну структурную единицу из заявки (по pk).
    POST(create): Создает заявку на мероприятие.
    DELETE(destroy): Удаляет одну структурную единицу из заявки (по pk).
    """
    _STRUCTURAL_MAPPING = {
        'Центральные штабы': ShortCentralHeadquarterSerializerME,
        'Окружные штабы': ShortDistrictHeadquarterSerializerME,
        'Региональные штабы': ShortRegionalHeadquarterSerializerME,
        'Местные штабы': ShortLocalHeadquarterSerializerME,
        'Образовательные штабы': ShortEducationalHeadquarterSerializerME,
        'Отряды': ShortDetachmentSerializerME
    }
    serializer_class = MultiEventApplicationSerializer
    queryset = MultiEventApplication.objects.all()
    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == 'list':
            event_pk = self.kwargs.get('event_pk')
            event = get_object_or_404(Event, pk=event_pk)
            return self._STRUCTURAL_MAPPING.get(
                event.available_structural_units
            )
        return super().get_serializer_class()

    def get_queryset(self):
        event_pk = self.kwargs.get('event_pk')
        event = get_object_or_404(Event, pk=event_pk)
        if self.action == 'list':
            return self.get_serializer_class().Meta.model.objects.filter(
                commander=self.request.user
            )
        return MultiEventApplication.objects.filter(event=event)

    def get_permissions(self):
        if self.action == 'list' or self.action == 'create':
            return [
                permissions.IsAuthenticated(), IsCommander()
            ]
        if self.action == 'destroy' or self.action == 'retrieve':
            return [
                permissions.IsAuthenticated(), IsAuthorMultiEventApplication()
            ]
        return super().get_permissions()

    def list(self, request, *args, **kwargs):
        """Выводит список подвластных структурных единиц
        доступных к подаче в заявке.

        Доступ:
            - только командир структурной единицы, типу которых
              разрешена подача заявок.
            - командир должен быть верифицирован.
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
            request_body=MultiEventApplicationSerializer(many=True)
    )
    def create(self, request, event_pk, *args, **kwargs):
        """Создание многоэтапной заявки на мероприятие.

        Принимает список со структурными единицами. Формат:
        ```
        [
            {
                "название_одной_из_структурных_единиц": id,
                "emblem": эмблема структурной единицы (необязательное поле),
                "participants_count": members_count
            },
            ...
        ]
        ```
        Доступ:
            - только командир структурной единицы, типу которых
              разрешена подача заявок.

        Дубли и структурные единицы без хотя бы одного участника игнорируются.
        """
        event = get_object_or_404(Event, id=event_pk)
        if MultiEventApplication.objects.filter(
            event=event, organizer_id=request.user.id
        ).exists():
            raise serializers.ValidationError(
                'Вы уже подали заявку на участие в этом мероприятии.'
            )

        data_set = []
        for item in request.data:
            if item in data_set:
                continue
            if item.get('participants_count') == 0:
                continue
            data_set.append(item)

        total_participants = sum(
           int(item.get('participants_count', 0)) for item in data_set
        )

        if (event.participants_number and
                total_participants > event.participants_number):
            raise serializers.ValidationError(
                'Общее количество поданых участников превышает общее'
                'разрешенное количество участников мероприятя.'
            )

        serializer = self.get_serializer(data=data_set,
                                         many=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save(event=event,
                            organizer_id=request.user.id,
                            is_approved=False)
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False,
            methods=['get'],
            url_path='me',
            serializer_class=MultiEventApplicationSerializer,
            permission_classes=(permissions.IsAuthenticated,))
    def me(self, request, event_pk):
        """Выводит список структурных единиц, поданных текущим пользователем
        в многоэтапной заявке на мероприятие.

        Доступ:
            - все авторизованные пользователи.
        """
        queryset = self.get_queryset().filter(organizer_id=request.user.id)
        if not len(queryset):
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False,
            methods=['delete'],
            url_path='me/delete',
            serializer_class=MultiEventApplicationSerializer,
            permission_classes=(permissions.IsAuthenticated,))
    def delete_me_application(self, request, event_pk):
        """Удаление многоэтапной заявки на мероприятие поданной
        текущим пользователем.

        Доступ:
            - все авторизованные пользователи.
        """
        queryset = self.get_queryset().filter(organizer_id=request.user.id)
        if not len(queryset):
            return Response(status=status.HTTP_404_NOT_FOUND)
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            methods=['delete'],
            url_path=r'delete/(?P<organizer_id>\d+)',
            serializer_class=MultiEventApplicationSerializer,
            permission_classes=(permissions.IsAuthenticated, IsEventOrganizer))
    def delete_all_applications(self, request, event_pk, organizer_id):
        """Удаление многоэтапной заявки на мероприятие поданной
        пользователем, id которого был передан в эндпоинте.

        Доступ:
            - пользователи из модели организаторов мероприятий.
        """
        queryset = self.get_queryset().filter(organizer_id=organizer_id)
        if not len(queryset):
            return Response(status=status.HTTP_404_NOT_FOUND)
        queryset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={})
    )
    @action(detail=False,
            methods=['post'],
            url_path=r'confirm/(?P<organizer_id>\d+)',
            serializer_class=MultiEventApplicationSerializer,
            permission_classes=(permissions.IsAuthenticated, IsEventOrganizer))
    def confirm(self, request, event_pk, organizer_id):
        """Подтверждение многоэтапной заявки на мероприятие поданной
        пользователем, id которого был передан в эндпоинте.

        Доступ:
            - пользователи из модели организаторов мероприятий.
        """
        queryset = self.get_queryset().filter(organizer_id=organizer_id)
        if not len(queryset):
            return Response({"error": "Заявка не найдена"},
                            status=status.HTTP_404_NOT_FOUND)
        queryset = queryset.filter(
            is_approved=False
        )
        if not len(queryset):
            return Response({"message": "Заявка уже подтверждена"},
                            status=status.HTTP_400_BAD_REQUEST)
        queryset.update(is_approved=True)
        return Response(status=status.HTTP_201_CREATED)

    @swagger_auto_schema(method='POST',
                         request_body=MultiEventParticipantsSerializer(
                             many=True))
    @action(detail=False,
            methods=['get', 'post'],
            url_path='compile_lists',
            serializer_class=MultiEventParticipantsSerializer,
            permission_classes=(permissions.IsAuthenticated,))
    def compile_lists(self, request, event_pk):
        """Action для формирования списков участников мероприятия.

        GET():Выводит список бойцов структурных единиц из одобренной
              заявки на мероприятие.
        POST(): Заносит полученных пользователей в бд как участников
                мероприятия, дополнительно удаляя заявку на многоэтапное
                мероприятие.

        Доступ:
            - чтение - все авторизованные. Если пользователь не имеет
              заявки на мероприятие - выводится HTTP_404_NOT_FOUND.
            - запись - все авторизованные. Если пользователь не имеет
              подтвержденной заявки на мероприятие - выводится
              HTTP_404_NOT_FOUND.
        """
        queryset = self.get_queryset().filter(organizer_id=request.user.id)
        if not len(queryset):
            return Response({'error': 'Заявка не существует'},
                            status=status.HTTP_404_NOT_FOUND)
        queryset = queryset.filter(is_approved=True)
        if not len(queryset):
            return Response({'error': 'Ваша заявка еще не подтверждена'},
                            status=status.HTTP_404_NOT_FOUND)

        if request.method == 'POST':
            event = get_object_or_404(Event, pk=event_pk)
            serializer = MultiEventParticipantsSerializer(
                data=request.data,
                many=True
            )
            serializer.is_valid(raise_exception=True)
            participants_to_create = []
            for participant in serializer.data:
                participants_to_create.append(
                    EventParticipants(
                        user_id=participant.get('user'),
                        event_id=event_pk
                    )
                )
            if not len(participants_to_create):
                return Response(
                    {'message': 'Нужно подать хотя бы 1 участника'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            available_participants = (event.participants_number
                                      - event.event_participants.count())
            if len(participants_to_create) > (available_participants):
                return Response(
                    {'message': f'Слишком много участников, в мероприятии '
                                f'осталось {available_participants} мест'},
                    status=status.HTTP_200_OK
                )
            try:
                with transaction.atomic():
                    EventParticipants.objects.bulk_create(
                        participants_to_create
                    )
                    queryset.delete()
            except Exception as e:
                return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_201_CREATED)

        central_headquarter_members = (
            queryset.filter(central_headquarter__isnull=False)
                    .values_list('central_headquarter__members__user__id',
                                 flat=True)
        )
        district_headquarter_members = (
            queryset.filter(district_headquarter__isnull=False)
                    .values_list('district_headquarter__members__user__id',
                                 flat=True)
        )
        regional_headquarter_members = (
            queryset.filter(regional_headquarter__isnull=False)
                    .values_list('regional_headquarter__members__user__id',
                                 flat=True)
        )
        local_headquarter_members = (
            queryset.filter(local_headquarter__isnull=False)
                    .values_list('local_headquarter__members__user__id',
                                 flat=True)
        )
        educational_headquarter_members = (
            queryset.filter(educational_headquarter__isnull=False)
                    .values_list('educational_headquarter__members__user__id',
                                 flat=True)
        )
        detachment_members = (
            queryset.filter(detachment__isnull=False)
                    .values_list('detachment__members__user__id',
                                 flat=True)
        )
        all_members_ids = set(itertools.chain(
            central_headquarter_members,
            district_headquarter_members,
            regional_headquarter_members,
            local_headquarter_members,
            educational_headquarter_members,
            detachment_members
        ))
        users_already_participating = EventParticipants.objects.filter(
            event__id=event_pk
        )
        if users_already_participating.exists():
            all_members_ids = list(
                all_members_ids -
                set(users_already_participating.values_list('user', flat=True))
            )
        all_members = RSOUser.objects.filter(id__in=all_members_ids,
                                             is_verified=True)
        if not len(all_members) or all_members is None:
            return Response(
                {"error":
                    "В поданых структурных единицах нет доступных бойцов. "
                    "Возможно они уже участники этого мероприятия"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = ShortUserSerializer(all_members, many=True)
        return Response(serializer.data)

    @action(detail=False,
            methods=['get'],
            url_path=r'detail/(?P<organizer_id>\d+)',
            permission_classes=(permissions.IsAuthenticated, IsEventOrganizer))
    def get_detail(self, request, event_pk, organizer_id):
        """Выводит список структурных единиц, поданных пользователем
        (id которого равен organizer_id) в многоэтапную заявку на мероприятие.

        Доступ:
            - пользователи из модели организаторов мероприятий.
        """
        queryset = self.get_queryset().filter(organizer_id=organizer_id)
        if not len(queryset):
            return Response({'error': 'Заявка не существует'},
                            status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False,
            methods=['get'],
            url_path='all',
            serializer_class=ShortMultiEventApplicationSerializer,
            permission_classes=(permissions.IsAuthenticated, IsEventOrganizer))
    def all_applications(self, request, event_pk):
        """Выводит список новых заявок по этому эвенту.

        Выводит новые заявки и заявки по которым заявители
        еще не сформировали списки.

        Доступ:
            - пользователи из модели организаторов мероприятий.
        """
        queryset = self.get_queryset()
        if not len(queryset):
            return Response({'message': 'Заявок пока нет'},
                            status=status.HTTP_200_OK)
        users = RSOUser.objects.filter(
            id__in=queryset.values_list('organizer_id', flat=True)
        ).all()
        event = get_object_or_404(Event, pk=event_pk)
        headquarter_model = self._STRUCTURAL_MAPPING.get(
                event.available_structural_units
            ).Meta.model
        serializer = self.get_serializer(
            users,
            context={'headquarter_model': headquarter_model},
            many=True
        )
        return Response(serializer.data)


class CompetitionViewSet(viewsets.ModelViewSet):
    """Представление конкурсов.

    Доступ:
        - чтение: все пользователи
        - запись/удаление/редактирование: только администраторы
    """
    queryset = Competitions.objects.all()
    serializer_class = CompetitionSerializer
    permission_classes = (permissions.IsAdminUser,)

    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            return (permissions.AllowAny(),)
        return super().get_permissions()

    def get_detachment(self):
        """
        Возвращает отряд, созданный после 25 января 2024 года
        """
        return Detachment.objects.filter(
            Q(founding_date__lt=date(*settings.DATE_JUNIOR_SQUAD))
            & Q(commander=self.request.user)
        ).first()

    def get_free_junior_detachments_ids(self):
        """
        Возвращает список ID младших отрядов, которые
        не подали заявки или не участвуют в текущем конкурсе.
        """
        competition_id = self.get_object().id
        in_applications_junior_detachment_ids = list(
            CompetitionApplications.objects.filter(
                competition__id=competition_id
                ).values_list(
                'junior_detachment__id', flat=True
            )
        )
        participants_junior_detachment_ids = list(
            CompetitionParticipants.objects.filter(
                competition__id=competition_id
                ).values_list(
                'junior_detachment__id', flat=True
            )
        )
        return list(Detachment.objects.exclude(
                id__in=in_applications_junior_detachment_ids
                + participants_junior_detachment_ids
            ).values_list('id', flat=True)
        )

    def get_junior_detachments(self):
        """
        Возвращает экземпляры свободных младших отрядов.
        """
        user_detachment = self.get_detachment()
        if not user_detachment:
            return None
        free_junior_detachments_ids = (
            self.get_free_junior_detachments_ids()
        )
        detachments = Detachment.objects.filter(
            Q(founding_date__gte=date(*settings.DATE_JUNIOR_SQUAD)) &
            Q(region=user_detachment.region) &
            Q(id__in=free_junior_detachments_ids)
        )
        return detachments

    @action(detail=True,
            methods=['get'],
            url_path='junour_detachments',
            permission_classes=(permissions.IsAuthenticated,))
    @swagger_auto_schema(responses=response_junior_detachments)
    def junior_detachments(self, request, pk):
        """Action для получения списка младших отрядов.

        Выводит свободные младшие отряды этого региона доступные к
        подаче в тандем заявку.

        Доступ - только авторизированные пользователи.
        Если юзер не командир старшего отряда - возвращает пустой массив.
        """
        junior_detachments = self.get_junior_detachments()
        serializer = ShortDetachmentSerializer(
            junior_detachments, many=True
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True,
            methods=['get'],
            url_path='check_detachment_status',
            permission_classes=(permissions.IsAuthenticated,))
    def status(self, request, pk):
        """Action для получения статуса отряда пользователя в конкурсе.

        Доступ:
            - только командиры отрядов.

        Если отряд участвует в конкурсе - возвращает "Вы участник".
        Если отряд не участвует в конкурсе - возвращает "Еще не участвуете".
        Если отряд подал заявку на конкурс - возвращает
            "Заявка на рассмотрении".
        """
        detachment = Detachment.objects.filter(
            commander=request.user
        ).first()
        if not detachment:
            return Response(
                {'error': 'Пользователь не командир отряда'},
                status=status.HTTP_403_FORBIDDEN
            )
        if CompetitionApplications.objects.filter(
            Q(junior_detachment=detachment) |
            Q(detachment=detachment)
        ).exists():
            return Response(
                {'status': 'Заявка на рассмотрении'},
                status=status.HTTP_200_OK
            )
        if CompetitionParticipants.objects.filter(
            Q(junior_detachment=detachment) |
            Q(detachment=detachment)
        ).exists():
            return Response(
                {'status': 'Вы участник'},
                status=status.HTTP_200_OK
            )
        return Response(
            {'status': 'Еще не участвуете'},
            status=status.HTTP_200_OK
        )

    @staticmethod
    def download_file_competitions(filepath, filename):
        if os.path.exists(filepath):
            with open(filepath, 'rb') as file:
                response = HttpResponse(
                    file.read(), content_type='application/pdf'
                )
                response['Content-Disposition'] = (
                    f'attachment; filename="{filename}"'
                )
                return response
        else:
            return Response(
                {'detail': 'Файл не найден.'},
                status=status.HTTP_204_NO_CONTENT
            )

    @action(
        detail=False,
        methods=('get',),
        url_path='download_regulation_file',
        permission_classes=(permissions.AllowAny,)
    )
    def download_regulation_file(self, request):
        """Скачивание положения конкурса РСО.

        Доступ - все пользователи.
        """
        filename = 'Regulation_on_the_best_LSO_2024.pdf'
        filepath = str(BASE_DIR) + '/templates/competitions/' + filename
        return self.download_file_competitions(filepath, filename)


class CompetitionApplicationsViewSet(viewsets.ModelViewSet):
    """Представление заявок на конкурс.

    Доступ:
        - чтение(list) - региональный командир или админ.
          В первом случае выводятся заявки этого региона,
          во втором - все заявки.
        - чтение(retrieve) - региональный командир, админ или
          один из отрядов этой заявки.
        - удаление - региональный командир, админ или один из
          отрядов этой заявки.
        - обновление - только командир младшего отряда,
          изменить можно только поле is_confirmed_by_junior
          (функционал подтверждения заявки младшим отрядом).
    """
    queryset = CompetitionApplications.objects.all()
    serializer_class = CompetitionApplicationsSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        if self.action == 'list':
            regional_headquarter = RegionalHeadquarter.objects.filter(
                commander=self.request.user
            )
            if regional_headquarter:
                user_region = regional_headquarter.first().region
                return CompetitionApplications.objects.filter(
                    junior_detachment__region=user_region
                )
            return CompetitionApplications.objects.filter(
                competition_id=self.kwargs.get('competition_pk')
            )
        return CompetitionApplications.objects.filter(
            competition_id=self.kwargs.get('competition_pk')
        )

    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'list':
            return CompetitionApplicationsObjectSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action == 'destroy' or self.action == 'retrieve':
            return [permissions.IsAuthenticated(),
                    IsRegionalCommanderOrAdminOrAuthor()]
        if self.action == 'list':
            return [permissions.IsAuthenticated(),
                    IsRegionalCommanderOrAdmin()]
        return super().get_permissions()

    def get_detachment(self, user):
        """Возвращает отряд, в котором юзер командир.

        Если юзер не командир, то возвращает None
        """
        try:
            detachment = Detachment.objects.get(commander=user)
            return detachment
        except Detachment.DoesNotExist:
            return None
        except Detachment.MultipleObjectsReturned:
            return Response({'error':
                             'Пользователь командир нескольких отрядов'},
                            status=status.HTTP_400_BAD_REQUEST)

    def get_junior_detachment(self, request_data):
        if 'junior_detachment' in request_data:
            return get_object_or_404(Detachment,
                                     id=request_data['junior_detachment'])

    @swagger_auto_schema(
        request_body=response_create_application
    )
    def create(self, request, *args, **kwargs):
        """Создание заявки в конкурс

        Если передается junior_detachment: id, то создается заявка-тандем,
        если нет - индивидуальная заявка.

        Доступ - только командир отряда.
        """
        current_detachment = self.get_detachment(request.user)
        if current_detachment is None:
            return Response({'error': 'Пользователь не является командиром'},
                            status=status.HTTP_400_BAD_REQUEST)

        MIN_DATE = (f'{settings.DATE_JUNIOR_SQUAD[2]}'
                    f'.{settings.DATE_JUNIOR_SQUAD[1]}.'
                    f'{settings.DATE_JUNIOR_SQUAD[0]} года')
        if current_detachment.founding_date < date(
            *settings.DATE_JUNIOR_SQUAD
        ):
            detachment = current_detachment
            junior_detachment = self.get_junior_detachment(request.data)
        else:
            if 'junior_detachment' in request.data:
                return Response(
                    {'error': f'- дата основания отряда позднее {MIN_DATE}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            junior_detachment = current_detachment
            detachment = None
        competition = get_object_or_404(Competitions,
                                        pk=self.kwargs.get('competition_pk'))

        serializer = self.get_serializer(
            data=request.data,
            context={'detachment': detachment,
                     'junior_detachment': junior_detachment,
                     'competition': competition,
                     'request': request})
        if serializer.is_valid(raise_exception=True):
            serializer.save(competition=competition,
                            detachment=detachment,
                            junior_detachment=junior_detachment,
                            is_confirmed_by_junior=False)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def is_commander_of_junior_detachment(self, user, instance):
        junior_detachment = instance.junior_detachment
        if not junior_detachment:
            return False
        return user == junior_detachment.commander

    def handle_junior_detachment_update(self, request, instance):
        if self.is_commander_of_junior_detachment(request.user, instance):
            data = {
                'is_confirmed_by_junior':
                request.data.get('is_confirmed_by_junior')
            }
            serializer = self.get_serializer(instance,
                                             data=data,
                                             partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        else:
            return Response({'error': 'Доступ запрещен'},
                            status=status.HTTP_403_FORBIDDEN)

    @swagger_auto_schema(
        request_body=request_update_application
    )
    def update(self, request, *args, **kwargs):
        """Изменение заявки на мероприятие

        Изменить можно только поле is_confirmed_by_junior.
        Доступ - только командир младшего отряда.
        """
        instance = self.get_object()
        return self.handle_junior_detachment_update(request, instance)

    @swagger_auto_schema(
        request_body=request_update_application
    )
    def partial_update(self, request, *args, **kwargs):
        """Изменение заявки на мероприятие

        Изменить можно только поле is_confirmed_by_junior.
        Доступ - только командир младшего отряда.
        """
        instance = self.get_object()
        return self.handle_junior_detachment_update(request, instance)

    @action(detail=False,
            methods=['get'],
            url_path='me',
            permission_classes=[permissions.IsAuthenticated])
    @swagger_auto_schema(responses=response_competitions_applications)
    def me(self, request, *args, **kwargs):
        """Получение заявки на мероприятие отряда текущего пользователя.

        Доступ - все авторизованные пользователи.
        Если пользователь не является командиром отряда, либо
        у его отряда нет заявки на участие - запрос вернет ошибку 404.
        """
        detachment = self.get_detachment(request.user)
        application = self.get_queryset().filter(
            Q(detachment=detachment) | Q(junior_detachment=detachment)
        ).first()
        if application is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = CompetitionApplicationsObjectSerializer(
            application,
            context={'request': request}
        )
        return Response(serializer.data)

    @action(detail=True,
            methods=['post'],
            url_path='confirm',
            permission_classes=(permissions.IsAuthenticated,
                                IsRegionalCommanderOrAdmin,))
    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
    ))
    def confirm(self, request, *args, **kwargs):
        """Подтверждение заявки на участие в мероприятии и создание участника.

        После подтверждения заявка удаляется.
        Доступ: администраторы и командиры региональных штабов.
        """
        instance = self.get_object()
        serializer = CompetitionParticipantsSerializer(
            data=request.data,
            context={'request': request,
                     'application': instance}
        )
        serializer.is_valid(raise_exception=True)
        try:
            with transaction.atomic():
                serializer.save(detachment=instance.detachment,
                                junior_detachment=instance.junior_detachment,
                                competition=instance.competition)
                instance.delete()
        except Exception as e:
            return Response(str(e), status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_201_CREATED)

    @action(detail=False,
            methods=['get'],
            url_path='all',
            permission_classes=(permissions.AllowAny,))
    def all(self, request, *args, **kwargs):
        """Получение всех не верифицированных заявок на участие в конкурсе.

        Доступ: любой пользователь.
        """
        queryset = self.get_queryset()
        serializer = CompetitionApplicationsObjectSerializer(
            queryset,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class CompetitionParticipantsViewSet(ListRetrieveDestroyViewSet):
    """ Вью сет для участников мероприятия.

    Доступ:
        - чтение: все
        - удаление: только админы и командиры региональных штабов.
    """
    queryset = CompetitionParticipants.objects.all()
    serializer_class = CompetitionParticipantsSerializer
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        return CompetitionParticipants.objects.filter(
            competition_id=self.kwargs.get('competition_pk')
        )

    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'list':
            return CompetitionParticipantsObjectSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action == 'destroy':
            return [permissions.IsAuthenticated(),
                    IsRegionalCommanderOrAdmin()]
        return super().get_permissions()

    def get_detachment(self, user):
        """Возвращает отряд, в котором юзер командир.

        Если юзер не командир, то возвращает None
        """
        try:
            detachment = Detachment.objects.get(commander=user)
            return detachment
        except Detachment.DoesNotExist:
            return None
        except Detachment.MultipleObjectsReturned:
            return Response({'error':
                             'Пользователь командир нескольких отрядов'},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False,
            methods=['get'],
            url_path='me',
            permission_classes=(permissions.IsAuthenticated,))
    @swagger_auto_schema(responses=response_competitions_participants)
    def me(self, request, *args, **kwargs):
        """Action для получения всей информации по верифицированной заявке.

        Доступен всем авторизованным пользователям.

        Если текущий пользователь не является командиром,
        или его отряд не участвует в мероприятии -
        выводится HTTP_404_NOT_FOUND.
        """
        detachment = self.get_detachment(request.user)
        participant_unit = self.get_queryset().filter(
            Q(detachment=detachment) | Q(junior_detachment=detachment)
        ).first()
        if participant_unit is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = CompetitionParticipantsObjectSerializer(participant_unit)
        return Response(serializer.data)
