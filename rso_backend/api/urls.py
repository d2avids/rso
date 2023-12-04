from django.urls import include, path
from djoser.views import UserViewSet
from rest_framework.routers import DefaultRouter

from api.constants import (CREATE_DELETE, CREATE_METHOD,
                           CRUD_METHODS_WITHOUT_LIST, DELETE,
                           DOWNLOAD_ALL_FORMS, DOWNLOAD_CONSENT_PD,
                           DOWNLOAD_MEMBERSHIP_FILE,
                           DOWNLOAD_PARENT_CONSENT_PD, LIST, RETRIEVE_CREATE,
                           UPDATE, RETRIEVE)
from api.views import (CentralPositionViewSet, CentralViewSet,
                       DetachmentAcceptViewSet, DetachmentApplicationViewSet,
                       DetachmentPositionViewSet, DetachmentViewSet,
                       DistrictPositionViewSet, DistrictViewSet,
                       EducationalPositionViewSet, EducationalViewSet,
                       LocalPositionViewSet, LocalViewSet,
                       RegionalPositionViewSet, RegionalViewSet, RegionViewSet,
                       RSOUserViewSet, UserDocumentsViewSet,
                       UserEducationViewSet, UserMediaViewSet,
                       UserPrivacySettingsViewSet,
                       UserProfessionalEducationViewSet, UserRegionViewSet,
                       UsersParentViewSet, UserStatementDocumentsViewSet,
                       ForeignUserDocumentsViewSet, UsersRolesViewSet,
                       apply_for_verification, verify_user)

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
UserStatementMembershipDownloadVS = UserStatementDocumentsViewSet.as_view(
    DOWNLOAD_MEMBERSHIP_FILE
)
UserStatementConsentPDDownloadVS = UserStatementDocumentsViewSet.as_view(
    DOWNLOAD_CONSENT_PD
)
UserStatementParentConsentPDDownloadVS = UserStatementDocumentsViewSet.as_view(
    DOWNLOAD_PARENT_CONSENT_PD
)
UserStatementDownloadAllVS = UserStatementDocumentsViewSet.as_view(
    DOWNLOAD_ALL_FORMS
)
ForeignUserDocsVS = ForeignUserDocumentsViewSet.as_view(
    CRUD_METHODS_WITHOUT_LIST
)
UsersRolesVS = UsersRolesViewSet.as_view(RETRIEVE)
UsersRoleForStuffVS = UsersRolesViewSet.as_view(
    CRUD_METHODS_WITHOUT_LIST
)

DetachmentAcceptVS = DetachmentAcceptViewSet.as_view(CREATE_DELETE)
DetachmentApplicationVS = DetachmentApplicationViewSet.as_view(CREATE_DELETE)
DetachmentPositionListVS = DetachmentPositionViewSet.as_view(LIST)
DetachmentPositionUpdateVS = DetachmentPositionViewSet.as_view(UPDATE)
EducationalPositionListVS = EducationalPositionViewSet.as_view(LIST)
EducationalPositionUpdateVS = EducationalPositionViewSet.as_view(UPDATE)
LocalPositionListVS = LocalPositionViewSet.as_view(LIST)
LocalPositionUpdateVS = LocalPositionViewSet.as_view(UPDATE)
RegionalPositionListVS = RegionalPositionViewSet.as_view(LIST)
RegionalPositionUpdateVS = RegionalPositionViewSet.as_view(UPDATE)
DistrictPositionListVS = DistrictPositionViewSet.as_view(LIST)
DistrictPositionUpdateVS = DistrictPositionViewSet.as_view(UPDATE)
CentralPositionListVS = CentralPositionViewSet.as_view(LIST)
CentralPositionUpdateVS = CentralPositionViewSet.as_view(UPDATE)

user_nested_urls = [
    path('users/me/education/', UserEduVS, name='user-education'),
    path('users/me/documents/', UserDocVS, name='user-documents'),
    path(
        'users/me/foreign_documents/',
        ForeignUserDocsVS,
        name='foreign-documents'
    ),
    path('users/me/region/', UserRegVS, name='user-region'),
    path('users/me/privacy/', UserPrivacyVS, name='user-privacy'),
    path('users/me/media/', UserMediaVS, name='user-media'),
    path('users/me/statement/', UserStatementVS, name='user-statement'),
    path('users/me/parent/', UsersParentVS, name='user-parent'),
    path(
        'users/me/statement/download_membership_statement_file/',
        UserStatementMembershipDownloadVS,
        name='download-membership-file'
    ),
    path(
        (
            'users/me/statement/'
            'download_consent_to_the_processing_of_personal_data/'
        ),
        UserStatementConsentPDDownloadVS,
        name='download-consent-pd'
    ),
    path(
        (
            'users/me/statement/'
            'download_parent_consent_to_the_processing_of_personal_data/'
        ),
        UserStatementParentConsentPDDownloadVS,
        name='download-parent-consent-pd'
    ),
    path(
        'users/me/statement/download_all_forms/',
        UserStatementDownloadAllVS,
        name='download-all-forms'
    ),
    path('users/me/roles/', UsersRolesVS, name='user-roles'),
    path(
        'users/<int:pk>/role/',
        UsersRoleForStuffVS,
        name='user-role-for-stuff'
    ),
    path(
        'users/me/apply_for_verification/',
        apply_for_verification,
        name='user-verification'
    ),
    path(
        'users/<int:pk>/verify/',
        verify_user,
        name='user-verify'
    ),
    path(
        'detachments/<int:pk>/applications/',
        DetachmentApplicationVS,
        name='detachment-application'
    ),
    path(
        'detachments/<int:pk>/applications/<int:application_pk>/accept/',
        DetachmentAcceptVS,
        name='user-apply'
    ),
    path(
        'detachments/<int:pk>/members/',
        DetachmentPositionListVS,
        name='detachment-members-list'
    ),
    path(
        'detachments/<int:pk>/members/<int:member_pk>/',
        DetachmentPositionUpdateVS,
        name='detachment-members-update'
    ),
    path(
        'educationals/<int:pk>/members/',
        EducationalPositionListVS,
        name='educational-members-list'
    ),
    path(
        'educationals/<int:pk>/members/<int:member_pk>/',
        EducationalPositionUpdateVS,
        name='educational-members-update'
    ),
    path(
        'locals/<int:pk>/members/',
        LocalPositionListVS,
        name='local-members-list'
    ),
    path(
        'locals/<int:pk>/members/<int:member_pk>/',
        LocalPositionUpdateVS,
        name='local-members-update'
    ),
    path(
        'regionals/<int:pk>/members/',
        RegionalPositionListVS,
        name='regional-members-list'
    ),
    path(
        'regionals/<int:pk>/members/<int:member_pk>/',
        RegionalPositionUpdateVS,
        name='regional-members-update'
    ),
    path(
        'districts/<int:pk>/members/',
        DistrictPositionListVS,
        name='district-members-list'
    ),
    path(
        'districts/<int:pk>/members/<int:member_pk>/',
        DistrictPositionUpdateVS,
        name='district-members-update'
    ),
    path(
        'centrals/<int:pk>/members/',
        CentralPositionListVS,
        name='central-members-list'
    ),
    path(
        'centrals/<int:pk>/members/<int:member_pk>/',
        CentralPositionUpdateVS,
        name='central-members-update'
    ),
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
    path('register/', UserViewSet.as_view(CREATE_METHOD), name='user-create'),
    path('', include(router.urls)),
] + user_nested_urls
