from rest_framework import serializers
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import status
from events.models import Event


class EventSwaggerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = (
            'format',
            'direction',
            'status',
            'name',
            'banner',
            'scale',
            'conference_link',
            'address',
            'participants_number',
            'description',
            'application_type',
            'available_structural_units',
        )


applications_response = {
    status.HTTP_200_OK: openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'user': openapi.Schema(type=openapi.TYPE_OBJECT)
        }
    )
}

answer = {
            'id': openapi.Schema(
                type=openapi.TYPE_INTEGER, read_only=True, title='ID'
            ),
            'issue': openapi.Schema(
                type=openapi.TYPE_STRING, title='Вопрос'
            ),
            'answer': openapi.Schema(
                type=openapi.TYPE_STRING, title='Ответ'
            ),
            'event': openapi.Schema(
                type=openapi.TYPE_INTEGER, read_only=True, title='Мероприятие'
            ),
            'user': openapi.Schema(
                type=openapi.TYPE_INTEGER, read_only=True, title='Пользователь'
            ),
        }

short_user = {
    'id': openapi.Schema(
        type=openapi.TYPE_INTEGER, read_only=True, title='ID'
    ),
    'username': openapi.Schema(
        type=openapi.TYPE_STRING, read_only=True, title='Логин'
    ),
    'avatar': openapi.Schema(
        type=openapi.TYPE_OBJECT, read_only=True, title='Аватар'
    ),
    'email': openapi.Schema(
        type=openapi.TYPE_STRING, read_only=True, title='Email'
    ),
    'first_name': openapi.Schema(
        type=openapi.TYPE_STRING, read_only=True, title='Имя'
    ),
    'last_name': openapi.Schema(
        type=openapi.TYPE_STRING, read_only=True, title='Фамилия'
    ),
    'patronymic_name': openapi.Schema(
        type=openapi.TYPE_STRING, read_only=True, title='Отчество'
    ),
    'date_of_birth': openapi.Schema(
        type=openapi.TYPE_STRING, read_only=True, title='Дата рождения'
    ),
    'membership_fee': openapi.Schema(
        type=openapi.TYPE_BOOLEAN, read_only=True, title='Членский взнос оплачен'
    ),
}

short_event = {
    'id': openapi.Schema(
        type=openapi.TYPE_INTEGER, read_only=True, title='ID'
    ),
    'name': openapi.Schema(
        type=openapi.TYPE_STRING, read_only=True, title='Название'
    ),
    'banner': openapi.Schema(
        type=openapi.TYPE_STRING, read_only=True, title='Баннер'
    )
}

document = {
    'id': openapi.Schema(
        type=openapi.TYPE_INTEGER, read_only=True, title='ID'
    ),
    'user': openapi.Schema(
        type=openapi.TYPE_OBJECT, title='Пользователь'
    ),
    'event': openapi.Schema(
        type=openapi.TYPE_OBJECT, title='Мероприятие'
    ),
    'document': openapi.Schema(
        type=openapi.TYPE_STRING, title='Документ'
    ),
}

answer_response = {
    status.HTTP_200_OK: openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties=answer
    )
}

application_me_response = {
    status.HTTP_200_OK: openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'id': openapi.Schema(
                type=openapi.TYPE_INTEGER, read_only=True, title='ID'
            ),
            'user': openapi.Schema(
                type=openapi.TYPE_OBJECT,
                read_only=True,
                title='Пользователь',
                properties=short_user
            ),
            'event': openapi.Schema(
                type=openapi.TYPE_OBJECT,
                read_only=True,
                properties=short_event,
                title='Мероприятие'
            ),
            'answers': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(
                    type=openapi.TYPE_OBJECT,
                    title='Ответы',
                    properties=answer
                )
            ),
            'documents': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(
                    type=openapi.TYPE_OBJECT,
                    title='Документы',
                    properties=document
                )
            ),
            'created_at': openapi.Schema(
                type=openapi.TYPE_STRING,
                format='date-time',
                read_only=True,
                title='Дата создания заявки'
            ),
        }
    )
}


participant_me_response = {
    status.HTTP_200_OK: openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'id': openapi.Schema(
                type=openapi.TYPE_INTEGER, read_only=True, title='ID'
            ),
            'event': openapi.Schema(
                type=openapi.TYPE_OBJECT,
                read_only=True,
                properties=short_event,
                title='Мероприятие'
            ),
            'user': openapi.Schema(
                type=openapi.TYPE_OBJECT,
                read_only=True,
                title='Пользователь',
                properties=short_user
            ),
            'answers': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(
                    type=openapi.TYPE_OBJECT,
                    title='Ответы',
                    properties=answer
                )
            ),
            'documents': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(
                    type=openapi.TYPE_OBJECT,
                    title='Документы',
                    properties=document
                )
            )
        }
    )
}

request_update_application = (
    openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'is_confirmed_by_junior': openapi.Schema(
                    type=openapi.TYPE_BOOLEAN,
                    title='Подтверждено младшим отрядом')
            }
    )
)

response_create_application = (
    openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'junior_detachment': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    title='ID младшего отряда',
                )
            }
    )
)

response_competitions_applications = {
    status.HTTP_200_OK: openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'id': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                title='ID',
                read_only=True
            ),
            'competition': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                title='Конкурс',
                read_only=True
            ),
            'detachment': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                title='Отряд',
                read_only=True
            ),
            'junior_detachment': openapi.Schema(
                type=[openapi.TYPE_INTEGER],
                title='Младший отряд',
                x_nullable=True
            ),
            'created_at': openapi.Schema(
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATETIME,
                title='Дата и время создания заявки',
                read_only=True
            ),
            'is_confirmed_by_junior': openapi.Schema(
                type=openapi.TYPE_BOOLEAN,
                title='Подтверждено младшим отрядом'
            ),
        }
    )
}

response_competitions_participants = {
    status.HTTP_200_OK: openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'id': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                title='ID',
                read_only=True
            ),
            'competition': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                title='Конкурс',
                read_only=True
            ),
            'detachment': openapi.Schema(
                type=openapi.TYPE_INTEGER,
                title='Отряд',
                read_only=True
            ),
            'junior_detachment': openapi.Schema(
                type=[openapi.TYPE_INTEGER],
                title='Младший отряд',
                read_only=True,
                x_nullable=True
            ),
            'created_at': openapi.Schema(
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATETIME,
                title='Дата и время создания заявки',
                read_only=True
            ),
        }
    )
}

short_detachment = {
    'id': openapi.Schema(
        type=openapi.TYPE_INTEGER,
        title='ID',
    ),
    'name': openapi.Schema(
        type=openapi.TYPE_STRING,
        title='Название',
    ),
    'banner': openapi.Schema(
        type=openapi.TYPE_STRING,
        title='Путь к баннеру',
    ),
}

response_junior_detachments = {
    status.HTTP_200_OK: openapi.Schema(
        type=openapi.TYPE_ARRAY,
        items=openapi.Items(
            type=openapi.TYPE_OBJECT,
            properties=short_detachment,
            title='Младшие отряды'
        )
    )
}
