from django.contrib import admin

from events.forms import (EventApplicationForm, EventForm,
                          EventOrganizationDataForm, EventParticipantDataForm)
from events.models import (Event, EventAdditionalIssue, EventApplications,
                           EventDocument, EventDocumentData, EventIssueAnswer,
                           EventOrganizationData, EventParticipants,
                           EventTimeData, EventUserDocument,
                           MultiEventApplication)


class EventTimeDataInline(admin.TabularInline):
    model = EventTimeData
    extra = 1
    max_num = 1


class EventDocumentInline(admin.TabularInline):
    model = EventDocument
    extra = 1


class EventDocumentDataInline(admin.TabularInline):
    model = EventDocumentData
    extra = 1
    max_num = 1


class EventOrganizationDataInline(admin.TabularInline):
    model = EventOrganizationData
    extra = 1
    form = EventOrganizationDataForm


class EventAdditionalIssuesInline(admin.TabularInline):
    model = EventAdditionalIssue
    extra = 1


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'format', 'direction', 'status', 'author', 'created_at')
    list_filter = ('format', 'direction', 'status', 'created_at')
    search_fields = ('name',)
    inlines = [
        EventTimeDataInline,
        EventDocumentInline,
        EventDocumentDataInline,
        EventOrganizationDataInline,
        EventAdditionalIssuesInline,
    ]
    fieldsets = [
        ('Basic Information', {'fields': ['name', 'author', 'format', 'direction', 'scale', 'status']}),
        ('Time Information', {'fields': ['participants_number', 'description']}),
        ('Location Information', {'fields': ['address', 'conference_link']}),
        ('Application Information', {'fields': ['application_type', 'available_structural_units']}),
        ('Banner and Documents', {'fields': ['banner']}),
    ]
    form = EventForm


@admin.register(EventParticipants)
class EventParticipantsAdmin(admin.ModelAdmin):
    form = EventParticipantDataForm


@admin.register(EventApplications)
class EventApplicationAdmin(admin.ModelAdmin):
    form = EventApplicationForm
