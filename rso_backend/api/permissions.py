from rest_framework.permissions import BasePermission, SAFE_METHODS

from api.constants import STUFF_LIST


def is_safe_method(request):
    return request.method in SAFE_METHODS


def is_admin_or_central_commander(request):
    return (
        request.user.is_authenticated
        and request.user.users_role.role == 'admin'
        or request.user.users_role.role == 'central_commander'
        or request.user.is_superuser
    )


def is_users_region(request, view):
    """Проверка региона пользователя.

    При  запросе пользователя к эндпоинту проверяет регион пользователя.
    Если регион совпал с регионом штаба/отряда, возвращает True.
    """

    request.user.region == view.get_object().region


class IsAdminOrCentralCommander(BasePermission):
    """Пермишен для админа и командира центрального штаба.

    Роли 'админ' и 'командир центрального штаба' возвращают True.
    Остальные пользователи получают True, если обращаются к эндпоинту
    с безопасным запросом (GET, HEAD, OPTIONS).
    """

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
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
        return request.method in SAFE_METHODS or (
            request.user.is_superuser
            or request.user.users_role.role in STUFF_LIST
            or request.user == obj.user
        )


class IsRegionalCommander(BasePermission):
    """Пермишен для командира окружного штаба.

    Роль 'админ' всегде возвращается True. Роли 'командир окружного штаба' и
    'доверенный пользователь' возвращают True, если редактируют свой штаб
    или штабы ниже из своего региона.
    Остальные пользователи получают True, если обращаются к эндпоинту
    с безопасным запросом (GET, HEAD, OPTIONS).
    """

    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or is_admin_or_central_commander(request)
            or request.user.users_role.role == 'regional_commander'
        ) and is_users_region(request, view)
