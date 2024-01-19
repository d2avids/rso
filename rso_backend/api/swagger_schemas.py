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

application_me_response = {
    status.HTTP_200_OK: openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'id': openapi.Schema(
                type=openapi.TYPE_INTEGER, read_only=True, title='ID'
            ),
            'user': openapi.Schema(
                type=openapi.TYPE_INTEGER, read_only=True, title='Пользователь'
            ),
            'event': openapi.Schema(
                type=openapi.TYPE_INTEGER, read_only=True, title='Мероприятие'
            ),
            'answers': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(
                    type='object',
                    title='Ответы',
                    properties={
                        'id': openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            title='ID',
                        ),
                        'issue': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            title='Вопрос',
                        ),
                        'answer': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            title='Ответ',
                        ),
                        'event': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            title='Мероприятие',
                        ),
                        'user': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            title='Пользователь',
                        )
                    },
                )
            ),
            'documents': openapi.Schema(
                type=openapi.TYPE_STRING, read_only=True, title='Документы'
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
