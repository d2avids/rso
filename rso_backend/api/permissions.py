from rest_framework.permissions import BasePermission

from api.constants import STUFF_LIST
from api.utils import is_admin_or_central_commander, is_safe_method


class IsAdminOrCentralCommander(BasePermission):
    """Пермишен для админа и командира центрального штаба.

    Роли 'админ' и 'командир центрального штаба' возвращают True.
    Остальные пользователи получают True, если обращаются к эндпоинту
    с безопасным запросом (GET, HEAD, OPTIONS).
    """

    def has_permission(self, request, view):
        return (
            is_safe_method(request)
            or is_admin_or_central_commander(request)
        )


class IsStuffOrAuthor(BasePermission):
    """Пермишен для стаффа и автора.

    Роли 'админ', 'командир' и 'доверенный пользователь' возвращают True.
    Остальные пользователи получают True, если обращаются к эндпоинту
    с безопасным запросом (GET, HEAD, OPTIONS).
    """

    def has_object_permission(self, request, view, obj):
        print(obj)
        return is_safe_method(request) or (
            request.user.is_superuser
            or request.user.users_role.role in STUFF_LIST
            or request.user == obj.user
        )


class IsDistrictCommander(BasePermission):
    """Пермишен для командира окружного штаба.

    Роль 'админ' всегда возвращается True. Роли 'командир ОШ' и
    'доверенный пользователь' возвращают True, если редактируют свой район
    или районы ниже из своего региона.
    Остальные пользователи получают True, если обращаются к эндпоинту
    с безопасным запросом (GET, HEAD, OPTIONS).
    """

    def has_permission(self, request, view):
        """Метод, для проверки доступа к эндпоинтам ОШ.

        check_roles - проверяет http-методы пользователя или роли.
        """

        check_roles = (
                is_safe_method(request)
                or is_admin_or_central_commander(request)
                or request.user.users_role.role == 'district_commander'
        )
        return check_roles


class IsRegionalCommander(BasePermission):
    """Пермишен для командира регионального штаба.

    Роль 'админ' всегде возвращается True. Роли 'командир регионального штаба'
    и 'доверенный пользователь' возвращают True, если редактируют свой штаб
    или штабы ниже из своего региона.
    Остальные пользователи получают True, если обращаются к эндпоинту
    с безопасным запросом (GET, HEAD, OPTIONS).
    """

    def has_permission(self, request, view):
        """Метод, для проверки доступа к эндпоинтам РШ.

        check_roles - проверяет http-методы пользователя или роли.
        """

        check_roles = (
                is_safe_method(request)
                or is_admin_or_central_commander(request)
                or request.user.users_role.role == 'regional_commander'
            )
        return check_roles
