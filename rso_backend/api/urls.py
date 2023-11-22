from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.constants import CRUD_METHODS_WITHOUT_LIST
from api.views import (RegionViewSet, RSOUserViewSet, UserDocumentsViewSet,
                       UserEducationViewSet, UserMediaViewSet,
                       UserPrivacySettingsViewSet, UserRegionViewSet,
                       UserStatementDocumentsViewSet)

router = DefaultRouter()

router.register(r'users', RSOUserViewSet)
router.register(r'regions', RegionViewSet)

UserEduVS = UserEducationViewSet.as_view(CRUD_METHODS_WITHOUT_LIST)
UserDocVS = UserDocumentsViewSet.as_view(CRUD_METHODS_WITHOUT_LIST)
UserRegVS = UserRegionViewSet.as_view(CRUD_METHODS_WITHOUT_LIST)
UserPrivacyVS = UserPrivacySettingsViewSet.as_view(CRUD_METHODS_WITHOUT_LIST)
UserMediaVS = UserMediaViewSet.as_view(CRUD_METHODS_WITHOUT_LIST)
UserStatementVS = UserStatementDocumentsViewSet.as_view(
    CRUD_METHODS_WITHOUT_LIST
)

user_nested_urls = [
    path('users/me/education/', UserEduVS, name='user-education'),
    path('users/me/documents/', UserDocVS, name='user-documents'),
    path('users/me/region/', UserRegVS, name='user-region'),
    path('users/me/privacy/', UserPrivacyVS, name='user-privacy'),
    path('users/me/media/', UserMediaVS, name='user-media'),
    path('users/me/statement/', UserStatementVS, name='user-statement'),
]

urlpatterns = [
    path('', include(router.urls)),
] + user_nested_urls
