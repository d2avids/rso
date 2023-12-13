import os
import re
from datetime import datetime as dt

from django.core.exceptions import ValidationError
from django.conf import settings


def image_path(instance, filename):
    """Функция для формирования пути сохранения изображения.

    :param instance: Экземпляр модели.
    :param filename: Имя файла. Добавляем к имени текущую дату и время.
    :return: Путь к изображению.
    Сохраняем в filepath/{instance.name}/filename
    """

    filename = dt.today().strftime('%Y%m%d%H%M%S') + '_' + filename
    filepath = 'images/users'
    return os.path.join(filepath, instance.name, filename)


def document_path(instance, filename):
    """Функция для формирования пути сохранения сканов документов юзера.

    :param instance: Экземпляр модели.
    :param filename: Имя файла. Добавляем к имени текущую дату и время.
    :return: Путь к скану документа.
    Сохраняем в filepath/{instance.name}/filename
    """

    filename = dt.today().strftime('%Y%m%d%H%M%S') + '_' + filename
    filepath = 'documents/users'
    return os.path.join(filepath, instance.name, filename)


def validate_years(value):
    """Функция для проверки корректности ввода года обучения."""
    if not re.match(r'^\d{4}-\d{4}$', value):
        raise ValidationError(
            'Ошибка ввода срока обучения. Используйте формат "YYYY-YYYY".'
        )
    start, end = value.split('-')
    if int(start) >= int(end):
        raise ValidationError('Начальный год должен быть меньше конечного.')


def unique_email_validator(value):
    """Валидация Email - уникальный, либо None."""

    if value is not None:
        if settings.AUTH_USER_MODEL.objects.filter(
            email=value.lower()
        ).exists():
            raise ValidationError('Данный Email уже зарегистрирован.')
