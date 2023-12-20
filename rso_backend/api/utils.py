import mimetypes
import os
import shutil

from django.db import IntegrityError
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.permissions import SAFE_METHODS

from headquarters.models import (UserDistrictHeadquarterPosition,
                                 UserEducationalHeadquarterPosition,
                                 UserLocalHeadquarterPosition,
                                 UserRegionalHeadquarterPosition,
                                 UserDetachmentPosition,
                                 CentralHeadquarter)


def create_first_or_exception(self, validated_data, instance, error_msg: str):
    """
    Создает запись или выводит исключение, если уже есть связанная
    с пользователем запись.
    """
    try:
        return instance.objects.create(**validated_data)
    except IntegrityError:
        raise serializers.ValidationError({'detail': error_msg})


def check_folder_delete(instance):
    """
    Функция для проверки существования папки с файлами
    при удалении объекта модели штаба/оттряда.
    """
    try:
        shutil.rmtree(os.path.dirname(instance.emblem.path))
    except ValueError:
        return


def check_folder_delete_usermedia(instance):
    """
    Функция для проверки существования папки с файлами
    при удалении объекта модели юзера.
    """
    try:
        shutil.rmtree(os.path.dirname(instance.banner.path))
    except ValueError:
        return


def download_file(filepath, filename):
    """Функция скачивания бланков заявлений.

    На вход получает путь до файла и имя файла.
    """

    path = open(filepath, 'r')
    mime_type, _ = mimetypes.guess_type(filepath)
    response = HttpResponse(path, content_type=mime_type)
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    return response


def is_safe_method(request):
    """Проверка методов пользователя при запросе к эндпоинту.

    Безопасные возвращают True.
    """

    return request.method in SAFE_METHODS


def is_stuff_or_central_commander(request):
    """Проверка роли пользователя.

    При  запросе пользователя к эндпоинту проверяет роль пользователя.
    Если роль совпал с ролью админа или цомандира ЦШ, возвращает True.
    """

    check_central_commander = False
    try:
        commander_id = CentralHeadquarter.objects.get(
            commander_id=request.user.id
        ).commander_id
        if request.user.id == commander_id:
            check_central_commander = True
        return (request.user.is_authenticated
                and any([
                    check_central_commander,
                    request.user.is_superuser,
                    request.user.is_staff
                ]))
    except CentralHeadquarter.DoesNotExist:
        return False


def check_role_get(request, model, position_in_quarter):
    """Проверка роли пользователя.

    model - модель 'Члены штаба'/'Члены отряда',
    в котором проверяется должность пользователя.
    request - запрос к эндпоинту
    position_in_quarter - требуемая должность для получения True.
    """

    try:
        user_headquarter_object = model.objects.get(user_id=request.user.id)
        position_name = (
            user_headquarter_object.position.name
            if user_headquarter_object.position else None
        )
    except model.DoesNotExist:
        return False
    return (
        request.user.is_authenticated and position_name == position_in_quarter
    )


def check_trusted_user(request, model, obj):
    """Проверка доверенного пользователя.

    model - модель штаба/отряда, в котором проверяется статус доверенности.
    request - запрос к эндпоинту.
    Функция проверяет является ли пользователь доверенным
    в той структурной единице, к которой пользователь сделал запрос.
    """

    try:
        member = model.objects.filter(
            user_id=request.user.id,
            headquarter_id=obj.id
        ).first()
        is_trusted = member.is_trusted
    except AttributeError:
        return False
    return (
        request.user.is_authenticated and is_trusted
    )


def check_trusted_for_detachments(request, obj):
    """Проверка доверенного пользователя для отряда.

    request - запрос к эндпоинту.
    obj - отряд, к которому пользователь сделал запрос.
    Управлять отрядом может любой доверенный пользователь из отряда
    или из штабов. Функция проверяет существует ли запись о юзере
    в штабах выше и если существует, то возвращает статус доверенности.
    """

    detachment_trusted = False
    regional_trusted = district_trusted = False
    user_id = request.user.id
    detachment_position = UserDetachmentPosition.objects.filter(
        headquarter_id=obj.id,
        user_id=user_id
    )
    try:
        headquarter_id = obj.educational_headquarter.id
        edu_position = UserEducationalHeadquarterPosition.objects.get(
            headquarter_id=headquarter_id,
            user_id=user_id
        )
        edu_trusted = edu_position.first().is_trusted
    except (UserEducationalHeadquarterPosition.DoesNotExist, AttributeError):
        edu_trusted = False
    try:
        headquarter_id = obj.local_headquarter.id
        local_position = UserLocalHeadquarterPosition.objects.get(
            headquarter_id=headquarter_id,
            user_id=user_id
        )
        local_trusted = local_position.first().is_trusted
    except (UserLocalHeadquarterPosition.DoesNotExist, AttributeError):
        local_trusted = False
    regional_position = UserRegionalHeadquarterPosition.objects.filter(
        headquarter_id=obj.regional_headquarter.id,
        user_id=user_id
    )
    district_position = UserDistrictHeadquarterPosition.objects.filter(
        headquarter_id=obj.regional_headquarter.district_headquarter.id,
    )
    if detachment_position.exists():
        detachment_trusted = detachment_position.first().is_trusted
    if regional_position.exists():
        regional_trusted = regional_position.first().is_trusted
    if district_position.exists():
        district_trusted = district_position.first().is_trusted

    return any([
        detachment_trusted,
        edu_trusted,
        local_trusted,
        regional_trusted,
        district_trusted
    ])


def check_trusted_for_eduhead(request, obj):
    """Проверка доверенного пользователя для Образовательного Штаба.

    request - запрос к эндпоинту.
    obj - штаб, к которому пользователь сделал запрос.
    Управлять Обр. штабом может любой доверенный пользователь из штабов выше.
    Функция проверяет существует ли запись о юзере
    в штабах выше и если существует, то возвращает статус доверенности.
    """

    edu_trusted = False
    regional_trusted = district_trusted = False
    user_id = request.user.id
    user_id = request.user.id
    edu_position = UserEducationalHeadquarterPosition.objects.filter(
        headquarter_id=obj.id,
        user_id=user_id
    )
    try:
        headquarter_id = obj.local_headquarter.id
        local_position = UserLocalHeadquarterPosition.objects.get(
            headquarter_id=headquarter_id,
            user_id=user_id
        )
        local_trusted = local_position.first().is_trusted
    except (UserLocalHeadquarterPosition.DoesNotExist, AttributeError):
        local_trusted = False
    regional_position = UserRegionalHeadquarterPosition.objects.filter(
        headquarter_id=obj.regional_headquarter.id,
        user_id=user_id
    )
    district_position = UserDistrictHeadquarterPosition.objects.filter(
        headquarter_id=obj.regional_headquarter.district_headquarter.id,
    )
    if edu_position.exists():
        edu_trusted = edu_position.first().is_trusted
    if regional_position.exists():
        regional_trusted = regional_position.first().is_trusted
    if district_position.exists():
        district_trusted = district_position.first().is_trusted
    return any([
        edu_trusted,
        local_trusted,
        regional_trusted,
        district_trusted
    ])


def check_trusted_for_localhead(request, obj):
    """Проверка доверенного пользователя для Местного Штаба.

    request - запрос к эндпоинту.
    obj - штаб, к которому пользователь сделал запрос.
    Управлять МШ может любой доверенный пользователь из штабов выше.
    Функция проверяет существует ли запись о юзере
    в штабах выше и если существует, то возвращает статус доверенности.
    """

    local_trusted = regional_trusted = district_trusted = False
    user_id = request.user.id
    local_position = UserLocalHeadquarterPosition.objects.filter(
        headquarter_id=obj.id,
        user_id=user_id
    )
    regional_position = UserRegionalHeadquarterPosition.objects.filter(
        headquarter_id=obj.regional_headquarter.id,
        user_id=user_id
    )
    district_position = UserDistrictHeadquarterPosition.objects.filter(
        headquarter_id=obj.regional_headquarter.district_headquarter.id,
    )
    if local_position.exists():
        local_trusted = local_position.first().is_trusted
    if regional_position.exists():
        regional_trusted = regional_position.first().is_trusted
    if district_position.exists():
        district_trusted = district_position.first().is_trusted
    return any([
        local_trusted,
        regional_trusted,
        district_trusted
    ])


def check_trusted_for_regionalhead(request, obj):
    """Проверка доверенного пользователя для Регионального Штаба.

    request - запрос к эндпоинту.
    obj - штаб, к которому пользователь сделал запрос.
    Управлять РШ может любой доверенный пользователь из Окружного Штаба.
    Функция проверяет существует ли запись о юзере
    в Окружном штабе и если существует, то возвращает статус доверенности.
    """

    regional_trusted = district_trusted = False
    user_id = request.user.id
    regional_position = UserRegionalHeadquarterPosition.objects.filter(
        headquarter_id=obj.id,
        user_id=user_id
    )
    district_position = UserDistrictHeadquarterPosition.objects.filter(
        headquarter_id=obj.district_headquarter.id,
    )
    if regional_position.exists():
        regional_trusted = regional_position.first().is_trusted
    if district_position.exists():
        district_trusted = district_position.first().is_trusted
    return any([
        regional_trusted,
        district_trusted
    ])


def check_trusted_for_districthead(request, obj):
    """Проверка доверенного пользователя для Окружного Штаба.

    request - запрос к эндпоинту.
    obj - штаб, к которому пользователь сделал запрос.
    Функция проверяет существует ли запись о юзере
    в Окружном штабе и если существует, то возвращает статус доверенности.
    """

    district_trusted = False
    user_id = request.user.id
    district_position = UserDistrictHeadquarterPosition.objects.filter(
        headquarter_id=obj.id,
        user_id=user_id
    )
    if district_position.exists():
        district_trusted = district_position.first().is_trusted
    return district_trusted


def check_roles_for_edit(request, roles_models: dict):
    """Проверка нескольких ролей.

    Аргумент  'roles_models' - словарь.
    Ключ - должность пользователя, для которой функция вернет True.
    models - список моделей 'Члены отряда/штаба',
    в которых проверяем должность пользователя из списка выше.
    """
    for role, model in roles_models.items():
        if check_role_get(request, model, role):
            return True
    return False


def check_trusted_in_headquarters(request, roles_models: dict, obj):
    """Проверка на наличие флага 'доверенный пользователь'.

    Проверка производится по моделям, указанным в словаре 'roles_models'
    """

    for _, model in roles_models.items():
        if check_trusted_user(request, model, obj):
            return True


def get_headquarter_users_positions_queryset(self,
                                             headquarter_instance,
                                             headquarter_position_instance):
    """
    Получение отфильтрованного запроса для должностей пользователей внутри
    конкретного штаба.

    Эта функция возвращает запрос для должностей пользователей внутри
    указанного штаба.
    Она предназначена для использования внутри viewset'ов для фильтрации и
    получения должностей пользователей
    на основе предоставленных `headquarter_instance` и
    `headquarter_position_instance`.

    Параметры:
    - `self`: Экземпляр viewset'а, который вызывает эту функцию.
    - `headquarter_instance`: Класс модели для штаба (например,
       CentralHeadquarter).
    - `headquarter_position_instance`: Класс модели для должности в штабе (
    например, UserCentralHeadquarterPosition).

    Возвращает:
    - Отфильтрованный запрос для должностей пользователей в указанном штабе.

    Пример использования внутри viewset'а:
    ```
    queryset = self.get_headquarter_users_positions(
        CentralHeadquarter, UserCentralHeadquarterPosition
    )
    return self.filter_by_name(queryset)
    ```
    """

    headquarter_id = self.kwargs.get('pk')
    headquarter = get_object_or_404(headquarter_instance, id=headquarter_id)
    queryset = headquarter_position_instance.objects.filter(
        headquarter=headquarter
    )
    return self.filter_by_name(queryset)
