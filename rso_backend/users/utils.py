import os
import re
import shutil
from datetime import datetime as dt

from django.core.exceptions import ValidationError


def image_path(instance, filename):
    """Функция для формирования пути сохранения изображения.

    :param instance: Экземпляр модели.
    :param filename: Имя файла. Добавляем к имени текущую дату и время.
    :return: Путь к изображению.
    Сохраняем в filepath/{instance.user.name}/filename
    """

    filename = dt.today().strftime('%Y%m%d%H%M%S') + '_' + filename
    filepath = 'images/users'
    return os.path.join(filepath, instance.user.username, filename)


def document_path(instance, filename):
    """Функция для формирования пути сохранения сканов документов юзера.

    :param instance: Экземпляр модели.
    :param filename: Имя файла. Добавляем к имени текущую дату и время.
    :return: Путь к скану документа.
    Сохраняем в filepath/{instance.name}/filename
    """

    filename = dt.today().strftime('%Y%m%d%H%M%S') + '_' + filename
    filepath = 'documents/users'
    print(instance)
    return os.path.join(filepath, instance.user.username, filename)


def validate_years(value):
    """Функция для проверки корректности ввода года обучения."""
    if not re.match(r'^\d{4}-\d{4}$', value):
        raise ValidationError(
            'Ошибка ввода срока обучения. Используйте формат "YYYY-YYYY".'
        )
    start, end = value.split('-')
    if int(start) >= int(end):
        raise ValidationError('Начальный год должен быть меньше конечного.')


def user_image_folder_delete(instance):
    """Функция для удаления папки с изображениями.

    Удаляет папку media для всех моделей - наследников Unit.
    :param instance: Экземпляр модели.
    """

    try:
        banner_path = os.path.dirname(instance.banner.path)
        shutil.rmtree(banner_path)
        return
    except ValueError:
        pass
    try:
        photo_path = os.path.dirname(instance.photo.path)
        shutil.rmtree(photo_path)
        return
    except ValueError:
        pass
    try:
        photo1_path = os.path.dirname(instance.photo1.path)
        shutil.rmtree(photo1_path)
        return
    except ValueError:
        pass
    try:
        photo2_path = os.path.dirname(instance.photo2.path)
        shutil.rmtree(photo2_path)
        return
    except ValueError:
        pass
    try:
        photo3_path = os.path.dirname(instance.photo3.path)
        shutil.rmtree(photo3_path)
        return
    except ValueError:
        pass
    try:
        photo4_path = os.path.dirname(instance.photo4.path)
        shutil.rmtree(photo4_path)
        return
    except ValueError:
        pass


def user_statement_folder_delete(instance):
    """Функция для удаления папки с изображениями.

    Удаляет папку media для всех моделей - наследников Unit.
    :param instance: Экземпляр модели.
    """

    try:
        statement_path = os.path.dirname(instance.statement.path)
        shutil.rmtree(statement_path)
        return
    except ValueError:
        pass
    try:
        consent_personal_data_path = os.path.dirname(
            instance.consent_personal_data.path
        )
        shutil.rmtree(consent_personal_data_path)
        return
    except ValueError:
        pass
    try:
        consent_personal_data_representative_path = os.path.dirname(
            instance.consent_personal_data_representative.path
        )
        shutil.rmtree(consent_personal_data_representative_path)
        return
    except ValueError:
        pass
    try:
        passport = os.path.dirname(instance.passport.path)
        shutil.rmtree(passport)
        return
    except ValueError:
        pass
    try:
        passport_representative = os.path.dirname(
            instance.passport_representative.path
        )
        shutil.rmtree(passport_representative)
        return
    except ValueError:
        pass
    try:
        snils_file = os.path.dirname(instance.snils_file.path)
        shutil.rmtree(snils_file)
        return
    except ValueError:
        pass
    try:
        inn_file = os.path.dirname(instance.inn_file.path)
        shutil.rmtree(inn_file)
        return
    except ValueError:
        pass
    try:
        employment_document = os.path.dirname(
            instance.employment_document.path
        )
        shutil.rmtree(employment_document)
        return
    except ValueError:
        pass
    try:
        military_document = os.path.dirname(instance.military_document.path)
        shutil.rmtree(military_document)
        return
    except ValueError:
        pass
    try:
        international_passport = os.path.dirname(
            instance.international_passport.path
        )
        shutil.rmtree(international_passport)
        return
    except ValueError:
        pass
    try:
        additional_document = os.path.dirname(
            instance.additional_document.path
        )
        shutil.rmtree(additional_document)
        return
    except ValueError:
        pass
