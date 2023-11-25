import os
from datetime import datetime as dt


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
