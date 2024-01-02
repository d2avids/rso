from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import mixins, viewsets, permissions, serializers, status
from .models import Event, EventApplications, EventIssueAnswer
from .serializers import (
    AnswerSerializer, EventApplicationsSerializer,
    EventApplicationsCreateSerializer
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
        user = request.user
        event_pk = self.kwargs.get('event_pk')
        event = get_object_or_404(Event, pk=event_pk)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(event=event, user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_update(self, serializer):
        is_owner = self.request.user == serializer.instance.event.author
        if is_owner:
            serializer.save()
        else:
            raise serializers.ValidationError(
                "У вас нет прав на обновление поля is_approved."
            )

    def get_permissions(self): # раскомментить, когда будут написаны пермишены
        # read_only_actions = ['list', 'retrieve', 'partial_update']
        # if self.action in read_only_actions:
        #     # Доступ только для автора мероприятия
        #     return [permissions.IsAuthenticated(), IsEventAuthor()]
        # elif self.action == 'destroy':
        #     # Доступ для автора заявки или организатора мероприятия
        #     return [permissions.IsAuthenticated(),
        #             IsApplicationAuthorOrEventOrganizer()]
        # else:
        return super().get_permissions()

    @action(detail=True,
            methods=['get', 'post'],
            url_path='answers',
            serializer_class=AnswerSerializer)
    def answers(self, request, event_pk, pk):
        application = get_object_or_404(EventApplications, id=pk)
        event = get_object_or_404(Event, id=event_pk)
        questions = event.additional_issues.all()

        if request.method == 'POST':
            answers_to_create = [
                EventIssueAnswer(application=application,
                                 issue=question,
                                 answer=request.data.get(question.id))
                for question in questions
                if request.data.get(question.id) is not None
            ]
            EventIssueAnswer.objects.bulk_create(answers_to_create)

            return Response(status=status.HTTP_201_CREATED)
        else:
            answers = EventIssueAnswer.objects.filter(application=application)
            serializer = AnswerSerializer(answers, many=True)
            return Response(serializer.data)
