import os

from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from users.models import UserMedia, UserStatementDocuments
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


@receiver(pre_save, sender=UserMedia)
def delete_user_media(sender, instance, **kwargs):
    """
    Удаление на сервере картинок юзера при загрузке новых.
    """

    if instance.pk:
        try:
            old_instance = UserMedia.objects.get(pk=instance.pk)
            try:
                if old_instance.banner != instance.banner:
                    os.remove(old_instance.banner.path)
            except (ValueError, FileNotFoundError):
                pass
            try:
                if old_instance.photo != instance.photo:
                    os.remove(old_instance.photo.path)
            except (ValueError, FileNotFoundError):
                pass
            try:
                if old_instance.photo1 != instance.photo1:
                    os.remove(old_instance.photo1.path)
            except (ValueError, FileNotFoundError):
                pass
            try:
                if old_instance.photo2 != instance.photo2:
                    os.remove(old_instance.photo2.path)
            except (ValueError, FileNotFoundError):
                pass
            try:
                if old_instance.photo3 != instance.photo3:
                    os.remove(old_instance.photo3.path)
            except (ValueError, FileNotFoundError):
                pass
            try:
                if old_instance.photo4 != instance.photo4:
                    os.remove(old_instance.photo4.path)
            except (ValueError, FileNotFoundError):
                pass
        except UserMedia.DoesNotExist:
            pass


@receiver(pre_save, sender=UserStatementDocuments)
def delete_user_statement_documents(sender, instance, **kwargs):
    """
    Удаление на сервере картинок юзера при загрузке новых.
    """

    if instance.pk:
        try:
            old_instance = UserStatementDocuments.objects.get(pk=instance.pk)
            try:
                if old_instance.statement != instance.statement:
                    os.remove(old_instance.statement.path)
            except (ValueError, FileNotFoundError):
                pass
            try:
                if (
                    old_instance.consent_personal_data
                    != instance.consent_personal_data
                ):
                    os.remove(old_instance.consent_personal_data.path)
            except (ValueError, FileNotFoundError):
                pass
            try:
                if (
                    old_instance.consent_personal_data_representative
                    != instance.consent_personal_data_representative
                ):
                    os.remove(
                        old_instance.consent_personal_data_representative.path
                    )
            except (ValueError, FileNotFoundError):
                pass
            try:
                if old_instance.passport != instance.passport:
                    os.remove(old_instance.passport.path)
            except (ValueError, FileNotFoundError):
                pass
            try:
                if (
                    old_instance.passport_representative
                    != instance.passport_representative
                ):
                    os.remove(old_instance.passport_representative.path)
            except (ValueError, FileNotFoundError):
                pass
            try:
                if old_instance.snils_file != instance.snils_file:
                    os.remove(old_instance.snils_file.path)
            except (ValueError, FileNotFoundError):
                pass
            try:
                if old_instance.inn_file != instance.inn_file:
                    os.remove(old_instance.inn_file.path)
            except (ValueError, FileNotFoundError):
                pass
            try:
                if (
                    old_instance.employment_document
                    != instance.employment_document
                ):
                    os.remove(old_instance.employment_document.path)
            except (ValueError, FileNotFoundError):
                pass
            try:
                if (
                    old_instance.military_document
                    != instance.military_document
                ):
                    os.remove(old_instance.military_document.path)
            except (ValueError, FileNotFoundError):
                pass
            try:
                if (
                    old_instance.international_passport
                    != instance.international_passport
                ):
                    os.remove(old_instance.international_passport.path)
            except (ValueError, FileNotFoundError):
                pass
            try:
                if (
                    old_instance.additional_document
                    != instance.additional_document
                ):
                    os.remove(old_instance.additional_document.path)
            except (ValueError, FileNotFoundError):
                pass
        except UserStatementDocuments.DoesNotExist:
            pass
