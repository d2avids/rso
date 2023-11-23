from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (RSOUserViewSet, UserEducationViewSet, UserDocumentsViewSet,
                    UserRegionViewSet, UserPrivacySettingsViewSet,
                    UserMediaViewSet, RegionViewSet)

app_name = 'api'

router = DefaultRouter()

router.register(r'users', RSOUserViewSet)
router.register(r'regions', RegionViewSet)

user_nested_urls = [
    path('users/<int:user_id>/education/', UserEducationViewSet.as_view({
        'get': 'list',
        'post': 'create',
        'put': 'update',
        'delete': 'destroy'
    }), name='user-education'),
    path('users/<int:user_id>/documents/', UserDocumentsViewSet.as_view({
        'get': 'list',
        'post': 'create',
        'put': 'update',
        'delete': 'destroy'
    }), name='user-documents'),
    path('users/<int:user_id>/region/', UserRegionViewSet.as_view({
        'get': 'list',
        'post': 'create',
        'put': 'update',
        'delete': 'destroy'
    }), name='user-region'),
    path('users/<int:user_id>/privacy/', UserPrivacySettingsViewSet.as_view({
        'get': 'list',
        'post': 'create',
        'put': 'update',
        'delete': 'destroy'
    }), name='user-privacy'),
    path('users/<int:user_id>/media/', UserMediaViewSet.as_view({
        'get': 'list',
        'post': 'create',
        'put': 'update',
        'delete': 'destroy'
    }), name='user-media'),
]

urlpatterns = [
    path('', include(router.urls)),
] + user_nested_urls
