from django.db import models


class Gender(models.TextChoices):
    """Выбор пола."""
    MALE = 'male', 'Мужской'
    FEMALE = 'female', 'Женский'


class UnitType(models.TextChoices):
    """Структурные единицы."""
    DETACHMENT = 'detachment', 'Отряд'
    OTHER_UNIT = 'other_unit', 'Другая структурная единица'


class StudyForm(models.TextChoices):
    """Формы обучения."""
    full_time = 'full_time', 'очная'
    part_time = 'part_time', 'очно-заочная'
    extramural_studies = 'extramural_studies', 'заочная'
    distant_studies = 'distant_studies', 'дистанционное'


class MilitaryDocType(models.TextChoices):
    """Типы военных документов."""
    military_certificate = (
        'military_certificate',
        'Удостоверение гражданина подлежащего вызову на срочную военную службу'
    )
    military_ticket = 'military_ticket', 'Военный билет'


class PrivacyOption(models.TextChoices):
    """Настройки приватности пользователя."""
    ALL = 'all', 'Все'
    DETACHMENT_MEMBERS = 'detachment_members', 'Члены отряда',
    MANAGEMENT_MEMBERS = 'management_members', 'Руководство'


class PositionsOption(models.TextChoices):
    """Позиции пользователя."""
    no_position = 'no_position', 'Без должности'
    comissioner = 'comissioner', 'Комиссар'
    master_methodologist = 'master_methodologist', 'Мастер-методист'
    specialist = 'specialist', 'Специалист'
    commander = 'commander', 'Командир'
