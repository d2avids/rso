from headquarters.models import CentralHeadquarter, DistrictHeadquarter, RegionalHeadquarter, LocalHeadquarter, EducationalHeadquarter, Detachment
from headquarters.serializers import CentralHeadquarterSerializer, ShortDistrictHeadquarterSerializer, ShortRegionalHeadquarterSerializer, ShortLocalHeadquarterSerializer, ShortEducationalHeadquarterSerializer, ShortDetachmentSerializer


EVENT_TIME_DATA_RAW_EXISTS = (
        'Информация о времени проведения данного мероприятия уже существует'
)
EVENT_DOCUMENT_DATA_RAW_EXISTS = (
        'Информация о необходимых документах для данного мероприятия уже '
        'существует'
)

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