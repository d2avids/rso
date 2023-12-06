import mimetypes

from django.db import IntegrityError
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import serializers


def create_first_or_exception(self, validated_data, instance, error_msg: str):
    """
    Создает запись или выводит исключение, если уже есть связанная
    с пользователем запись.
    """
    try:
        return instance.objects.create(**validated_data)
    except IntegrityError:
        raise serializers.ValidationError({'detail': error_msg})


def download_file(filepath, filename):
    """Функция скачивания бланков заявлений.

    На вход получает путь до файла и имя файла.
    """

    path = open(filepath, 'r')
    mime_type, _ = mimetypes.guess_type(filepath)
    response = HttpResponse(path, content_type=mime_type)
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    return response


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
