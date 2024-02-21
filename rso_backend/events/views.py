import itertools

from dal import autocomplete
from django.db import transaction
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, permissions, serializers, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from api.mixins import (CreateListRetrieveDestroyViewSet,
                        CreateRetrieveUpdateViewSet,
                        ListRetrieveDestroyViewSet,
                        RetrieveUpdateDestroyViewSet, RetrieveUpdateViewSet)
from api.permissions import (IsApplicantOrOrganizer,
                             IsAuthorMultiEventApplication, IsAuthorPermission,
                             IsCommander, IsDetachmentCommander,
                             IsDistrictCommander, IsEducationalCommander,
                             IsEventAuthor, IsEventOrganizer,
                             IsEventOrganizerOrAuthor, IsLocalCommander,
                             IsRegionalCommander, IsStuffOrCentralCommander,
                             IsVerifiedPermission)
from events.filters import EventFilter
from events.models import (Event, EventAdditionalIssue, EventApplications,
                           EventDocumentData, EventIssueAnswer,
                           EventOrganizationData, EventParticipants,
                           EventTimeData, EventUserDocument)
from events.serializers import (AnswerSerializer,
                                CreateMultiEventApplicationSerializer,
                                EventAdditionalIssueSerializer,
                                EventApplicationsCreateSerializer,
                                EventApplicationsSerializer,
                                EventDocumentDataSerializer,
                                EventOrganizerDataSerializer,
                                EventParticipantsSerializer, EventSerializer,
                                EventTimeDataSerializer,
                                EventUserDocumentSerializer,
                                MultiEventApplication,
                                MultiEventApplicationSerializer,
                                MultiEventParticipantsSerializer,
                                ShortCentralHeadquarterSerializerME,
                                ShortDetachmentSerializerME,
                                ShortDistrictHeadquarterSerializerME,
                                ShortEducationalHeadquarterSerializerME,
                                ShortLocalHeadquarterSerializerME,
                                ShortMultiEventApplicationSerializer,
                                ShortRegionalHeadquarterSerializerME)
from events.swagger_schemas import (EventSwaggerSerializer, answer_response,
                                    application_me_response,
                                    participant_me_response)
from users.models import RSOUser
from users.serializers import ShortUserSerializer


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
        permission_classes = [
            permissions.AllowAny
        ]
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
            permission_classes = [IsEventOrganizerOrAuthor]
        print(permission_classes)
        print('ПЕРМИШЕНЫ ВЫШЕ ------')
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


class EventApplicationsViewSet(CreateListRetrieveDestroyViewSet):
    """Представление заявок на участие в мероприятии.

    Доступ:
        - создание - авторизованные + верифицированные пользователи;
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

        Доступ: авторизованные + верифицированные пользователи из модели
        организаторов мероприятий и авторы заявок.
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
        application = get_object_or_404(EventApplications, pk=pk)
        answers = EventIssueAnswer.objects.filter(user=application.user,
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


class AnswerDetailViewSet(RetrieveUpdateDestroyViewSet):
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
            request_body=CreateMultiEventApplicationSerializer(many=True)
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
              разрешена подача заявок. Командир должен быть верифицирован.

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
                'Общее количество поданых участников превышает общее '
                'разрешенное количество участников мероприятя.'
            )

        serializer = CreateMultiEventApplicationSerializer(
            data=data_set,
            many=True
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save(event=event,
                            organizer_id=request.user.id,
                            is_approved=False)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
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


class EventAutoComplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Event.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs.order_by('name')

    def get_ordering(self):
        pass
