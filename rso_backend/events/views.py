import itertools

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, permissions
from rest_framework import serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from api import constants

from api.serializers import EventParticipantsSerializer, ShortUserSerializer
from events.models import Event, EventParticipants, MultiEventApplication
from events.serializers import (
    MultiEventParticipantsSerializer, ShortCentralHeadquarterSerializer, ShortDetachmentSerializer,
    ShortDistrictHeadquarterSerializer, ShortLocalHeadquarterSerializer,
    ShortRegionalHeadquarterSerializer, ShortEducationalHeadquarterSerializer,
    MultiEventApplicationSerializer
)
from headquarters.models import (
    CentralHeadquarter, Detachment, DistrictHeadquarter,
    EducationalHeadquarter, LocalHeadquarter, RegionalHeadquarter
)
from api.mixins import CreateListRetrieveDestroyViewSet
from users.models import RSOUser


class MultiEventViewSet(CreateListRetrieveDestroyViewSet):
    """Вьюсет для многоэтапной заявки на мероприятие.

    GET(list): Выводит список подвластных структурных единиц
               доступных к подаче в заявке.
    GET(retrieve): Выводит одну структурную единицу из заявки (по pk).
    POST(create): Создает заявку на мероприятие.
    DELETE(destroy): Удаляет одну структурную единицу из заявки (по pk).
    """
    _STRUCTURAL_MAPPING = {
        'central': ShortCentralHeadquarterSerializer,
        'districts': ShortDistrictHeadquarterSerializer,
        'regionals': ShortRegionalHeadquarterSerializer,
        'locals': ShortLocalHeadquarterSerializer,
        'educationals': ShortEducationalHeadquarterSerializer,
        'detachments': ShortDetachmentSerializer
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

    def list(self, request, *args, **kwargs):
        """Выводит список подвластных структурных единиц
        доступных к подаче в заявке.

        Доступ:
            - только командир структурной единицы, типу которых
              разрешена подача заявок.
        """
        queryset = self.get_queryset()
        if not len(queryset):  # TODO: перенести в пермишн)
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=MultiEventApplicationSerializer(many=True))
    def create(self, request, event_pk, *args, **kwargs):
        """Создание многоэтапной заявки на мероприятие.

        Принимает список с структурными единицами. Формат:
        ```
        [
            {
                "название_одной_из_структурных_единиц": id,
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
            permission_classes=(permissions.IsAuthenticated,)) # TODO: поменять на пермишн организатора
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
            permission_classes=(permissions.IsAuthenticated,)) # TODO: поменять на пермишн организатора
    def confirm(self, request, event_pk, organizer_id):
        """Подтверждение многоэтапной заявки на мероприятие поданной
        пользователем, id которого был передан в эндпоинте.

        Доступ:
            - пользователи из модели организаторов мероприятий.
        """
        queryset = self.get_queryset().filter(organizer_id=organizer_id)
        if not len(queryset):
            return Response(status=status.HTTP_404_NOT_FOUND)
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

        if request.method == 'POST':
            queryset = queryset.filter(is_approved=True)
            if not len(queryset):
                return Response({'error': 'Ваша заявка еще не подтверждена'},
                                status=status.HTTP_404_NOT_FOUND)
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
            try:
                with transaction.atomic():
                    EventParticipants.objects.bulk_create(participants_to_create)
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
        all_members = RSOUser.objects.filter(id__in=all_members_ids)
        if not len(all_members) or all_members is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = ShortUserSerializer(all_members, many=True)
        return Response(serializer.data)
