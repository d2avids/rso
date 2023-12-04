from django.db import models


class Gender(models.TextChoices):
    """Выбор пола."""

    MALE = 'male', 'Мужской'
    FEMALE = 'female', 'Женский'


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


class RelationshipType(models.TextChoices):
    """Типы отношений."""

    father = 'father', 'Отец'
    mother = 'mother', 'Мать'
    guardian = 'guardian', 'Опекун'


class UsersRolesChoices(models.TextChoices):
    """Пользовательские роли."""

    admin = 'admin', 'Администратор'
    commander = 'commander', 'Коммандир штаба'
    candidate = 'candidate', 'Кандидат'
    fighter = 'fighter', 'Боец'
    unregistered_user = (
        'unregistered_user', 'Незарегистрированный пользователь'
    )
    unverified_user = (
        'unverified_user', 'Неверифицированный пользователь'
    )
    verified_user = (
        'verified_user', 'Верифицированный пользователь'
    )
    trusted_user = (
        'trusted_user', 'Доверенный пользователь'
    )
