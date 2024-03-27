from drf_yasg import openapi

answers_request_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'answers': openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Items(
                type=openapi.TYPE_OBJECT,
                properties={
                    'question_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Идентификатор вопроса'),
                    'answer_option_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Идентификатор выбранного варианта ответа'),
                },
            ),
            description='Список ответов пользователя'
        )
    },
)