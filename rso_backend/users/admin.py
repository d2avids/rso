from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

from .models import (Area, Detachment, Region, RSOUser, UserDocuments,
                     UserEducation, UserMedia, UserPrivacySettings, UserRegion)


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


@admin.register(RSOUser)
class UserAdmin(BaseUserAdmin):
    inlines = [UserRegionInline, UserMediaInline, UserEducationInline, UserDocumentsInline, UserPrivacySettingsInline]

    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    readonly_fields = ('date_joined', 'last_login')

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    pass


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    pass


@admin.register(Detachment)
class DetachmentAdmin(admin.ModelAdmin):
    pass


admin.site.unregister(Group)
