from rest_framework.permissions import BasePermission


from api.utils import (is_stuff_or_central_commander, is_safe_method,
                       check_trusted_for_regionalhead)
from headquarters.models import (RegionalHeadquarter,
                                 UserRegionalHeadquarterPosition)
from users.models import UserCertInternal, UserCertExternal


class IsRegionalCommanderCert(BasePermission):
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
