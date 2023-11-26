from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from users.models import (RSOUser, UserDocuments, UserEducation, UserMedia,
                          UserPrivacySettings, UserRegion, UsersParent)


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
    model = UsersParent
    extra = 1


@admin.register(RSOUser)
class UserAdmin(BaseUserAdmin):
    inlines = [
        UserRegionInline,
        UserMediaInline,
        UserEducationInline,
        UserDocumentsInline,
<<<<<<< HEAD
        UserPrivacySettingsInline,
        UsersParentInline
=======
        UserPrivacySettingsInline
>>>>>>> aa2f949b4ed3bf54733d76f456d011247f791064
    ]

    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    readonly_fields = ('date_joined', 'last_login')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


admin.site.unregister(Group)
