from django.db.models.signals import pre_delete
from django.dispatch import receiver

from headquarters.models import (CentralHeadquarter, Detachment,
                                 DistrictHeadquarter, EducationalHeadquarter,
                                 LocalHeadquarter, RegionalHeadquarter)
from headquarters.utils import headquarter_media_folder_delete


@receiver(pre_delete, sender=CentralHeadquarter)
def delete_image_with_object_central_headquarter(sender, instance, **kwargs):
    """
    Функция для удаления папки с изображениями, связанными с
    объектом модели CentralHeadquarter.
    """

    headquarter_media_folder_delete(instance)


@receiver(pre_delete, sender=DistrictHeadquarter)
def delete_image_with_object_district_headquarter(sender, instance, **kwargs):
    """
    Функция для удаления папки с изображениями, связанными с
    объектом модели DistrictHeadquarter.
    """

    headquarter_media_folder_delete(instance)


@receiver(pre_delete, sender=RegionalHeadquarter)
def delete_image_with_object_regional_headquarter(sender, instance, **kwargs):
    """
    Функция для удаления папки с изображениями, связанными с
    объектом модели RegionalHeadquarter.
    """

    headquarter_media_folder_delete(instance)


@receiver(pre_delete, sender=LocalHeadquarter)
def delete_image_with_object_local_headquarter(sender, instance, **kwargs):
    """
    Функция для удаления папки с изображениями, связанными с
    объектом модели LocalHeadquarter.
    """

    headquarter_media_folder_delete(instance)


@receiver(pre_delete, sender=EducationalHeadquarter)
def delete_image_with_object_edu_headquarter(sender, instance, **kwargs):
    """
    Функция для удаления папки с изображениями, связанными с
    объектом модели EducationalHeadquarter.
    """

    headquarter_media_folder_delete(instance)


@receiver(pre_delete, sender=Detachment)
def delete_image_with_object_detachment(sender, instance, **kwargs):
    """
    Функция для удаления папки с изображениями, связанными с
    объектом модели Detachment.
    """

    headquarter_media_folder_delete(instance)
