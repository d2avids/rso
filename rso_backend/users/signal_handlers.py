import os
import shutil

from django.db.models.signals import pre_delete
from django.dispatch import receiver

from users.models import UserMedia, UserStatementDocuments


@receiver(pre_delete, sender=UserMedia)
def delete_image_with_object_user_media(sender, instance, **kwargs):
    """
    Функция для удаления папки с файлами, связанными с
    объектом модели UserMedia.
    """

    folder_path = os.path.dirname(instance.banner.path)
    shutil.rmtree(folder_path)


@receiver(pre_delete, sender=UserStatementDocuments)
def delete_image_with_object_user_statement_docs(sender, instance, **kwargs):
    """
    Функция для удаления папки с файлами, связанными с
    объектом модели UserStatementDocuments.
    """

    folder_path = os.path.dirname(instance.statement.path)
    shutil.rmtree(folder_path)
