import os
import shutil
from datetime import datetime as dt

from users.models import UserVerificationRequest


def image_path(instance, filename):
    """Функция для формирования пути сохранения изображения.

    :param instance: Экземпляр модели.
    :param filename: Имя файла. Добавляем к имени текущую дату и время.
    :return: Путь к изображению.
    Сохраняем в filepath/{instance.id}/filename
    """

    filename = (
            dt.today().strftime('%Y%m%d%') + '_' + filename[:15] +
            filename[-5:]
    )
    filepath = 'images/headquarters'
    return os.path.join(filepath, instance.name[:15], filename)


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


def headquarter_image_delete(instance, model):
    """Функция для удаления изображения.

    Удаляет изображение для всех моделей - наследников Unit.
    :param instance: Экземпляр модели.
    """

    if instance.pk:
        try:
            old_instance = model.objects.get(pk=instance.pk)
            try:
                if old_instance.banner != instance.banner:
                    os.remove(old_instance.banner.path)
            except (ValueError, FileNotFoundError):
                pass
            try:
                if old_instance.emblem != instance.emblem:
                    os.remove(old_instance.emblem.path)
            except (ValueError, FileNotFoundError):
                pass
        except model.DoesNotExist:
            pass


def get_detachment_members_to_verify(detachment):
    user_ids_in_verification_request = (
        UserVerificationRequest.objects.values_list(
            'user_id', flat=True
        )
    )
    members_to_verify = detachment.members.filter(
        user__id__in=user_ids_in_verification_request
    ).select_related('user')
    return members_to_verify


def get_regional_hq_members_to_verify(regional_headquarter):
    return UserVerificationRequest.objects.filter(
            user__region=regional_headquarter.region,
        ).select_related('user')
