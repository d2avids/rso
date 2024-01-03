from django.contrib import admin

from events.models import (Event, EventAdditionalIssue, EventDocument,
                           EventDocumentData, EventOrganizationData, 
                           EventParticipants, EventTimeData, EventIssueAnswer,
                           EventApplications)


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


class EventAdditionalIssuesInline(admin.TabularInline):
    model = EventAdditionalIssue
    extra = 1


class EventAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'format', 'direction', 'status', 'author', 'created_at')
    list_filter = ('format', 'direction', 'status', 'created_at')
    search_fields = ('name', 'description')
    inlines = [
        EventTimeDataInline,
        EventDocumentInline,
        EventDocumentDataInline,
        EventOrganizationDataInline,
        EventAdditionalIssuesInline,
    ]
    fieldsets = [
        ('Basic Information', {'fields': ['name', 'author', 'format', 'direction', 'status']}),
        ('Time Information', {'fields': ['participants_number', 'description']}),
        ('Location Information', {'fields': ['address', 'conference_link']}),
        ('Application Information', {'fields': ['application_type', 'available_structural_units']}),
        ('Banner and Documents', {'fields': ['banner']}),
    ]


admin.site.register(Event, EventAdmin)
admin.site.register(EventApplications)
admin.site.register(EventIssueAnswer)
admin.site.register(EventParticipants)
