from django.db.models.signals import pre_delete
from django.dispatch import receiver

from api.utils import check_folder_delete, check_folder_delete_usermedia
from users.models import UserMedia, UserStatementDocuments


@receiver(pre_delete, sender=UserMedia)
def delete_image_with_object_user_media(sender, instance, **kwargs):
    """
    Функция для удаления папки с файлами, связанными с
    объектом модели UserMedia.
    """

    check_folder_delete_usermedia(instance)


@receiver(pre_delete, sender=UserStatementDocuments)
def delete_image_with_object_user_statement_docs(sender, instance, **kwargs):
    """
    Функция для удаления папки с файлами, связанными с
    объектом модели UserStatementDocuments.
    """

    check_folder_delete(instance)
