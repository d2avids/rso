import os
import shutil

from django.db.models.signals import pre_delete
from django.dispatch import receiver

from headquarters.models import (CentralHeadquarter, Detachment,
                                 DistrictHeadquarter, EducationalHeadquarter,
                                 LocalHeadquarter, RegionalHeadquarter)


@receiver(pre_delete, sender=CentralHeadquarter)
def delete_image_with_object_central_headquarter(sender, instance, **kwargs):
    """
    Функция для удаления папки с изображениями, связанными с
    объектом модели CentralHeadquarter.
    """
    folder_path = os.path.dirname(instance.emblem.path)
    shutil.rmtree(folder_path)


@receiver(pre_delete, sender=DistrictHeadquarter)
def delete_image_with_object_district_headquarter(sender, instance, **kwargs):
    """
    Функция для удаления папки с изображениями, связанными с
    объектом модели DistrictHeadquarter.
    """
    folder_path = os.path.dirname(instance.emblem.path)
    shutil.rmtree(folder_path)


@receiver(pre_delete, sender=RegionalHeadquarter)
def delete_image_with_object_regional_headquarter(sender, instance, **kwargs):
    """
    Функция для удаления папки с изображениями, связанными с
    объектом модели RegionalHeadquarter.
    """
    folder_path = os.path.dirname(instance.emblem.path)
    shutil.rmtree(folder_path)


@receiver(pre_delete, sender=LocalHeadquarter)
def delete_image_with_object_local_headquarter(sender, instance, **kwargs):
    """
    Функция для удаления папки с изображениями, связанными с
    объектом модели LocalHeadquarter.
    """
    folder_path = os.path.dirname(instance.emblem.path)
    shutil.rmtree(folder_path)


@receiver(pre_delete, sender=EducationalHeadquarter)
def delete_image_with_object_edu_headquarter(sender, instance, **kwargs):
    """
    Функция для удаления папки с изображениями, связанными с
    объектом модели EducationalHeadquarter.
    """
    folder_path = os.path.dirname(instance.emblem.path)
    shutil.rmtree(folder_path)


@receiver(pre_delete, sender=Detachment)
def delete_image_with_object_detachment(sender, instance, **kwargs):
    """
    Функция для удаления папки с изображениями, связанными с
    объектом модели Detachment.
    """

    folder_path = os.path.dirname(instance.emblem.path)
    shutil.rmtree(folder_path)
