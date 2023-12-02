from django.urls import include, path
from djoser.views import UserViewSet
from rest_framework.routers import DefaultRouter

from api.constants import (CREATE_DELETE, CREATE_METHOD,
                           CRUD_METHODS_WITHOUT_LIST, LIST, RETRIEVE_CREATE,
                           UPDATE, DELETE)
from api.views import (CentralViewSet, DetachmentViewSet, DistrictViewSet,
                       EducationalViewSet, LocalViewSet, RegionalViewSet,
                       RegionViewSet, RSOUserViewSet, UserDocumentsViewSet,
                       UserEducationViewSet, UserMediaViewSet,
                       UserPrivacySettingsViewSet, UserRegionViewSet,
                       UserStatementDocumentsViewSet,
                       UsersParentViewSet,
                       DetachmentPositionViewSet,
                       UserProfessionalEducationViewSet)

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
UserProfEduRetrieveCreateVS = UserProfessionalEducationViewSet.as_view(
    RETRIEVE_CREATE
)
UserProfEduPUDVS = UserProfessionalEducationViewSet.as_view(UPDATE | DELETE)
UserDocVS = UserDocumentsViewSet.as_view(CRUD_METHODS_WITHOUT_LIST)
UserRegVS = UserRegionViewSet.as_view(CRUD_METHODS_WITHOUT_LIST)
UserPrivacyVS = UserPrivacySettingsViewSet.as_view(CRUD_METHODS_WITHOUT_LIST)
UserMediaVS = UserMediaViewSet.as_view(CRUD_METHODS_WITHOUT_LIST)
UserStatementVS = UserStatementDocumentsViewSet.as_view(
    CRUD_METHODS_WITHOUT_LIST
)
UsersParentVS = UsersParentViewSet.as_view(CRUD_METHODS_WITHOUT_LIST)
DetachmentPositionVS = DetachmentPositionViewSet.as_view(CREATE_METHOD)

user_nested_urls = [
    path('users/me/education/', UserEduVS, name='user-education'),
    path('users/me/documents/', UserDocVS, name='user-documents'),
    path('users/me/region/', UserRegVS, name='user-region'),
    path('users/me/privacy/', UserPrivacyVS, name='user-privacy'),
    path('users/me/media/', UserMediaVS, name='user-media'),
    path('users/me/statement/', UserStatementVS, name='user-statement'),
    path('users/me/parent/', UsersParentVS, name='user-parent'),
    path(
        'users/me/professional_education/',
        UserProfEduRetrieveCreateVS,
        name='user-prof-education_retrieve_create',
    ),
    path(
        'users/me/professional_education/<int:pk>/',
        UserProfEduPUDVS,
        name='user-prof-education_post_update_delete',
    )
]

urlpatterns = [
    path('detachments/apply/', DetachmentPositionVS, name='user-apply'),
    path('register/', UserViewSet.as_view(CREATE_METHOD), name='user-create'),
    path('', include(router.urls)),
] + user_nested_urls
