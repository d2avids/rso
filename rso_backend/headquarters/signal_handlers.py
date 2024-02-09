import os

from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from headquarters.models import (CentralHeadquarter, Detachment,
                                 DistrictHeadquarter, EducationalHeadquarter,
                                 LocalHeadquarter, RegionalHeadquarter)
from headquarters.utils import (headquarter_image_delete,
                                headquarter_media_folder_delete)


@receiver(pre_delete, sender=CentralHeadquarter)
def delete_images_folder_with_central_headquarter(sender, instance, **kwargs):
    """
    Функция для удаления папки с изображениями, связанными с
    объектом модели CentralHeadquarter.
    """

    headquarter_media_folder_delete(instance)


@receiver(pre_delete, sender=DistrictHeadquarter)
def delete_images_folder_with_district_headquarter(sender, instance, **kwargs):
    """
    Функция для удаления папки с изображениями, связанными с
    объектом модели DistrictHeadquarter.
    """

    headquarter_media_folder_delete(instance)


@receiver(pre_delete, sender=RegionalHeadquarter)
def delete_images_folder_with_regional_headquarter(sender, instance, **kwargs):
    """
    Функция для удаления папки с изображениями, связанными с
    объектом модели RegionalHeadquarter.
    """

    headquarter_media_folder_delete(instance)


@receiver(pre_delete, sender=LocalHeadquarter)
def delete_images_folder_with_local_headquarter(sender, instance, **kwargs):
    """
    Функция для удаления папки с изображениями, связанными с
    объектом модели LocalHeadquarter.
    """

    headquarter_media_folder_delete(instance)


@receiver(pre_delete, sender=EducationalHeadquarter)
def delete_images_folder_with_edu_headquarter(sender, instance, **kwargs):
    """
    Функция для удаления папки с изображениями, связанными с
    объектом модели EducationalHeadquarter.
    """

    headquarter_media_folder_delete(instance)


@receiver(pre_delete, sender=Detachment)
def delete_images_folder_with_detachment(sender, instance, **kwargs):
    """
    Функция для удаления папки с изображениями, связанными с
    объектом модели Detachment.
    """

    headquarter_media_folder_delete(instance)


@receiver(pre_save, sender=CentralHeadquarter)
def delete_image_with_object_central_headquarter(sender, instance, **kwargs):
    """
    Функция для удаления изображений, связанных с
    объектом модели CentralHeadquarter,
    при обновлении изображения.
    """

    headquarter_image_delete(instance, CentralHeadquarter)


@receiver(pre_save, sender=DistrictHeadquarter)
def delete_image_with_object_distrit_headquarter(sender, instance, **kwargs):
    """
    Функция для удаления изображений, связанных с
    объектом модели DistrictHeadquarter,
    при обновлении изображения.
    """

    headquarter_image_delete(instance, DistrictHeadquarter)


@receiver(pre_save, sender=RegionalHeadquarter)
def delete_image_with_object_regional_headquarter(sender, instance, **kwargs):
    """
    Функция для удаления изображений, связанных с
    объектом модели RegionalHeadquarter,
    при обновлении изображения.
    """

    headquarter_image_delete(instance, RegionalHeadquarter)


@receiver(pre_save, sender=LocalHeadquarter)
def delete_image_with_object_local_headquarter(sender, instance, **kwargs):
    """
    Функция для удаления изображений, связанных с
    объектом модели LocalHeadquarter,
    при обновлении изображения.
    """

    headquarter_image_delete(instance, LocalHeadquarter)


@receiver(pre_save, sender=EducationalHeadquarter)
def delete_image_with_object_edu_headquarter(sender, instance, **kwargs):
    """
    Функция для удаления изображений, связанных с
    объектом модели EducationalHeadquarter,
    при обновлении изображения.
    """

    headquarter_image_delete(instance, EducationalHeadquarter)


@receiver(pre_save, sender=Detachment)
def delete_image_with_detachment_headquarter(sender, instance, **kwargs):
    """
    Функция для удаления изображений, связанных с
    объектом модели Detachment,
    при обновлении изображения.
    """

    if instance.pk:
        try:
            old_instance = Detachment.objects.get(pk=instance.pk)
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
        except Detachment.DoesNotExist:
            pass
