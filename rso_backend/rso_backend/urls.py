import os

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

swagger_url = os.getenv('SWAGGER_URL')

if swagger_url:
    schema_view = get_schema_view(
       openapi.Info(
          title="RSO API",
          default_version='v1',
          description="Documentation",
          terms_of_service="https://www.google.com/policies/terms/",
          contact=openapi.Contact(email="rso.login@yandex.ru"),
          license=openapi.License(name="BSD License"),
       ),
       public=True,
       permission_classes=(permissions.AllowAny,),
       url=swagger_url
    )
else:
    schema_view = get_schema_view(
       openapi.Info(
          title="RSO API",
          default_version='v1',
          description="Documentation",
          terms_of_service="https://www.google.com/policies/terms/",
          contact=openapi.Contact(email="rso.login@yandex.ru"),
          license=openapi.License(name="BSD License"),
       ),
       public=True,
       permission_classes=(permissions.AllowAny,),
    )

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('api.urls')),
    path('api/v1/', include('djoser.urls')),
    path('api/v1/', include('djoser.urls.authtoken')),
    path(
        'swagger<format>/',
        schema_view.without_ui(cache_timeout=0),
        name='schema-json'
    ),
    path(
        'swagger/',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui'
    ),
    path(
        'redoc/',
        schema_view.with_ui('redoc', cache_timeout=0),
        name='schema-redoc'
    ),
    path('headquarters/v1/', include('headquarters.urls')),
    path('events/v1/', include('events.urls')),
    path('users/v1/', include('users.urls'))
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
