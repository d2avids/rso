from django.contrib.auth import get_user_model
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from djoser.signals import user_registered

from users.models import UserMedia, UserStatementDocuments, RSOUser
from users.utils import user_image_folder_delete, user_statement_folder_delete
from api.tasks import send_activation_email

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
def handle_user_registered(sender, user, request, **kwargs):

    print(request.data,'AAAAAAAAAAAAAAAAAAAA')
    # user = RSOUser.objects.get(id=user.id)

    user_id=int(user.id)
    print(user.id, user_id,'BBBBBBBBB')
    send_activation_email.delay(user_id, request.data)