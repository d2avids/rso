from headquarters.models import CentralHeadquarter, DistrictHeadquarter, RegionalHeadquarter, LocalHeadquarter, EducationalHeadquarter, Detachment


EVENT_TIME_DATA_RAW_EXISTS = (
        'Информация о времени проведения данного мероприятия уже существует'
)
EVENT_DOCUMENT_DATA_RAW_EXISTS = (
        'Информация о необходимых документах для данного мероприятия уже '
        'существует'
)

MODELS_MAPPING = {
        'Центральные штабы': CentralHeadquarter,
        'Окружные штабы': DistrictHeadquarter,
        'Региональные штабы': RegionalHeadquarter,
        'Местные штабы': LocalHeadquarter,
        'Образовательные штабы': EducationalHeadquarter,
        'Отряды': Detachment
}
