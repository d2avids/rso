from django.db import models


class Question(models.Model):
    class Block(models.TextChoices):
        HISTORY = '1', 'История РСО'
        REGULATORY_DOCUMENTS = '2', 'Нормативные документы'
        TEAM_COMPETENCIES = '3', 'Компетенции командного состава и отряда'
        CASE_SOLUTIONS = '4', 'Решение кейсовых ситуаций'
        WORK_SAFETY = '5', 'Охрана труда'

    block = models.CharField(
        max_length=2,
        choices=Block.choices,
        default=Block.HISTORY,
        verbose_name='Блок вопросов'
    )
    title = models.TextField(verbose_name='Вопрос')
    image = models.ImageField(
        upload_to='questions/',
        blank=True,
        null=True,
        verbose_name='Изображение'
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'


class AnswerOption(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='answer_options'
    )
    text = models.TextField(blank=True)
    image = models.ImageField(upload_to='answers/', blank=True, null=True)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text if self.text else 'Ответ картинкой'

    class Meta:
        verbose_name = 'Вариант ответа'
        verbose_name_plural = 'Варианты ответов'


class Attempt(models.Model):
    class Category(models.TextChoices):
        UNIVERSITY = 'university', ('Тест по обучению '
                                    '(корпоративный университет)')
        SAFETY = 'safety', 'Тест по безопасности и охране труда'

    user = models.ForeignKey(
        'users.RSOUser', on_delete=models.CASCADE, related_name='attempts'
    )
    timestamp = models.DateTimeField(
        auto_now_add=True, verbose_name='Время начала попытки'
    )
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.UNIVERSITY,
        verbose_name='Категория попытки'
    )
    questions = models.ManyToManyField(
        Question, related_name='included_in_attempts'
    )
    score = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='Количество баллов'
    )

    def __str__(self):
        return (
            f"{self.user.last_name} {self.user.first_name} id {self.user_id} "
            f"получил(а) вопросы от {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
        )

    class Meta:
        verbose_name = 'Попытка пользователя'
        verbose_name_plural = 'Попытки пользователей'


class UserAnswer(models.Model):
    attempt = models.ForeignKey(
        Attempt,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='Попытка'
    )
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, verbose_name='Вопрос'
    )
    answer_option = models.ForeignKey(
        AnswerOption, on_delete=models.CASCADE, verbose_name='Вариант ответа'
    )

    def __str__(self):
        return (
            f"{self.attempt.user.last_name} {self.attempt.user.first_name} - "
            f"{self.question.title} - {self.answer_option.text}"
        )

    class Meta:
        verbose_name = 'Ответ пользователя'
        verbose_name_plural = 'Ответы пользователей'
        unique_together = ('attempt', 'question')
