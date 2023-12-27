from django.db import models


class PositionsOption(models.TextChoices):
    """Позиции пользователя в рамках структурной единицы."""
    no_position = 'no_position', 'Без должности'
    comissioner = 'comissioner', 'Комиссар'
    master_methodologist = 'master_methodologist', 'Мастер-методист'
    specialist = 'specialist', 'Специалист'
    commander = 'commander', 'Командир'
    central_commander = (
        'central_commander',
        'Коммандир центрального штаба'
    )
    district_commander = 'district_commander', 'Коммандир окружного штаба'
    regional_commander = 'regional_commander', 'Коммандир регионального штаба'
    local_commander = 'local_commander', 'Коммандир местного штаба'
    edu_commander = (
        'edu_commander',
        'Коммандир штаба образовательной организации'
    )
    detachment_commander = (
        'detachment_commander',
        'Коммандир отряда'
    )
    candidate = 'candidate', 'Кандидат'
    fighter = 'fighter', 'Боец'
