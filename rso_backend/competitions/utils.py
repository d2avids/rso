import os
from datetime import datetime as dt
from django.utils import timezone


def format_filename(filename):
    """Функция для форматирования имени файла."""
    current_time = str(timezone.now().strftime('%Y%m%d%H%M%S'))
    current_time = 'ksk'
    return f"{current_time}_{filename}"


def create_directory_if_not_exists(path):
    """Функция для создания директории, если ее нет."""
    if not os.path.exists(path):
        os.makedirs(path)


def get_certificate_scans_path(instance, filename):
    """
    Функция для получения пути к сканам грамот и сертификатов.

    :param instance: Экземпляр модели.
    :param filename: Имя файла. Добавляем к имени текущую дату и время.
    :return: Путь к изображению.
    Сохраняем в filepath/{instance.__class__.__name__}/filename
    """
    model_name = instance.__class__.__name__
    filename = format_filename(filename)
    filepath = os.path.join('competitions/certificates_scans', model_name)
    create_directory_if_not_exists(filepath)
    return os.path.join(filepath, filename)


def document_path(instance, filename):
    """Функция для формирования пути сохранения сканов документов юзера.

    :param instance: Экземпляр модели.
    :param filename: Имя файла. Добавляем к имени текущую дату и время.
    :return: Путь к скану документа.
    Сохраняем в filepath/{instance.name}/filename
    """

    filename = dt.today().strftime('%Y%m%d%H%M%S') + '_' + filename[:15]
    filepath = 'documents/users'
    return os.path.join(filepath, instance.user.username, filename)


def is_competition_participant(detachment, competition):
    """Проверяет, является ли отряд участником конкурса."""
    return detachment in (competition.junior_detachment.all() +
                          competition.detachment.all())


def round_math(num, decimals=0):
    """
    Функция математического округления.

    :param num: округляемое число
    :param decimals: количество знаков после запятой
    :return: округленное число

    Решает проблему округления round(2.5) = 2
    (округления к ближайшему четному)
    """
    if isinstance(num, int):
        return num
    elif decimals < 0:
        raise ValueError("decimal places has to be 0 or more")
    if not isinstance(decimals, int):
        raise ValueError("decimal places has to be an integer")
    factor = int('1' + '0' * decimals)
    return int(num * factor + 0.5) / factor
