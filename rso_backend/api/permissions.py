from django.db.models import Q, QuerySet
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status
from rest_framework.permissions import BasePermission
from rest_framework.response import Response

from api.utils import (check_commander_or_not, check_roles_for_edit,
                       check_trusted_for_centralhead,
                       check_trusted_for_detachments,
                       check_trusted_for_districthead,
                       check_trusted_for_eduhead, check_trusted_for_localhead,
                       check_trusted_for_regionalhead,
                       check_trusted_in_headquarters, check_trusted_user,
                       is_commander_this_detachment,
                       is_regional_commander, is_regional_commissioner,
                       is_safe_method,
                       is_stuff_or_central_commander)
from competitions.models import CompetitionParticipants, Competitions
from competitions.utils import is_competition_participant
from events.models import Event, EventOrganizationData
from headquarters.models import (CentralHeadquarter, Detachment,
                                 DistrictHeadquarter, EducationalHeadquarter,
                                 LocalHeadquarter, RegionalHeadquarter,
                                 UserCentralHeadquarterPosition,
                                 UserDetachmentPosition,
                                 UserDistrictHeadquarterPosition,
                                 UserEducationalHeadquarterPosition,
                                 UserLocalHeadquarterPosition,
                                 UserRegionalHeadquarterPosition)
from users.models import RSOUser
from users.serializers import UserCommanderSerializer, UserTrustedSerializer


class IsStuffOrCentralCommander(BasePermission):
    """Пермишен для стаффа и командира центрального штаба.

    Роли 'стафф', 'админ' и 'командир центрального штаба' возвращают True.
    Остальные пользователи получают True, если обращаются к эндпоинту
    с безопасным запросом (GET, HEAD, OPTIONS).
    """
    def has_permission(self, request, view):
        return any([
            is_safe_method(request),
            is_stuff_or_central_commander(request)
        ])

    def has_object_permission(self, request, view, obj):
        return any([
            is_safe_method(request),
            is_stuff_or_central_commander(request),
        ])


class IsStuffOrCentralCommanderOrTrusted(IsStuffOrCentralCommander):
    """Пермишен для стаффа,командира ЦШ и доверенного в ЦШ.

    Роли 'стафф', 'командир ЦШ' и 'доверенный в ЦШ' возвращают True.
    Остальные пользователи получают True, если обращаются к эндпоинту
    с безопасным запросом (GET, HEAD, OPTIONS).
    """

    def has_object_permission(self, request, view, obj):
        return any([
            is_safe_method(request),
            is_stuff_or_central_commander(request),
            check_trusted_user(
                request=request,
                model=UserCentralHeadquarterPosition,
                obj=obj
            )
        ])


class IsDistrictCommander(BasePermission):
    """Пермишен для командира окружного штаба.

    Для ролей 'is stuff' и 'superuser' возвращается True.
    Роль 'командир окружного штаба' и 'доверенный пользователь'
    возвращают True, если редактируют свой штаб и штабы ниже своего.
    Остальные пользователи получают True, если обращаются к эндпоинту
    с безопасным запросом (GET, HEAD, OPTIONS).
    """

    def has_permission(self, request, view):
        if request.method in ('PATCH', 'PUT'):
            return self.has_object_permission(request, view, view.get_object())
        return any([
            is_safe_method(request),
            is_stuff_or_central_commander(request),
            check_trusted_for_centralhead(request),
        ])

    def has_object_permission(self, request, view, obj):
        check_model_instance = False
        user_id = request.user.id
        if (
                isinstance(obj, DistrictHeadquarter)
                and user_id == obj.commander_id
        ):
            check_model_instance = True
        check_roles = any([
            is_safe_method(request),
            is_stuff_or_central_commander(request),
            check_trusted_for_districthead(request, obj)
        ])
        return check_roles or check_model_instance


class IsRegionalCommander(BasePermission):
    """Пермишен для командира регионального штаба.

    Для ролей 'is stuff' и 'superuser' возвращается True.
    Роль 'командир регионального штаба' и 'доверенный пользователь'
    возвращают True, если редактируют свой штаб и штабы ниже своего.
    Остальные пользователи получают True, если обращаются к эндпоинту
    с безопасным запросом (GET, HEAD, OPTIONS).
    """

    def has_permission(self, request, view):
        if request.method in ('PATCH', 'PUT'):
            return self.has_object_permission(request, view, view.get_object())
        headquarters = [
            DistrictHeadquarter,
            RegionalHeadquarter
        ]
        return any([
            is_safe_method(request),
            is_stuff_or_central_commander(request),
            check_trusted_for_centralhead(request),
            check_trusted_for_regionalhead(request),
            check_commander_or_not(request, headquarters),
        ])

    def has_object_permission(self, request, view, obj):
        """Метод, для проверки доступа к эндпоинтам РШ.

        check_roles - проверяет http-методы пользователя или роли.
        """

        check_model_instance = False
        user_id = request.user.id
        if isinstance(obj, RegionalHeadquarter) and (
                user_id == obj.commander_id
                or (
                        user_id == obj.district_headquarter.commander_id
                )
        ):
            check_model_instance = True
        check_roles = any([
            is_safe_method(request),
            is_stuff_or_central_commander(request),
            check_trusted_for_regionalhead(request, obj)
        ])
        return check_roles or check_model_instance


class IsLocalCommander(BasePermission):
    """Пермишен для командира местного штаба.

    Для ролей 'is stuff' и 'superuser возвращается True.
    Роль 'командир местного штаба' и 'доверенный пользователь'
    возвращают True, если редактируют свой штаб и штабы ниже своего.
    Остальные пользователи получают True, если обращаются к эндпоинту
    с безопасным запросом (GET, HEAD, OPTIONS).
    """

    def has_permission(self, request, view):
        if request.method in ('PATCH', 'PUT'):
            return self.has_object_permission(request, view, view.get_object())
        headquarters = [
            LocalHeadquarter,
            RegionalHeadquarter,
            DistrictHeadquarter
        ]
        return any([
            is_safe_method(request),
            is_stuff_or_central_commander(request),
            check_trusted_for_centralhead(request),
            check_trusted_for_localhead(request),
            check_commander_or_not(request, headquarters),
        ])

    def has_object_permission(self, request, view, obj):
        """Метод, для проверки доступа к эндпоинтам МШ.

        check_roles - проверяет http-методы пользователя или роли.
        """

        check_model_instance = False
        user_id = request.user.id
        regional_head = obj.regional_headquarter
        if isinstance(obj, LocalHeadquarter) and any(
                user_id == commander.commander_id
                for commander in [
                    obj,
                    regional_head,
                    regional_head.district_headquarter
                ]
        ):
            check_model_instance = True
        check_roles = any([
            is_safe_method(request),
            is_stuff_or_central_commander(request),
            check_trusted_for_localhead(request, obj),
        ])
        return check_roles or check_model_instance


class IsEducationalCommander(BasePermission):
    """Пермишен для командира образовательного штаба.

    Для ролей 'is stuff' и 'superuser' возвращается True.
    Роль 'командир образовательного штаба' и 'доверенный пользователь'
    возвращают True, если редактируют свой штаб и штабы ниже своего.
    Остальные пользователи получают True, если обращаются к эндпоинту
    с безопасным запросом (GET, HEAD, OPTIONS).
    """

    def has_permission(self, request, view):
        if request.method in ('PATCH', 'PUT'):
            return self.has_object_permission(request, view, view.get_object())
        headquarters = [
            EducationalHeadquarter,
            LocalHeadquarter,
            RegionalHeadquarter,
            DistrictHeadquarter
        ]
        return any([
            is_safe_method(request),
            is_stuff_or_central_commander(request),
            check_trusted_for_centralhead(request),
            check_trusted_for_eduhead(request),
            check_commander_or_not(request, headquarters),
        ])

    def has_object_permission(self, request, view, obj):
        """Метод, для проверки доступа к эндпоинтам ШОО.

        check_roles - проверяет http-методы пользователя или роли.
        """

        check_model_instance = False
        check_local_head = False
        user_id = request.user.id
        regional_head = obj.regional_headquarter
        if isinstance(obj, EducationalHeadquarter) and any(
                user_id == commander.commander_id
                for commander in [
                    obj,
                    regional_head,
                    regional_head.district_headquarter
                ]
        ):
            check_model_instance = True
        if local_head := obj.local_headquarter:
            if isinstance(obj, Detachment) and (
                    user_id == local_head.commander_id
            ):
                check_local_head = True
        check_roles = any([
            is_safe_method(request),
            is_stuff_or_central_commander(request),
            check_trusted_for_eduhead(request, obj)
        ])
        return any([
            check_roles,
            check_model_instance,
            check_local_head
        ])


class IsDetachmentCommander(BasePermission):
    """Пермишен для командира отряда.

    Для ролей 'is stuff' и 'superuser' возвращается True.
    Роль 'командир отряда' и 'доверенный пользователь'
    возвращают True, если редактируют свой штаб и штабы ниже своего.
    Остальные пользователи получают True, если обращаются к эндпоинту
    с безопасным запросом (GET, HEAD, OPTIONS).
    """

    @classmethod
    def check_instances(cls, request, obj=None):
        check_model_instance = False
        check_local_head = False
        check_edu_head = False
        user_id = request.user.id
        regional_head = obj.regional_headquarter
        if isinstance(obj, Detachment) and any(
                user_id == commander.commander_id
                for commander in [
                    obj,
                    regional_head,
                    regional_head.district_headquarter
                ]
        ):
            check_model_instance = True
        if local_head := obj.local_headquarter:
            if isinstance(obj, Detachment) and (
                    user_id == local_head.commander_id
            ):
                check_local_head = True
        if edu_head := obj.educational_headquarter:
            if isinstance(obj, Detachment) and (
                    user_id == edu_head.commander_id
            ):
                check_edu_head = True
        return any([
            check_model_instance,
            check_local_head,
            check_edu_head
        ])

    def has_permission(self, request, view):
        if request.method in ('PATCH', 'PUT'):
            return self.has_object_permission(request, view, view.get_object())
        headquarters = [
            Detachment,
            EducationalHeadquarter,
            LocalHeadquarter,
            RegionalHeadquarter,
            DistrictHeadquarter
        ]
        return any([
            is_safe_method(request),
            is_stuff_or_central_commander(request),
            check_trusted_for_centralhead(request),
            check_trusted_for_detachments(request),
            check_commander_or_not(request, headquarters),
        ])

    def has_object_permission(self, request, view, obj):

        return any([
            is_safe_method(request),
            is_stuff_or_central_commander(request),
            check_trusted_for_detachments(request, obj),
            self.check_instances(request, obj),
        ])


class IsStuffOrAuthor(BasePermission):
    """Пермишен для стаффа и автора.

    Роли 'is stuff', 'is superuser', 'командир' и 'автор' возвращают True.
    Остальные пользователи получают True, если обращаются к эндпоинту
    с безопасным запросом (GET, HEAD, OPTIONS).
    """

    def has_permission(self, request, view):
        if request.method in ('PATCH', 'PUT', 'DELETE'):
            return self.has_object_permission(request, view, view.get_object())
        return any([
            is_safe_method(request),
            is_stuff_or_central_commander(request),
            request.user.is_authenticated
        ])

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, QuerySet):
            queryset = obj.filter(id=view.kwargs.get('pk'), user=request.user)
            if queryset.count() == 0:
                return False
            else:
                obj = queryset.first()
        roles_models = {
            'district_commander': UserDistrictHeadquarterPosition,
            'regional_commander': UserRegionalHeadquarterPosition,
            'local_commander': UserLocalHeadquarterPosition,
            'edu_commander': UserEducationalHeadquarterPosition,
            'detachment_commander': UserDetachmentPosition,
        }
        check_roles = any([
            is_safe_method(request),
            is_stuff_or_central_commander(request),
            check_roles_for_edit(request=request, roles_models=roles_models),
            check_trusted_in_headquarters(
                request=request,
                roles_models=roles_models,
                obj=obj
            )
        ])
        return any([
            request.user.is_superuser,
            request.user == obj.user,
            check_roles
        ])


class IsRegStuffOrDetCommander(BasePermission):
    """Пермишен для верификации пользователя.

    Верифицировать пользователя может лишь командир или доверенные лица
    регионального отделения по региону пользователя, либо же командир
    соответствующего отряда, если пользователь вступил в отряд.
    """

    def has_permission(self, request, view):
        user = request.user
        user_to_verify = get_object_or_404(RSOUser, id=view.kwargs.get('pk'))
        user_to_verify_region = user_to_verify.region
        # изменить на get когда один
        # регион сможет относиться к какому-то РШ
        reg_headquarter = RegionalHeadquarter.objects.filter(
            region=user_to_verify_region
        ).first()
        if not reg_headquarter:
            return Response(
                {
                    'detail': ('Не найден региональный штаб,'
                               ' совпадающий с регионом пользователя')
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if reg_headquarter.commander == user:
            return True

        try:
            reg_headquarter_member = (
                UserRegionalHeadquarterPosition.
                objects.get(user=user, headquarter=reg_headquarter)
            )
        except (UserRegionalHeadquarterPosition.DoesNotExist, AttributeError):
            reg_headquarter_member = None

        if reg_headquarter_member:
            if reg_headquarter_member.is_trusted:
                return True

        try:
            user_in_detachment = UserDetachmentPosition.objects.get(
                user=user_to_verify
            )
        except (UserDetachmentPosition.DoesNotExist, AttributeError):
            return False

        if user_in_detachment.headquarter.commander == user:
            return True
        return False


class MembershipFeePermission(BasePermission):
    """Пермишен для смены статуса оплаты членского взноса пользователю.

    Только для командира или дов. членов РШ.
    """

    def has_permission(self, request, view):
        user = request.user
        user_to_change = get_object_or_404(RSOUser, id=view.kwargs.get('pk'))
        try:
            reg_headquarter = (
                UserRegionalHeadquarterPosition.
                objects.get(user=user_to_change)
            ).headquarter
        except (UserRegionalHeadquarterPosition.DoesNotExist, AttributeError):
            return False

        if reg_headquarter.commander == user:
            return True

        try:
            reg_headquarter_member = (
                UserRegionalHeadquarterPosition.
                objects.get(user=user, headquarter=reg_headquarter)
            )
        except (UserRegionalHeadquarterPosition.DoesNotExist, AttributeError):
            return False
        if reg_headquarter_member:
            if reg_headquarter_member.is_trusted:
                return True
        return False


class IsRegionalCommanderForCert(BasePermission):
    """Пермишен для командира выдачи справок.

    Для ролей 'is stuff' и 'superuser' возвращается True.
    Роль 'командир регионального штаба' и 'доверенный пользователь'
    возвращают True.
    Остальные пользователи получают True, если обращаются к эндпоинту
    с безопасным запросом (GET, HEAD, OPTIONS).
    """

    def has_permission(self, request, view):
        """Проверка прав пользователя для выдачи справки."""

        check_model_instance = True
        request_user_id = request.user.id
        ids = request.data.get('ids')
        if ids is None:
            return Response(
                {'detail': 'Поле "ids" не может быть пустым.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            commanders_regional_head_id = RegionalHeadquarter.objects.filter(
                commander_id=request_user_id
            ).id
            for id in ids:
                if id == 0:
                    return Response(
                        {'detail': 'Поле "ids" не может содержать 0.'},
                    )
                users_regional_head_id = (
                    UserRegionalHeadquarterPosition.objects.get(
                        user_id=id
                    ).headquarter_id
                )
                if (
                    users_regional_head_id != commanders_regional_head_id
                ):
                    check_model_instance = False
                    break
        except (
            RegionalHeadquarter.DoesNotExist,
            AttributeError,
            UserRegionalHeadquarterPosition.DoesNotExist
        ):
            check_model_instance = False
        return any([
            is_safe_method(request),
            is_stuff_or_central_commander(request),
            check_model_instance
        ])


class IsAuthorPermission(BasePermission):
    """Проверяет, является ли пользователь автором объекта."""
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class IsEventAuthor(BasePermission):
    """
    Проверяет, является ли пользователем автором

    мероприятия при редактировании, создании или удалении
    объекта, связанного с мероприятием.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        event_pk = view.kwargs.get('event_pk')
        if event_pk is not None:
            event = Event.objects.filter(pk=event_pk).first()
            if event is not None:
                return event.author == request.user
        return False

    def has_object_permission(self, request, view, obj):
        return obj.event.author == request.user


class IsEventOrganizer(BasePermission):
    """
    Проверяет, является ли пользователь автором
    мероприятия при чтении или редактировании одного или нескольких
    объектов связанных с мероприятием.
    """
    def has_permission(self, request, view):
        if EventOrganizationData.objects.filter(
            organizer=request.user
        ).exists():
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if EventOrganizationData.objects.filter(
            organizer=request.user
        ).exists():
            return True


class IsEventOrganizerOrAuthor(BasePermission):
    """
    Проверяет, является ли пользователем автором
    мероприятия при чтении или редактировании одного или нескольких
    объектов связанных с мероприятием.
    Для операций с одним объектом дополнительно проверяется,
    является ли пользователь автором.
    """
    def has_permission(self, request, view):
        if EventOrganizationData.objects.filter(
            organizer=request.user
        ).exists():
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if EventOrganizationData.objects.filter(
            organizer=request.user
        ).exists():
            return True
        return obj.user == request.user


class IsApplicantOrOrganizer(BasePermission):
    """
    Проверяет, является ли пользователь автором заявки
    или организатором мероприятия. Только одиночных объектов.
    """
    def has_object_permission(self, request, view, obj):
        if EventOrganizationData.objects.filter(
            organizer=request.user
        ).exists():
            return True
        return obj.user == request.user


class IsCommander(BasePermission):
    """Проверяет, является ли пользователь командиром
    структурной единицы, типу которых разрешена подача
    заявок на многоэтапное мероприятие.
    Дополнительно проверяет верифицирован ли пользователь.
    """
    _STRUCTURAL_MAPPING = {
        'Центральные штабы': CentralHeadquarter,
        'Окружные штабы': DistrictHeadquarter,
        'Региональные штабы': RegionalHeadquarter,
        'Местные штабы': LocalHeadquarter,
        'Образовательные штабы': EducationalHeadquarter,
        'Отряды': Detachment
    }

    def has_permission(self, request, view):
        event = get_object_or_404(Event, pk=view.kwargs.get('event_pk'))
        available_structural_model = self._STRUCTURAL_MAPPING.get(
            event.available_structural_units
        )
        return available_structural_model.objects.filter(
            commander=request.user
        ).exists() and request.user.is_verified


class IsAuthorMultiEventApplication(BasePermission):
    """Проверяет, является ли пользователь автором
    заявки на многоэтапное мероприятие.
    """
    def has_object_permission(self, request, view, obj):
        return obj.organizer_id == request.user.id


class IsVerifiedPermission(BasePermission):
    """Проверяет, верифицирован ли пользователь."""
    def has_permission(self, request, view):
        return request.user.is_verified


class IsUserModelPositionCommander(permissions.BasePermission):
    """
    Проверка является ли юзер коммандиром штаба/отряда
    при обращении к эндпоинтам членов штабов.
    """

    POSITIONS = {
        UserCentralHeadquarterPosition: [
            'centralheadquarter_commander',
            'centralheadquarter_trusted'
        ],
        UserDistrictHeadquarterPosition: [
            'districtheadquarter_commander',
            'districtheadquarter_trusted'
        ],
        UserRegionalHeadquarterPosition: [
            'regionalheadquarter_commander',
            'regionalheadquarter_trusted'
        ],
        UserLocalHeadquarterPosition: [
            'localheadquarter_commander',
            'localheadquarter_trusted'
        ],
        UserEducationalHeadquarterPosition: [
            'educationalheadquarter_commander',
            'educationalheadquarter_trusted'
        ],
        UserDetachmentPosition: [
            'detachment_commander',
            'detachment_trusted'
        ]
    }

    def prepare_data_commander(self, request):
        """Метод создает словарь со штабами/отрядами, где юзер - командир.

        Пример словаря prepared_data, возвращаемого этим методом:
        {
            'centralheadquarter_commander': 1,
            'localheadquarter_commander': 2,
            ...
            'detachment_commander': 3
        }
        """

        data = UserCommanderSerializer(request.user).data
        prepared_data = {}
        for key, value in data.items():
            if value and type(value) is not int:
                prepared_data[key] = value['id']
            else:
                prepared_data[key] = value
        return prepared_data

    def prepare_data_trusted(self, request):
        """Метод создает словарь со штабами/отрядами, где юзер - доверенный.

        Пример словаря prepared_data, возвращаемого этим методом:
        {
            'centralheadquarter_trusted': 1,
            'localheadquarter_trusted': 2,
        }
        """

        data = UserTrustedSerializer(request.user).data
        prepared_data = {}
        for key, value in data.items():
            if value:
                prepared_data[key] = value
        return prepared_data

    def has_permission(self, request, view):
        if (
            request.method in ['PUT', 'PATCH']
            and request.user.is_authenticated
        ):
            return self.has_object_permission(request, view, view.get_object())
        if request.method in permissions.SAFE_METHODS:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        headquarter_id = obj.headquarter.id
        prepared_data = (
            self.prepare_data_commander(request)
            | self.prepare_data_trusted(request)
        )
        for prepared_key, prepared_value in prepared_data.items():
            for model_position, commander_or_trusted in self.POSITIONS.items():
                if prepared_key in commander_or_trusted:
                    if isinstance(obj, model_position):
                        if headquarter_id == prepared_value:
                            return True
        return False


class IsCommanderOrTrustedAnywhere(BasePermission):
    """
    Возвращает True, если пользователь является командиром или доверенным
    лицом хотя бы где-либо.
    """
    def has_object_permission(self, request, view, obj):
        print('Пермишен отработал')
        commander_data = UserCommanderSerializer(request.user).data
        trusted_data = UserTrustedSerializer(request.user).data
        if any(commander_data.values()) or any(trusted_data.values()):
            return True
        return False


class IsRegionalCommanderOrAdmin(BasePermission):
    """
    Проверяет, является ли пользователь командиром
    регионального штаба или администратором.
    """

    def has_permission(self, request, view):
        return is_regional_commander(request.user)

    def has_object_permission(self, request, view, obj):
        return is_regional_commander(request.user)


class IsRegionalCommanderOrAdminOrAuthor(BasePermission):
    """
    Для операций с одним объектом.
    Проверяет, является ли пользователь командиром
    регионального штаба, администратором или отрядом из заявки в конкурс.
    """

    def has_object_permission(self, request, view, obj):
        application = obj
        current_detachment = view.get_detachment(request.user)
        if current_detachment:
            return (application.junior_detachment == current_detachment or
                    application.detachment == current_detachment or
                    is_regional_commander(request.user))
        return is_regional_commander(request.user)


class IsCommanderAndCompetitionParticipant(BasePermission):
    """
    Для detail=False - проверяет, является ли пользователь командиром
    отряда, который является участником конкурса.
    Для detail=True - проверяет, является ли пользователь командиром отряда
    из инстанса(отчета), и этот отряд является участником конкурса.
    """
    def has_permission(self, request, view):
        competition = Competitions.objects.get(
            pk=view.kwargs.get('competition_pk')
        )
        try:
            detachment = request.user.detachment_commander
        except Detachment.DoesNotExist:
            return False
        return (
            CompetitionParticipants.objects.filter(
                Q(competition=competition, detachment=detachment) |
                Q(competition=competition, junior_detachment=detachment)
            ).exists()
        )

    def has_object_permission(self, request, view, obj):
        detachment = obj.detachment
        competition = obj.competition
        if detachment:
            return (
                is_commander_this_detachment(request.user, detachment) and
                is_competition_participant(detachment, competition)
            )


class IsCommanderDetachmentInParameterOrRegionalCommissioner(
    BasePermission
):
    """
    Проверяет, является ли пользователь командиром отряда из
    инстанса параметра или региональным комиссаром.

    Только для операций с одиночными объектами.
    """

    def has_object_permission(self, request, view, obj):
        detachment = obj.detachment
        if detachment:
            return (
                is_commander_this_detachment(request.user, detachment) or
                is_regional_commissioner(request.user)
            )


class IsRegionalCommissioner(BasePermission):
    """
    Проверяет, является ли пользователь комиссаром регионального штаба.
    """
    def has_permission(self, request, view):
        return is_regional_commissioner(request.user)

    def has_object_permission(self, request, view, obj):
        return is_regional_commissioner(request.user)


class IsRegionalCommissionerOrCommanderDetachmentWithVerif(
    BasePermission
):
    """
    Для операций с одиночным объектом.
    Если заявка верифицирована, проверяет, является ли пользователь
    комиссаром регионального штаба.
    Если заявка не верифицирована, проверяет, является ли пользователь
    комиссаром регионального штаба или командиром отряда из заявки.
    Пермишен для 'update', 'partial_update', 'destroy' отчетов конкурса.
    """

    def has_object_permission(self, request, view, obj):
        if obj.is_verified:
            return is_regional_commissioner(request.user)
        return (
            is_regional_commissioner(request.user) or
            is_commander_this_detachment(request.user, obj.detachment)
        )