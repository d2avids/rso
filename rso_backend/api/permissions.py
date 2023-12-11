from rest_framework.permissions import BasePermission


from api.utils import (is_stuff_or_central_commander, is_safe_method,
                       check_role_get, check_trusted_user,
                       check_trusted_in_headquarters, check_roles_for_edit, check_users_headqurter)
from headquarters.models import (UserCentralHeadquarterPosition,
                                 UserDistrictHeadquarterPosition,
                                 UserRegionalHeadquarterPosition,
                                 UserLocalHeadquarterPosition,
                                 UserEducationalHeadquarterPosition,
                                 UserDetachmentPosition)


class IsStuffOrCentralCommander(BasePermission):
    """Пермишен для админа и командира центрального штаба.

    Роли 'админ' и 'командир центрального штаба' возвращают True.
    Остальные пользователи получают True, если обращаются к эндпоинту
    с безопасным запросом (GET, HEAD, OPTIONS).
    """

    def has_permission(self, request, view):
        return (
            is_safe_method(request)
            or is_stuff_or_central_commander(request)
            or check_trusted_user(
                request=request,
                model=UserCentralHeadquarterPosition
            )
        )


class IsDistrictCommander(BasePermission):
    """Пермишен для командира окружного штаба.

    Для ролей 'is stuff' и 'superuser' возвращается True.
    Роль 'командир окружного штаба' и 'доверенный пользователь'
    возвращают True, если редактируют свой штаб и штабы ниже своего.
    Остальные пользователи получают True, если обращаются к эндпоинту
    с безопасным запросом (GET, HEAD, OPTIONS).
    """

    # def has_permission(self, request, view):
    #     """Метод, для проверки доступа к эндпоинтам ОШ.

    #     check_roles - проверяет http-методы пользователя или роли.
    #     """

    #     check_roles = (
    #             is_safe_method(request)
    #             or is_stuff_or_central_commander(request)
    #             or check_role_get(
    #                 request=request,
    #                 model=UserDistrictHeadquarterPosition,
    #                 position_in_quarter='district_commander'
    #             )
    #             or check_trusted_user(
    #                 request=request,
    #                 model=UserDistrictHeadquarterPosition
    #             )
    #     )
    #     return check_roles

    def has_object_permission(self, request, view, obj):
        check_roles = (
                is_safe_method(request)
                or is_stuff_or_central_commander(request)
                or check_role_get(
                    request=request,
                    model=UserDistrictHeadquarterPosition,
                    position_in_quarter='district_commander'
                )
                or check_trusted_user(
                    request=request,
                    model=UserDistrictHeadquarterPosition
                )
        )
        return is_safe_method(request) or (
            request.user.is_superuser
            or check_users_headqurter(
                request,
                UserDistrictHeadquarterPosition,
                obj
            )
            or check_roles
        )


class IsRegionalCommander(BasePermission):
    """Пермишен для командира регионального штаба.

    Для ролей 'is stuff' и 'superuser' возвращается True.
    Роль 'командир регионального штаба' и 'доверенный пользователь'
    возвращают True, если редактируют свой штаб и штабы ниже своего.
    Остальные пользователи получают True, если обращаются к эндпоинту
    с безопасным запросом (GET, HEAD, OPTIONS).
    """

    def has_permission(self, request, view):
        """Метод, для проверки доступа к эндпоинтам РШ.

        check_roles - проверяет http-методы пользователя или роли.
        """

        roles_models = {
            'district_commander': UserDistrictHeadquarterPosition,
            'regional_commander': UserRegionalHeadquarterPosition,
        }
        check_roles = (
                is_safe_method(request)
                or is_stuff_or_central_commander(request)
                or check_roles_for_edit(
                    request=request,
                    roles_models=roles_models,
                )
                or check_trusted_in_headquarters(
                    request=request,
                    roles_models=roles_models
                )
        )
        return check_roles


class IsLocalCommander(BasePermission):
    """Пермишен для командира местного штаба.

    Для ролей 'is stuff' и 'superuser возвращается True.
    Роль 'командир местного штаба' и 'доверенный пользователь'
    возвращают True, если редактируют свой штаб и штабы ниже своего.
    Остальные пользователи получают True, если обращаются к эндпоинту
    с безопасным запросом (GET, HEAD, OPTIONS).
    """

    def has_permission(self, request, view):
        """Метод, для проверки доступа к эндпоинтам МШ.

        check_roles - проверяет http-методы пользователя или роли.
        """

        roles_models = {
            'district_commander': UserDistrictHeadquarterPosition,
            'regional_commander': UserRegionalHeadquarterPosition,
            'local_commander': UserLocalHeadquarterPosition,
        }
        check_roles = (
                is_safe_method(request)
                or is_stuff_or_central_commander(request)
                or check_roles_for_edit(
                    request=request,
                    roles_models=roles_models,
                )
                or check_trusted_in_headquarters(
                    request=request,
                    roles_models=roles_models
                )
        )
        return check_roles


class IsEducationalCommander(BasePermission):
    """Пермишен для командира образовательного штаба.

    Для ролей 'is stuff' и 'superuser' возвращается True.
    Роль 'командир образовательного штаба' и 'доверенный пользователь'
    возвращают True, если редактируют свой штаб и штабы ниже своего.
    Остальные пользователи получают True, если обращаются к эндпоинту
    с безопасным запросом (GET, HEAD, OPTIONS).
    """

    def has_permission(self, request, view):
        """Метод, для проверки доступа к эндпоинтам ШОО.

        check_roles - проверяет http-методы пользователя или роли.
        """

        roles_models = {
            'district_commander': UserDistrictHeadquarterPosition,
            'regional_commander': UserRegionalHeadquarterPosition,
            'local_commander': UserLocalHeadquarterPosition,
            'edu_commander': UserEducationalHeadquarterPosition,
        }
        check_roles = (
                is_safe_method(request)
                or is_stuff_or_central_commander(request)
                or check_roles_for_edit(
                    request=request,
                    roles_models=roles_models,
                )
                or check_trusted_in_headquarters(
                    request=request,
                    roles_models=roles_models
                )
        )
        return check_roles


class IsDetachmentCommander(BasePermission):
    """Пермишен для командира отряда.

    Для ролей 'is stuff' и 'superuser' возвращается True.
    Роль 'командир отряда' и 'доверенный пользователь'
    возвращают True, если редактируют свой штаб и штабы ниже своего.
    Остальные пользователи получают True, если обращаются к эндпоинту
    с безопасным запросом (GET, HEAD, OPTIONS).
    """

    def has_permission(self, request, view):
        """Метод, для проверки доступа к эндпоинтам отряда.

        check_roles - проверяет http-методы пользователя или роли.
        """

        roles_models = {
            'district_commander': UserDistrictHeadquarterPosition,
            'regional_commander': UserRegionalHeadquarterPosition,
            'local_commander': UserLocalHeadquarterPosition,
            'edu_commander': UserEducationalHeadquarterPosition,
            'detachment_commander': UserDetachmentPosition,
        }
        check_roles = (
                is_safe_method(request)
                or is_stuff_or_central_commander(request)
                or check_roles_for_edit(
                    request=request,
                    roles_models=roles_models,
                )
                or check_trusted_in_headquarters(
                    request=request,
                    roles_models=roles_models
                )
        )
        return check_roles


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
        check_roles = (
                is_safe_method(request)
                or is_stuff_or_central_commander(request)
                or check_roles_for_edit(
                    request=request,
                    roles_models=roles_models,
                )
                or check_trusted_in_headquarters(
                    request=request,
                    roles_models=roles_models
                )
        )
        return is_safe_method(request) or (
            request.user.is_superuser
            or request.user == obj.user
            or check_roles
        )
