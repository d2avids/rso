from events.models import (EventApplications, GroupEventApplication,
                           MultiEventApplication)

EVENT_TIME_DATA_RAW_EXISTS = (
        'Информация о времени проведения данного мероприятия уже существует'
)
EVENT_DOCUMENT_DATA_RAW_EXISTS = (
        'Информация о необходимых документах для данного мероприятия уже '
        'существует'
)

EVENT_APPLICATIONS_MODEL = {
        'Персональная': EventApplications,
        'Групповая': GroupEventApplication,
        'Мультиэтапная': MultiEventApplication,
}
