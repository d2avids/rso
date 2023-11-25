from django.urls import include, path
from djoser.views import UserViewSet
from rest_framework.routers import DefaultRouter

from api.constants import CRUD_METHODS_WITHOUT_LIST
from api.views import (CentralViewSet, DetachmentViewSet, DistrictViewSet,
                       EducationalViewSet, LocalViewSet, RegionalViewSet,
                       RegionViewSet, RSOUserViewSet, UserDocumentsViewSet,
                       UserEducationViewSet, UserMediaViewSet,
                       UserPrivacySettingsViewSet, UserRegionViewSet,
                       UserStatementDocumentsViewSet)

app_name = 'api'

router = DefaultRouter()

router.register(r'users', RSOUserViewSet)
router.register(r'regions', RegionViewSet)
router.register(r'districts', DistrictViewSet)
router.register(r'regionals', RegionalViewSet)
router.register(r'educationals', EducationalViewSet)
router.register(r'locals', LocalViewSet)
router.register(r'detachments', DetachmentViewSet)
router.register(r'centrals', CentralViewSet)

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
    path('register/', UserViewSet.as_view({'post': 'create'}),
         name='user-create'),
    path('', include(router.urls)),
] + user_nested_urls
