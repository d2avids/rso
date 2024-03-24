from django.db import models


class Question(models.Model):
    class Block(models.TextChoices):
        HISTORY = '1', 'История РСО'
        REGULATORY_DOCUMENTS = '2', 'Нормативные документы'
        TEAM_COMPETENCIES = '3', 'Компетенции командного состава и отряда'
        CASE_SOLUTIONS = '4', 'Решение кейсовых ситуаций'

    block = models.CharField(
        max_length=2,
        choices=Block.choices,
        default=Block.HISTORY,
    )
    title = models.TextField()
    image = models.ImageField(upload_to='questions/', blank=True, null=True)

    def __str__(self):
        return self.title


