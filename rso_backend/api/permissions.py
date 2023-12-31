from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import BasePermission
from rest_framework.response import Response

from api.utils import (check_roles_for_edit, check_trusted_for_detachments,
                       check_trusted_for_districthead,
                       check_trusted_for_eduhead, check_trusted_for_localhead,
                       check_trusted_for_regionalhead,
                       check_trusted_in_headquarters, check_trusted_user,
                       is_safe_method, is_stuff_or_central_commander)
from headquarters.models import (Detachment, DistrictHeadquarter,
                                 EducationalHeadquarter, LocalHeadquarter,
                                 RegionalHeadquarter,
                                 UserCentralHeadquarterPosition,
                                 UserDetachmentPosition,
                                 UserDistrictHeadquarterPosition,
                                 UserEducationalHeadquarterPosition,
                                 UserLocalHeadquarterPosition,
                                 UserRegionalHeadquarterPosition)
from users.models import RSOUser


class IsStuffOrCentralCommander(BasePermission):
    """Пермишен для админа и командира центрального штаба.

    Роли 'админ' и 'командир центрального штаба' возвращают True.
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

    def has_object_permission(self, request, view, obj):
        """Метод, для проверки доступа к эндпоинтам отряда.

        check_roles - проверяет http-методы пользователя или роли.
        """

        user_id = request.user.id
        check_model_instance = False
        check_local_head = False
        check_edu_head = False
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
        check_roles = any([
            is_safe_method(request),
            is_stuff_or_central_commander(request),
            check_trusted_for_detachments(request, obj)
        ])
        return any([
            check_roles,
            check_model_instance,
            check_local_head,
            check_edu_head
        ])


class IsStuffOrAuthor(BasePermission):
    """Пермишен для стаффа и автора.

    Роли 'is stuff', 'is superuser', 'командир' и 'автор' возвращают True.
    Остальные пользователи получают True, если обращаются к эндпоинту
    с безопасным запросом (GET, HEAD, OPTIONS).
    """

    def has_object_permission(self, request, view, obj):
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
                roles_models=roles_models
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
        reg_headquarter = get_object_or_404(
            RegionalHeadquarter, region=user_to_verify_region
        )

        if reg_headquarter.commander == user:
            return True

        try:
            reg_headquarter_member = (
                UserRegionalHeadquarterPosition.
                objects.get(user=user, headquarter=reg_headquarter)
            )
        except UserRegionalHeadquarterPosition.DoesNotExist:
            reg_headquarter_member = None

        if reg_headquarter_member:
            if reg_headquarter_member.is_trusted:
                return True

        try:
            user_in_detachment = UserDetachmentPosition.objects.get(
                user=user_to_verify
            )
        except UserDetachmentPosition.DoesNotExist:
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
        except UserRegionalHeadquarterPosition.DoesNotExist:
            return False

        if reg_headquarter.commander == user:
            return True

        try:
            reg_headquarter_member = (
                UserRegionalHeadquarterPosition.
                objects.get(user=user, headquarter=reg_headquarter)
            )
        except UserRegionalHeadquarterPosition.DoesNotExist:
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
                {'detail': 'Поле ids не может быть пустым.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            commander_regheadquarter_id = RegionalHeadquarter.objects.filter(
                commander_id=request_user_id
            ).first().id
            for id in ids:
                if id == 0:
                    return Response(
                        {'detail': 'Поле ids не может содержать 0.'},
                    )
                user_reghead_id = UserRegionalHeadquarterPosition.objects.get(
                    user_id=id
                ).headquarter_id
                if user_reghead_id != commander_regheadquarter_id:
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
