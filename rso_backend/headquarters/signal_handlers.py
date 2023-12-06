from django.db.models.signals import pre_delete
from django.dispatch import receiver

from api.utils import check_folder_delete
from headquarters.models import (CentralHeadquarter, Detachment,
                                 DistrictHeadquarter, EducationalHeadquarter,
                                 LocalHeadquarter, RegionalHeadquarter)


@receiver(pre_delete, sender=CentralHeadquarter)
def delete_image_with_object_central_headquarter(sender, instance, **kwargs):
    """
    Функция для удаления папки с изображениями, связанными с
    объектом модели CentralHeadquarter.
    """
    check_folder_delete(instance)


@receiver(pre_delete, sender=DistrictHeadquarter)
def delete_image_with_object_district_headquarter(sender, instance, **kwargs):
    """
    Функция для удаления папки с изображениями, связанными с
    объектом модели DistrictHeadquarter.
    """
    check_folder_delete(instance)


@receiver(pre_delete, sender=RegionalHeadquarter)
def delete_image_with_object_regional_headquarter(sender, instance, **kwargs):
    """
    Функция для удаления папки с изображениями, связанными с
    объектом модели RegionalHeadquarter.
    """
    check_folder_delete(instance)


@receiver(pre_delete, sender=LocalHeadquarter)
def delete_image_with_object_local_headquarter(sender, instance, **kwargs):
    """
    Функция для удаления папки с изображениями, связанными с
    объектом модели LocalHeadquarter.
    """
    check_folder_delete(instance)


@receiver(pre_delete, sender=EducationalHeadquarter)
def delete_image_with_object_edu_headquarter(sender, instance, **kwargs):
    """
    Функция для удаления папки с изображениями, связанными с
    объектом модели EducationalHeadquarter.
    """
    check_folder_delete(instance)


@receiver(pre_delete, sender=Detachment)
def delete_image_with_object_detachment(sender, instance, **kwargs):
    """
    Функция для удаления папки с изображениями, связанными с
    объектом модели Detachment.
    """

    check_folder_delete(instance)
