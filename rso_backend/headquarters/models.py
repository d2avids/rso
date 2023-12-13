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
        verbose_name='Описание',
    )
    emblem = models.ImageField(
        upload_to=image_path,
        verbose_name='Эмблема',
        blank=True,
        null=True
    )
    social_vk = models.CharField(
        max_length=50,
        verbose_name='Ссылка ВК',
    )
    social_tg = models.CharField(
        max_length=50,
        verbose_name='Ссылка Телеграм',
    )
    city = models.CharField(
        max_length=100,
        verbose_name='Город (нас. пункт)',
        blank=True,
        null=True,
    )
    banner = models.ImageField(
        upload_to=image_path,
        blank=True,
        null=True,
        verbose_name='Баннер'
    )
    slogan = models.CharField(
        max_length=100,
        verbose_name='Девиз'
    )
    founding_date = models.DateField(
        verbose_name='Дата основания',
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
    name_for_certificates = models.CharField(
        max_length=250,
        verbose_name='Наименование штаба (для справок)',
    )
    conference_date = models.DateField(
        verbose_name='Дата учр. конференции регионального штаба',
        null=True,
        blank=True,
    )
    registry_date = models.DateField(
        verbose_name='Дата регистрации в реестре молодежных и детских '
                     'общественных объединений...',
        null=True,
        blank=True,
    )
    registry_number = models.CharField(
        max_length=250,
        verbose_name='Наименование штаба в Предложном падеже',
    )
    case_name = models.CharField(
        max_length=250,
        verbose_name='Наименование штаба в Предложном падеже (для справок)',
    )
    legal_address = models.CharField(
        max_length=250,
        verbose_name='Юридический адрес (для справок)',
    )
    requisites = models.CharField(
        max_length=250,
        verbose_name='Реквизиты (для справок)',
    )

    class Meta:
        verbose_name_plural = 'Региональные штабы'
        verbose_name = 'Региональный штаб'


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
        blank=True,
        null=True,
    )
    region = models.ForeignKey(
        'Region',
        related_name='detachments',
        on_delete=models.PROTECT,
        verbose_name='Привязка к региону'
    )
    educational_institution = models.ForeignKey(
        'EducationalInstitution',
        related_name='detachments',
        on_delete=models.PROTECT,
        verbose_name='Привязка к учебному заведению'
    )
    area = models.ForeignKey(
        'Area',
        null=False,
        blank=False,
        on_delete=models.PROTECT,
        verbose_name='Направление'
    )
    photo1 = models.ImageField(
        upload_to=image_path,
        blank=True,
        verbose_name='Фото 1'
    )
    photo2 = models.ImageField(
        upload_to=image_path,
        blank=True,
        verbose_name='Фото 2'
    )
    photo3 = models.ImageField(
        upload_to=image_path,
        blank=True,
        verbose_name='Фото 3'
    )
    photo4 = models.ImageField(
        upload_to=image_path,
        blank=True,
        verbose_name='Фото 4'
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
        if self.regional_headquarter:
            if self.region != self.regional_headquarter.region:
                raise ValidationError({
                    'region': 'Этот регион не совпадает с регионом '
                              'выбранного регионального штаба.'
                })
        if self.educational_headquarter:
            if (
                    self.educational_headquarter.educational_institution !=
                    self.educational_institution
            ):
                raise ValidationError({
                    'educational_institution': 'Это учебное заведение '
                                               'не совпадает с учебным '
                                               'заведением выбранного '
                                               'образовательного штаба.'
                })

    def save(self, *args, **kwargs):
        """Автоматически заполняет региональный штаб по региону."""
        if not self.regional_headquarter:
            self.regional_headquarter = self.region.headquarters.first()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Отряды'
        verbose_name = 'Отряд'


class Position(models.Model):
    """Хранение наименований должностей для членов отрядов и штабов."""

    name = models.CharField(max_length=150, verbose_name='Должность')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Должности'
        verbose_name = 'Должность'


class UserUnitPosition(models.Model):
    """
    Абстрактная базовая модель для представления пользователя в качестве
    члена тех или иных структурных единиц.

    Эта модель определяет общие атрибуты для хранения информации о
    пользователе, его должности и статусе доверенности в конкретной структурной
    единице.
    """
    user = models.ForeignKey(
        'users.RSOUser',
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name="%(class)s_position"
    )
    position = models.ForeignKey(
        'Position',
        on_delete=models.CASCADE,
        verbose_name='Должность',
        null=True,
        blank=True,
    )
    is_trusted = models.BooleanField(default=False, verbose_name='Доверенный')

    def save(self, *args, **kwargs):
        """
        Родительский метод хранит логику добавления пользователя в качестве
        участника во все структурные единицы, стоящие выше по иерархии того
        отряда, в который он был добавлен.

        Принимает параметры 'headquarter' и 'class_above', переданные в kwargs,
        которые указывают на структурную единицу и связанную модель выше по
        иерархии соответственно.

        Исключения:
        - ValueError: выбрасывается, если в дочернем классе не предоставлены
        необходимые параметры 'headquarter' и 'class_above' при создании
        нового объекта (не вызывается для центрального штаба).
        """
        if self._state.adding:
            headquarter = kwargs.pop('headquarter', None)
            class_above = kwargs.pop('class_above', None)
            if headquarter and class_above:
                user_id = self.user_id
                if self.__class__.objects.filter(user_id=user_id).exists():
                    raise ValidationError(
                        'Пользователь уже является членом одного из отрядов.'
                    )
                class_above.objects.create(
                    user_id=user_id,
                    headquarter=headquarter
                )
            else:
                raise ValueError(
                    'headquarter и class_above должны быть переданы '
                    'в качестве kwargs в подклассах'
                )
        super().save(*args, **kwargs)

    def delete_user_from_all_units(self):
        """
        Удаляет пользователя из всех связанных структурных единиц.
        """
        UserCentralHeadquarterPosition.objects.filter(user=self.user).delete()
        UserDistrictHeadquarterPosition.objects.filter(user=self.user).delete()
        UserRegionalHeadquarterPosition.objects.filter(user=self.user).delete()
        UserLocalHeadquarterPosition.objects.filter(user=self.user).delete()
        UserEducationalHeadquarterPosition.objects.filter(
            user=self.user).delete()
        UserDetachmentPosition.objects.filter(user=self.user).delete()

    def delete(self, *args, **kwargs):
        """
        Переопределяет стандартный метод delete для обеспечения
        удаления пользователя из всех структурных единиц при его удалении
        из одной из структур.
        """
        self.delete_user_from_all_units()
        super().delete(*args, **kwargs)

    class Meta:
        abstract = True

    def __str__(self):
        position = self.position.name if self.position else 'без должности'
        return (
            f'Пользователь {self.user.username} - '
            f'{position} '
            f'в структурной единице "{self.headquarter.name}"'
        )


class UserCentralHeadquarterPosition(UserUnitPosition):
    headquarter = models.ForeignKey(
        'CentralHeadquarter',
        on_delete=models.CASCADE,
        verbose_name='Центральный штаб',
        related_name='members'
    )

    def save(self, *args, **kwargs):
        if self._state.adding:
            return
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Члены центрального штаба'
        verbose_name = 'Член центрального штаба'


class UserDistrictHeadquarterPosition(UserUnitPosition):
    headquarter = models.ForeignKey(
        'DistrictHeadquarter',
        on_delete=models.CASCADE,
        verbose_name='Окружной штаб',
        related_name='members'
    )

    def save(self, *args, **kwargs):
        if self._state.adding:
            central_position = UserCentralHeadquarterPosition.objects.create(
                user_id=self.user_id,
                headquarter=CentralHeadquarter.objects.first(),
            )
            central_position.save_base(force_insert=True)
            kwargs['headquarter'] = self.headquarter.central_headquarter
            kwargs['class_above'] = UserCentralHeadquarterPosition
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Члены окружных штабов'
        verbose_name = 'Член окружного штаба'


class UserRegionalHeadquarterPosition(UserUnitPosition):
    headquarter = models.ForeignKey(
        'RegionalHeadquarter',
        on_delete=models.CASCADE,
        verbose_name='Региональный штаб',
        related_name='members'
    )

    def save(self, *args, **kwargs):
        if self._state.adding:
            kwargs['headquarter'] = self.headquarter.district_headquarter
            kwargs['class_above'] = UserDistrictHeadquarterPosition
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Члены региональных штабов'
        verbose_name = 'Член регионального штаба'


class UserLocalHeadquarterPosition(UserUnitPosition):
    headquarter = models.ForeignKey(
        'LocalHeadquarter',
        on_delete=models.CASCADE,
        verbose_name='Локальный штаб',
        related_name='members'
    )

    def save(self, *args, **kwargs):
        if self._state.adding:
            kwargs['headquarter'] = self.headquarter.regional_headquarter
            kwargs['class_above'] = UserRegionalHeadquarterPosition
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Члены локальных штабов'
        verbose_name = 'Член локального штаба'


class UserEducationalHeadquarterPosition(UserUnitPosition):
    headquarter = models.ForeignKey(
        'EducationalHeadquarter',
        on_delete=models.CASCADE,
        verbose_name='Образовательный штаб',
        related_name='members'
    )

    def get_first_filled_headquarter(self):
        """
        Возвращает первый связанный с ШОО заполненный штаб по иерархии:
        МШ или РШ.
        """
        local_headquarter = self.headquarter.local_headquarter
        if local_headquarter:
            return local_headquarter
        return self.headquarter.regional_headquarter

    def save(self, *args, **kwargs):
        if self._state.adding:
            kwargs['headquarter'] = self.get_first_filled_headquarter()
            kwargs['class_above'] = UserLocalHeadquarterPosition
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Члены образовательных штабов'
        verbose_name = 'Член образовательного штаба'


class UserDetachmentPosition(UserUnitPosition):
    headquarter = models.ForeignKey(
        'Detachment',
        on_delete=models.CASCADE,
        verbose_name='Отряд',
        related_name='members'
    )

    def get_first_filled_headquarter(self):
        """
        Возвращает первый связанный с отрядом заполненный штаб по иерархии: 
        ШОО, МШ или РШ.
        """
        educational_headquarter = self.headquarter.educational_headquarter
        if educational_headquarter:
            return educational_headquarter
        local_headquarter = self.headquarter.local_headquarter
        if local_headquarter:
            return local_headquarter
        return self.headquarter.regional_headquarter

    def save(self, *args, **kwargs):
        if self._state.adding:
            kwargs['headquarter'] = self.get_first_filled_headquarter()
            kwargs['class_above'] = UserEducationalHeadquarterPosition
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = 'Члены отрядов'
        verbose_name = 'Член отряда'


class UserDetachmentApplication(models.Model):
    """Таблица для подачи заявок на вступление в отряд."""
    user = models.ForeignKey(
        'users.RSOUser',
        on_delete=models.CASCADE,
        verbose_name='Пользователь, подавший заявку на вступление в отряд',
        related_name='applications',
    )
    detachment = models.ForeignKey(
        'Detachment',
        on_delete=models.CASCADE,
        verbose_name='Отряд, в который была подана заявка на вступление',
        related_name='applications',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'detachment'],
                                    name='unique_constraint')
        ]
        verbose_name_plural = 'Заявки на вступление в отряды'
        verbose_name = 'Заявка на вступление в отряд'
