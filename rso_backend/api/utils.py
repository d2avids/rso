import io
import mimetypes
import zipfile
from datetime import datetime

from django.db import IntegrityError
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.permissions import SAFE_METHODS

from headquarters.models import (CentralHeadquarter, UserDetachmentPosition,
                                 UserDistrictHeadquarterPosition,
                                 UserEducationalHeadquarterPosition,
                                 UserLocalHeadquarterPosition,
                                 UserRegionalHeadquarterPosition,
                                 UserCentralHeadquarterPosition)
from users.models import RSOUser


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


def is_safe_method(request):
    """Проверка методов пользователя при запросе к эндпоинту.

    Безопасные возвращают True.
    """

    return request.method in SAFE_METHODS


def is_stuff_or_central_commander(request):
    """Проверка роли пользователя.

    При запросе пользователя к эндпоинту проверяет роль пользователя.
    Если роль совпала с ролью админа или командира ЦШ, возвращает True.
    """

    check_central_commander = False
    try:
        commander_id = CentralHeadquarter.objects.get(
            commander_id=request.user.id
        ).commander_id
        if request.user.id == commander_id:
            check_central_commander = True
    except (CentralHeadquarter.DoesNotExist, AttributeError):
        return False
    return (request.user.is_authenticated
            and any([
                check_central_commander,
                request.user.is_superuser,
                request.user.is_staff
            ]))


def check_commander_or_not(request, headquarters):
    """Проверка является ли юзер командиром.

    headquarters - список моделей, в которых проверяется роль пользователя.
    request - запрос к эндпоинту
    """

    for headquarter in headquarters:
        try:
            # поменять на get когда добавим валидацию на 1 командира на уровень
            if headquarter.objects.filter(
                commander_id=request.user.id
            ).first().exists():
                return True
            return False
        except (headquarter.DoesNotExist, AttributeError):
            pass
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
    except (model.DoesNotExist, AttributeError):
        return False
    return (
        request.user.is_authenticated and position_name == position_in_quarter
    )


def search_trusted_in_list(user_id, tables_list):
    """Поиск первого доверенного пользователя в списке таблиц.

    tables_list - список таблиц, в котором производится поиск.
    """

    index = 0
    number_of_tables = len(tables_list)
    while index < number_of_tables:
        try:
            if tables_list[index].objects.get(
                user_id=user_id
            ).is_trusted:
                return True
            index += 1
        except (tables_list[index].DoesNotExist, AttributeError):
            index += 1
    return False


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


def check_trusted_for_detachments(request, obj=None):
    """Проверка доверенного пользователя для отряда.

    request - запрос к эндпоинту.
    obj - отряд, к которому пользователь сделал запрос.
    Управлять отрядом может любой доверенный пользователь из отряда
    или из штабов. Функция проверяет существует ли запись о юзере
    в штабах выше и если существует, то возвращает статус доверенности.
    """

    tables_for_check = [
        UserDetachmentPosition,
        UserEducationalHeadquarterPosition,
        UserLocalHeadquarterPosition,
        UserRegionalHeadquarterPosition,
        UserDistrictHeadquarterPosition
    ]
    user_id = request.user.id
    if obj is not None:
        try:
            detachment_trusted = UserDetachmentPosition.objects.get(
                headquarter_id=obj.id,
                user_id=user_id
            ).is_trusted
        except (UserDetachmentPosition.DoesNotExist, AttributeError):
            detachment_trusted = False
        try:
            headquarter_id = obj.educational_headquarter.id
            edu_trusted = UserEducationalHeadquarterPosition.objects.get(
                headquarter_id=headquarter_id,
                user_id=user_id
            ).is_trusted
        except (
            UserEducationalHeadquarterPosition.DoesNotExist, AttributeError
        ):
            edu_trusted = False
        try:
            headquarter_id = obj.local_headquarter.id
            local_trusted = UserLocalHeadquarterPosition.objects.get(
                headquarter_id=headquarter_id,
                user_id=user_id
            ).is_trusted
        except (UserLocalHeadquarterPosition.DoesNotExist, AttributeError):
            local_trusted = False
        try:
            regional_trusted = UserRegionalHeadquarterPosition.objects.get(
                headquarter_id=obj.regional_headquarter.id,
                user_id=user_id
            ).is_trusted
        except (UserRegionalHeadquarterPosition.DoesNotExist, AttributeError):
            regional_trusted = False
        try:
            headquarter_id = obj.regional_headquarter.district_headquarter.id
            district_trusted = UserDistrictHeadquarterPosition.objects.get(
                headquarter_id=headquarter_id,
                user_id=user_id
            ).is_trusted
        except (UserDistrictHeadquarterPosition.DoesNotExist, AttributeError):
            district_trusted = False
        return any([
            detachment_trusted,
            edu_trusted,
            local_trusted,
            regional_trusted,
            district_trusted
        ])
    else:
        return search_trusted_in_list(user_id, tables_for_check)


def check_trusted_for_eduhead(request, obj=None):
    """Проверка доверенного пользователя для Образовательного Штаба.

    request - запрос к эндпоинту.
    obj - штаб, к которому пользователь сделал запрос.
    Управлять Обр. штабом может любой доверенный пользователь из штабов выше.
    Функция проверяет существует ли запись о юзере
    в штабах выше и если существует, то возвращает статус доверенности.
    """

    tables_for_check = [
        UserEducationalHeadquarterPosition,
        UserLocalHeadquarterPosition,
        UserRegionalHeadquarterPosition,
        UserDistrictHeadquarterPosition
    ]
    user_id = request.user.id
    if obj is not None:
        try:
            edu_trusted = UserEducationalHeadquarterPosition.objects.get(
                headquarter_id=obj.id,
                user_id=user_id
            ).is_trusted
        except (
            UserEducationalHeadquarterPosition.DoesNotExist, AttributeError
        ):
            edu_trusted = False
        try:
            headquarter_id = obj.local_headquarter.id
            local_trusted = UserLocalHeadquarterPosition.objects.get(
                headquarter_id=headquarter_id,
                user_id=user_id
            ).is_trusted
        except (UserLocalHeadquarterPosition.DoesNotExist, AttributeError):
            local_trusted = False
        try:
            regional_trusted = UserRegionalHeadquarterPosition.objects.get(
                headquarter_id=obj.regional_headquarter.id,
                user_id=user_id
            ).is_trusted
        except (
            UserRegionalHeadquarterPosition.DoesNotExist, AttributeError
        ):
            regional_trusted = False
        try:
            head_id = obj.regional_headquarter.district_headquarter.id
            district_trusted = UserDistrictHeadquarterPosition.objects.get(
                headquarter_id=head_id,
                user_id=user_id
            ).is_trusted
        except (
            UserDistrictHeadquarterPosition.DoesNotExist, AttributeError
        ):
            district_trusted = False
        return any([
            edu_trusted,
            local_trusted,
            regional_trusted,
            district_trusted
        ])
    else:
        return search_trusted_in_list(user_id, tables_for_check)


def check_trusted_for_localhead(request, obj=None):
    """Проверка доверенного пользователя для Местного Штаба.

    request - запрос к эндпоинту.
    obj - штаб, к которому пользователь сделал запрос.
    Управлять МШ может любой доверенный пользователь из штабов выше.
    Функция проверяет существует ли запись о юзере
    в штабах выше и если существует, то возвращает статус доверенности.
    """

    tables_for_check = [
        UserLocalHeadquarterPosition,
        UserRegionalHeadquarterPosition,
        UserDistrictHeadquarterPosition
    ]
    user_id = request.user.id
    if obj is not None:
        try:
            local_trusted = UserLocalHeadquarterPosition.objects.get(
                headquarter_id=obj.id,
                user_id=user_id
            ).is_trusted
        except (UserLocalHeadquarterPosition.DoesNotExist, AttributeError):
            local_trusted = False
        try:
            regional_trusted = UserRegionalHeadquarterPosition.objects.get(
                headquarter_id=obj.regional_headquarter.id,
                user_id=user_id
            ).is_trusted
        except (UserRegionalHeadquarterPosition.DoesNotExist, AttributeError):
            regional_trusted = False
        try:
            headquarter_id = obj.regional_headquarter.district_headquarter.id
            district_trusted = UserDistrictHeadquarterPosition.objects.get(
                headquarter_id=headquarter_id,
                user_id=user_id
            ).is_trusted
        except (UserDistrictHeadquarterPosition.DoesNotExist, AttributeError):
            district_trusted = False
        return any([
            local_trusted,
            regional_trusted,
            district_trusted
        ])
    else:
        return search_trusted_in_list(user_id, tables_for_check)


def check_trusted_for_regionalhead(request, obj=None):
    """Проверка доверенного пользователя для Регионального Штаба.

    request - запрос к эндпоинту.
    obj - штаб, к которому пользователь сделал запрос.
    Управлять РШ может любой доверенный пользователь из Окружного Штаба.
    Функция проверяет существует ли запись о юзере
    в Окружном штабе и если существует, то возвращает статус доверенности.
    """

    user_id = request.user.id
    if obj is not None:
        try:
            regional_trusted = UserRegionalHeadquarterPosition.objects.get(
                headquarter_id=obj.id,
                user_id=user_id
            ).is_trusted
        except (UserRegionalHeadquarterPosition.DoesNotExist, AttributeError):
            regional_trusted = False
        try:
            district_trusted = UserDistrictHeadquarterPosition.objects.get(
                headquarter_id=obj.district_headquarter.id,
                user_id=user_id
            ).is_trusted
        except (UserDistrictHeadquarterPosition.DoesNotExist, AttributeError):
            district_trusted = False
    else:
        try:
            regional_trusted = UserRegionalHeadquarterPosition.objects.get(
                user_id=user_id
            ).is_trusted
        except (UserRegionalHeadquarterPosition.DoesNotExist, AttributeError):
            regional_trusted = False
        try:
            district_trusted = UserDistrictHeadquarterPosition.objects.get(
                user_id=user_id
            ).is_trusted
        except (UserDistrictHeadquarterPosition.DoesNotExist, AttributeError):
            district_trusted = False
    return any([
        regional_trusted,
        district_trusted
    ])


def check_trusted_for_districthead(request, obj=None):
    """Проверка доверенного пользователя для Окружного Штаба.

    request - запрос к эндпоинту.
    obj - штаб, к которому пользователь сделал запрос.
    Функция проверяет существует ли запись о юзере
    в Окружном штабе и если существует, то возвращает статус доверенности.
    """

    user_id = request.user.id
    if obj is not None:
        try:
            return UserDistrictHeadquarterPosition.objects.get(
                headquarter_id=obj.id,
                user_id=user_id
            ).is_trusted
        except (UserDistrictHeadquarterPosition.DoesNotExist, AttributeError):
            return False
    else:
        try:
            return UserDistrictHeadquarterPosition.objects.get(
                user_id=user_id
            ).is_trusted
        except (UserDistrictHeadquarterPosition.DoesNotExist, AttributeError):
            return False


def check_trusted_for_centralhead(request):
    """Проверка доверенного пользователя для Центрального Штаба.

    request - запрос к эндпоинту.
    Функция проверяет существует ли запись о юзере
    в Центральном штабе и если существует, то возвращает статус доверенности.
    """

    request_user_id = request.user.id
    try:
        return UserCentralHeadquarterPosition.objects.get(
            user_id=request_user_id
        ).is_trusted
    except (
        UserCentralHeadquarterPosition.DoesNotExist,
        AttributeError
    ):
        return False


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
