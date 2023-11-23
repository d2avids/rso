from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (RegionViewSet, RSOUserViewSet, UserDocumentsViewSet,
                    UserEducationViewSet, UserMediaViewSet,
                    UserPrivacySettingsViewSet, UserRegionViewSet,
                    UserStatementDocumentsViewSet)

router = DefaultRouter()

router.register(r'users', RSOUserViewSet)
router.register(r'regions', RegionViewSet)

user_nested_urls = [
    path('users/me/education/', UserEducationViewSet.as_view({
        'get': 'retrieve',
        'post': 'create',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='user-education'),
    path('users/me/documents/', UserDocumentsViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'post': 'create',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='user-documents'),
    path('users/me/region/', UserRegionViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'post': 'create',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='user-region'),
    path('users/me/privacy/', UserPrivacySettingsViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'post': 'create',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='user-privacy'),
    path('users/me/media/', UserMediaViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'post': 'create',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='user-media'),
    path('users/me/statement/', UserStatementDocumentsViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'post': 'create',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='user-statement'),
]

urlpatterns = [
    path('', include(router.urls)),
] + user_nested_urls
