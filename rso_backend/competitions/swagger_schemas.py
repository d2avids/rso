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


q7schema_request = openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                required=['event_name', 'number_of_participants', 'links'],
                properties={
                    'event_name': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        title='Название мероприятия',
                        required='true'
                    ),
                    'number_of_participants': openapi.Schema(
                        type=openapi.TYPE_INTEGER,
                        title='Количество участников',
                        required='true',
                        minimum=1,
                        maximum=100
                    ),
                    'links': openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        description='Ссылки на публикации',
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            required=['link'],
                            properties={
                                'link': openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    title='Ссылка на публикацию о мероприятии',
                                    format='url',
                                    minLength=1,
                                    maxLength=500
                                )
                            }
                        )
                    ),
                    'certificate_scans': openapi.Schema(
                        type=openapi.TYPE_STRING,
                        title='Сканы сертификатов',
                        format='url',
                        x_nullable=True
                    )
                }
            )
        )
