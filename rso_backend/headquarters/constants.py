from django.db import models


class PositionsOption(models.TextChoices):
    """Позиции пользователя в рамках структурной единицы."""
    no_position = 'no_position', 'Без должности'
    comissioner = 'comissioner', 'Комиссар'
    master_methodologist = 'master_methodologist', 'Мастер-методист'
    specialist = 'specialist', 'Специалист'
    commander = 'commander', 'Командир'
