from django.core.exceptions import ValidationError
from django.db import models

from headquarters.utils import image_path


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
    region = models.OneToOneField(
        'Region',
        related_name='institutions',
        on_delete=models.PROTECT,
        verbose_name='Регион'
    )


class Region(models.Model):
    name = models.CharField(
        max_length=100,
        db_index=True,
        verbose_name='Название'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'регионы'
        verbose_name = 'Регион'


class Area(models.Model):
    name = models.CharField(
        max_length=50,
        blank=False,
        verbose_name='Название направления'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'направления'
        verbose_name = 'Направление'


class Unit(models.Model):
    """Базовая модель структурной единицы."""

    name = models.CharField(
        max_length=100,
        db_index=True,
        verbose_name='Название'
    )
    commander = models.OneToOneField(
        'users.RSOUser',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        verbose_name='Командир'
    )
    about = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='Описание',
        default=''
    )
    emblem = models.ImageField(
        upload_to=image_path,
        blank=True,
        verbose_name='Эмблема'
    )
    social_vk = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Ссылка ВК',
        default='https://vk.com/'
    )
    social_tg = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Ссылка Телеграм',
        default='https://'
    )
    banner = models.ImageField(
        upload_to=image_path,
        blank=True,
        verbose_name='Баннер'
    )
    slogan = models.CharField(
        max_length=100,
        blank=True,
        default='',
        verbose_name='Девиз'
    )
    founding_date = models.DateField(
        blank=True,
        null=True,
        verbose_name='Дата основания'
    )

    # Уровень Линейный отряд, Штаб учебного заведения, Региональное отделение,
    # (Направление)
    # area = models.ForeignKey(
    # 'Area',
    # null=True,
    # blank=True,
    # on_delete=models.PROTECT,
    # verbose_name='Направление'
    # )
    #
    # flag = models.ImageField(
    # upload_to='flags/%Y/%m/%d', blank=True, verbose_name='Флаг'
    # )

    def __str__(self):
        return self.name

    class Meta:
        abstract = True
        verbose_name_plural = 'Структурные единицы'
        verbose_name = 'Структурная единица'


class CentralHeadquarter(Unit):
    pass


class DistrictHeadquarter(Unit):
    pass


class RegionalHeadquarter(Unit):

    region = models.OneToOneField(
        'Region',
        related_name='headquarters',
        on_delete=models.PROTECT,
        verbose_name='Регион'
    )


class LocalHeadquarter(Unit):
    pass


class EducationalHeadquarter(Unit):
    pass


class Detachment(Unit):
    area = models.ForeignKey(
        Area,
        null=False,
        blank=False,
        on_delete=models.PROTECT,
        verbose_name='Направление'
    )

    def clean(self):
        if not self.commander:
            raise ValidationError('Отряд должен иметь командира.')

    # регион
    # institution = models.ForeignKey(
    # 'Institution',
    # null=True,
    # blank=True,
    # on_delete=models.PROTECT,
    # verbose_name='Учебное заведение'
    # )
    # город
    # Местный штаб

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'отряды'
        verbose_name = 'Отряд'
