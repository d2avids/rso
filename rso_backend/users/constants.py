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

    ALL = 'Все', 'Все'
    DETACHMENT_MEMBERS = 'Члены отрядаs', 'Члены отряда',
    MANAGEMENT_MEMBERS = 'Руководство', 'Руководство'


class RelationshipType(models.TextChoices):
    """Типы отношений."""

    father = 'father', 'Отец'
    mother = 'mother', 'Мать'
    guardian = 'guardian', 'Опекун'


DOCUMENTS_RAW_EXISTS = 'Документы для данного пользователя уже существуют'
PRIVACY_RAW_EXISTS = (
        'Настройки приватности для данного пользователя уже существуют'
)
MEDIA_RAW_EXISTS = 'Медиа-данные для данного пользователя уже существуют'
STATEMENT_RAW_EXISTS = (
        'Документы пользователя для вступления в РСО уже '
        'существуют для данного пользователя'
)
REGION_RAW_EXISTS = (
        'Данные региона для данного пользователя уже существуют'
)
TOO_MANY_EDUCATIONS = (
        'Уже существует 5 записей о допобразовании.'
)
EDUCATION_RAW_EXISTS = (
        'Образовательная информация для данного пользователя уже существует'
)
