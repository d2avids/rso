from rest_framework.permissions import BasePermission


from api.utils import (is_stuff_or_central_commander, is_safe_method)
from headquarters.models import (RegionalHeadquarter,
                                 UserRegionalHeadquarterPosition)


class IsRegionalCommanderForCert(BasePermission):
    """Пермишен для командира регионального штаба.

    Для ролей 'is stuff' и 'superuser' возвращается True.
    Роль 'командир регионального штаба' и 'доверенный пользователь'
    возвращают True, если редактируют свой штаб и штабы ниже своего.
    Остальные пользователи получают True, если обращаются к эндпоинту
    с безопасным запросом (GET, HEAD, OPTIONS).
    """

    def has_permission(self, request, view):
        """Проверка прав пользователя для выдачи справки."""

        check_model_instance = True
        request_user_id = request.user.id
        ids = request.data.get('ids')
        try:
            commander_regheadquarter_id = RegionalHeadquarter.objects.filter(
                commander_id=request_user_id
            ).first().id
            for id in ids:
                user_reghead_id = UserRegionalHeadquarterPosition.objects.get(
                    user_id=id
                ).headquarter_id
                if user_reghead_id != commander_regheadquarter_id:
                    check_model_instance = False
                    break
        except (RegionalHeadquarter.DoesNotExist, AttributeError):
            check_model_instance = False
        return any([
            is_safe_method(request),
            # is_stuff_or_central_commander(request),
            check_model_instance
        ])
