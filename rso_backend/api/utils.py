import io
import mimetypes
import zipfile
from datetime import datetime

from django.db import IntegrityError
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.permissions import SAFE_METHODS

from users.models import RSOUser
from headquarters.models import (CentralHeadquarter,
                                 UserRegionalHeadquarterPosition,
                                 UserDistrictHeadquarterPosition)


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


def get_user(self):
    user_id = self.kwargs.get('pk', None)
    user = get_object_or_404(
        RSOUser, id=user_id
    ) if user_id else self.request.user
    return user


def get_user_by_id(id):
    user = get_object_or_404(
        RSOUser, id=id
    )
    return user


def text_to_lines(text, proportion):
    """Функция разбивает текст на строки по заданной доле ширины."""

    text_length = len(text)
    text_list = text.split()
    lines = []
    line = ''
    for word in text_list:
        if len(line) + len(word) > text_length * proportion:
            lines.append(line)
            line = word + ' '
        else:
            line += word + ' '
    lines.append(line)
    return lines


def create_and_return_archive(files: dict):
    """Функция создает архив и возвращает его с указанными файлами."""

    archive_buffer = io.BytesIO()
    with zipfile.ZipFile(archive_buffer, 'w') as archive:
        for file_name, file_content in files.items():
            archive.writestr(file_name, file_content)

    archive_buffer.seek(0)
    response = HttpResponse(
        archive_buffer.read(), content_type='application/zip'
    )
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f'certs_{current_datetime}.zip'
    response['Content-Disposition'] = (
        f'attachment; filename={filename}'
    )
    return response
