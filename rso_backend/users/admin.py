from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django_celery_beat.models import (ClockedSchedule, CrontabSchedule,
                                       IntervalSchedule, PeriodicTask,
                                       SolarSchedule)
from import_export.admin import ImportExportModelAdmin

from users.models import (RSOUser, UserDocuments, UserEducation, UserMedia,
                          UserMembershipLogs, UserParent, UserPrivacySettings,
                          UserRegion, UserStatementDocuments,
                          UserMemberCertLogs)
from users.resources import RSOUserResource


class UserRegionInline(admin.StackedInline):
    model = UserRegion
    extra = 1


class UserMediaInline(admin.StackedInline):
    model = UserMedia
    extra = 1


class UserEducationInline(admin.StackedInline):
    model = UserEducation
    extra = 1


class UserDocumentsInline(admin.StackedInline):
    model = UserDocuments
    extra = 1


class UserPrivacySettingsInline(admin.StackedInline):
    model = UserPrivacySettings
    extra = 1


class UsersParentInline(admin.StackedInline):
    model = UserParent
    extra = 1


class UserStatementDocumentsInLine(admin.StackedInline):
    model = UserStatementDocuments
    extra = 1


@admin.register(RSOUser)
class UserAdmin(ImportExportModelAdmin, BaseUserAdmin):
    resource_class = RSOUserResource
    inlines = [
        UserRegionInline,
        UserMediaInline,
        UserEducationInline,
        UserDocumentsInline,
        UserPrivacySettingsInline,
        UsersParentInline,
        UserStatementDocumentsInLine,
    ]

    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    readonly_fields = ('date_joined', 'last_login')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


@admin.register(UserMembershipLogs)
class UserMembershipLogsAdmin(admin.ModelAdmin):
    list_display = ('user', 'status_changed_by', 'date', 'period', 'status')
    readonly_fields = ('user', 'status_changed_by', 'date', 'period', 'status')
    search_fields = ('user', 'status_changed_by',)
    list_filter = ('date', 'period', 'status')


@admin.register(UserMemberCertLogs)
class UserMemberCertLogsAdmin(admin.ModelAdmin):
    list_display = ('user', 'cert_issued_by', 'date', 'cert_type')
    readonly_fields = ('user', 'cert_issued_by', 'date', 'cert_type')
    search_fields = ('user', 'cert_issued_by')
    list_filter = ('date', 'cert_issued_by', 'cert_type')


admin.site.unregister(Group)
admin.site.unregister(PeriodicTask)
admin.site.unregister(IntervalSchedule)
admin.site.unregister(CrontabSchedule)
admin.site.unregister(ClockedSchedule)
admin.site.unregister(SolarSchedule)
