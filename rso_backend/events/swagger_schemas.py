from drf_yasg import openapi
from rest_framework import serializers, status

from events.models import Event


class GroupApplicantIdSerializer(serializers.Serializer):
    user_ids = serializers.ListField(child=serializers.IntegerField())


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
            'org_central_headquarter',
            'org_district_headquarter',
            'org_regional_headquarter',
            'org_local_headquarter',
            'org_educational_headquarter',
            'org_detachment',
        )


MEMBERSHIP_FEE = openapi.Parameter(
    'membership_fee',
    openapi.IN_QUERY,
    description="Членский взнос",
    type=openapi.TYPE_BOOLEAN
)
BIRTH_DATE_FROM = openapi.Parameter(
    'birth_date_from',
    openapi.IN_QUERY,
    description="Возраст от",
    type=openapi.TYPE_INTEGER
)
BIRTH_DATE_TO = openapi.Parameter(
    'birth_date_to',
    openapi.IN_QUERY,
    description="Возраст до",
    type=openapi.TYPE_INTEGER
)
GENDER = openapi.Parameter(
    'gender',
    openapi.IN_QUERY,
    description="male/female",
    type=openapi.TYPE_STRING
)

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
        type=openapi.TYPE_BOOLEAN, read_only=True,
        title='Членский взнос оплачен'
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
