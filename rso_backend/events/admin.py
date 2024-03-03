from django.contrib import admin
from events.forms import (EventApplicationForm, EventForm,
                          EventOrganizationDataForm, EventParticipantDataForm,
                          GroupEventApplicationForm, MultiEventApplicationForm)
from events.models import (Event, EventAdditionalIssue, EventApplications,
                           EventDocument, EventDocumentData,
                           EventOrganizationData, EventParticipants,
                           EventTimeData, GroupEventApplication,
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
        ('Organization Information', {'fields': ['org_central_headquarter',
                                                 'org_district_headquarter',
                                                 'org_regional_headquarter',
                                                 'org_local_headquarter',
                                                 'org_educational_headquarter',
                                                 'org_detachment']}),
        ('Location Information', {'fields': ['address', 'conference_link']}),
        ('Application Information', {'fields': ['application_type', 'available_structural_units']}),
        ('Banner and Documents', {'fields': ['banner']}),
    ]
    form = EventForm


@admin.register(EventParticipants)
class EventParticipantsAdmin(admin.ModelAdmin):
    form = EventParticipantDataForm
    list_display = ('id', 'event', 'user',)
    search_fields = ('event__name', 'user__username')
    list_filter = ('event',)
    ordering = ('-id',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('event', 'user')
        return queryset


@admin.register(EventApplications)
class EventApplicationAdmin(admin.ModelAdmin):
    form = EventApplicationForm
    list_display = ('id', 'event', 'user',)
    search_fields = ('event__name', 'user__username')
    list_filter = ('event',)
    ordering = ('-id',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('event', 'user')
        return queryset


@admin.register(GroupEventApplication)
class GroupEventApplicationAdmin(admin.ModelAdmin):
    form = GroupEventApplicationForm
    list_display = ('id', 'event', 'author', 'created_at')
    search_fields = ('event__name', 'author__username', 'id')
    list_filter = ('created_at', 'event',)
    ordering = ('-created_at',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related(
            'event', 'author'
        ).prefetch_related('applicants')
        return queryset


@admin.register(MultiEventApplication)
class MultiEventApplicationAdmin(admin.ModelAdmin):
    form = MultiEventApplicationForm
    list_display = (
        'id',
        'event',
        'organizer_id',
        'is_approved',
        'participants_count',
        'created_at'
    )
    search_fields = ('event__name', 'organizer_id')
    list_filter = ('is_approved', 'created_at', 'event')
    ordering = ('-created_at',)

    fieldsets = (
        (None, {
            'fields': (
                'event',
                'organizer_id',
                'is_approved',
                'participants_count',
                'emblem',
            ),
        }),
        ('Штаб-организатор:', {
            'fields': (
                'central_headquarter',
                'district_headquarter',
                'regional_headquarter',
                'local_headquarter',
                'educational_headquarter',
                'detachment'
            ),
        }),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related(
            'event',
            'central_headquarter',
            'district_headquarter',
            'regional_headquarter',
            'local_headquarter',
            'educational_headquarter',
            'detachment'
        )
        return queryset
