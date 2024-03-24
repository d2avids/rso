from django.http import Http404
from django.utils import timezone
from datetime import datetime
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from questions.models import Question, Attempt, UserAnswer
from questions.serializers import QuestionSerializer
import random


class QuestionsView(APIView):
    """
    Предоставляет вопросы пользователям на основе заданной категории
    через параметры запроса.

    ## Эндпоинт поддерживает следующие параметры запроса:
    - `category` (строка): указывает на категорию вопросов, которые необходимо
    получить.
      Допустимые значения: 'university' и 'safety'.

    ## Ограничения по датам:
    - Вопросы из первого блока ('university') доступны до 10 апреля 2024 года
    включительно.
    - Вопросы из категории 'safety' доступны до 15 июня 2024 года включительно.


    ## Правила:
    - Пользователь должен быть аутентифицирован.
    - Для каждой категории пользователь может совершить не более 3 попыток
     получения вопросов.
    - Вопросы в категории 'university' подбираются из смешанных блоков в
    следующем порядке:
        - 6 вопросов из блока 1,
        - 8 вопросов из блока 2,
        - 5 вопросов из блока 3,
        - 1 вопрос из блока 4.
      Вопросы перемешиваются перед возвратом.
    - Вопросы в категории 'safety' выбираются случайным образом из блока 5
    (всего 15 вопросов).

    ## Ответы:
    При успешном выполнении запроса возвращается список вопросов в формате JSON,
    соответствующих указанной категории. Каждый вопрос включает в себя название,
    изображение (если есть) и варианты ответов.

    В случае ошибки (например, превышения количества попыток или
    неверной категории)
    возвращается сообщение об ошибке и соответствующий HTTP статус.
    """

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        user = request.user
        category = request.query_params.get('category', None)

        current_date = datetime.now().date()
        university_deadline = datetime(2024, 4, 10)
        safety_deadline = datetime(2024, 6, 15)

        attempts_count = Attempt.objects.filter(
            user=user, category=category
        ).count()
        if attempts_count >= 3:
            return Response(
                {"error": "Превышено макс. число попыток (3)"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if category == 'university' and current_date > university_deadline:
            return Response(
                {"error": "Срок получения вопросов по "
                          "категории 'university' истек."},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif category == 'safety' and current_date > safety_deadline:
            return Response(
                {"error": "Срок получения вопросов по "
                          "категории 'safety' истек."},
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            return Response(
                {
                    "error": "Неверная категория. "
                             "Выберите university или safety."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        attempt = Attempt.objects.create(user=user, category=category)
        attempt.questions.set(questions)
        attempt.save()

        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)

    def get_university_questions_mix(self):
        questions_mix = []
        questions_mix.extend(self.get_block_questions(1, 6))
        questions_mix.extend(self.get_block_questions(2, 8))
        questions_mix.extend(self.get_block_questions(3, 5))
        questions_mix.extend(self.get_block_questions(4, 1))
        random.shuffle(questions_mix)
        return questions_mix

    def get_block_questions(self, block_number, count):
        questions = Question.objects.filter(block=block_number).order_by('?')[
                    :count]
        return list(questions)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def submit_answers(request):
    """
    Функция проверяет принадлежность вопросов к последней попытке, регистрирует
    ответы пользователя и вычисляет итоговый счет на основе
    правильности ответов.

    Принимаемые данные:
    Функция принимает POST-запрос с JSON телом, содержащим список ответов
    пользователя. Каждый ответ представлен словарем с двумя ключами:

    question_id - идентификатор вопроса (целое число),
    answer_option_id - идентификатор выбранного варианта ответа (целое число).
    Формат тела запроса:
    ```
    {
      "answers": [
            {
              "question_id": 1,
              "answer_option_id": 3
            },
            {
              "question_id": 2,
              "answer_option_id": 5
            },
            ...
        ]
    }
    ```
    Ответ функции:
    Функция возвращает JSON объект с сообщением о результате операции.
    В случае успешного приема и обработки ответов, возвращается
    общее количество набранных баллов.

    При успешной обработке ответов:
    ```
    {
        "message": "Ответы успешно отправлены. Получено баллов: X"
    }
    ```
    Где X - итоговое количество набранных баллов (целое число).

    При возникновении ошибки (например, если вопросы не принадлежат
    последней попытке или попытка не найдена):
    ```
    {
        "error": "Текст ошибки"
    }
    ```

    Сообщение об ошибке будет соответствовать причине отказа.

    Ограничения и проверки:
    - Пользователь должен быть аутентифицирован.
    - Должна существовать активная попытка пользователя.
    - Для каждой попытки допускается отправка ответов только один раз.
    Все вопросы в отправленных ответах должны соответствовать вопросам
    последней активной попытки пользователя.

    Баллы:
    - За каждый правильный ответ начисляется фиксированное количество баллов.
    - Количество баллов за правильный ответ может варьироваться в зависимости от
    категории попытки (указывается в параметре scores_per_answer).

    HTTP Статусы ответа:
    - 200 OK - запрос успешно обработан,
    - 400 Bad Request - в запросе обнаружена ошибка (например, не все
    вопросы принадлежат последней попытке или ответы уже были отправлены).
    """
    user = request.user
    answers_data = request.data.get('answers', [])

    # Получаем последнюю попытку
    latest_attempt = Attempt.objects.filter(
        user=user
    ).order_by('-timestamp').first()
    if not latest_attempt:
        return Response(
            {'error': 'Сначала нужны получить вопросы.'}, status=400
        )

    score = 0
    scores_per_answer = 6.66 if latest_attempt.category == 'safety' else 5

    with transaction.atomic():
        # Проверяем, есть ли уже ответы для этой попытки
        if UserAnswer.objects.filter(attempt=latest_attempt).exists():
            return Response(
                {'error': 'Ответы по попытке уже были приняты.'},
                status=400
            )

        for answer in answers_data:
            question_id = answer.get('question_id')
            answer_option_id = answer.get('answer_option_id')

            # Проверяем, принадлежит ли вопрос к последней попытке
            if not Question.objects.filter(
                    id=question_id, attempt=latest_attempt
            ).exists():
                return Response(
                    {'error': 'Вопрос не относится '
                                'к последней попытке.'},
                    status=400
                )

            question = get_object_or_404(Question, id=question_id)
            answer_option = get_object_or_404(
                question.answer_options, id=answer_option_id
            )

            UserAnswer.objects.create(
                attempt=latest_attempt,
                question=question,
                answer_option=answer_option
            )
            if answer_option.is_correct:
                score += scores_per_answer

    latest_attempt.score = round(score)
    latest_attempt.save()

    return Response(
        {
            'message': f'Ответы успешно отправлены. '
                    f'Получено баллов: {score}'
        },
        status=status.HTTP_200_OK
    )
