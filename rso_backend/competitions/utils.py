import os
from datetime import datetime as dt
from django.utils import timezone
from django.utils.text import camel_case_to_spaces


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


def tandem_or_start(competition, detachment, competition_model) -> bool:
    """Вычисление Тандем | Старт."""

    is_tandem = False
    try:
        if ((competition_model.objects.filter(
            competition=competition,
            detachment=detachment
        ).exists())
         or (
            competition_model.objects.filter(
                competition=competition,
                junior_detachment=detachment
            ).exclude(detachment=None)
        )):
            is_tandem = True
    except (competition_model.DoesNotExist, ValueError):
        is_tandem = False
    return is_tandem
