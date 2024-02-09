import os
import shutil

from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from events.models import Event, EventDocument, EventUserDocument


@receiver(pre_delete, sender=Event)
def delete_images_folder_with_event(sender, instance, **kwargs):
    """
    Функция для удаления папки с изображениями, связанными с
    объектом модели Event.
    """

    try:
        banner_path = os.path.dirname(instance.banner.path)
        shutil.rmtree(banner_path)
    except (ValueError, FileNotFoundError):
        pass


@receiver(pre_save, sender=Event)
def delete_image_with_event(sender, instance, **kwargs):
    """
    Функция для удаления изображений, связанных с
    объектом модели Event,
    при обновлении изображения.
    """

    if instance.pk:
        try:
            old_instance = Event.objects.get(pk=instance.pk)
            try:
                if old_instance.banner != instance.banner:
                    os.remove(old_instance.banner.path)
            except (ValueError, FileNotFoundError):
                pass
        except Event.DoesNotExist:
            pass


@receiver(pre_delete, sender=EventDocument)
def delete_images_folder_with_event_document(sender, instance, **kwargs):
    """
    Функция для удаления папки с файлами, связанными с
    объектом модели EventDocument.
    """

    try:
        document_path = os.path.dirname(instance.document.path)
        shutil.rmtree(document_path)
    except (ValueError, FileNotFoundError):
        pass


@receiver(pre_save, sender=EventDocument)
def delete_image_with_event_document(sender, instance, **kwargs):
    """
    Функция для удаления файлов, связанных с
    объектом модели EventDocument,
    при обновлении изображения.
    """

    if instance.pk:
        try:
            old_instance = EventDocument.objects.get(pk=instance.pk)
            try:
                if old_instance.document != instance.document:
                    os.remove(old_instance.document.path)
            except (ValueError, FileNotFoundError):
                pass
        except EventDocument.DoesNotExist:
            pass


@receiver(pre_delete, sender=EventUserDocument)
def delete_images_folder_with_event_user_document(sender, instance, **kwargs):
    """
    Функция для удаления папки с файлами, связанными с
    объектом модели EventUserDocument.
    """

    try:
        document_path = os.path.dirname(instance.document.path)
        shutil.rmtree(document_path)
    except (ValueError, FileNotFoundError):
        pass


@receiver(pre_save, sender=EventUserDocument)
def delete_image_with_event_user_document(sender, instance, **kwargs):
    """
    Функция для удаления файлов, связанных с
    объектом модели EventUserDocument,
    при обновлении изображения.
    """

    if instance.pk:
        try:
            old_instance = EventUserDocument.objects.get(pk=instance.pk)
            try:
                if old_instance.document != instance.document:
                    os.remove(old_instance.document.path)
            except (ValueError, FileNotFoundError):
                pass
        except EventUserDocument.DoesNotExist:
            pass
