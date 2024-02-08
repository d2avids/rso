import mimetypes
import os
import zipfile

from dal import autocomplete
from django.db.models import Q
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from api.mixins import RetrieveViewSet
from api.permissions import IsCommanderOrTrustedAnywhere, IsStuffOrAuthor
from api.tasks import send_reset_password_email_without_user
from api.utils import download_file, get_user
from rso_backend.settings import BASE_DIR
from users.filters import RSOUserFilter
from users.models import (RSOUser, UserDocuments, UserEducation,
                          UserForeignDocuments, UserMedia, UserParent,
                          UserPrivacySettings, UserProfessionalEducation,
                          UserRegion, UserStatementDocuments,
                          UserVerificationRequest)
from users.serializers import (EmailSerializer, ForeignUserDocumentsSerializer,
                               ProfessionalEductionSerializer,
                               RSOUserSerializer, UserCommanderSerializer,
                               UserDocumentsSerializer,
                               UserEducationSerializer,
                               UserHeadquarterPositionSerializer,
                               UserMediaSerializer,
                               UserPrivacySettingsSerializer,
                               UserProfessionalEducationSerializer,
                               UserRegionSerializer, UsersParentSerializer,
                               UserStatementDocumentsSerializer,
                               UserTrustedSerializer)


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
    - date_of_birth,
    - region.
    """

    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    search_fields = ('username', 'first_name', 'last_name', 'patronymic_name')
    filterset_class = RSOUserFilter
    ordering_fields = ('last_name')

    @action(
            methods=['post'],
            detail=False,
            permission_classes=(permissions.AllowAny,),
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
    """

    queryset = RSOUser.objects.all()
    serializer_class = RSOUserSerializer
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
    permission_classes = (permissions.IsAuthenticated, IsStuffOrAuthor,)
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
    permission_classes = (permissions.IsAuthenticated, IsStuffOrAuthor,)

    def get_object(self):
        return get_object_or_404(UserDocuments, user=self.request.user)


class ForeignUserDocumentsViewSet(BaseUserViewSet):
    """Представляет документы иностранного пользователя."""

    queryset = UserForeignDocuments.objects.all()
    serializer_class = ForeignUserDocumentsSerializer
    permission_classes = (permissions.IsAuthenticated, IsStuffOrAuthor,)

    def get_object(self):
        return get_object_or_404(UserForeignDocuments, user=self.request.user)


class UserRegionViewSet(BaseUserViewSet):
    """Представляет информацию о проживании пользователя."""

    queryset = UserRegion.objects.all()
    serializer_class = UserRegionSerializer
    permission_classes = (permissions.IsAuthenticated, IsStuffOrAuthor,)

    def get_object(self):
        return get_object_or_404(UserRegion, user=self.request.user)


class UserPrivacySettingsViewSet(BaseUserViewSet):
    """Представляет настройки приватности пользователя."""

    queryset = UserPrivacySettings.objects.all()
    serializer_class = UserPrivacySettingsSerializer
    permission_classes = (permissions.IsAuthenticated, IsStuffOrAuthor,)

    def get_object(self):
        return get_object_or_404(UserPrivacySettings, user=self.request.user)


class UserMediaViewSet(BaseUserViewSet):
    """Представляет медиа-данные пользователя."""

    queryset = UserMedia.objects.all()
    serializer_class = UserMediaSerializer
    permission_classes = (permissions.IsAuthenticated, IsStuffOrAuthor,)

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
    permission_classes = (permissions.IsAuthenticated, IsStuffOrAuthor,)

    def get_object(self):
        return get_object_or_404(UserParent, user=self.request.user)


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


class UserAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = RSOUser.objects.all()

        if self.q:
            qs = qs.filter(
                Q(username__icontains=self.q) |
                Q(first_name__icontains=self.q) |
                Q(last_name__icontains=self.q) |
                Q(patronymic_name__icontains=self.q)
            )
        return qs