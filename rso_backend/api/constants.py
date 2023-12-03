CREATE_DELETE = {
        'post': 'create',
        'delete': 'destroy'
    }
LIST = {
        'get': 'list',
    }
UPDATE = {
        'put': 'update',
        'patch': 'partial_update',
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
CREATE_METHOD = {'post': 'create', }
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
