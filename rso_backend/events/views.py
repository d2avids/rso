from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import mixins, viewsets, permissions, status
from .models import (
    Event, EventApplications, EventIssueAnswer, EventParticipants
)
from .serializers import (
    AnswerSerializer, EventApplicationsSerializer,
    EventApplicationsCreateSerializer, EventParticipantsSerializer
)


class EventApplicationsViewSet(mixins.ListModelMixin,
                               mixins.CreateModelMixin,
                               mixins.RetrieveModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):
    queryset = EventApplications.objects.all()
    serializer_class = EventApplicationsSerializer
    permission_classes = (permissions.IsAuthenticated,)

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

    def create(self, request, *args, **kwargs):
        """ Создание заявки на участие в мероприятии. """
        user = request.user
        event_pk = self.kwargs.get('event_pk')
        event = get_object_or_404(Event, pk=event_pk)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(event=event, user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,
            methods=['post'],
            url_path='confirm',
            serializer_class=EventParticipantsSerializer)
    # дописать пермишн на Организатор мероприятия
    def confirm(self, request, *args, **kwargs):
        """
        Подтверждение заявки на участие в мероприятии и создание участника.
        После подтверждения заявка удаляется.
        Доступен только для организаторов мероприятия.
        Если пользователь уже участвует в мероприятии,
        выводится предупреждение.
        """
        instance = self.get_object()
        serializer = EventParticipantsSerializer(data=request.data,
                                                 context={'request': request})
        serializer.is_valid(raise_exception=True)
        with transaction.atomic():
            serializer.save(user=instance.user, event=instance.event)
            instance.delete()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # раскомментить, когда будут написаны пермишены
    def get_permissions(self): # раскомментить, когда будут написаны пермишены
        # read_only_actions = ['list', 'retrieve']
        # if self.action in read_only_actions:
        #     # Доступ только для автора мероприятия
        #     return [permissions.IsAuthenticated(), IsEventAuthor()]
        # elif self.action == 'destroy':
        #     # Доступ для автора заявки или организатора мероприятия
        #     return [permissions.IsAuthenticated(),
        #             IsApplicationAuthorOrEventOrganizer()]
        # else:
        return super().get_permissions()


class EventParticipantsViewSet(mixins.ListModelMixin,
                               mixins.RetrieveModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):
    """ Представление участников мероприятия. """
    queryset = EventParticipants.objects.all()
    serializer_class = EventParticipantsSerializer
    # дописать пермишн доступ только организаторам мероприятия, на удаление + участник (только свою)
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        """ Получение участников конкретного мероприятия. """
        queryset = super().get_queryset()
        event_pk = self.kwargs.get('event_pk')
        if event_pk is not None:
            queryset = queryset.filter(event__id=event_pk)
        return queryset
