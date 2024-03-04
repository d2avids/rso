from headquarters.models import (CentralHeadquarter, Detachment,
                                 DistrictHeadquarter, EducationalHeadquarter,
                                 LocalHeadquarter, RegionalHeadquarter)
from headquarters.serializers import (CentralHeadquarterSerializer,
                                      ShortDetachmentSerializer,
                                      ShortDistrictHeadquarterSerializer,
                                      ShortEducationalHeadquarterSerializer,
                                      ShortLocalHeadquarterSerializer,
                                      ShortRegionalHeadquarterSerializer)

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
POST_RESET_PASSWORD = {'post': 'reset_password'}
DOWNLOAD_MEMBERSHIP_FILE = {'get': 'download_membership_file'}
DOWNLOAD_CONSENT_PD = {'get': 'download_consent_personal_data'}
DOWNLOAD_PARENT_CONSENT_PD = {'get': 'download_parent_consent_personal_data'}
DOWNLOAD_ALL_FORMS = {'get': 'download_all_forms'}

HEADQUARTERS_MODELS_MAPPING = {
        'Центральные штабы': CentralHeadquarter,
        'Окружные штабы': DistrictHeadquarter,
        'Региональные штабы': RegionalHeadquarter,
        'Местные штабы': LocalHeadquarter,
        'Образовательные штабы': EducationalHeadquarter,
        'Отряды': Detachment
}

SHORT_HEADQUARTERS_SERIALIZERS_MAPPING = {
        'Центральные штабы': CentralHeadquarterSerializer,
        'Окружные штабы': ShortDistrictHeadquarterSerializer,
        'Региональные штабы': ShortRegionalHeadquarterSerializer,
        'Местные штабы': ShortLocalHeadquarterSerializer,
        'Образовательные штабы': ShortEducationalHeadquarterSerializer,
        'Отряды': ShortDetachmentSerializer
}
