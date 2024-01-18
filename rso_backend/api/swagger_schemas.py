from rest_framework import serializers
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import status
from api.serializers import ShortDetachmentSerializer
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

answer_response = {
    status.HTTP_200_OK: openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
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

response_start_page_competitions = {
    status.HTTP_200_OK: openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'is_auth': openapi.Schema(
                type=openapi.TYPE_BOOLEAN,
                title='Авторизирован ли пользователь',
            ),
            'is_commander_and_not_junior': openapi.Schema(
                type=openapi.TYPE_BOOLEAN,
                title='Является ли пользователь командиром старого отряда',
            ),
            'is_participant': openapi.Schema(
                type=openapi.TYPE_BOOLEAN,
                title='Участвует ли уже пользователь в конкурсе',
            ),
            'is_application': openapi.Schema(
                type=openapi.TYPE_BOOLEAN,
                title='Подал ли пользователь уже заявку',
            ),
            'application_status': openapi.Schema(
                type=openapi.TYPE_STRING,
                title=('Статус заявки, варианты: '
                       '"Ждет верификации", '
                       '"Ждет подтверждения младшего отряда"')
            ),
            'detachment_list': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(
                    type='object',
                    properties={
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
                    },
                    title='Список свободных отрядов-новичков',
                )
            ),
        }
    )
}
