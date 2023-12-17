import mimetypes
import os
import zipfile

from django.db.models import Q
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from api.mixins import (CreateDeleteViewSet, ListRetrieveUpdateViewSet,
                        ListRetrieveViewSet)
from api.permissions import (IsStuffOrCentralCommander, IsStuffOrAuthor,
                             IsDistrictCommander, IsRegionalCommander,
                             IsLocalCommander, IsEducationalCommander,
                             IsDetachmentCommander)
from api.serializers import (CentralHeadquarterSerializer,
                             CentralPositionSerializer,
                             DetachmentPositionSerializer,
                             DetachmentSerializer,
                             DistrictHeadquarterSerializer,
                             DistrictPositionSerializer,
                             EducationalHeadquarterSerializer,
                             EducationalPositionSerializer,
                             LocalHeadquarterSerializer,
                             LocalPositionSerializer,
                             ProfessionalEductionSerializer,
                             RegionalHeadquarterSerializer,
                             RegionalPositionSerializer, RegionSerializer,
                             RSOUserSerializer,
                             UserDetachmentApplicationSerializer,
                             UserDocumentsSerializer, UserEducationSerializer,
                             UserMediaSerializer,
                             UserPrivacySettingsSerializer,
                             UserProfessionalEducationSerializer,
                             UserRegionSerializer, UsersParentSerializer,
                             UserStatementDocumentsSerializer,
                             ForeignUserDocumentsSerializer,
                             AreaSerializer)
from api.utils import (download_file,
                       get_headquarter_users_positions_queryset)
from headquarters.models import (CentralHeadquarter, Detachment,
                                 DistrictHeadquarter, EducationalHeadquarter,
                                 LocalHeadquarter, Region, RegionalHeadquarter,
                                 UserCentralHeadquarterPosition,
                                 UserDetachmentApplication,
                                 UserDetachmentPosition,
                                 UserDistrictHeadquarterPosition,
                                 UserEducationalHeadquarterPosition,
                                 UserLocalHeadquarterPosition,
                                 UserRegionalHeadquarterPosition, Area)
from rso_backend.settings import BASE_DIR
from users.models import (ProfessionalEduction, RSOUser, UserDocuments,
                          UserEducation, UserMedia, UserPrivacySettings,
                          UserRegion, UsersParent, UserStatementDocuments,
                          UserVerificationRequest, ForeignUserDocuments)


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
    permission_classes = [IsStuffOrAuthor,]

    def get_object(self):
        """Определяет instance для операций с объектом (get, upd, del)."""
        return get_object_or_404(UserEducation, user=self.request.user)


class UserProfessionalEducationViewSet(BaseUserViewSet):
    """Представляет профессиональную информацию пользователя.

    Дополнительные профобразования пользователя доступны по ключу
    'users_prof_educations'.
    """

    queryset = ProfessionalEduction.objects.all()
    permission_classes = [IsStuffOrAuthor,]

    def get_object(self):
        return ProfessionalEduction.objects.filter(
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

    queryset = ForeignUserDocuments.objects.all()
    serializer_class = ForeignUserDocumentsSerializer
    permission_classes = (IsStuffOrAuthor,)

    def get_object(self):
        return get_object_or_404(ForeignUserDocuments, user=self.request.user)


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

    queryset = UsersParent.objects.all()
    serializer_class = UsersParentSerializer
    permission_classes = (IsStuffOrAuthor,)

    def get_object(self):
        return get_object_or_404(UsersParent, user=self.request.user)


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


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def apply_for_verification(request):
    """Подать заявку на верификацию."""
    if request.method == 'POST':
        user = request.user
        UserVerificationRequest.objects.create(
            user=user
        )
        if request.user.is_verified:
            return Response(
                {'error': 'Пользователь не авторизован'},
                status=status.HTTP_403_FORBIDDEN
            )
        return Response(status=status.HTTP_201_CREATED)


@api_view(['POST', 'DELETE'])
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
def change_membership_fee_status(request, pk):
    """Изменить статус оплаты членского взноса пользователю."""
    user = get_object_or_404(RSOUser, id=pk)
    if request.method == 'POST':
        user.membership_fee = True
        user.save()
        return Response(status=status.HTTP_202_ACCEPTED)
    user.membership_fee = False
    user.save()
    return Response(status=status.HTTP_204_NO_CONTENT)
