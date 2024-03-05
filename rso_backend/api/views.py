import io
import os
from datetime import datetime

import pdfrw
from django.conf import settings
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from pdfrw.buildxobj import pagexobj
from pdfrw.toreportlab import makerl
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from api.filters import EducationalInstitutionFilter
from api.mixins import ListRetrieveViewSet
from api.permissions import (IsRegionalCommanderForCert,
                             IsRegStuffOrDetCommander,
                             IsStuffOrCentralCommander,
                             MembershipFeePermission)
from api.serializers import (AreaSerializer, EducationalInstitutionSerializer,
                             MemberCertSerializer, RegionSerializer)
from api.swagger_schemas import properties, properties_external
from api.utils import (create_and_return_archive, get_user, get_user_by_id,
                       text_to_lines)
from headquarters.models import (Area, EducationalInstitution, Region,
                                 RegionalHeadquarter,
                                 UserRegionalHeadquarterPosition)
from users.models import (MemberCert, RSOUser, UserDocuments,
                          UserMemberCertLogs, UserMembershipLogs,
                          UserVerificationLogs, UserVerificationRequest)


class EducationalInstitutionViewSet(ListRetrieveViewSet):
    """Представляет учебные заведения. Доступны только операции чтения.

    Доступен фильтр по названию региона. Ключ region__name.
    """
    queryset = EducationalInstitution.objects.all()
    serializer_class = EducationalInstitutionSerializer
    filter_backends = (filters.SearchFilter, DjangoFilterBackend)
    search_fields = ('name',)
    filterset_class = EducationalInstitutionFilter
    ordering = ('name',)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            return cache.get_or_set(
                f'educational_institutions_page_{request.GET.get("page", "1")}',
                lambda: self.get_paginated_response(self.get_serializer(page, many=True).data),
                timeout=settings.EDU_INST_CACHE_TTL
            )

        data = cache.get_or_set(
            'educational_institutions_all',
            lambda: self.get_serializer(queryset, many=True).data,
            timeout=settings.EDU_INST_CACHE_TTL
        )
        return Response(data)


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


@api_view(['POST', 'DELETE'])
@permission_classes([permissions.IsAuthenticated, IsRegStuffOrDetCommander])
def verify_user(request, pk):
    """Принять/отклонить заявку пользователя на верификацию.

    Доступно только командирам и доверенным лицам региональных штабов
    (относящихся к тому же региону, что и юзер) и отрядов (в котором
    состоит юзер).
    """
    if not request.user.is_verified:
        return Response(
            status=status.HTTP_403_FORBIDDEN,
            data={'detail': (
                'Пройдите верификацию,'
                ' чтобы верифицировать других пользователей.'
            )}
        )
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
@permission_classes([permissions.IsAuthenticated, MembershipFeePermission])
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
    """Представляет сертификаты пользователей.

    Разрешение на выдачу справок имеет только командир РШ.
    """

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
            if inn is None or snils is None:
                return Response(
                    status=status.HTTP_400_BAD_REQUEST,
                    data={
                        'detail': 'Документы пользователя '
                        f'{username} не заполнены.'
                    }
                )
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
            str(settings.BASE_DIR),
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
                    str(settings.BASE_DIR),
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
                    str(settings.BASE_DIR),
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
            properties=properties | properties_external,
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
                        status=status.HTTP_400_BAD_REQUEST
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
            properties=properties,
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
                        status=status.HTTP_400_BAD_REQUEST
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
