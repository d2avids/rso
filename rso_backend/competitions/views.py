import os
from datetime import date

from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from api.mixins import ListRetrieveDestroyViewSet
from api.permissions import (
    IsCommanderAndCompetitionParticipant,
    IsCommanderDetachmentInParameterOrRegionalCommissioner,
    IsRegionalCommanderOrAdmin, IsRegionalCommanderOrAdminOrAuthor,
    IsRegionalCommissioner,
    IsRegionalCommissionerOrCommanderDetachmentWithVerif
)
from competitions.models import (
    CompetitionApplications, CompetitionParticipants, Competitions,
    ParticipationInAllRussianEvents,
    ParticipationInDistrAndInterregEvents, PrizePlacesInAllRussianEvents,
    PrizePlacesInAllRussianLaborProjects,
    PrizePlacesInDistrAndInterregEvents,
    PrizePlacesInDistrAndInterregLaborProjects, Q13EventOrganization,
    Q13DetachmentReport, Q13Ranking, Q13TandemRanking
)
from competitions.q_calculations import calculate_q13_place
from competitions.serializers import (
    CompetitionApplicationsObjectSerializer, CompetitionApplicationsSerializer,
    CompetitionParticipantsObjectSerializer, CompetitionParticipantsSerializer,
    CompetitionSerializer, ConfirmParticipationInAllRussianEventsSerializer,
    ConfirmParticipationInDistrictAndInterregionalEventsSerializer,
    ConfirmPrizePlacesInAllRussianEventsSerializer,
    ConfirmPrizePlacesInAllRussianLaborProjectsSerializer,
    ConfirmPrizePlacesInDistrAndInterregEventsSerializer,
    ConfirmPrizePlacesInDistrAndInterregLaborProjectsSerializer,
    CreateParticipationInAllRussianEventsSerializer,
    CreatePrizePlacesInAllRussianEventsSerializer,
    CreatePrizePlacesInAllRussianLaborProjectsSerializer,
    CreatePrizePlacesInDistrAndInterregEventsSerializer,
    CreatePrizePlacesInDistrAndInterregLaborProjectsSerializer,
    ParticipationInAllRussianEventsSerializer,
    CreateParticipationInDistrAndInterregEventsSerializer,
    ParticipationInDistrAndInterregEventsSerializer,
    PrizePlacesInAllRussianEventsSerializer,
    PrizePlacesInAllRussianLaborProjectsSerializer,
    PrizePlacesInDistrAndInterregEventsSerializer,
    PrizePlacesInDistrAndInterregLaborProjectsSerializer,
    ShortDetachmentCompetitionSerializer, Q13EventOrganizationSerializer,
    Q13DetachmentReportSerializer, Q18DetachmentReportSerializer
)
# сигналы ниже не удалять, иначе сломается
from competitions.signal_handlers import create_score_q7, create_score_q8
from competitions.swagger_schemas import (request_update_application,
                                          response_competitions_applications,
                                          response_competitions_participants,
                                          response_create_application,
                                          response_junior_detachments)
from headquarters.models import Detachment, RegionalHeadquarter
from rso_backend.settings import BASE_DIR


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
        ).values_list('id', flat=True))

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
        serializer = ShortDetachmentCompetitionSerializer(
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
        # except Detachment.DoesNotExist:
        #     return None
        except Exception:
            return None

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
        if detachment is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
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
    Поиск:
        - ключ для поиска: ?search
        - поле для поиска: name младшего отряда и отряда-наставника.
    """
    queryset = CompetitionParticipants.objects.all()
    serializer_class = CompetitionParticipantsSerializer
    permission_classes = (permissions.AllowAny,)
    filter_backends = (filters.SearchFilter, )
    search_fields = (
        'detachment__name',
        'junior_detachment__name'
    )

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
        if detachment is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        participant_unit = self.get_queryset().filter(
            Q(detachment=detachment) | Q(junior_detachment=detachment)
        ).first()
        if participant_unit is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = CompetitionParticipantsObjectSerializer(participant_unit)
        return Response(serializer.data)


class ParticipationInDistrictAndInterregionalEventsViewSet(
    viewsets.ModelViewSet
):
    """Вью сет для показателя 'Участие членов студенческого отряда в
    окружных и межрегиональных мероприятиях.'.

    Доступ:
        - чтение: Командир отряда из инстанса объекта к которому
                  нужен доступ, а также комиссары региональных штабов.
        - чтение(list): только комиссары региональных штабов.
        - изменение: Если заявка не подтверждена - командир отряда из
                     инстанса объекта который изменяют,
                     а также комиссары региональных штабов.
                     Если подтверждена - только комиссар регионального штаба.
        - удаление: Если заявка не подтверждена - командир отряда из
                    инстанса объекта который удаляют,
                    а также комиссары региональных штабов.
                    Если подтверждена - только комиссар регионального штаба.
    ! При редактировании нельзя изменять event_name.
    Поиск:
        - ключ для поиска: ?search
        - поле для поиска: id отряда и id конкурса.
    """
    queryset = ParticipationInDistrAndInterregEvents.objects.all()
    serializer_class = ParticipationInDistrAndInterregEventsSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        IsCommanderDetachmentInParameterOrRegionalCommissioner
    )
    filter_backends = (filters.SearchFilter, )
    search_fields = ('detachment__name', 'competition__name')

    def get_queryset(self):
        if self.action == 'list':
            regional_headquarter = (
                self.request.user.userregionalheadquarterposition.headquarter
            )
            return self.serializer_class.Meta.model.objects.filter(
                detachment__regional_headquarter=regional_headquarter,
                competition_id=self.kwargs.get('competition_pk')
            )
        if self.action == 'me':
            return self.serializer_class.Meta.model.objects.filter(
                detachment__commander=self.request.user,
                competition_id=self.kwargs.get('competition_pk')
            )
        return self.serializer_class.Meta.model.objects.filter(
            competition_id=self.kwargs.get('competition_pk')
        )

    def get_permissions(self):
        if self.action == 'retrieve':
            return [permissions.IsAuthenticated(),
                    IsCommanderDetachmentInParameterOrRegionalCommissioner()]
        if self.action == 'create':
            return [permissions.IsAuthenticated(),
                    IsCommanderAndCompetitionParticipant()]
        if self.action == 'list':
            return [permissions.IsAuthenticated(), IsRegionalCommissioner()]
        if self.action in ['update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(),
                    IsRegionalCommissionerOrCommanderDetachmentWithVerif()]
        return super().get_permissions()

    def get_competitions(self):
        return get_object_or_404(
            Competitions, id=self.kwargs.get('competition_pk')
        )

    def create(self, request, *args, **kwargs):
        """Action для создания отчета.

        Доступ: командиры отрядов, которые участвуют в конкурсе.
        'event_name' к передаче обязателен.
        """
        # TODO: как согласуем схему ответа, дописать event_name в сваггере как обязательный
        competition = self.get_competitions()
        detachment = get_object_or_404(
            Detachment, id=request.user.detachment_commander.id
        )
        serializer = CreateParticipationInDistrAndInterregEventsSerializer(
            data=request.data,
            context={'request': request,
                     'competition': competition,
                     'detachment': detachment})
        serializer.is_valid(raise_exception=True)
        serializer.save(competition=competition,
                        detachment=detachment,
                        is_verified=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True,
            methods=['post'],
            url_path='accept',
            permission_classes=(permissions.IsAuthenticated,
                                IsRegionalCommissioner,))
    @swagger_auto_schema(
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={})
    )
    def accept_report(self, request, competition_pk, pk, *args, **kwargs):
        """
        Action для верификации отчета рег. комиссаром.

        Принимает пустой POST запрос.
        """
        report = self.get_object()
        if report.is_verified:
            return Response({'error': 'Отчет уже подтвержден.'},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = (
            ConfirmParticipationInDistrictAndInterregionalEventsSerializer(
                report,
                data={'is_verified': True},
                context={'request': request},
                partial=True)
        )
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as error:
            return Response({'error': str(error)},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False,
            methods=['get'],
            url_path='me',
            permission_classes=(permissions.IsAuthenticated,))
    def me(self, request, competition_pk, *args, **kwargs):
        """
        Action для получения списка всех отчетов об участии
        в региональных и межрегиональных мероприятиях текущего пользователя.

        Доступ: все пользователи, кроме анонимов.
        Если пользователь не командир отряда, и у его отряда нет
        поданых отчетов, вернется пустой список.
        """
        return super().list(request, *args, **kwargs)


class ParticipationInAllRussianEventsViewSet(
    ParticipationInDistrictAndInterregionalEventsViewSet
):
    """Вью сет для показателя 'Участие членов студенческого отряда во
    всероссийских мероприятиях.'.

    Доступ:
        - чтение: Командир отряда из инстанса объекта к которому
                  нужен доступ, а также комиссары региональных штабов.
        - чтение(list): только комиссары региональных штабов.
        - изменение: Если заявка не подтверждена - командир отряда из
                     инстанса объекта который изменяют,
                     а также комиссары региональных штабов.
                     Если подтверждена - только комиссар регионального штаба.
        - удаление: Если заявка не подтверждена - командир отряда из
                    инстанса объекта который удаляют,
                    а также комиссары региональных штабов.
                    Если подтверждена - только комиссар регионального штаба.
    ! При редактировании нельзя изменять event_name.
    Поиск:
        - ключ для поиска: ?search
        - поле для поиска: id отряда и id конкурса.
    """
    queryset = ParticipationInAllRussianEvents.objects.all()
    serializer_class = ParticipationInAllRussianEventsSerializer

    def create(self, request, *args, **kwargs):
        """Action для создания отчета.

        Доступ: командиры отрядов, которые участвуют в конкурсе.
        'event_name' к передаче обязателен.
        """
        # TODO: как согласуем схему ответа, дописать event_name в сваггере как обязательный
        competition = get_object_or_404(
            Competitions, id=self.kwargs.get('competition_pk')
        )
        detachment = get_object_or_404(
            Detachment, id=request.user.detachment_commander.id
        )
        serializer = CreateParticipationInAllRussianEventsSerializer(
            data=request.data,
            context={'request': request,
                     'competition': competition,
                     'detachment': detachment})
        serializer.is_valid(raise_exception=True)
        serializer.save(competition=competition,
                        detachment=detachment,
                        is_verified=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True,
            methods=['post'],
            url_path='accept',
            permission_classes=(permissions.IsAuthenticated,
                                IsRegionalCommissioner,))
    @swagger_auto_schema(
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={})
    )
    def accept_report(self, request, competition_pk, pk, *args, **kwargs):
        """
        Action для верификации отчета рег. комиссаром.

        Принимает пустой POST запрос.
        """
        report = self.get_object()
        if report.is_verified:
            return Response({'error': 'Отчет уже подтвержден.'},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = (
            ConfirmParticipationInAllRussianEventsSerializer(
                report,
                data={'is_verified': True},
                context={'request': request},
                partial=True)
        )
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as error:
            return Response({'error': str(error)},
                            status=status.HTTP_400_BAD_REQUEST)


class PrizePlacesInDistrAndInterregEventsViewSet(
    ParticipationInDistrictAndInterregionalEventsViewSet
):
    """Вью сет для показателя 'Призовые места отряда в
    окружных и межрегиональных мероприятиях и конкурсах РСО.'.

    Доступ:
        - чтение: Командир отряда из инстанса объекта к которому
                  нужен доступ, а также комиссары региональных штабов.
        - чтение(list): только комиссары региональных штабов.
        - изменение: Если заявка не подтверждена - командир отряда из
                     инстанса объекта который изменяют,
                     а также комиссары региональных штабов.
                     Если подтверждена - только комиссар регионального штаба.
        - удаление: Если заявка не подтверждена - командир отряда из
                    инстанса объекта который удаляют,
                    а также комиссары региональных штабов.
                    Если подтверждена - только комиссар регионального штаба.
    ! При редактировании нельзя изменять event_name.
    Поиск:
        - ключ для поиска: ?search
        - поле для поиска: id отряда и id конкурса.
    """
    queryset = PrizePlacesInDistrAndInterregEvents.objects.all()
    serializer_class = PrizePlacesInDistrAndInterregEventsSerializer

    def create(self, request, *args, **kwargs):
        """Action для создания отчета.

        Доступ: командиры отрядов, которые участвуют в конкурсе.
        'event_name' к передаче обязателен.
        """
        # TODO: как согласуем схему ответа, дописать event_name в сваггере как обязательный
        competition = get_object_or_404(
            Competitions, id=self.kwargs.get('competition_pk')
        )
        detachment = get_object_or_404(
            Detachment, id=request.user.detachment_commander.id
        )
        serializer = CreatePrizePlacesInDistrAndInterregEventsSerializer(
            data=request.data,
            context={'request': request,
                     'competition': competition,
                     'detachment': detachment})
        serializer.is_valid(raise_exception=True)
        serializer.save(competition=competition,
                        detachment=detachment,
                        is_verified=False)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)

    @action(detail=True,
            methods=['post'],
            url_path='accept',
            permission_classes=(permissions.IsAuthenticated,
                                IsRegionalCommissioner,))
    @swagger_auto_schema(
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={})
    )
    def accept_report(self, request, competition_pk, pk, *args, **kwargs):
        """
        Action для верификации отчета рег. комиссаром.

        Принимает пустой POST запрос.
        """
        report = self.get_object()
        if report.is_verified:
            return Response({'error': 'Отчет уже подтвержден.'},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = (
            ConfirmPrizePlacesInDistrAndInterregEventsSerializer(
                report,
                data={'is_verified': True},
                context={'request': request},
                partial=True)
        )
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as error:
            return Response({'error': str(error)},
                            status=status.HTTP_400_BAD_REQUEST)


class PrizePlacesInAllRussianEventsViewSet(
    ParticipationInDistrictAndInterregionalEventsViewSet
):
    """Вью сет для показателя 'Призовые места отряда во
    всероссийских мероприятиях и конкурсах РСО.'.

    Доступ:
        - чтение: Командир отряда из инстанса объекта к которому
                  нужен доступ, а также комиссары региональных штабов.
        - чтение(list): только комиссары региональных штабов.
        - изменение: Если заявка не подтверждена - командир отряда из
                     инстанса объекта который изменяют,
                     а также комиссары региональных штабов.
                     Если подтверждена - только комиссар регионального штаба.
        - удаление: Если заявка не подтверждена - командир отряда из
                    инстанса объекта который удаляют,
                    а также комиссары региональных штабов.
                    Если подтверждена - только комиссар регионального штаба.
    ! При редактировании нельзя изменять event_name.
    Поиск:
        - ключ для поиска: ?search
        - поле для поиска: id отряда и id конкурса.
    """
    queryset = PrizePlacesInAllRussianEvents.objects.all()
    serializer_class = PrizePlacesInAllRussianEventsSerializer

    def create(self, request, *args, **kwargs):
        """Action для создания отчета.

        Доступ: командиры отрядов, которые участвуют в конкурсе.
        'event_name' к передаче обязателен.
        """
        # TODO: как согласуем схему ответа, дописать event_name в сваггере как обязательный
        competition = get_object_or_404(
            Competitions, id=self.kwargs.get('competition_pk')
        )
        detachment = get_object_or_404(
            Detachment, id=request.user.detachment_commander.id
        )
        serializer = CreatePrizePlacesInAllRussianEventsSerializer(
            data=request.data,
            context={'request': request,
                     'competition': competition,
                     'detachment': detachment})
        serializer.is_valid(raise_exception=True)
        serializer.save(competition=competition,
                        detachment=detachment,
                        is_verified=False)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)

    @action(detail=True,
            methods=['post'],
            url_path='accept',
            permission_classes=(permissions.IsAuthenticated,
                                IsRegionalCommissioner,))
    @swagger_auto_schema(
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={})
    )
    def accept_report(self, request, competition_pk, pk, *args, **kwargs):
        """
        Action для верификации отчета рег. комиссаром.

        Принимает пустой POST запрос.
        """
        report = self.get_object()
        if report.is_verified:
            return Response({'error': 'Отчет уже подтвержден.'},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = (
            ConfirmPrizePlacesInAllRussianEventsSerializer(
                report,
                data={'is_verified': True},
                context={'request': request},
                partial=True)
        )
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as error:
            return Response({'error': str(error)},
                            status=status.HTTP_400_BAD_REQUEST)


class PrizePlacesInDistrAndInterregLaborProjectsViewSet(
    ParticipationInDistrictAndInterregionalEventsViewSet
):
    """Вью сет для показателя 'Призовые места отряда в
    окружных и межрегиональных трудовых проектах'.

    Доступ:
        - чтение: Командир отряда из инстанса объекта к которому
                  нужен доступ, а также комиссары региональных штабов.
        - чтение(list): только комиссары региональных штабов.
        - изменение: Если заявка не подтверждена - командир отряда из
                     инстанса объекта который изменяют,
                     а также комиссары региональных штабов.
                     Если подтверждена - только комиссар регионального штаба.
        - удаление: Если заявка не подтверждена - командир отряда из
                    инстанса объекта который удаляют,
                    а также комиссары региональных штабов.
                    Если подтверждена - только комиссар регионального штаба.
    ! При редактировании нельзя изменять event_name.
    Поиск:
        - ключ для поиска: ?search
        - поле для поиска: id отряда и id конкурса.
    """
    queryset = PrizePlacesInDistrAndInterregLaborProjects.objects.all()
    serializer_class = PrizePlacesInDistrAndInterregLaborProjectsSerializer

    def create(self, request, *args, **kwargs):
        """Action для создания отчета.

        Доступ: командиры отрядов, которые участвуют в конкурсе.
        'event_name' к передаче обязателен.
        """
        # TODO: как согласуем схему ответа, дописать event_name в сваггере как обязательный
        competition = get_object_or_404(
            Competitions, id=self.kwargs.get('competition_pk')
        )
        detachment = get_object_or_404(
            Detachment, id=request.user.detachment_commander.id
        )
        serializer = (
            CreatePrizePlacesInDistrAndInterregLaborProjectsSerializer(
                data=request.data,
                context={'request': request,
                         'competition': competition,
                         'detachment': detachment})
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(competition=competition,
                        detachment=detachment,
                        is_verified=False)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)

    @action(detail=True,
            methods=['post'],
            url_path='accept',
            permission_classes=(permissions.IsAuthenticated,
                                IsRegionalCommissioner,))
    @swagger_auto_schema(
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={})
    )
    def accept_report(self, request, competition_pk, pk, *args, **kwargs):
        """
        Action для верификации отчета рег. комиссаром.

        Принимает пустой POST запрос.
        """
        report = self.get_object()
        if report.is_verified:
            return Response({'error': 'Отчет уже подтвержден.'},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = (
            ConfirmPrizePlacesInDistrAndInterregLaborProjectsSerializer(
                report,
                data={'is_verified': True},
                context={'request': request},
                partial=True)
        )
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as error:
            return Response({'error': str(error)},
                            status=status.HTTP_400_BAD_REQUEST)


class PrizePlacesInAllRussianLaborProjectsViewSet(
    ParticipationInDistrictAndInterregionalEventsViewSet
):
    """Вью сет для показателя 'Призовые места отряда во
    всероссийских трудовых проектах'.

    Доступ:
        - чтение: Командир отряда из инстанса объекта к которому
                  нужен доступ, а также комиссары региональных штабов.
        - чтение(list): только комиссары региональных штабов.
        - изменение: Если заявка не подтверждена - командир отряда из
                     инстанса объекта который изменяют,
                     а также комиссары региональных штабов.
                     Если подтверждена - только комиссар регионального штаба.
        - удаление: Если заявка не подтверждена - командир отряда из
                    инстанса объекта который удаляют,
                    а также комиссары региональных штабов.
                    Если подтверждена - только комиссар регионального штаба.
    ! При редактировании нельзя изменять event_name.
    Поиск:
        - ключ для поиска: ?search
        - поле для поиска: id отряда и id конкурса.
    """
    queryset = PrizePlacesInAllRussianLaborProjects.objects.all()
    serializer_class = PrizePlacesInAllRussianLaborProjectsSerializer

    def create(self, request, *args, **kwargs):
        """Action для создания отчета.

        Доступ: командиры отрядов, которые участвуют в конкурсе.
        'event_name' к передаче обязателен.
        """
        # TODO: как согласуем схему ответа, дописать event_name в сваггере как обязательный
        competition = get_object_or_404(
            Competitions, id=self.kwargs.get('competition_pk')
        )
        detachment = get_object_or_404(
            Detachment, id=request.user.detachment_commander.id
        )
        serializer = CreatePrizePlacesInAllRussianLaborProjectsSerializer(
            data=request.data,
            context={'request': request,
                     'competition': competition,
                     'detachment': detachment})
        serializer.is_valid(raise_exception=True)
        serializer.save(competition=competition,
                        detachment=detachment,
                        is_verified=False)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)

    @action(detail=True,
            methods=['post'],
            url_path='accept',
            permission_classes=(permissions.IsAuthenticated,
                                IsRegionalCommissioner,))
    @swagger_auto_schema(
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={})
    )
    def accept_report(self, request, competition_pk, pk, *args, **kwargs):
        """
        Action для верификации отчета рег. комиссаром.

        Принимает пустой POST запрос.
        """
        report = self.get_object()
        if report.is_verified:
            return Response({'error': 'Отчет уже подтвержден.'},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = (
            ConfirmPrizePlacesInAllRussianLaborProjectsSerializer(
                report,
                data={'is_verified': True},
                context={'request': request},
                partial=True)
        )
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as error:
            return Response({'error': str(error)},
                            status=status.HTTP_400_BAD_REQUEST)


class Q13DetachmentReportViewSet(viewsets.ModelViewSet):
    """Пример POST-запроса:
    ```
    {
      "organization_data": [
        {
          "event_type": "Спортивное",
          "event_link": "https://some-link.com"
        },
        {
          "event_type": "Волонтерское",
          "event_link": "https://some-link.com"
        }
      ]
    }
    ```
    """

    serializer_class = Q13DetachmentReportSerializer

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['organization_data'],
            properties={
                'organization_data': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    description="Список организованных мероприятий",
                    items=openapi.Items(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'event_type': openapi.Schema(
                                type=openapi.TYPE_STRING,
                                description="Тип мероприятия",
                                enum=[
                                    "Спортивное",
                                    "Волонтерское",
                                    "Интеллектуальное",
                                    "Творческое",
                                    "Внутреннее"
                                ]
                            ),
                            'event_link': openapi.Schema(
                                type=openapi.TYPE_STRING,
                                description="Ссылка на публикацию "
                                            "о мероприятии",
                                format='url'
                            )
                        }
                    )
                )
            }
        ),
    )
    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            organization_data = request.data.get('organization_data', [])
            competition = get_object_or_404(
                Competitions, id=self.kwargs.get('competition_pk')
            )
            detachment = get_object_or_404(
                Detachment, id=self.request.user.detachment_commander.id
            )
            report, created = Q13DetachmentReport.objects.get_or_create(
                competition_id=competition.id,
                detachment_id=detachment.id
            )

            for event_data in organization_data:
                event_serializer = Q13EventOrganizationSerializer(data=event_data)
                if event_serializer.is_valid(raise_exception=True):
                    Q13EventOrganization.objects.create(
                        **event_serializer.validated_data,
                        detachment_report=report
                    )
                else:
                    return Response(event_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response(self.get_serializer(report).data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    def get_queryset(self):
        competition = get_object_or_404(
            Competitions, id=self.kwargs.get('competition_pk')
        )
        return Q13DetachmentReport.objects.filter(
            competition_id=competition.id
        )

    def perform_create(self, serializer):
        competition = get_object_or_404(
            Competitions, id=self.kwargs.get('competition_pk')
        )
        detachment = get_object_or_404(
            Detachment, id=self.request.user.detachment_commander.id
        )
        serializer.save(competition=competition, detachment=detachment)

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='verify-event/(?P<event_id>\d+)'
    )
    def verify_event(self, request, pk=None, event_id=None):
        """
        Верифицирует конкретное мероприятие по его ID.
        """
        report = self.get_object()
        event = get_object_or_404(
            Q13EventOrganization,
            pk=event_id,
            detachment_report=report
        )
        if request.method == 'POST':
            event.is_verified = True
            event.save()
            participants_entry = CompetitionParticipants.objects.filter(
                junior_detachment=report.detachment
            ).first()

            # Подсчет места для индивидуальных и тандем участников:
            if participants_entry and not participants_entry.detachment:
                Q13Ranking.objects.get_or_create(
                    detachment=report.detachment,
                    place=calculate_q13_place(
                        Q13EventOrganization.objects.filter(
                            detachment_report=report
                        )
                    )
                )
            else:
                if participants_entry:
                    tandem_ranking = Q13TandemRanking.objects.get_or_create(
                        detachment=report.detachment,
                    )
                    tandem_ranking.place = calculate_q13_place(
                        Q13EventOrganization.objects.filter(
                            detachment_report=report
                        )
                    )
                    tandem_ranking.place += calculate_q13_place(
                        Q13EventOrganization.objects.filter(
                            tandem_ranking.junior_detachment.q13detachmentreport_detachment_reports
                        )
                    )
                else:
                    tandem_ranking = CompetitionParticipants.objects.filter(
                        junior_detachment=report.detachment
                    ).first()
                    tandem_ranking.place = calculate_q13_place(
                        Q13EventOrganization.objects.filter(
                            detachment_report=report
                        )
                    )
                    tandem_ranking.place = calculate_q13_place(
                        Q13EventOrganization.objects.filter(
                            detachment_report=tandem_ranking.detachment.q13detachmentreport_detachment_reports
                        )
                    )
            return Response(
                {"status": "Данные по организации "
                           "мероприятия верифицированы"},
                status=status.HTTP_200_OK
            )
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class Q18DetachmentReportViewSet(viewsets.ModelViewSet):
    serializer_class = Q18DetachmentReportSerializer

    def get_serializer_context(self):
        """
        Переопределение стандартного контекста,
        добавление competition и detachment.
        """
        context = super().get_serializer_context()
        competition_id = self.kwargs.get('competition_pk')
        detachment_id = self.request.user.detachment_commander.id
        context['competition'] = get_object_or_404(
            Competitions, id=competition_id
        )
        context['detachment'] = get_object_or_404(Detachment, id=detachment_id)
        return context

    def get_queryset(self):
        detachment_id = self.kwargs.get('detachment_pk')
        competition_id = self.kwargs.get('competition_pk')
        return Q13DetachmentReport.objects.filter(
            detachment_id=detachment_id,
            competition_id=competition_id
        )

    def perform_create(self, serializer):
        competition = get_object_or_404(
            Competitions, id=self.kwargs.get('competition_pk')
        )
        detachment = get_object_or_404(
            Detachment, id=self.kwargs.get('detachment_pk')
        )
        serializer.save(competition=competition, detachment=detachment)

    @action(
        detail=True,
        url_path='verify',
        methods=(['POST', 'DELETE']),
        permission_classes=[permissions.IsAuthenticated]
    )
    def verify(self, *args, **kwargs):
        """Верификация отчета по показателю.

        Доступно только командиру РШ связанного с отрядом.
        Если отчет уже верифицирован, возвращается 400 Bad Request с описанием
        ошибки {"detail": "Данный отчет уже верифицирован"}.
        """
        detachment_report = self.get_object()
        if detachment_report.is_verified:
            return Response({
                'detail': 'Данный отчет уже верифицирован'
            }, status=status.HTTP_400_BAD_REQUEST)
        if self.request.method == 'POST':
            detachment_report.is_verified = True
            detachment_report.save()
            return Response(status=status.HTTP_201_CREATED)
        if self.request.method == 'DELETE':
            detachment_report.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
