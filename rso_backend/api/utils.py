import mimetypes
import os
import shutil

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http.response import HttpResponse
from rest_framework import serializers
from rest_framework.permissions import SAFE_METHODS


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

    if request.user.region == view.get_object().region:
        return True
    return False


def check_roles_save(role, roles_with_rights, serializer):
    if role in roles_with_rights:
        return serializer.save()
    raise ValidationError(
            'У Вас нет прав для создания этой структурной единицы.'
        )
