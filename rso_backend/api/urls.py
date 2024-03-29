from django.urls import include, path
from djoser.views import UserViewSet
from rest_framework.routers import DefaultRouter

from api.constants import (CREATE_DELETE, CREATE_METHOD, DELETE,
                           DOWNLOAD_ALL_FORMS, DOWNLOAD_CONSENT_PD,
                           DOWNLOAD_MEMBERSHIP_FILE,
                           DOWNLOAD_PARENT_CONSENT_PD, LIST, LIST_CREATE,
                           POST_RESET_PASSWORD, RETRIEVE_CREATE, UPDATE_DELETE,
                           UPDATE_RETRIEVE)
from api.views import (AreaViewSet, EducationalInstitutionViewSet,
                       MemberCertViewSet, RegionViewSet,
                       change_membership_fee_status, verify_user)
from competitions.models import Q5EducatedParticipant
from competitions.views import (
    CompetitionApplicationsViewSet, CompetitionParticipantsViewSet,
    CompetitionViewSet, Q10ViewSet, Q11ViewSet, Q12ViewSet, Q15DetachmentReportViewSet,
    Q19DetachmentReportViewset, Q20ViewSet, Q2DetachmentReportViewSet,
    Q7ViewSet,
    Q13DetachmentReportViewSet, Q13EventOrganizationViewSet,
    Q18DetachmentReportViewSet, Q8ViewSet, Q9ViewSet, get_place_q1,
    get_place_q3, get_place_q4,
    Q5DetachmentReport, Q5DetachmentReportViewSet, Q5EducatedParticipantViewSet
)
from events.views import (AnswerDetailViewSet, EventAdditionalIssueViewSet,
                          EventApplicationsViewSet,
                          EventOrganizationDataViewSet,
                          EventParticipantsViewSet, EventUserDocumentViewSet,
                          EventViewSet, MultiEventViewSet,
                          GroupEventApplicationViewSet,
                          create_answers, group_applications,
                          group_applications_me)
from headquarters.views import (CentralPositionViewSet, CentralViewSet,
                                DetachmentAcceptViewSet,
                                DetachmentApplicationViewSet,
                                DetachmentPositionViewSet, DetachmentViewSet,
                                DistrictPositionViewSet, DistrictViewSet,
                                EducationalPositionViewSet, EducationalViewSet,
                                LocalPositionViewSet, LocalViewSet,
                                PositionViewSet, RegionalPositionViewSet,
                                RegionalViewSet, get_structural_units)
from users.views import (CustomUserViewSet, ForeignUserDocumentsViewSet,
                         RSOUserViewSet, SafeUserViewSet, UserDocumentsViewSet,
                         UserEducationViewSet, UserMediaViewSet,
                         UserPrivacySettingsViewSet,
                         UserProfessionalEducationViewSet, UserRegionViewSet,
                         UsersParentViewSet, UserStatementDocumentsViewSet,
                         apply_for_verification)
from questions.views import QuestionsView, submit_answers

app_name = 'api'

router = DefaultRouter()

router.register(r'save_users', SafeUserViewSet, basename='save_users')
router.register(r'rsousers', RSOUserViewSet, basename='rsousers')
router.register(r'regions', RegionViewSet)
router.register(r'areas', AreaViewSet)
router.register(r'districts', DistrictViewSet, basename='districts')
router.register(r'regionals', RegionalViewSet, basename='regionals')
router.register(r'educationals', EducationalViewSet)
router.register(r'locals', LocalViewSet)
router.register(r'detachments', DetachmentViewSet)
router.register(r'centrals', CentralViewSet, basename='centrals')
router.register(r'positions', PositionViewSet)
router.register(
    'eduicational_institutions',
    EducationalInstitutionViewSet,
    basename='educational-institution'
)
router.register('membership_certificates', MemberCertViewSet)
router.register('events', EventViewSet, basename='events')
router.register(
    r'events/(?P<event_pk>\d+)/group_applications/all',
    GroupEventApplicationViewSet,
    basename='group-applications'
)
router.register(
    r'events/(?P<event_pk>\d+)/applications',
    EventApplicationsViewSet,
    basename='event-applications'
)
router.register(
    r'events/(?P<event_pk>\d+)/participants',
    EventParticipantsViewSet,
    basename='event-participants'
)
router.register(
    r'events/(?P<event_pk>\d+)/answers',
    AnswerDetailViewSet,
    basename='answer'
)
router.register(
    r'events/(?P<event_pk>\d+)/user_documents',
    EventUserDocumentViewSet,
    basename='event-user-document'
)
router.register(
    r'events/(?P<event_pk>\d+)/multi_applications',
    MultiEventViewSet,
    basename='multi-applications'
)
router.register(
    r'competitions',
    CompetitionViewSet,
    basename='competition'
)
router.register(
    r'competitions/(?P<competition_pk>\d+)/applications',
    CompetitionApplicationsViewSet,
    basename='competition-applications'
)
router.register(
    r'competitions/(?P<competition_pk>\d+)/participants',
    CompetitionParticipantsViewSet,
    basename='competition-participants'
)
router.register(
    r'competitions/(?P<competition_pk>\d+)/reports/q2',
    Q2DetachmentReportViewSet,
    basename='q2_report'
)
router.register(
    r'competitions/(?P<competition_pk>\d+)/reports/q7',
    Q7ViewSet,
    basename='q7'
)
router.register(
    r'competitions/(?P<competition_pk>\d+)/reports/q8',
    Q8ViewSet,
    basename='q8'
)
router.register(
    r'competitions/(?P<competition_pk>\d+)/reports/q9',
    Q9ViewSet,
    basename='q9'
)
router.register(
    r'competitions/(?P<competition_pk>\d+)/reports/q10',
    Q10ViewSet,
    basename='q10'
)
router.register(
    r'competitions/(?P<competition_pk>\d+)/reports/q11',
    Q11ViewSet,
    basename='q11'
)
router.register(
    r'competitions/(?P<competition_pk>\d+)/reports/q12',
    Q12ViewSet,
    basename='q12'
)
router.register(
    r'competitions/(?P<competition_pk>\d+)/reports/q15',
    Q15DetachmentReportViewSet,
    basename='q15_report'
)
router.register(
    r'competitions/(?P<competition_pk>\d+)/reports/q19',
    Q19DetachmentReportViewset,
    basename='q19'
)
router.register(
    r'competitions/(?P<competition_pk>\d+)/reports/q20',
    Q20ViewSet,
    basename='q20'
)
router.register(
    r'competitions/(?P<competition_pk>\d+)/reports/q18',
    Q18DetachmentReportViewSet,
    basename='q18'
)
router.register(
    r'competitions/(?P<competition_pk>\d+)/reports/q13',
    Q13DetachmentReportViewSet,
    basename='q13'
)
router.register(
    r'competitions/(?P<competition_pk>\d+)/reports/q13/(?P<report_pk>\d+)/events',
    Q13EventOrganizationViewSet,
    basename='q13eventorganization'
)
router.register(
    r'competitions/(?P<competition_pk>\d+)/reports/q15',
    Q15DetachmentReportViewSet,
    basename='q15'
)
router.register(
    r'competitions/(?P<competition_pk>\d+)/reports/q5',
    Q5DetachmentReportViewSet,
    basename='q5'
)
router.register(
    r'competitions/(?P<competition_pk>\d+)/reports/q5/(?P<report_pk>\d+)/participants',
    Q5EducatedParticipantViewSet,
    basename='q5educatedparticipant'
)

UserEduVS = UserEducationViewSet.as_view(UPDATE_RETRIEVE)
UserProfEduRetrieveCreateVS = UserProfessionalEducationViewSet.as_view(
    RETRIEVE_CREATE
)
UserProfEduPUDVS = UserProfessionalEducationViewSet.as_view(
    UPDATE_RETRIEVE | DELETE
)
UserDocVS = UserDocumentsViewSet.as_view(UPDATE_RETRIEVE)
UserRegVS = UserRegionViewSet.as_view(UPDATE_RETRIEVE)
UserPrivacyVS = UserPrivacySettingsViewSet.as_view(UPDATE_RETRIEVE)
UserMediaVS = UserMediaViewSet.as_view(UPDATE_RETRIEVE)
UserStatementVS = UserStatementDocumentsViewSet.as_view(
    UPDATE_RETRIEVE
)
UsersParentVS = UsersParentViewSet.as_view(UPDATE_RETRIEVE)
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
    UPDATE_RETRIEVE
)
DetachmentAcceptVS = DetachmentAcceptViewSet.as_view(CREATE_DELETE)
DetachmentApplicationVS = DetachmentApplicationViewSet.as_view(CREATE_DELETE)
DetachmentPositionListVS = DetachmentPositionViewSet.as_view(LIST)
DetachmentPositionUpdateVS = DetachmentPositionViewSet.as_view(UPDATE_RETRIEVE)
EducationalPositionListVS = EducationalPositionViewSet.as_view(LIST)
EducationalPositionUpdateVS = EducationalPositionViewSet.as_view(
    UPDATE_RETRIEVE
)
LocalPositionListVS = LocalPositionViewSet.as_view(LIST)
LocalPositionUpdateVS = LocalPositionViewSet.as_view(UPDATE_RETRIEVE)
RegionalPositionListVS = RegionalPositionViewSet.as_view(LIST)
RegionalPositionUpdateVS = RegionalPositionViewSet.as_view(UPDATE_RETRIEVE)
DistrictPositionListVS = DistrictPositionViewSet.as_view(LIST)
DistrictPositionUpdateVS = DistrictPositionViewSet.as_view(UPDATE_RETRIEVE)
CentralPositionListVS = CentralPositionViewSet.as_view(LIST)
CentralPositionUpdateVS = CentralPositionViewSet.as_view(UPDATE_RETRIEVE)
EventOrganizationDataListVS = EventOrganizationDataViewSet.as_view(LIST_CREATE)
EventOrganizationDataObjVS = EventOrganizationDataViewSet.as_view(
    UPDATE_DELETE
)
EventAdditionalIssueListVS = EventAdditionalIssueViewSet.as_view(LIST_CREATE)
EventAdditionalIssueObjVS = EventAdditionalIssueViewSet.as_view(UPDATE_DELETE)

user_nested_urls = [
    path('rsousers/me/education/', UserEduVS, name='user-education'),
    path('rsousers/me/documents/', UserDocVS, name='user-documents'),
    path(
        'rsousers/me/foreign_documents/',
        ForeignUserDocsVS,
        name='foreign-documents'
    ),
    path('rsousers/me/region/', UserRegVS, name='user-region'),
    path('rsousers/me/privacy/', UserPrivacyVS, name='user-privacy'),
    path('rsousers/me/media/', UserMediaVS, name='user-media'),
    path('rsousers/me/statement/', UserStatementVS, name='user-statement'),
    path('rsousers/me/parent/', UsersParentVS, name='user-parent'),
    path(
        'rsousers/me/statement/download_membership_statement_file/',
        UserStatementMembershipDownloadVS,
        name='download-membership-file'
    ),
    path(
        (
            'rsousers/me/statement/'
            'download_consent_to_the_processing_of_personal_data/'
        ),
        UserStatementConsentPDDownloadVS,
        name='download-consent-pd'
    ),
    path(
        (
            'rsousers/me/statement/'
            'download_parent_consent_to_the_processing_of_personal_data/'
        ),
        UserStatementParentConsentPDDownloadVS,
        name='download-parent-consent-pd'
    ),
    path(
        'rsousers/me/statement/download_all_forms/',
        UserStatementDownloadAllVS,
        name='download-all-forms'
    ),
    path(
        'rsousers/me/apply_for_verification/',
        apply_for_verification,
        name='user-verification'
    ),
    path(
        'rsousers/<int:pk>/verify/',
        verify_user,
        name='user-verify'
    ),
    path(
        'rsousers/<int:pk>/membership_fee_status/',
        change_membership_fee_status,
        name='user-membership-fee'
    ),
    path(
        'detachments/<int:pk>/apply/',
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
        'detachments/<int:pk>/members/<int:membership_pk>/',
        DetachmentPositionUpdateVS,
        name='detachment-members-update'
    ),
    path(
        'educationals/<int:pk>/members/',
        EducationalPositionListVS,
        name='educational-members-list'
    ),
    path(
        'educationals/<int:pk>/members/<int:membership_pk>/',
        EducationalPositionUpdateVS,
        name='educational-members-update'
    ),
    path(
        'locals/<int:pk>/members/',
        LocalPositionListVS,
        name='local-members-list'
    ),
    path(
        'locals/<int:pk>/members/<int:membership_pk>/',
        LocalPositionUpdateVS,
        name='local-members-update'
    ),
    path(
        'regionals/<int:pk>/members/',
        RegionalPositionListVS,
        name='regional-members-list'
    ),
    path(
        'regionals/<int:pk>/members/<int:membership_pk>/',
        RegionalPositionUpdateVS,
        name='regional-members-update'
    ),
    path(
        'districts/<int:pk>/members/',
        DistrictPositionListVS,
        name='district-members-list'
    ),
    path(
        'districts/<int:pk>/members/<int:membership_pk>/',
        DistrictPositionUpdateVS,
        name='district-members-update'
    ),
    path(
        'centrals/<int:pk>/members/',
        CentralPositionListVS,
        name='central-members-list'
    ),
    path(
        'centrals/<int:pk>/members/<int:membership_pk>/',
        CentralPositionUpdateVS,
        name='central-members-update'
    ),
    path(
        'rsousers/me/professional_education/',
        UserProfEduRetrieveCreateVS,
        name='user-prof-education_retrieve_create',
    ),
    path(
        'rsousers/me/professional_education/<int:pk>/',
        UserProfEduPUDVS,
        name='user-prof-education_post_update_delete',
    ),
    path(
        'structural_units/',
        get_structural_units,
        name='structural-units'
    ),
    path(
        'events/<int:event_pk>/organizers/',
        EventOrganizationDataListVS,
        name='event-organization-list'
    ),
    path(
        'events/<int:event_pk>/organizers/<int:pk>/',
        EventOrganizationDataObjVS,
        name='event-organization-objects'
    ),
    path(
        'events/<int:event_pk>/issues/',
        EventAdditionalIssueListVS,
        name='event-organization-list'
    ),
    path(
        'events/<int:event_pk>/issues/<int:pk>/',
        EventAdditionalIssueObjVS,
        name='event-organization-objects'
    ),
    path(
        'events/<int:event_pk>/answers/',
        create_answers,
        name='create-answers'
    ),
    path(
        'events/<int:event_pk>/group_applications/',
        group_applications,
        name='get-group-applications'
    ),
    path(
        'events/<int:event_pk>/group_applications/me/',
        group_applications_me,
        name='get-group-applications-me'
    ),
    path(
        'competitions/<int:competition_pk>/reports/q1/get_place/',
        get_place_q1,
        name='get-place-q1'
    ),
    path(
        'competitions/<int:competition_pk>/reports/q3/get_place/',
        get_place_q3,
        name='get-place-q3'
    ),
    path(
        'competitions/<int:competition_pk>/reports/q4/get_place/',
        get_place_q4,
        name='get-place-q4'
    ),
    path('', include('djoser.urls')),
]

urlpatterns = [
    path('register/', UserViewSet.as_view(CREATE_METHOD), name='user-create'),
    path(
        'reset_password/',
        CustomUserViewSet.as_view(POST_RESET_PASSWORD),
        name='reset_password'
    ),
    path(
        'rsousers', CustomUserViewSet.as_view(LIST),
    ),
    path('questions/', QuestionsView.as_view(), name='questions'),
    path('submit_answers/', submit_answers, name='submit-answers'),
    path('', include(router.urls)),
] + user_nested_urls
