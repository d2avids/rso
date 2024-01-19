from datetime import date
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.response import Response
from rest_framework import filters
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from events.models import Сompetition, СompetitionApplications, СompetitionParticipants
from events.serializers import (
    СompetitionSerializer,
    СompetitionApplicationsSerializer, СompetitionParticipantsSerializer
)
from api.serializers import ShortDetachmentSerializer
from api.permissions import IsRegionalCommander, IsLocalCommander
from api.mixins import CreateListRetrieveDestroyViewSet, ListRetrieveDestroyViewSet
from api.swagger_schemas import (
    request_update_application, response_create_application,
    response_competitions_applications, response_competitions_participants,
    response_start_page_competitions
)
from headquarters.models import Detachment


class CompetitionViewSet(viewsets.ModelViewSet):
    queryset = Сompetition.objects.all()
    serializer_class = СompetitionSerializer
    permission_classes = (permissions.IsAuthenticated,) # TODO: change to AdminOnly for creation...

    def get_junior_detachments(self):
        detachments = Detachment.objects.filter(
            founding_date__gte=date(2023, 1, 25)
        )
        return detachments

    def get_detachment(self):
        user = self.request.user
        return Detachment.objects.filter(
            Q(founding_date__lt=date(2023, 1, 25))
            & Q(commander=user)
        ).first()

    def get_application_info(self, detachment):
        _STATUS_MAPPING = {
            True: 'Ждет верификации',
            False: 'Ждет подтверждения младшего отряда',
        }
        application = СompetitionApplications.objects.filter(
            detachment=detachment
        ).first()
        if not application:
            return None, False
        application_status = _STATUS_MAPPING.get(
            application.is_confirmed_by_junior
        )
        is_application = True if application else False
        return application_status, is_application

    def get_is_participant(self, detachment):
        return СompetitionParticipants.objects.filter(
            detachment=detachment
        ).exists()

    @action(detail=True,
            methods=['get'],
            url_path='start_page',
            permission_classes=(permissions.AllowAny,))
    @swagger_auto_schema(responses=response_start_page_competitions)
    def start_page(self, request, *args, **kwargs):
        """Action для получения всей информации для страницы конкурса

        Доступ - все пользователи.

        Для снижения нагрузки на БД вывод дробный:
        - если пользователь не авторизован, вернется `{'is_auth': False}`.

        - если пользователь не командир старого отряда, вернется
        `{'is_auth': True,
        'is_commander_and_not_junior': False}`.

        - если пользователь уже участвует в конкурсе, вернется
        `{'is_auth': True,
        'is_commander_and_not_junior': True,
        'is_participant': True}`.

        В остальных случаях вернется полный комплект строк.
        """
        user = request.user
        if not user.is_authenticated:
            return Response(
                {'is_auth': False},
                status=status.HTTP_200_OK
            )
        detachment = self.get_detachment()
        if not detachment:
            return Response(
                {'is_auth': True,
                 'is_commander_and_not_junior': False},
                status=status.HTTP_200_OK
            )

        is_participant = self.get_is_participant(detachment)
        if is_participant:
            return Response(
                {'is_auth': True,
                 'is_commander_and_not_junior': True,
                 'is_participant': True},
                status=status.HTTP_200_OK
            )
        application_status, is_application = self.get_application_info(
            detachment
        )
        junior_detachments = self.get_junior_detachments()
        serializer = ShortDetachmentSerializer(
            junior_detachments, many=True
        )
        return Response(
            {
                'is_auth': True,
                'is_commander_and_not_junior': True,
                'is_participant': is_participant,
                'is_application': is_application,
                'application_status': application_status,
                'detachment_list': serializer.data
            },
            status=status.HTTP_200_OK
        )


class CompetitionApplicationsViewSet(viewsets.ModelViewSet):
    queryset = СompetitionApplications.objects.all()
    serializer_class = СompetitionApplicationsSerializer
    permission_classes = (permissions.IsAuthenticated,)
    # TODO: чтение поставить только админам + кто подтверждать будет(уточнить регионы).
    # TODO: на удаление дописать, что может командир любого отряда из заявки (отказ)

    def get_queryset(self):
        return СompetitionApplications.objects.filter(
            competition_id=self.kwargs.get('competition_pk')
        )

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
        """Создание заявки на мероприятие

        Если передается junior_detachment: id, то создается заявка-тандем,
        если нет - индивидуальная заявка.

        Доступ - только командир старшего отряда, созданного ранее 25.01.2023.
        """
        detachment = self.get_detachment(request.user)
        competition = get_object_or_404(Сompetition,
                                        pk=self.kwargs.get('competition_pk'))
        if detachment is None:
            return Response({'error': 'Пользователь не является командиром'},
                            status=status.HTTP_400_BAD_REQUEST)
        junior_detachment = self.get_junior_detachment(request.data)
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
    def me(self, request, competition_pk):
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
        serializer = СompetitionApplicationsSerializer(
            application,
            context={'request': request}
        )
        return Response(serializer.data)

    @action(detail=True,
            methods=['post'],
            url_path='confirm',
            serializer_class=СompetitionParticipantsSerializer,
            permission_classes=(permissions.IsAuthenticated,))  # TODO: Добавить пермишены админы и регионы
    def confirm(self, request, *args, **kwargs):
        """Подтверждение заявки на участие в мероприятии и создание участника.

        После подтверждения заявка удаляется.
        Доступ - ??? админы и регионы?
        """
        instance = self.get_object()
        serializer = СompetitionParticipantsSerializer(
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
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class СompetitionParticipantsViewSet(ListRetrieveDestroyViewSet): # Заменить на чтение и удаление
    queryset = СompetitionParticipants.objects.all()
    serializer_class = СompetitionParticipantsSerializer
    permission_classes = (permissions.IsAuthenticated,)
    # TODO: Поставить пермишены гет-все.
    # TODO: Удаление - только админы и командиры отрядов.(надо отрядам вообще?)

    def get_queryset(self):
        return СompetitionParticipants.objects.filter(
            competition_id=self.kwargs.get('competition_pk')
        )

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
            serializer_class=СompetitionParticipantsSerializer,
            permission_classes=(permissions.IsAuthenticated,))
    @swagger_auto_schema(responses=response_competitions_participants)
    def me(self, request, competition_pk):
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
        serializer = СompetitionParticipantsSerializer(participant_unit)
        return Response(serializer.data)
