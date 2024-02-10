from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django_celery_beat.models import (ClockedSchedule, CrontabSchedule,
                                       IntervalSchedule, PeriodicTask,
                                       SolarSchedule)
from import_export.admin import ImportExportModelAdmin
from rest_framework.authtoken.models import TokenProxy

from users.forms import RSOUserForm
from users.models import (RSOUser, UserDocuments, UserEducation, UserMedia,
                          UserMemberCertLogs, UserMembershipLogs, UserParent,
                          UserPrivacySettings, UserRegion,
                          UserStatementDocuments, UserVerificationLogs)
from users.resources import RSOUserResource


class UserRegionInline(admin.StackedInline):
    model = UserRegion
    extra = 0


class UserMediaInline(admin.StackedInline):
    model = UserMedia
    extra = 0


class UserEducationInline(admin.StackedInline):
    model = UserEducation
    extra = 0


class UserDocumentsInline(admin.StackedInline):
    model = UserDocuments
    extra = 0


class UserPrivacySettingsInline(admin.StackedInline):
    model = UserPrivacySettings
    extra = 0


class UsersParentInline(admin.StackedInline):
    model = UserParent
    extra = 0


class UserStatementDocumentsInLine(admin.StackedInline):
    model = UserStatementDocuments
    extra = 0


@admin.register(RSOUser)
class UserAdmin(ImportExportModelAdmin, BaseUserAdmin):
    resource_class = RSOUserResource
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'email',
                'first_name',
                'last_name',
                'patronymic_name',
                'gender',
                'region',
                'password1',
                'password2'
            ),
        }),
    )
    inlines = [
        UserRegionInline,
        UserMediaInline,
        UserEducationInline,
        UserDocumentsInline,
        UserPrivacySettingsInline,
        UsersParentInline,
        UserStatementDocumentsInLine,
    ]

    list_display = (
        'username',
        'id',
        'email',
        'first_name',
        'last_name',
        'patronymic_name',
        'is_verified',
        'membership_fee',
        'is_staff',
        'date_joined',
        'last_login'
    )
    search_fields = (
        'username',
        'first_name',
        'last_name',
        'patronymic_name',
        'email',
        'first_name',
        'last_name'
    )
    readonly_fields = ('date_joined', 'last_login')
    list_filter = (
        'date_joined',
        'last_login',
        'is_verified',
        'membership_fee',
        'is_staff',
    )

    filter_horizontal = ()
    fieldsets = ()


@admin.register(UserMembershipLogs)
class UserMembershipLogsAdmin(admin.ModelAdmin):
    list_display = ('user', 'status_changed_by', 'date', 'period', 'status',)
    readonly_fields = (
        'user', 'status_changed_by', 'date', 'period', 'status', 'description'
    )
    list_filter = ('date', 'period', 'status')


@admin.register(UserMemberCertLogs)
class UserMemberCertLogsAdmin(admin.ModelAdmin):
    list_display = ('user', 'cert_issued_by', 'date', 'cert_type')
    readonly_fields = (
        'user', 'cert_issued_by', 'date', 'cert_type', 'description'
    )
    list_filter = ('date', 'cert_type')


@admin.register(UserVerificationLogs)
class UserVerificationLogsAdmin(admin.ModelAdmin):
    """Таблица логов верификации пользователей."""

    list_display = ('user', 'date', 'description', 'verification_by')
    readonly_fields = ('user', 'date', 'description', 'verification_by')
    list_filter = ('date', 'description')


admin.site.unregister(Group)
admin.site.unregister(PeriodicTask)
admin.site.unregister(IntervalSchedule)
admin.site.unregister(CrontabSchedule)
admin.site.unregister(ClockedSchedule)
admin.site.unregister(SolarSchedule)

if not settings.DEBUG:
    admin.site.unregister(TokenProxy)
