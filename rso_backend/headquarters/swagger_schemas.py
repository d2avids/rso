from drf_yasg import openapi
from rest_framework import status

applications_response = {
    status.HTTP_200_OK: openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'user': openapi.Schema(type=openapi.TYPE_OBJECT)
        }
    )
}
