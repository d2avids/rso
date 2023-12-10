from rest_framework.permissions import BasePermission


from api.utils import (is_stuff_or_central_commander, is_safe_method,
                       check_role_get, check_trusted_user,
                       check_roles_with_rights, check_trusted_in_headquarters)
from headquarters.models import (UserDistrictHeadquarterPosition,
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
        )


class IsDistrictCommander(BasePermission):
    """Пермишен для командира окружного штаба.

    Для ролей 'is stuff' и 'superuser возвращается True.
    Роль 'командир окружного штаба' и 'доверенный пользователь'
    возвращают True,если редактируют штабы ниже своего.
    Остальные пользователи получают True, если обращаются к эндпоинту
    с безопасным запросом (GET, HEAD, OPTIONS).
    """

    def has_permission(self, request, view):
        """Метод, для проверки доступа к эндпоинтам ОШ.

        check_roles - проверяет http-методы пользователя или роли.
        """

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
        return check_roles


class IsRegionalCommander(BasePermission):
    """Пермишен для командира регионального штаба.

    Для ролей 'is stuff' и 'superuser возвращается True.
    Роль 'командир регионального штаба' и 'доверенный пользователь'
    возвращают True,если редактируют штабы ниже своего.
    Остальные пользователи получают True, если обращаются к эндпоинту
    с безопасным запросом (GET, HEAD, OPTIONS).
    """

    def has_permission(self, request, view):
        """Метод, для проверки доступа к эндпоинтам РШ.

        check_roles - проверяет http-методы пользователя или роли.
        """

        roles_with_rights = [
            'district_commander',
            'regional_commander',
        ]
        models = [
            UserDistrictHeadquarterPosition,
            UserRegionalHeadquarterPosition,
        ]
        check_roles = (
                is_safe_method(request)
                or is_stuff_or_central_commander(request)
                or check_roles_with_rights(
                    request=request,
                    roles_with_rights=roles_with_rights,
                    models=models
                )
                or check_trusted_in_headquarters(
                    request=request,
                    headquarters=models
                )
        )
        return check_roles


class IsLocalCommander(BasePermission):
    """Пермишен для командира местного штаба.

    Для ролей 'is stuff' и 'superuser возвращается True.
    Роль 'командир местного штаба' и 'доверенный пользователь'
    возвращают True,если редактируют штабы ниже своего.
    Остальные пользователи получают True, если обращаются к эндпоинту
    с безопасным запросом (GET, HEAD, OPTIONS).
    """

    def has_permission(self, request, view):
        """Метод, для проверки доступа к эндпоинтам МШ.

        check_roles - проверяет http-методы пользователя или роли.
        """

        roles_with_rights = [
            'district_commander',
            'regional_commander',
            'local_commander',
        ]
        models = [
            UserDistrictHeadquarterPosition,
            UserRegionalHeadquarterPosition,
            UserLocalHeadquarterPosition,
        ]
        check_roles = (
                is_safe_method(request)
                or is_stuff_or_central_commander(request)
                or check_roles_with_rights(
                    request=request,
                    roles_with_rights=roles_with_rights,
                    models=models
                )
                or check_trusted_in_headquarters(
                    request=request,
                    headquarters=models
                )
        )
        return check_roles


class IsEducationalCommander(BasePermission):
    """Пермишен для командира образовательного штаба.

    Для ролей 'is stuff' и 'superuser возвращается True.
    Роль 'командир образовательного штаба' и 'доверенный пользователь'
    возвращают True,если редактируют штабы ниже своего.
    Остальные пользователи получают True, если обращаются к эндпоинту
    с безопасным запросом (GET, HEAD, OPTIONS).
    """

    def has_permission(self, request, view):
        """Метод, для проверки доступа к эндпоинтам ШОО.

        check_roles - проверяет http-методы пользователя или роли.
        """

        roles_with_rights = [
            'district_commander',
            'regional_commander',
            'local_commander',
            'edu_commander',
        ]
        models = [
            UserDistrictHeadquarterPosition,
            UserRegionalHeadquarterPosition,
            UserLocalHeadquarterPosition,
            UserEducationalHeadquarterPosition,
        ]
        check_roles = (
                is_safe_method(request)
                or is_stuff_or_central_commander(request)
                or check_roles_with_rights(
                    request=request,
                    roles_with_rights=roles_with_rights,
                    models=models
                )
                or check_trusted_in_headquarters(
                    request=request,
                    headquarters=models
                )
        )
        return check_roles


class IsDetachmentCommander(BasePermission):
    """Пермишен для командира отряда.

    Для ролей 'is stuff' и 'superuser возвращается True.
    Роль 'командир отряда' и 'доверенный пользователь'
    возвращают True,если редактируют штабы ниже своего.
    Остальные пользователи получают True, если обращаются к эндпоинту
    с безопасным запросом (GET, HEAD, OPTIONS).
    """

    def has_permission(self, request, view):
        """Метод, для проверки доступа к эндпоинтам отряда.

        check_roles - проверяет http-методы пользователя или роли.
        """

        roles_with_rights = [
            'district_commander',
            'regional_commander',
            'local_commander',
            'edu_commander',
            'detachment_commander'
        ]
        models = [
            UserDistrictHeadquarterPosition,
            UserRegionalHeadquarterPosition,
            UserLocalHeadquarterPosition,
            UserEducationalHeadquarterPosition,
            UserDetachmentPosition
        ]
        check_roles = (
                is_safe_method(request)
                or is_stuff_or_central_commander(request)
                or check_roles_with_rights(
                    request=request,
                    roles_with_rights=roles_with_rights,
                    models=models
                )
                or check_trusted_in_headquarters(
                    request=request,
                    headquarters=models
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
        roles_with_rights = [
            'district_commander',
            'regional_commander',
            'local_commander',
            'edu_commander',
            'detachment_commander'
        ]
        models = [
            UserDistrictHeadquarterPosition,
            UserRegionalHeadquarterPosition,
            UserLocalHeadquarterPosition,
            UserEducationalHeadquarterPosition,
            UserDetachmentPosition
        ]
        check_roles = (
                is_safe_method(request)
                or is_stuff_or_central_commander(request)
                or check_roles_with_rights(
                    request=request,
                    roles_with_rights=roles_with_rights,
                    models=models
                )
                or check_trusted_in_headquarters(
                    request=request,
                    headquarters=models
                )
        )
        print(request.user == obj.user, request.user, obj.user)
        return is_safe_method(request) or (
            request.user.is_superuser
            or request.user == obj.user
            or check_roles
        )
