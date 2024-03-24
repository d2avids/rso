import os
from datetime import date

from django.conf import settings
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.db import transaction
from django.db.models import Q
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response
from rest_framework.serializers import ListSerializer

from api.mixins import (
    CreateListRetrieveUpdateViewSet, ListRetrieveDestroyViewSet,
    RetrieveCreateViewSet, UpdateDestroyViewSet
)
from api.permissions import (
    IsCommanderAndCompetitionParticipant,
    IsCommanderDetachmentInParameterOrRegionalCommissioner,
    IsCompetitionParticipantAndCommander,
    IsRegionalCommanderOrAdmin, IsRegionalCommanderOrAdminOrAuthor,
    IsRegionalCommanderOrAuthor,
    IsRegionalCommissioner,
    IsRegionalCommissionerOrCommanderDetachmentWithVerif,
    IsDetachmentReportAuthor
)
from api.utils import get_detachment_start, get_detachment_tandem
from competitions.models import (
    Q10, Q11, Q12, Q7, Q8, Q9, CompetitionApplications,
    CompetitionParticipants, Competitions, Q10Report, Q11Report, Q12Report,
    Q13EventOrganization,
    Q13DetachmentReport, Q13Ranking, Q13TandemRanking, Q19Report, Q1Ranking,
    Q1TandemRanking, Q20Report, Q2DetachmentReport, Q2Ranking,
    Q2TandemRanking, Q7Report, Q18DetachmentReport,
    Q18TandemRanking, Q18Ranking, Q8Report, Q9Report, Q19Ranking,
    Q19TandemRanking
)
from competitions.q_calculations import calculate_q13_place, \
    calculate_q19_place
from competitions.serializers import (
    CompetitionApplicationsObjectSerializer, CompetitionApplicationsSerializer,
    CompetitionParticipantsObjectSerializer, CompetitionParticipantsSerializer,
    CompetitionSerializer, CreateQ10Serializer, CreateQ11Serializer,
    CreateQ12Serializer, CreateQ7Serializer, CreateQ8Serializer,
    CreateQ9Serializer, Q10ReportSerializer, Q10Serializer,
    Q11ReportSerializer, Q11Serializer, Q12ReportSerializer, Q12Serializer,
    Q19DetachmenrtReportSerializer, Q20ReportSerializer, Q2DetachmentReportSerializer, Q7ReportSerializer, Q7Serializer,
    Q8ReportSerializer, Q8Serializer, Q9ReportSerializer, Q9Serializer,
    ShortDetachmentCompetitionSerializer, Q13EventOrganizationSerializer,
    Q13DetachmentReportSerializer, Q18DetachmentReportSerializer
)
from competitions.utils import tandem_or_start
# сигналы ниже не удалять, иначе сломается
from competitions.signal_handlers import (
    create_score_q7, create_score_q8, create_score_q9, create_score_q10,
    create_score_q11, create_score_q12, create_score_q20
)
from competitions.swagger_schemas import (request_update_application,
                                          response_competitions_applications,
                                          response_competitions_participants,
                                          response_create_application,
                                          response_junior_detachments,
                                          q7schema_request, q9schema_request)
from headquarters.models import Detachment, RegionalHeadquarter, UserDetachmentPosition
from users.models import RSOUser


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
        filepath = str(settings.BASE_DIR) + '/templates/competitions/' + filename
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
    filter_backends = (filters.SearchFilter,)
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

    @action(detail=False,
            methods=['get'],
            url_path='status',
            permission_classes=(permissions.IsAuthenticated,))
    @swagger_auto_schema(responses={
        status.HTTP_200_OK: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'is_commander_detachment': openapi.Schema(
                    type=openapi.TYPE_BOOLEAN,
                    title='Является ли командиром отряда-участника конкурса',
                    read_only=True
                ),
                'is_commissar_detachment': openapi.Schema(
                    type=openapi.TYPE_BOOLEAN,
                    title='Является ли комиссаром отряда-участника конкурса',
                    read_only=True
                )
            }
            )
        })
    def status(self, request, competition_pk, *args, **kwargs):
        """Action для получения статуса пользователя в конкурсе.

        Доступ: все пользователи.
        """
        if self.get_queryset().filter(
            Q(detachment__commander=request.user) |
            Q(junior_detachment__commander=request.user)
        ).exists():
            return Response({
                'is_commander_detachment': True,
                'is_commissar_detachment': False
            })
        try:
            position = request.user.userdetachmentposition.position
        except UserDetachmentPosition.DoesNotExist:
            return Response({
                'is_commander_detachment': False,
                'is_commissar_detachment': False
            })
        if position.name == 'Комиссар':
            return Response({
                'is_commander_detachment': False,
                'is_commissar_detachment': True
            })
        return Response({
            'is_commander_detachment': False,
            'is_commissar_detachment': False
        })


@api_view(['GET'])
def get_place_q1(request, competition_pk):
    """Вью для показателя 'Численность членов линейного студенческого
    отряда в соответствии с объемом уплаченных членских взносов'.

    Место в рейтинге автоматически рассчитается 15 апреля 2024 года,
    до этого дня для участников будет выводится ошибка 400
    {'error': 'Рейтинг еще не сформирован'}.

    После 15 апреля, при запросе участником мероприятия будет
    возвращаться место в формате {'place': int}

    Для тандем заявки место для обоих участников будет одинаковым.

    Доступ: все авторизованные пользователи.
    Если пользователь не командир, либо не участвует в мероприятии -
    выводится ошибка 404.
    """
    if request.user.is_anonymous:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    detachment_start = get_detachment_start(
        request.user, competition_pk
    )
    if detachment_start is None:
        detachment_tandem = get_detachment_tandem(
            request.user, competition_pk
        )
        # Если командир, но не участник старт и не участник тандем
        if detachment_tandem is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if detachment_start:
            ranking_start = Q1Ranking.objects.filter(
                competition_id=competition_pk,
                detachment=detachment_start
            ).first()
            if ranking_start:
                return Response({'place': ranking_start.place})

        if detachment_tandem:
            ranking_tandem = Q1TandemRanking.objects.filter(
                Q(competition_id=competition_pk) &
                Q(junior_detachment=detachment_tandem) |
                Q(detachment=detachment_tandem)
            ).first()
            if ranking_tandem:
                return Response({'place': ranking_tandem.place})

    # Если отряд является участником конкурса, но нет рейтинга
    return Response({'error': 'Рейтинг еще не сформирован'},
                    status=status.HTTP_400_BAD_REQUEST)


class Q2DetachmentReportViewSet(viewsets.ModelViewSet):

    """
    Пример POST-запроса:
    {
    "commander_achievement": true,
    "commissioner_achievement": true,
    "commander_link": "https://some-link.com",
    "commissioner_link": "https://some-link.com"
    }

    Поля “Региональная школа командного состава пройдена командиром отряда”
    и “Региональная школа командного состава пройдена комиссаром отряда”
    обязательные.
    При выборе “Да” обязательным также становится поле
    “Ссылка на публикацию о прохождении школы командного состава”,
    так как прохождение обучения засчитывается только
    при предоставлении ссылки на документ.

    Командир выбрал “Да” + Комиссар выбрал “Да” - 1 место
    Командир выбрал “Да” + Комиссар выбрал “Нет” - 2 место
    Командир выбрал “Нет” + Комиссар выбрал “Да” - 2 место
    Командир выбрал “Нет” + Комиссар выбрал “Нет” - 3 место
    """

    PLACE_FIRST = 1
    PLACE_SECOND = 2

    serializer_class = Q2DetachmentReportSerializer

    def get_queryset(self):
        competition = get_object_or_404(
            Competitions, id=self.kwargs.get('competition_pk')
        )
        return Q2DetachmentReport.objects.filter(
            competition=competition
        )

    def create(self, request, *args, **kwargs):
        competition = get_object_or_404(
            Competitions, id=self.kwargs.get('competition_pk')
        )
        try:
            detachment = get_object_or_404(
                Detachment, id=request.user.detachment_commander.id
            )
        except Detachment.DoesNotExist:
            return Response(
                {'error': 'Заполнять данные может только командир отряда.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not CompetitionParticipants.objects.filter(
            competition=competition, detachment=detachment
        ).exists():
            if not CompetitionParticipants.objects.filter(
                competition=competition, junior_detachment=detachment
            ).exists():
                return Response(
                    {
                        'error': 'Ваш отряд не зарегистрирован'
                        ' как участник конкурса.'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
        if Q2DetachmentReport.objects.filter(
            competition=competition,
            detachment=detachment
        ).exists():
            return Response(
                {'error': 'Отчет уже был подан ранее.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        commander_achievement = request.data.get(
            'commander_achievement'
        )
        commissioner_achievement = request.data.get(
            'commissioner_achievement'
        )
        commander_link = request.data.get('commander_link')
        commissioner_link = request.data.get('commissioner_link')
        q2_data = {
                'commander_achievement': commander_achievement,
                'commissioner_achievement': commissioner_achievement,
                'commander_link': commander_link,
                'commissioner_link': commissioner_link
        }
        if (commander_achievement and not commander_link) or (
            commissioner_achievement and not commissioner_link
        ):
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={'error': 'Не указана подтверждающая ссылка.'}
            )
        serializer = Q2DetachmentReportSerializer(
            data=q2_data,
            context={
                'request': request,
                'competition': competition,
                'detachment': detachment,
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(
            competition=competition,
            detachment=detachment,
            is_verified=False
        )
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        event_org = self.get_object()
        if event_org.is_verified:
            return Response(
                {
                    'detail': 'Нельзя редактировать/удалять верифицированные '
                              'записи.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        event_org = self.get_object()
        if event_org.is_verified:
            return Response(
                {
                    'detail': 'Нельзя редактировать/удалять верифицированные '
                              'записи.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)

    @action(
            detail=True,
            methods=['get'],
            url_path='get-place',
            serializer_class=None
    )
    def get_place(self, request, *args, **kwargs):
        """Определение места по показателю.

        Возвращается место или статус показателя.
        Если показатель не был подан ранее, то возвращается код 400.
        """

        report = self.get_object()
        is_verified = report.is_verified
        is_tandem = tandem_or_start(
            competition=report.competition,
            detachment=report.detachment,
            competition_model=CompetitionParticipants
        )

        if not is_verified:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={'detail': 'Показатель в обработке.'}
            )
        tandem_ranking = Q2TandemRanking.objects.filter(
            detachment=report.detachment
        ).first()
        if not tandem_ranking:
            tandem_ranking = Q2TandemRanking.objects.filter(
                junior_detachment=report.detachment
            ).first()

        if is_tandem:
            if tandem_ranking and tandem_ranking.place is not None:
                return Response(
                    {"place": tandem_ranking.place},
                    status=status.HTTP_200_OK
                )
        else:
            ranking = Q2Ranking.objects.filter(
                detachment=report.detachment
            ).first()
            if ranking and ranking.place is not None:
                return Response(
                    {"place": ranking.place}, status=status.HTTP_200_OK
                )

        """
        Если показателей нет в таблицах Rankin, то вычисляем место,
        так, как будто у отряда личный результат.

        Ниже вычисляем индивидуальное место. Третье место заполняется
        по умолчанию.
        Если ни одно условие не выполнено, то место остается равным 3.
        """

        commander_achievment = report.commander_achievement
        commissioner_achievement = report.commissioner_achievement
        place = None
        if commander_achievment and commissioner_achievement:
            place = self.PLACE_FIRST
        if (
            commander_achievment and not commissioner_achievement
        ) or (
            not commander_achievment and commissioner_achievement
        ):
            place = self.PLACE_SECOND
        if place:
            report.individual_place = place
            report.save()

        return Response(
                status=status.HTTP_404_NOT_FOUND,
                data={'detail': 'Показатель в обработке.'}
            )

    @action(
            detail=True,
            methods=['post', 'delete'],
            serializer_class=None,
            # permissions=[IsRegionalCommanderOrAuthor, ] TODO: раскомментировать после мерджа в ветку пказателей
    )
    def verify(self, *args, **kwargs):
        """Верификация отчета по показателю.

        Доступно только командиру РШ связанного с отрядом.
        Если отчет уже верифицирован, возвращается 400 Bad Request с описанием
        ошибки `{"detail": "Данный отчет уже верифицирован"}`.
        При удалении отчета удаляются записи из таблиц Rankin и TandemRankin.
        """

        detachment_report = self.get_object()
        competition = detachment_report.competition
        detachment = detachment_report.detachment

        if self.request.method == 'DELETE':
            with transaction.atomic():
                try:
                    Q2Ranking.objects.get(
                        detachment=detachment,
                    ).delete()
                except Q2Ranking.DoesNotExist:
                    try:
                        Q2TandemRanking.objects.get(
                            detachment=detachment,
                        ).delete()
                    except Q2TandemRanking.DoesNotExist:
                        try:
                            Q2TandemRanking.objects.get(
                                junior_detachment=detachment,
                            ).delete()
                        except Q2TandemRanking.DoesNotExist:
                            pass
                detachment_report.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
        with transaction.atomic():
            if detachment_report.is_verified:
                return Response({
                    'detail': 'Данный отчет уже верифицирован'
                }, status=status.HTTP_400_BAD_REQUEST)

            detachment_report.is_verified = True
            detachment_report.save()

            """Расчет мест по показателю и запись в таблицы Ranking."""

            is_tandem = tandem_or_start(
                competition=competition,
                detachment=detachment,
                competition_model=CompetitionParticipants
            )
            if is_tandem:
                try:
                    partner_detachment = CompetitionParticipants.objects.get(
                        competition=competition,
                        detachment=detachment
                    ).junior_detachment
                    partner_is_junior = True
                except CompetitionParticipants.DoesNotExist:
                    partner_detachment = (
                        CompetitionParticipants.objects.filter(
                            competition=competition,
                            junior_detachment=detachment
                        ).first().detachment
                    )
                    partner_is_junior = False
                try:
                    partner_detahcment_report = (
                        Q2DetachmentReport.objects.filter(
                            competition=competition,
                            detachment=partner_detachment
                        ).first()
                    )
                except Q2DetachmentReport.DoesNotExist:
                    return Response(
                        status=status.HTTP_404_NOT_FOUND,
                        data={
                            'detail': 'Отряд-напарник не подал отчет'
                            ' по показателю.'
                        }
                    )
                place_1 = detachment_report.individual_place
                place_2 = partner_detahcment_report.individual_place
                result_place = (place_1 + place_2)/2
                if partner_is_junior:
                    Q2TandemRanking.objects.create(
                        detachment=detachment,
                        junior_detachment=partner_detachment,
                        place=result_place
                    )
                else:
                    Q2TandemRanking.objects.create(
                        detachment=partner_detachment,
                        junior_detachment=detachment,
                        place=result_place
                    )
                return Response(
                    status=status.HTTP_201_CREATED,
                    data={
                        'detail': 'Отчет верифицирован, '
                        f'место - {result_place}.'
                    }
                )
            else:
                Q2Ranking.objects.create(
                    detachment=detachment,
                    place=detachment_report.individual_place
                )
                return Response(
                    status=status.HTTP_201_CREATED,
                    data={'detail': f'Отчет верифицирован, место - {place_1}.'}
                )


class Q7ViewSet(
    viewsets.ModelViewSet
):
    """Вью сет для показателя 'Участие членов студенческого отряда в
    окружных и межрегиональных мероприятиях.'.

    Доступ:
        - чтение: Командир отряда из инстанса объекта к которому
                  нужен доступ, а также комиссары региональных штабов.
        - чтение(list): только комиссары региональных штабов.
                        Выводятся заявки только его рег штаба.
        - изменение: Если заявка не подтверждена - командир отряда из
                     инстанса объекта который изменяют,
                     а также комиссары региональных штабов.
                     Если подтверждена - только комиссар регионального штаба.
        - удаление: Если заявка не подтверждена - командир отряда из
                    инстанса объекта который удаляют,
                    а также комиссары региональных штабов.
                    Если подтверждена - только комиссар регионального штаба.
    ! При редактировании нельзя изменять event_name.
    """
    serializer_class = Q7Serializer
    permission_classes = (
        permissions.IsAuthenticated,
        IsCommanderDetachmentInParameterOrRegionalCommissioner
    )

    def get_queryset(self):
        if self.action == 'list':
            regional_headquarter = (
                self.request.user.userregionalheadquarterposition.headquarter
            )
            return self.serializer_class.Meta.model.objects.filter(
                detachment_report__detachment__regional_headquarter=regional_headquarter,
                detachment_report__competition_id=self.kwargs.get('competition_pk')
            )
        if self.action == 'me':
            return self.serializer_class.Meta.model.objects.filter(
                detachment_report__detachment__commander=self.request.user,
                detachment_report__competition_id=self.kwargs.get('competition_pk')
            )
        return self.serializer_class.Meta.model.objects.filter(
            detachment_report__competition_id=self.kwargs.get('competition_pk')
        )

    def get_permissions(self):
        # if self.action == 'retrieve':
        #     return [permissions.IsAuthenticated(),
        #             IsCommanderDetachmentInParameterOrRegionalCommissioner()]
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

    def get_detachment(self, obj):
        return obj.detachment_report.detachment

    @swagger_auto_schema(
        # request_body=ListSerializer(child=CreateQ7Serializer()), # работает.
        request_body=q7schema_request,
        responses={201: Q7ReportSerializer}
    )
    def create(self, request, *args, **kwargs):
        """Action для создания отчета.

        Доступ: командиры отрядов, которые участвуют в конкурсе.
        'event_name' к передаче обязателен.
        """
        competition = self.get_competitions()
        detachment = get_object_or_404(
            Detachment, id=request.user.detachment_commander.id
        )
        detachment_report, _ = Q7Report.objects.get_or_create(
            detachment=detachment,
            competition=competition
        )
        for event in request.data:
            serializer = CreateQ7Serializer(
                data=event,
                context={'request': request,
                         'competition': competition,
                         'event': event,
                         'detachment_report': detachment_report},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(detachment_report=detachment_report,
                            is_verified=False)
        return Response(Q7ReportSerializer(detachment_report).data,
                        status=status.HTTP_201_CREATED)

    @action(detail=True,
            methods=['post', 'delete'],
            url_path='accept',
            permission_classes=(permissions.IsAuthenticated,
                                IsRegionalCommissioner,))
    @swagger_auto_schema(
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={},),
        responses={200: Q7Serializer}
    )
    def accept_report(self, request, competition_pk, pk, *args, **kwargs):
        """
        Action для верификации мероприятия рег. комиссаром.

        Принимает пустой POST запрос.
        Доступ: комиссары региональных штабов.
        """
        event = self.get_object()
        if event.is_verified:
            return Response({'error': 'Отчет уже подтвержден.'},
                            status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'POST':
            event.is_verified = True
            event.save()
            return Response(Q7Serializer(event).data,
                            status=status.HTTP_200_OK)
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            methods=['get'],
            url_path='me',
            permission_classes=(permissions.IsAuthenticated,))
    def me(self, request, competition_pk, *args, **kwargs):
        """
        Action для получения списка всех отчетов об участии
        в региональных и межрегиональных мероприятиях текущего пользователя.

        Доступ: все авторизованные пользователи.
        Если пользователь не командир отряда, и у его отряда нет
        поданных отчетов - вернется пустой список.
        """
        return super().list(request, *args, **kwargs)

    @action(detail=False,
            methods=['get'],
            url_path='get_place',
            permission_classes=(permissions.IsAuthenticated,
                                IsCommanderAndCompetitionParticipant))
    def get_place(self, request, competition_pk, *args, **kwargs):
        """
        Action для получения рейтинга по данному показателю.

        Доступ: командиры отрядов, которые участвуют в конкурсе.
        Если отчета еще не подан, вернется ошибка 404. (данные не отправлены)
        Если отчет подан, но еще не верифицировн - вернется
        {"place": "Показатель в обработке"}.
        Если отчет подан и верифицирован - вернется место в рейтинге:
        {"place": int}
        """
        detachment = request.user.detachment_commander
        report = self.serializer_class.Meta.model.objects.filter(
            detachment_report__detachment=detachment,
            detachment_report__competition_id=competition_pk
        ).first()
        if not report:
            # Отряд участник, но еще не подал отчет по данному показателю.
            return Response(status=status.HTTP_404_NOT_FOUND)
        class_name = self.serializer_class.Meta.model.__name__  # Q7
        ranking_fk = f'{class_name.lower()}ranking'  # q7ranking
        # Если есть FK на стартовый рейтинг
        ranking = getattr(detachment, ranking_fk).filter(
            competition_id=competition_pk
        ).first()
        if ranking:
            return Response(
                {"place": ranking.place}, status=status.HTTP_200_OK
            )
        #  Если нет, то ищем в тандем рейтингах
        tandem_ranking_fk = (
            f'{class_name.lower()}tandemranking_main_detachment'
        )
        # Если есть FK на наставника
        tandem_ranking = getattr(detachment, tandem_ranking_fk).filter(
            competition_id=competition_pk
        ).first()
        if tandem_ranking:
            return Response(
                {"place": tandem_ranking.place},
                status=status.HTTP_200_OK
            )
        tandem_ranking_fk = (
            f'{class_name.lower()}tandemranking_junior_detachment'
        )
        # Если есть FK на junior
        tandem_ranking = getattr(
            detachment, tandem_ranking_fk
            ).filter(competition_id=competition_pk).first()
        if tandem_ranking:
            return Response(
                {"place": tandem_ranking.place},
                status=status.HTTP_200_OK
            )
        # Отчет уже есть(проверяли в начале), значит еще не верифицировано ни одно мероприятие
        return Response(
            {"place": "Показатель в обработке"},
            status=status.HTTP_200_OK
        )


class Q8ViewSet(Q7ViewSet):
    """Вью сет для показателя 'Участие членов студенческого отряда во
    всероссийских мероприятиях.'.

    Доступ:
        - чтение: Командир отряда из инстанса объекта к которому
                  нужен доступ, а также комиссары региональных штабов.
        - чтение(list): только комиссары региональных штабов.
                        Выводятся заявки только его рег штаба.
        - изменение: Если заявка не подтверждена - командир отряда из
                     инстанса объекта который изменяют,
                     а также комиссары региональных штабов.
                     Если подтверждена - только комиссар регионального штаба.
        - удаление: Если заявка не подтверждена - командир отряда из
                    инстанса объекта который удаляют,
                    а также комиссары региональных штабов.
                    Если подтверждена - только комиссар регионального штаба.
    ! При редактировании нельзя изменять event_name.
    """
    queryset = Q8.objects.all()
    serializer_class = Q8Serializer

    @swagger_auto_schema(
        request_body=q7schema_request,
        responses={201: Q8ReportSerializer}
    )
    def create(self, request, *args, **kwargs):
        """Action для создания отчета.

        Доступ: командиры отрядов, которые участвуют в конкурсе.
        'event_name' к передаче обязателен.
        """
        competition = self.get_competitions()
        detachment = get_object_or_404(
            Detachment, id=request.user.detachment_commander.id
        )
        detachment_report, _ = Q8Report.objects.get_or_create(
            detachment=detachment,
            competition=competition
        )
        for event in request.data:
            serializer = CreateQ8Serializer(
                data=event,
                context={'request': request,
                         'competition': competition,
                         'event': event,
                         'detachment_report': detachment_report},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(detachment_report=detachment_report,
                            is_verified=False)
        return Response(Q8ReportSerializer(detachment_report).data,
                        status=status.HTTP_201_CREATED)

    @action(detail=True,
            methods=['post', 'delete'],
            url_path='accept',
            permission_classes=(permissions.IsAuthenticated,
                                IsRegionalCommissioner,))
    @swagger_auto_schema(
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={},),
        responses={200: Q8Serializer}
    )
    def accept_report(self, request, competition_pk, pk, *args, **kwargs):
        """
        Action для верификации мероприятия рег. комиссаром.

        Принимает пустой POST запрос.
        Доступ: комиссары региональных штабов.
        """
        event = self.get_object()
        if event.is_verified:
            return Response({'error': 'Отчет уже подтвержден.'},
                            status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'POST':
            event.is_verified = True
            event.save()
            return Response(Q8Serializer(event).data,
                            status=status.HTTP_200_OK)
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class Q9ViewSet(
    Q7ViewSet
):
    """Вью сет для показателя 'Призовые места отряда в
    окружных и межрегиональных мероприятиях и конкурсах РСО.'.

    Доступ:
        - чтение: Командир отряда из инстанса объекта к которому
                  нужен доступ, а также комиссары региональных штабов.
        - чтение(list): только комиссары региональных штабов.
                        Выводятся заявки только его рег штаба.
        - изменение: Если заявка не подтверждена - командир отряда из
                     инстанса объекта который изменяют,
                     а также комиссары региональных штабов.
                     Если подтверждена - только комиссар регионального штаба.
        - удаление: Если заявка не подтверждена - командир отряда из
                    инстанса объекта который удаляют,
                    а также комиссары региональных штабов.
                    Если подтверждена - только комиссар регионального штаба.
    ! При редактировании нельзя изменять event_name.
    """
    queryset = Q9.objects.all()
    serializer_class = Q9Serializer

    @swagger_auto_schema(
        request_body=q9schema_request,
        responses={201: Q9ReportSerializer}
    )
    def create(self, request, *args, **kwargs):
        """Action для создания отчета.

        Доступ: командиры отрядов, которые участвуют в конкурсе.
        'event_name' к передаче обязателен.
        """
        competition = self.get_competitions()
        detachment = get_object_or_404(
            Detachment, id=request.user.detachment_commander.id
        )
        detachment_report, _ = Q9Report.objects.get_or_create(
            detachment=detachment,
            competition=competition
        )
        if not request.data:
            return Response({'error': 'Отчет пустой.'},
                            status=status.HTTP_400_BAD_REQUEST)
        for event in request.data:
            serializer = CreateQ9Serializer(
                data=event,
                context={'request': request,
                         'competition': competition,
                         'event': event,
                         'detachment_report': detachment_report},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(detachment_report=detachment_report,
                            is_verified=False)
        return Response(Q9ReportSerializer(detachment_report).data,
                        status=status.HTTP_201_CREATED)

    @action(detail=True,
            methods=['post', 'delete'],
            url_path='accept',
            permission_classes=(permissions.IsAuthenticated,
                                IsRegionalCommissioner,))
    @swagger_auto_schema(
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={},),
        responses={200: Q9Serializer}
    )
    def accept_report(self, request, competition_pk, pk, *args, **kwargs):
        """
        Action для верификации мероприятия рег. комиссаром.

        Принимает пустой POST запрос.
        Доступ: комиссары региональных штабов.
        """
        event = self.get_object()
        if event.is_verified:
            return Response({'error': 'Отчет уже подтвержден.'},
                            status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'POST':
            event.is_verified = True
            event.save()
            return Response(Q9Serializer(event).data,
                            status=status.HTTP_200_OK)
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class Q10ViewSet(
    Q7ViewSet
):
    """Вью сет для показателя 'Призовые места отряда во
    всероссийских мероприятиях и конкурсах РСО.'.

    Доступ:
        - чтение: Командир отряда из инстанса объекта к которому
                  нужен доступ, а также комиссары региональных штабов.
        - чтение(list): только комиссары региональных штабов.
                        Выводятся заявки только его рег штаба.
        - изменение: Если заявка не подтверждена - командир отряда из
                     инстанса объекта который изменяют,
                     а также комиссары региональных штабов.
                     Если подтверждена - только комиссар регионального штаба.
        - удаление: Если заявка не подтверждена - командир отряда из
                    инстанса объекта который удаляют,
                    а также комиссары региональных штабов.
                    Если подтверждена - только комиссар регионального штаба.
    ! При редактировании нельзя изменять event_name.
    """
    queryset = Q10.objects.all()
    serializer_class = Q10Serializer

    @swagger_auto_schema(
        request_body=q9schema_request,
        responses={201: Q10ReportSerializer}
    )
    def create(self, request, *args, **kwargs):
        """Action для создания отчета.

        Доступ: командиры отрядов, которые участвуют в конкурсе.
        'event_name' к передаче обязателен.
        """
        competition = self.get_competitions()
        detachment = get_object_or_404(
            Detachment, id=request.user.detachment_commander.id
        )
        detachment_report, _ = Q10Report.objects.get_or_create(
            detachment=detachment,
            competition=competition
        )
        if not request.data:
            return Response({'error': 'Отчет пустой.'},
                            status=status.HTTP_400_BAD_REQUEST)
        for event in request.data:
            serializer = CreateQ10Serializer(
                data=event,
                context={'request': request,
                         'competition': competition,
                         'event': event,
                         'detachment_report': detachment_report},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(detachment_report=detachment_report,
                            is_verified=False)
        return Response(Q10ReportSerializer(detachment_report).data,
                        status=status.HTTP_201_CREATED)

    @action(detail=True,
            methods=['post', 'delete'],
            url_path='accept',
            permission_classes=(permissions.IsAuthenticated,
                                IsRegionalCommissioner,))
    @swagger_auto_schema(
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={},),
        responses={200: Q10Serializer}
    )
    def accept_report(self, request, competition_pk, pk, *args, **kwargs):
        """
        Action для верификации мероприятия рег. комиссаром.

        Принимает пустой POST запрос.
        Доступ: комиссары региональных штабов.
        """
        event = self.get_object()
        if event.is_verified:
            return Response({'error': 'Отчет уже подтвержден.'},
                            status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'POST':
            event.is_verified = True
            event.save()
            return Response(Q10Serializer(event).data,
                            status=status.HTTP_200_OK)
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class Q11ViewSet(
    Q7ViewSet
):
    """Вью сет для показателя 'Призовые места отряда в
    окружных и межрегиональных трудовых проектах'.

    Доступ:
        - чтение: Командир отряда из инстанса объекта к которому
                  нужен доступ, а также комиссары региональных штабов.
        - чтение(list): только комиссары региональных штабов.
                        Выводятся заявки только его рег штаба.
        - изменение: Если заявка не подтверждена - командир отряда из
                     инстанса объекта который изменяют,
                     а также комиссары региональных штабов.
                     Если подтверждена - только комиссар регионального штаба.
        - удаление: Если заявка не подтверждена - командир отряда из
                    инстанса объекта который удаляют,
                    а также комиссары региональных штабов.
                    Если подтверждена - только комиссар регионального штаба.
    ! При редактировании нельзя изменять event_name.
    """
    queryset = Q11.objects.all()
    serializer_class = Q11Serializer

    @swagger_auto_schema(
        request_body=q9schema_request,
        responses={201: Q11ReportSerializer}
    )
    def create(self, request, *args, **kwargs):
        """Action для создания отчета.

        Доступ: командиры отрядов, которые участвуют в конкурсе.
        'event_name' к передаче обязателен.
        """
        competition = self.get_competitions()
        detachment = get_object_or_404(
            Detachment, id=request.user.detachment_commander.id
        )
        detachment_report, _ = Q11Report.objects.get_or_create(
            detachment=detachment,
            competition=competition
        )
        if not request.data:
            return Response({'error': 'Отчет пустой.'},
                            status=status.HTTP_400_BAD_REQUEST)
        for event in request.data:
            serializer = CreateQ11Serializer(
                data=event,
                context={'request': request,
                         'competition': competition,
                         'event': event,
                         'detachment_report': detachment_report},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(detachment_report=detachment_report,
                            is_verified=False)
        return Response(Q11ReportSerializer(detachment_report).data,
                        status=status.HTTP_201_CREATED)

    @action(detail=True,
            methods=['post', 'delete'],
            url_path='accept',
            permission_classes=(permissions.IsAuthenticated,
                                IsRegionalCommissioner,))
    @swagger_auto_schema(
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={},),
        responses={200: Q11Serializer}
    )
    def accept_report(self, request, competition_pk, pk, *args, **kwargs):
        """
        Action для верификации мероприятия рег. комиссаром.

        Принимает пустой POST запрос.
        Доступ: комиссары региональных штабов.
        """
        event = self.get_object()
        if event.is_verified:
            return Response({'error': 'Отчет уже подтвержден.'},
                            status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'POST':
            event.is_verified = True
            event.save()
            return Response(Q11Serializer(event).data,
                            status=status.HTTP_200_OK)
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class Q12ViewSet(
    Q7ViewSet
):
    """Вью сет для показателя 'Призовые места отряда во
    всероссийских трудовых проектах'.

    Доступ:
        - чтение: Командир отряда из инстанса объекта к которому
                  нужен доступ, а также комиссары региональных штабов.
        - чтение(list): только комиссары региональных штабов.
                        Выводятся заявки только его рег штаба.
        - изменение: Если заявка не подтверждена - командир отряда из
                     инстанса объекта который изменяют,
                     а также комиссары региональных штабов.
                     Если подтверждена - только комиссар регионального штаба.
        - удаление: Если заявка не подтверждена - командир отряда из
                    инстанса объекта который удаляют,
                    а также комиссары региональных штабов.
                    Если подтверждена - только комиссар регионального штаба.
    ! При редактировании нельзя изменять event_name.
    """
    queryset = Q12.objects.all()
    serializer_class = Q12Serializer

    @swagger_auto_schema(
        request_body=q9schema_request,
        responses={201: Q12ReportSerializer}
    )
    def create(self, request, *args, **kwargs):
        """Action для создания отчета.

        Доступ: командиры отрядов, которые участвуют в конкурсе.
        'event_name' к передаче обязателен.
        """
        competition = self.get_competitions()
        detachment = get_object_or_404(
            Detachment, id=request.user.detachment_commander.id
        )
        detachment_report, _ = Q12Report.objects.get_or_create(
            detachment=detachment,
            competition=competition
        )
        if not request.data:
            return Response({'error': 'Отчет пустой.'},
                            status=status.HTTP_400_BAD_REQUEST)
        for event in request.data:
            serializer = CreateQ12Serializer(
                data=event,
                context={'request': request,
                         'competition': competition,
                         'event': event,
                         'detachment_report': detachment_report},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(detachment_report=detachment_report,
                            is_verified=False)
        return Response(Q12ReportSerializer(detachment_report).data,
                        status=status.HTTP_201_CREATED)

    @action(detail=True,
            methods=['post', 'delete'],
            url_path='accept',
            permission_classes=(permissions.IsAuthenticated,
                                IsRegionalCommissioner,))
    @swagger_auto_schema(
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={},),
        responses={200: Q12Serializer}
    )
    def accept_report(self, request, competition_pk, pk, *args, **kwargs):
        """
        Action для верификации мероприятия рег. комиссаром.

        Принимает пустой POST запрос.
        Доступ: комиссары региональных штабов.
        """
        event = self.get_object()
        if event.is_verified:
            return Response({'error': 'Отчет уже подтвержден.'},
                            status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'POST':
            event.is_verified = True
            event.save()
            return Response(Q12Serializer(event).data,
                            status=status.HTTP_200_OK)
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class Q13DetachmentReportViewSet(RetrieveCreateViewSet):
    """Показатель "Организация собственных мероприятий отряда".

    Пример POST-запроса:
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

    Доступ:
        - GET: Всем пользователям;
        - POST: Командирам отрядов, принимающих участие в конкурсе;
        - VERIFY-EVENT (POST/DELETE): Комиссарам РШ подвластных отрядов;
        - GET-PLACE (GET): Всем пользователям

    Note:
        - 404 возвращается в случае, если не найден объект конкурса или отряд,
          в котором юзер является командиром
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
        competition = get_object_or_404(
            Competitions, id=self.kwargs.get('competition_pk')
        )
        detachment = get_object_or_404(
            Detachment, id=self.request.user.detachment_commander.id
        )
        organization_data = request.data.get('organization_data', [])

        if not CompetitionParticipants.objects.filter(
                competition=competition,
                junior_detachment=detachment
        ).exists() and not CompetitionParticipants.objects.filter(
            competition=competition,
            detachment=detachment
        ).exists():
            return Response(
                {
                    'error': 'Отряд подающего пользователя не '
                             'участвует в конкурсе.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if not organization_data:
            return Response(
                {
                    'non_field_errors': 'organization_data '
                                        'должно быть заполнено'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        with transaction.atomic():
            report, created = Q13DetachmentReport.objects.get_or_create(
                competition_id=competition.id,
                detachment_id=detachment.id
            )

            for event_data in organization_data:
                event_serializer = Q13EventOrganizationSerializer(
                    data=event_data)
                if event_serializer.is_valid(raise_exception=True):
                    Q13EventOrganization.objects.create(
                        **event_serializer.validated_data,
                        detachment_report=report
                    )
                else:
                    return Response(event_serializer.errors,
                                    status=status.HTTP_400_BAD_REQUEST)

            return Response(
                self.get_serializer(report).data,
                status=(
                    status.HTTP_201_CREATED if created else status.HTTP_200_OK
                )
            )

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

    @action(detail=True, methods=['get'], url_path='get-place')
    def get_place(self, request, **kwargs):
        report = self.get_object()
        tandem_ranking = Q13TandemRanking.objects.filter(
            detachment=report.detachment
        ).first()
        if not tandem_ranking:
            tandem_ranking = Q13TandemRanking.objects.filter(
                junior_detachment=report.detachment
            ).first()

        # Пытаемся найти place в Q13TandemRanking
        if tandem_ranking and tandem_ranking.place is not None:
            return Response(
                {"place": tandem_ranking.place},
                status=status.HTTP_200_OK
            )

        # Если не найдено в Q13TandemRanking, ищем в Q13Ranking
        ranking = Q13Ranking.objects.filter(
            detachment=report.detachment
        ).first()
        if ranking and ranking.place is not None:
            return Response(
                {"place": ranking.place}, status=status.HTTP_200_OK
            )

        # Если не найдено ни в одной из моделей
        return Response(
            {"place": "Показатель в обработке"},
            status=status.HTTP_404_NOT_FOUND
        )

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='verify-event/(?P<event_id>\d+)',
        permission_classes=[
            permissions.IsAuthenticated, IsRegionalCommissioner,
        ]
    )
    def verify_event(self, request, competition_pk=None, pk=None,
                     event_id=None):
        """
        Верифицирует конкретное мероприятие по его ID.
        """
        report = self.get_object()
        event = get_object_or_404(
            Q13EventOrganization,
            pk=event_id,
            detachment_report=report
        )
        if event.is_verified:
            return Response({
                'detail': 'Данный отчет уже верифицирован'
            }, status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'POST':
            event.is_verified = True
            event.save()
            participants_entry = CompetitionParticipants.objects.filter(
                junior_detachment=report.detachment
            ).first()

            # Подсчет места для индивидуальных и тандем участников:
            if participants_entry and not participants_entry.detachment:
                Q13Ranking.objects.get_or_create(
                    competition_id=settings.COMPETITION_ID,
                    detachment=report.detachment,
                    place=calculate_q13_place(
                        Q13EventOrganization.objects.filter(
                            detachment_report=report,
                            is_verified=True
                        )
                    )
                )
            else:
                if participants_entry:
                    tandem_ranking, _ = Q13TandemRanking.objects.get_or_create(
                        competition_id=settings.COMPETITION_ID,
                        junior_detachment=report.detachment,
                        detachment=participants_entry.detachment
                    )
                    tandem_ranking.place = calculate_q13_place(
                        Q13EventOrganization.objects.filter(
                            detachment_report=report,
                            is_verified=True
                        )
                    )
                    elder_detachment_report = None
                    try:
                        elder_detachment_report = Q13DetachmentReport.objects.get(
                            detachment=tandem_ranking.detachment
                        )
                    except Q13DetachmentReport.DoesNotExist:
                        tandem_ranking.place += 6
                    if elder_detachment_report:
                        tandem_ranking.place += calculate_q13_place(
                            Q13EventOrganization.objects.filter(
                                detachment_report=elder_detachment_report,
                                is_verified=True
                            )
                        )
                else:
                    participants_entry = CompetitionParticipants.objects.filter(
                        detachment=report.detachment
                    ).first()
                    if not participants_entry:
                        return Response(
                            {'error': 'отряд не найден в участниках'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    tandem_ranking, _ = Q13TandemRanking.objects.get_or_create(
                        competition_id=settings.COMPETITION_ID,
                        junior_detachment=participants_entry.junior_detachment,
                        detachment=report.detachment
                    )
                    tandem_ranking.place = calculate_q13_place(
                        Q13EventOrganization.objects.filter(
                            detachment_report=report,
                            is_verified=True
                        )
                    )
                    junior_detachment_report = None
                    try:
                        junior_detachment_report = Q13DetachmentReport.objects.get(
                            detachment=tandem_ranking.junior_detachment
                        )
                    except Q13DetachmentReport.DoesNotExist:
                        tandem_ranking.place += 6
                    if junior_detachment_report:
                        tandem_ranking.place += calculate_q13_place(
                            Q13EventOrganization.objects.filter(
                                detachment_report=junior_detachment_report,
                                is_verified=True
                            )
                        )
                tandem_ranking.place = round(tandem_ranking / 2, 2)
                tandem_ranking.save()
            return Response(
                {"status": "Данные по организации "
                           "мероприятия верифицированы"},
                status=status.HTTP_200_OK
            )
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class Q13EventOrganizationViewSet(UpdateDestroyViewSet):
    """
    Обеспечивает возможность редактирования и
    удаления объектов Q13EventOrganization.

    - `PUT/PATCH`: Обновляет объект Q13EventOrganization, если
                   он не был верифицирован.
                   Ограничено для объектов, принадлежащих отчету подразделения
                   пользователя (где является командиром).

    - `DELETE`: Удаляет объект Q13EventOrganization,
                если он не был верифицирован.
                Ограничено для объектов, принадлежащих отчету
                подразделения пользователя (где является командиром).

    Примечание: Операции обновления и удаления доступны только
                если `is_verified` объекта равно `False`
                и если подразделение пользователя  (где является командиром)
                соответствует подразделению в отчете.
    """

    serializer_class = Q13EventOrganizationSerializer
    permission_classes = (IsDetachmentReportAuthor,)

    def get_queryset(self):
        report_pk = self.kwargs.get('report_pk')
        return Q13EventOrganization.objects.filter(
            detachment_report_id=report_pk
        )

    def update(self, request, *args, **kwargs):
        event_org = self.get_object()
        if event_org.is_verified:
            return Response(
                {
                    'detail': 'Нельзя редактировать/удалять верифицированные '
                              'записи.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        event_org = self.get_object()
        if event_org.is_verified:
            return Response(
                {
                    'detail': 'Нельзя редактировать/удалять верифицированные '
                              'записи.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)


class Q18DetachmentReportViewSet(RetrieveCreateViewSet):
    """
    Показатель "Охват бойцов, принявших участие во Всероссийском
    дне Ударного труда."

    Доступ:
        - GET: Всем пользователям;
        - POST: Командирам отрядов, принимающих участие в конкурсе;
        - VERIFY (POST/DELETE): Комиссарам РШ подвластных отрядов;
        - GET-PLACE (GET): Всем пользователям
    """
    serializer_class = Q18DetachmentReportSerializer

    @swagger_auto_schema(request_body=Q18DetachmentReportSerializer)
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def get_serializer_context(self):
        """
        Переопределение стандартного контекста,
        добавление competition и detachment.
        """
        if self.action == 'post':
            context = super().get_serializer_context()
            competition_id = self.kwargs.get('competition_pk')
            try:
                detachment_id = self.request.user.detachment_commander.id
            except Detachment.DoesNotExist:
                detachment_id = None
            context['competition'] = get_object_or_404(
                Competitions, id=competition_id
            )
            context['detachment'] = get_object_or_404(
                Detachment, id=detachment_id
            )
            return context

    def get_queryset(self):
        competition_id = self.kwargs.get('competition_pk')
        return Q18DetachmentReport.objects.filter(
            competition_id=competition_id
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
        url_path='verify',
        methods=(['POST', 'DELETE']),
        permission_classes=[
            permissions.IsAuthenticated, IsRegionalCommanderOrAdmin
        ]
    )
    def verify(self, *args, **kwargs):
        """Верификация отчета по показателю.

        Доступно только командиру РШ связанного с отрядом.
        Если отчет уже верифицирован, возвращается 400 Bad Request с описанием
        ошибки `{"detail": "Данный отчет уже верифицирован"}`.
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

    @action(detail=True, methods=['get'], url_path='get-place')
    def get_place(self, request, **kwargs):
        report = self.get_object()
        tandem_ranking = Q18TandemRanking.objects.filter(
            detachment=report.detachment
        ).first()
        if not tandem_ranking:
            tandem_ranking = Q18TandemRanking.objects.filter(
                junior_detachment=report.detachment
            ).first()

        # Пытаемся найти place в Q18TandemRanking
        if tandem_ranking and tandem_ranking.place is not None:
            return Response(
                {"place": tandem_ranking.place},
                status=status.HTTP_200_OK
            )

        # Если не найдено в Q18TandemRanking, ищем в Q18Ranking
        ranking = Q18Ranking.objects.filter(
            detachment=report.detachment
        ).first()
        if ranking and ranking.place is not None:
            return Response(
                {"place": ranking.place}, status=status.HTTP_200_OK
            )

        # Если не найдено ни в одной из моделей
        return Response(
            {"place": "Показатель в обработке"},
            status=status.HTTP_404_NOT_FOUND
        )


class Q19DetachmentReportViewset(CreateListRetrieveUpdateViewSet):
    """Вьюсет по показателю 'Отсутствие нарушений техники безопасности,
    охраны труда и противопожарной безопасности в трудовом семестре'.

    Доступ:
        - retrieve (GET) авторам отчета;
        - list (GET) командирам РШ, выводятся отчеты только его рег штаба;
        - create командирам отрядов-участников конкурса;
        - update командирам отрядов-участников конкурса;
    """
    serializer_class = Q19DetachmenrtReportSerializer
    permission_classes = (permissions.IsAuthenticated,
                          IsCompetitionParticipantAndCommander)

    def get_queryset(self):
        if self.action == 'list':
            try:
                regional_headquarter = (
                    self.request.user.regionalheadquarter_commander
                )
            except ObjectDoesNotExist:
                return Q19Report.objects.all()
            return Q19Report.objects.filter(
                detachment__regional_headquarter=regional_headquarter,
                competition_id=self.kwargs.get('competition_pk')
            )
        if self.action == 'me':
            return Q19Report.objects.filter(
                detachment__commander=self.request.user,
                competition_id=self.kwargs.get('competition_pk')
            )
        return Q19Report.objects.filter(
            competition_id=self.kwargs.get('competition_pk')
        )

    def get_permissions(self):
        if self.action == 'retrieve':
            return [permissions.IsAuthenticated(),
                    IsCommanderDetachmentInParameterOrRegionalCommissioner()]
        if self.action == 'list':
            return [permissions.IsAuthenticated(),
                    IsRegionalCommanderOrAdmin()]
        if self.action in ['update', 'partial_update']:
            return [permissions.IsAuthenticated(),
                    IsRegionalCommanderOrAuthor()]
        return super().get_permissions()

    def get_competitions(self):
        return get_object_or_404(
            Competitions, id=self.kwargs.get('competition_pk')
        )

    def get_detachment(self, obj):
        return obj.detachment

    @action(detail=False,
            methods=['get'],
            url_path='me',
            permission_classes=(permissions.IsAuthenticated,))
    def me(self, request, competition_pk, *args, **kwargs):
        """
        Action для получения своего отчета по параметру 19
        для текущего пользователя.

        Доступ: все авторизованные пользователи.
        Если пользователь не командир отряда, или у его отряда нет
        поданного отчета - вернется пустой список.
        """
        return super().list(request, *args, **kwargs)

    @action(detail=True,
            methods=['post', 'delete'],
            url_path='accept',
            permission_classes=(permissions.IsAuthenticated,
                                IsRegionalCommanderOrAdmin,))
    @swagger_auto_schema(
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={},),
        responses={200: Q19DetachmenrtReportSerializer}
    )
    def accept_report(self, request, competition_pk, pk, *args, **kwargs):
        """
        Action для верификации мероприятия рег. комиссаром.

        Принимает пустой POST запрос.

        Доступ: рег. командиры или админ
        """
        report = self.get_object()
        if report.is_verified:
            return Response({'error': 'Отчет уже подтвержден.'},
                            status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'POST':
            report.is_verified = True
            report.save()
            participants_entry = CompetitionParticipants.objects.filter(
                junior_detachment=report.detachment
            ).first()

            # Подсчет места для индивидуальных и тандем участников:
            if participants_entry and not participants_entry.detachment:
                Q19Ranking.objects.get_or_create(
                    competition_id=settings.COMPETITION_ID,
                    detachment=report.detachment,
                    place=calculate_q19_place(report)
                )
            else:
                if participants_entry:
                    tandem_ranking, _ = Q19TandemRanking.objects.get_or_create(
                        competition_id=settings.COMPETITION_ID,
                        junior_detachment=report.detachment,
                        detachment=participants_entry.detachment
                    )
                    tandem_ranking.place = calculate_q19_place(report)
                    elder_detachment_report = None
                    try:
                        elder_detachment_report = Q19Report.objects.get(
                            detachment=tandem_ranking.detachment
                        )
                    except Q19Report.DoesNotExist:
                        tandem_ranking.place += 2
                    if elder_detachment_report:
                        tandem_ranking.place += calculate_q19_place(elder_detachment_report)
                else:
                    participants_entry = CompetitionParticipants.objects.filter(
                        detachment=report.detachment
                    ).first()
                    if not participants_entry:
                        return Response(
                            {'error': 'отряд не найден в участниках'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    tandem_ranking, _ = Q19TandemRanking.objects.get_or_create(
                        competition_id=settings.COMPETITION_ID,
                        junior_detachment=participants_entry.junior_detachment,
                        detachment=report.detachment
                    )
                    tandem_ranking.place = calculate_q19_place(report)
                    junior_detachment_report = None
                    try:
                        junior_detachment_report = Q19Report.objects.get(
                            detachment=tandem_ranking.junior_detachment
                        )
                    except Q19Report.DoesNotExist:
                        tandem_ranking.place += 6
                    if junior_detachment_report:
                        tandem_ranking.place += calculate_q19_place(report)
                tandem_ranking.place = round(tandem_ranking / 2, 2)
                tandem_ranking.save()
        report.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            methods=['get'],
            url_path='get_place',
            permission_classes=(permissions.IsAuthenticated,
                                IsCompetitionParticipantAndCommander))
    def get_place(self, request, competition_pk, **kwargs):
        """
        Action для получения рейтинга по данному показателю.

        Доступ: командиры отрядов, которые участвуют в конкурсе.
        Если отчета еще не подан, вернется ошибка 404. (данные не отправлены)
        Если отчет подан, но еще не верифицировн - вернется
        {"place": "Показатель в обработке"}.
        Если отчет подан и верифицирован - вернется место в рейтинге:
        {"place": int}
        """
        detachment = self.request.user.detachment_commander
        report = Q19Report.objects.filter(
            detachment=detachment,
            competition_id=competition_pk
        ).first()
        if not report:
            return Response(status=status.HTTP_404_NOT_FOUND)
        ranking = getattr(
            detachment, 'q19ranking'
        ).filter(competition_id=competition_pk).first()
        if ranking:
            return Response(
                {"place": ranking.place}, status=status.HTTP_200_OK
            )
        tandem_ranking = getattr(
                    detachment, 'q19tandemranking_main_detachment'
        ).filter(competition_id=competition_pk).first()
        if tandem_ranking:
            return Response(
                {"place": tandem_ranking.place},
                status=status.HTTP_200_OK
            )
        tandem_ranking = getattr(
            detachment, 'q19tandemranking_junior_detachment'
            ).filter(competition_id=competition_pk).first()
        if tandem_ranking:
            return Response(
                {"place": tandem_ranking.place},
                status=status.HTTP_200_OK
            )
        return Response(
            {"place": "Показатель в обработке"},
            status=status.HTTP_200_OK
        )

    def create(self, request, competition_pk, *args, **kwargs):
        """
        Action для создания отчета по параметру 19
        для текущего пользователя.

        Доступ: командиры отрядов-участников конкурса.
        """
        competition = get_object_or_404(
            Competitions, id=competition_pk
        )
        detachment = get_object_or_404(
            Detachment, id=self.request.user.detachment_commander.id
        )
        serializer = Q19DetachmenrtReportSerializer(data=request.data,
                                                    context={'request': request,
                                                  'competition': competition,
                                                  'detachment': detachment})
        serializer.is_valid(raise_exception=True)
        serializer.save(competition=competition, detachment=detachment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class Q20ViewSet(CreateListRetrieveUpdateViewSet):
    """Вьюсет для показателя 'Соответствие требованиями положения символики
    и атрибутике форменной одежды и символики отрядов.'.

    Доступ:
        - чтение: Командир отряда из инстанса объекта к которому
                  нужен доступ, а также комиссары региональных штабов.
        - чтение(list): только комиссары региональных штабов.
                        Выводятся заявки только его рег штаба.
        - изменение: Если заявка не подтверждена - командир отряда из
                     инстанса объекта который изменяют,
                     а также комиссары региональных штабов.
                     Если подтверждена - только комиссар регионального штаба.
    """
    queryset = Q20Report.objects.all()
    serializer_class = Q20ReportSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        IsCommanderDetachmentInParameterOrRegionalCommissioner
    )

    def get_queryset(self):
        if self.action == 'list':
            regional_headquarter = (
                self.request.user.userregionalheadquarterposition.headquarter
            )
            return Q20Report.objects.filter(
                detachment__regional_headquarter=regional_headquarter,
                competition_id=self.kwargs.get('competition_pk')
            )
        if self.action == 'me':
            return Q20Report.objects.filter(
                detachment__commander=self.request.user,
                competition_id=self.kwargs.get('competition_pk')
            )
        return Q20Report.objects.filter(
            competition_id=self.kwargs.get('competition_pk')
        )

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.IsAuthenticated(),
                    IsCommanderAndCompetitionParticipant()]
        if self.action == 'list':
            return [permissions.IsAuthenticated(), IsRegionalCommissioner()]
        if self.action in ['update', 'partial_update']:
            return [permissions.IsAuthenticated(),
                    IsRegionalCommissionerOrCommanderDetachmentWithVerif()]
        return super().get_permissions()

    def get_competitions(self):
        return get_object_or_404(
            Competitions, id=self.kwargs.get('competition_pk')
        )

    def get_detachment(self, obj):
        return obj.detachment

    @action(detail=False,
            methods=['get'],
            url_path='me',
            permission_classes=(permissions.IsAuthenticated,))
    def me(self, request, competition_pk, *args, **kwargs):
        """
        Action для получения своего отчета по параметру 20
        для текущего пользователя.

        Доступ: все авторизованные пользователи.
        Если пользователь не командир отряда, или у его отряда нет
        поданного отчета - вернется пустой список.
        """
        return super().list(request, *args, **kwargs)

    @action(detail=True,
            methods=['post', 'delete'],
            url_path='accept',
            permission_classes=(permissions.IsAuthenticated,
                                IsRegionalCommissioner,))
    @swagger_auto_schema(
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={},),
        responses={200: Q20ReportSerializer}
    )
    def accept_report(self, request, competition_pk, pk, *args, **kwargs):
        """
        Action для верификации мероприятия рег. комиссаром.

        Принимает пустой POST запрос.
        Доступ: комиссары региональных штабов.
        """
        report = self.get_object()
        if report.is_verified:
            return Response({'error': 'Отчет уже подтвержден.'},
                            status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'POST':
            report.is_verified = True
            report.save()
            return Response(Q20ReportSerializer(report).data,
                            status=status.HTTP_200_OK)
        report.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            methods=['get'],
            url_path='get_place',
            permission_classes=(permissions.IsAuthenticated,
                                IsCompetitionParticipantAndCommander))
    def get_place(self, request, competition_pk, **kwargs):
        """
        Action для получения рейтинга по данному показателю.

        Доступ: командиры отрядов, которые участвуют в конкурсе.
        Если отчета еще не подан, вернется ошибка 404. (данные не отправлены)
        Если отчет подан, но еще не верифицировн - вернется
        {"place": "Показатель в обработке"}.
        Если отчет подан и верифицирован - вернется место в рейтинге:
        {"place": int}
        """
        detachment = self.request.user.detachment_commander
        report = Q20Report.objects.filter(
            detachment=detachment,
            competition_id=competition_pk
        ).first()
        if not report:
            return Response(status=status.HTTP_404_NOT_FOUND)
        ranking = getattr(
            detachment, 'q20ranking'
        ).filter(competition_id=competition_pk).first()
        if ranking:
            return Response(
                {"place": ranking.place}, status=status.HTTP_200_OK
            )
        tandem_ranking = getattr(
                    detachment, 'q20tandemranking_main_detachment'
        ).filter(competition_id=competition_pk).first()
        if tandem_ranking:
            return Response(
                {"place": tandem_ranking.place},
                status=status.HTTP_200_OK
            )
        tandem_ranking = getattr(
            detachment, 'q20tandemranking_junior_detachment'
            ).filter(competition_id=competition_pk).first()
        if tandem_ranking:
            return Response(
                {"place": tandem_ranking.place},
                status=status.HTTP_200_OK
            )
        return Response(
            {"place": "Показатель в обработке"},
            status=status.HTTP_200_OK
        )

    def create(self, request, competition_pk, *args, **kwargs):
        """
        Action для создания отчета по параметру 20
        для текущего пользователя.

        Доступ: командиры отрядов-участников конкурса.
        """
        competition = get_object_or_404(
            Competitions, id=competition_pk
        )
        detachment = get_object_or_404(
            Detachment, id=self.request.user.detachment_commander.id
        )
        serializer = Q20ReportSerializer(data=request.data,
                                         context={'request': request,
                                                  'competition': competition,
                                                  'detachment': detachment})
        serializer.is_valid(raise_exception=True)
        serializer.save(competition=competition, detachment=detachment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
