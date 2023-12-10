import mimetypes
import os
import shutil

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.permissions import SAFE_METHODS

from headquarters.models import UserCentralHeadquarterPosition


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
    при удалении объекта модели.
    """
    try:
        folder_path = os.path.dirname(instance.emblem.path)
        shutil.rmtree(folder_path)
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
    return request.method in SAFE_METHODS


def is_stuff_or_central_commander(request):
    """Проверка роли пользователя.

    При  запросе пользователя к эндпоинту проверяет роль пользователя.
    Если роль совпал с ролью админа или цомандира ЦШ, возвращает True.
    """

    user_id = request.user.id
    position_name = ''
    try:
        user = UserCentralHeadquarterPosition.objects.get(user_id=user_id)
        position_name = user.position.name if user.position else None
    except UserCentralHeadquarterPosition.DoesNotExist:
        return False
    return (request.user.is_authenticated
            and (
                position_name == 'central_commander'
                or request.user.is_superuser
                or request.user.is_staff
            ))


def check_role_get(request, model, position_in_quarter):
    """Проверка роли пользователя.

    model - модель штаба/отряда, в котором проверяется должность пользователя.
    requst - запрос к эндпоинту
    position_in_quarter - требуемая должность для получения True.
    """

    user_id = request.user.id
    position_name = ''
    try:
        user = model.objects.get(user_id=user_id)
        position_name = user.position.name if user.position else None
    except model.DoesNotExist:
        return False
    return (
        request.user.is_authenticated and position_name == position_in_quarter
    )


def check_trusted_user(request, model):
    """Проверка доверенного пользователя.

    model - модель штаба/отряда, в котором проверяется статус доверенности.
    requst - запрос к эндпоинту
    """

    user_id = request.user.id
    try:
        user = model.objects.get(user_id=user_id)
        is_trusted = user.is_trusted
    except model.DoesNotExist:
        return False
    return (
        request.user.is_authenticated and is_trusted
    )


def check_roles_with_rights(request, roles_with_rights, models):

    for counter in range(len(roles_with_rights)):
        role = roles_with_rights[counter]
        model = models[counter]
        if check_role_get(request, model, role):
            return True
    return False


def check_trusted_in_headquarters(request, headquarters):

    for headquarter in headquarters:
        if check_trusted_user(request, headquarter):
            return True


def check_roles_save(role, roles_with_rights, serializer):
    if role in roles_with_rights:
        return serializer.save()
    raise ValidationError(
            'У Вас нет прав для создания этой структурной единицы.'
        )


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
