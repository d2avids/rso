from drf_yasg import openapi
from rest_framework import status

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
    'area': openapi.Schema(
        type=openapi.TYPE_STRING,
        title='Направление',
    ),
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
                type=openapi.TYPE_OBJECT,
                properties=short_detachment,
                title='Отряд',
                read_only=True
            ),
            'junior_detachment': openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties=short_detachment,
                title='Младший отряд',
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
                type=openapi.TYPE_OBJECT,
                properties=short_detachment,
                title='Отряд',
                read_only=True
            ),
            'junior_detachment': openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties=short_detachment,
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
