import os
from datetime import datetime as dt

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from headquarters.constants import PositionsOption


def image_path(instance, filename):
    """Функция для формирования пути сохранения изображения.

    :param instance: Экземпляр модели.
    :param filename: Имя файла. Добавляем к имени текущую дату и время.
    :return: Путь к изображению.
    Сохраняем в filepath/{instance.name}/filename
    """

    filename = dt.today().strftime('%Y%m%d%H%M%S') + '_' + filename
    filepath = 'images/headquarters'
    return os.path.join(filepath, instance.name, filename)


class EducationalInstitution(models.Model):
    short_name = models.CharField(
        max_length=50,
        verbose_name='Короткое название образовательной '
                     'организации (например, РГГУ)'
    )
    name = models.CharField(
        max_length=250,
        unique=True,
        verbose_name='Полное название образовательной организации'
    )
    rector = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        verbose_name='ФИО ректора образовательной организации'
    )
    rector_email = models.EmailField(
        blank=True,
        null=True,
        verbose_name='Электронная почта ректора'
    )
    region = models.ForeignKey(
        'Region',
        related_name='institutions',
        on_delete=models.PROTECT,
        verbose_name='Регион'
    )

    class Meta:
        verbose_name_plural = 'Образовательные организации'
        verbose_name = 'Образовательная организация'

    def __str__(self):
        return self.name


class Region(models.Model):
    name = models.CharField(
        max_length=100,
        db_index=True,
        verbose_name='Название'
    )

    class Meta:
        verbose_name_plural = 'Регионы'
        verbose_name = 'Регион'

    def __str__(self):
        return self.name


class Area(models.Model):
    name = models.CharField(
        max_length=50,
        blank=False,
        verbose_name='Название направления'
    )

    class Meta:
        verbose_name_plural = 'направления'
        verbose_name = 'Направление'

    def __str__(self):
        return self.name


class Unit(models.Model):
    """Базовая модель структурной единицы."""

    name = models.CharField(
        max_length=100,
        verbose_name='Название'
    )
    commander = models.ForeignKey(
        'users.RSOUser',
        on_delete=models.PROTECT,
        verbose_name='Командир'
    )
    about = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='Описание',
    )
    emblem = models.ImageField(
        upload_to=image_path,
        blank=True,
        null=True,
        verbose_name='Эмблема'
    )
    social_vk = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Ссылка ВК',
        default='https://vk.com/'
    )
    social_tg = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Ссылка Телеграм',
        default='https://'
    )
    banner = models.ImageField(
        upload_to=image_path,
        blank=True,
        null=True,
        verbose_name='Баннер'
    )
    slogan = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Девиз'
    )
    founding_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Дата основания'
    )

    def clean(self):
        if not self.commander:
            raise ValidationError('Отряд должен иметь командира.')

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class CentralHeadquarter(Unit):
    class Meta:
        verbose_name_plural = 'Центральные штабы'
        verbose_name = 'Центральный штаб'


@receiver(pre_delete, sender=CentralHeadquarter)
def delete_image_with_object_central_headquarter(sender, instance, **kwargs):
    """
    Функция для удаления изображения, связанного с
    объектом модели CentralHeadquarter.
    """
    instance.emblem.delete(False)
    instance.banner.delete(False)


class DistrictHeadquarter(Unit):
    central_headquarter = models.ForeignKey(
        'CentralHeadquarter',
        related_name='district_headquarters',
        on_delete=models.PROTECT,
        verbose_name='Привязка к ЦШ'
    )

    class Meta:
        verbose_name_plural = 'Окружные штабы'
        verbose_name = 'Окружной штаб'


class RegionalHeadquarter(Unit):
    region = models.ForeignKey(
        'Region',
        related_name='headquarters',
        on_delete=models.PROTECT,
        verbose_name='Регион'
    )
    district_headquarter = models.ForeignKey(
        'DistrictHeadquarter',
        related_name='regional_headquarters',
        on_delete=models.PROTECT,
        verbose_name='Привязка к ОШ'
    )

    class Meta:
        verbose_name_plural = 'Региональные штабы'
        verbose_name = 'Региональный штаб'


@receiver(pre_delete, sender=RegionalHeadquarter)
def delete_image_with_object_regional_headquarter(sender, instance, **kwargs):
    """
    Функция для удаления изображения, связанного с
    объектом модели RegionalHeadquarter.
    """
    instance.emblem.delete(False)
    instance.banner.delete(False)


class LocalHeadquarter(Unit):
    regional_headquarter = models.ForeignKey(
        'RegionalHeadquarter',
        related_name='local_headquarters',
        on_delete=models.PROTECT,
        verbose_name='Привязка к РШ'
    )

    class Meta:
        verbose_name_plural = 'Местные штабы'
        verbose_name = 'Местный штаб'


class EducationalHeadquarter(Unit):
    local_headquarter = models.ForeignKey(
        'LocalHeadquarter',
        related_name='educational_headquarters',
        on_delete=models.PROTECT,
        verbose_name='Привязка к МШ',
        blank=True,
        null=True,
    )
    regional_headquarter = models.ForeignKey(
        'RegionalHeadquarter',
        related_name='educational_headquarters',
        on_delete=models.PROTECT,
        verbose_name='Привязка к РШ',
    )
    educational_institution = models.ForeignKey(
        'EducationalInstitution',
        related_name='headquarters',
        on_delete=models.PROTECT,
        verbose_name='Образовательная организация',
    )

    def clean(self):
        """
        Проверяет, что местный штаб (local_headquarter) связан с тем же
        региональным штабом (regional_headquarter),
        что и образовательный штаб (EducationalHeadquarter).
        """
        super().clean()

        if self.local_headquarter and self.regional_headquarter:
            if (
                self.local_headquarter.regional_headquarter !=
                self.regional_headquarter
            ):
                raise ValidationError({
                    'local_headquarter': 'Этот местный штаб связан '
                                         'с другим региональным штабом.'
                })

    class Meta:
        verbose_name_plural = 'Образовательные штабы'
        verbose_name = 'Образовательный штаб'


class Detachment(Unit):
    educational_headquarter = models.ForeignKey(
        'EducationalHeadquarter',
        related_name='detachments',
        on_delete=models.PROTECT,
        verbose_name='Привязка к ШОО',
        blank=True,
        null=True,
    )
    local_headquarter = models.ForeignKey(
        'LocalHeadquarter',
        related_name='detachments',
        on_delete=models.PROTECT,
        verbose_name='Привязка к МШ',
        blank=True,
        null=True,
    )
    regional_headquarter = models.ForeignKey(
        'RegionalHeadquarter',
        related_name='detachments',
        on_delete=models.PROTECT,
        verbose_name='Привязка к РШ',
    )
    area = models.ForeignKey(
        Area,
        null=False,
        blank=False,
        on_delete=models.PROTECT,
        verbose_name='Направление'
    )

    def clean(self):
        """
        Проверяет согласованность между
        образовательным штабом (educational_headquarter),
        местным штабом (local_headquarter)
        и региональным штабом (regional_headquarter).
        """
        super().clean()

        if self.educational_headquarter and self.local_headquarter:
            if (
                self.educational_headquarter.local_headquarter !=
                self.local_headquarter
            ):
                raise ValidationError({
                    'educational_headquarter': 'Этот образовательный штаб '
                                               'связан с другим местным '
                                               'штабом.'
                })

        if self.local_headquarter and self.regional_headquarter:
            if (
                self.local_headquarter.regional_headquarter !=
                self.regional_headquarter
            ):
                raise ValidationError({
                    'local_headquarter': 'Этот местный штаб связан с '
                                         'другим региональным штабом.'
                })

        if self.educational_headquarter and self.regional_headquarter:
            if (
                self.educational_headquarter.regional_headquarter !=
                self.regional_headquarter
            ):
                raise ValidationError({
                    'educational_headquarter': 'Этот образовательный штаб '
                                               'связан с другим региональным '
                                               'штабом.'
                })

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Отряды'
        verbose_name = 'Отряд'


class Position(models.Model):
    """Класс """


@receiver(pre_delete, sender=Detachment)
def delete_image_with_object_detachment(sender, instance, **kwargs):
    """
    Функция для удаления изображения, связанного с
    объектом модели Detachment.
    """
    instance.emblem.delete(False)
    instance.banner.delete(False)


