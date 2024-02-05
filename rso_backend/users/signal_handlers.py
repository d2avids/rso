from datetime import datetime
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from djoser.signals import user_registered

from users.models import (UserMedia, UserStatementDocuments,
                          UserVerificationLogs)
from users.utils import user_image_folder_delete, user_statement_folder_delete


@receiver(pre_delete, sender=UserMedia)
def delete_image_with_object_user_media(sender, instance, **kwargs):
    """
    Функция для удаления папки с файлами, связанными с
    объектом модели UserMedia.
    """

    user_image_folder_delete(instance)


@receiver(pre_delete, sender=UserStatementDocuments)
def delete_image_with_object_user_statement_docs(sender, instance, **kwargs):
    """
    Функция для удаления папки с файлами, связанными с
    объектом модели UserStatementDocuments.
    """

    user_statement_folder_delete(instance)


@receiver(user_registered)
def user_auto_verification(sender, user, request, **kwargs):
    """
    Функция для автоматической верификации юзера при регистрации.
    """
    user.is_verified = True
    user.save()
    UserVerificationLogs.objects.create(
        user=user,
        date=datetime.now(),
        verification_by=user,
        description='Автоматическая верификация'
    )
