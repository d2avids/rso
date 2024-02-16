import os
from django.utils import timezone


def format_filename(filename):
    """Функция для форматирования имени файла."""
    current_time = timezone.now().strftime('%Y%m%d%H%M%S')
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


def is_competition_participant(detachment, competition):
    """Проверяет, является ли отряд участником конкурса."""
    return detachment in (competition.junior_detachment.all() +
                          competition.detachment.all())