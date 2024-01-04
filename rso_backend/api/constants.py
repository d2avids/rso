from drf_yasg import openapi

CREATE_DELETE = {
        'post': 'create',
        'delete': 'destroy'
    }
LIST = {
        'get': 'list',
    }
UPDATE_RETRIEVE = {
        'put': 'update',
        'patch': 'partial_update',
        'get': 'retrieve',
}
RETRIEVE = {
        'get': 'retrieve',
}
RETRIEVE_CREATE = {
        'get': 'retrieve',
        'post': 'create',
}
DELETE = {
        'delete': 'destroy',
}
CRUD_METHODS_WITHOUT_LIST = {
        'get': 'retrieve',
        'put': 'update',
        'post': 'create',
        'patch': 'partial_update',
        'delete': 'destroy'
    }
LIST_CREATE = {
        'get': 'list',
        'post': 'create',
}
UPDATE_DELETE = {
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy',
}
CREATE_METHOD = {'post': 'create', }
DOWNLOAD_MEMBERSHIP_FILE = {'get': 'download_membership_file'}
DOWNLOAD_CONSENT_PD = {'get': 'download_consent_personal_data'}
DOWNLOAD_PARENT_CONSENT_PD = {'get': 'download_parent_consent_personal_data'}
DOWNLOAD_ALL_FORMS = {'get': 'download_all_forms'}
EDUCATION_RAW_EXISTS = (
        'Образовательная информация для данного пользователя уже существует'
)
DOCUMENTS_RAW_EXISTS = 'Документы для данного пользователя уже существуют'
PRIVACY_RAW_EXISTS = (
        'Настройки приватности для данного пользователя уже существуют'
)
MEDIA_RAW_EXISTS = 'Медиа-данные для данного пользователя уже существуют'
STATEMENT_RAW_EXISTS = (
        'Документы пользователя для вступления в РСО уже '
        'существуют для данного пользователя'
)
REGION_RAW_EXISTS = (
        'Данные региона для данного пользователя уже существуют'
)
TOO_MANY_EDUCATIONS = (
        'Уже существует 5 записей о допобразовании.'
)
EVENT_TIME_DATA_RAW_EXISTS = (
        'Информация о времени проведения данного мероприятия уже существует'
)
EVENT_DOCUMENT_DATA_RAW_EXISTS = (
        'Информация о необходимых документах для данного мероприятия уже '
        'существует'
)


properties = {
        'cert_start_date': openapi.Schema(
                type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
        ),
        'cert_end_date': openapi.Schema(
                type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
        ),
        'recipient': openapi.Schema(type=openapi.TYPE_STRING),
        'issue_date': openapi.Schema(
                type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE
        ),
        'number': openapi.Schema(type=openapi.TYPE_STRING),
        'ids': openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Schema(type=openapi.TYPE_INTEGER)
        ),
}

properties_external = {
        'signatory': openapi.Schema(type=openapi.TYPE_STRING),
        'position_procuration': openapi.Schema(
                type=openapi.TYPE_STRING
        ),
}
