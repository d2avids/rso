import os
import shutil
from datetime import datetime as dt


def image_path(instance, filename):
    """Функция для формирования пути сохранения изображения.

    :param instance: Экземпляр модели.
    :param filename: Имя файла. Добавляем к имени текущую дату и время.
    :return: Путь к изображению.
    Сохраняем в filepath/{instance.name}/filename
    """

    filename = dt.today().strftime('%Y%m%d%H%M%S') + '_' + filename
    filepath = 'images/headquarters'
    return os.path.join(filepath, instance.name, filename)


def headquarter_media_folder_delete(instance):
    """Функция для удаления папки с изображениями.

    Удаляет папку media для всех моделей - наследников Unit.
    :param instance: Экземпляр модели.
    """

    try:
        emblem_path = os.path.dirname(instance.emblem.path)
        shutil.rmtree(emblem_path)
        return
    except ValueError:
        pass
    try:
        banner_path = os.path.dirname(instance.banner.path)
        shutil.rmtree(banner_path)
    except ValueError:
        pass
