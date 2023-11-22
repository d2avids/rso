from django.db import models
from rest_framework.exceptions import ValidationError

from users.models import RSOUser
from users.utils import user_upload_path


class Region(models.Model):
    """Регион и региональное отделение."""
    name = models.CharField(
        max_length=100,
        db_index=True,
        blank=True,
        null=True,
        verbose_name='Название'
    )

    branch = models.CharField(
        max_length=100,
        db_index=True,
        blank=True,
        null=True,
        default='региональное отделение',
        verbose_name='Региональное отделение'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'регионы'
        verbose_name = 'Регион'


class Area(models.Model):
    """Направление деятельности"""
    name = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='Название направления'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'направления'
        verbose_name = 'Направление'


class Unit(models.Model):
    """Структурная единица"""
    name = models.CharField(
        max_length=100,
        db_index=True,
        blank=True,
        null=True,
        verbose_name='Название'
    )
    commander = models.OneToOneField(
        RSOUser,
        related_name='commander',
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        verbose_name='Командир'
    )
    about = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name='Описание',
        default=''
    )
    emblem = models.ImageField(
        upload_to=user_upload_path,
        blank=True,
        null=True,
        verbose_name='Эмблема'
    )
    social_vk = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        default='https://vk.com/',
        verbose_name='Ссылка ВК'
    )
    social_tg = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        default='https://',
        verbose_name='Ссылка Телеграм'
    )
    banner = models.ImageField(
        upload_to=user_upload_path,
        blank=True,
        null=True,
        verbose_name='Баннер'
    )
    slogan = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        default='',
        verbose_name='Девиз'
    )
    founding_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Дата основания'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'структурные единицы'
        verbose_name = 'Структурная единица'


class Detachment(Unit):
    """Отряд"""
    area = models.ForeignKey(
        Area,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        verbose_name='Направление'
    )

    def clean(self):
        if not self.commander:
            raise ValidationError('Отряд должен иметь командира.')

    # регион
    # institution = models.ForeignKey(
    #   'Institution',
    #   null=True,
    #   blank=True,
    #   on_delete=models.PROTECT,
    #   verbose_name='Учебное заведение'
    #  )
    # город
    # Местный штаб

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'отряды'
        verbose_name = 'Отряд'

# Штаб Образовательной Организации
# Регион
# Учебное заведение
# Местный штаб
#
# МестныйШтаб
# Регион
# Номер участника в реестре
# Дата участника в реестре
#
# Региональный Штаб
# Регион
# Год появления Отрядов в регионе
# Дата учредительной конференции
# Номер участника в реестре
# Дата участника в реестре
# Окружной штаб
#
# Окружной Штаб
