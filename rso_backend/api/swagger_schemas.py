from drf_yasg import openapi
from events.models import Event
from rest_framework import serializers, status

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