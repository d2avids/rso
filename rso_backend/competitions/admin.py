from django.contrib import admin

from competitions.forms import (CompetitionApplicationsForm,
                                CompetitionParticipantsForm)
from competitions.models import (CompetitionApplications,
                                 CompetitionParticipants, Competitions)


@admin.register(Competitions)
class CompetitionsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')
    list_display = ('id',
                    'name',
                    'count_tandem_applications',
                    'count_start_applications',
                    'count_tandem_participants',
                    'count_start_participants',
                    'created_at')

    @admin.display(description='Тандем участников')
    def count_tandem_participants(self, obj):
        return obj.competition_participants.filter(
            detachment__isnull=False
        ).count()

    @admin.display(description='Старт участников')
    def count_start_participants(self, obj):
        return obj.competition_participants.filter(
            detachment__isnull=True
        ).count()

    @admin.display(description='Тандем заявок')
    def count_tandem_applications(self, obj):
        return obj.competition_applications.filter(
            detachment__isnull=False
        ).count()

    @admin.display(description='Старт заявок')
    def count_start_applications(self, obj):
        return obj.competition_applications.filter(
            detachment__isnull=True
        ).count()


@admin.register(CompetitionApplications)
class CompetitionApplicationsAdmin(admin.ModelAdmin):
    form = CompetitionApplicationsForm
    list_filter = ('competition__name',)
    search_fields = ('detachment__name',
                     'junior_detachment__name',
                     'competition__name',
                     'detachment__region__name',
                     'junior_detachment__region__name')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    list_display = ('id',
                    'get_region',
                    'is_tandem',
                    'detachment',
                    'junior_detachment',
                    'created_at')
    ordering = ('detachment', 'junior_detachment', 'created_at')

    @admin.display(description='Регион')
    def get_region(self, obj):
        return obj.junior_detachment.region
    get_region.admin_order_field = 'junior_detachment__region__name'

    @admin.display(description='Тип заявки')
    def is_tandem(self, obj):
        return 'Тандем' if obj.detachment is not None else 'Старт'


@admin.register(CompetitionParticipants)
class CompetitionParticipantsAdmin(admin.ModelAdmin):
    form = CompetitionParticipantsForm
    list_filter = ('competition__name',)
    search_fields = ('detachment__name',
                     'junior_detachment__name',
                     'competition__name',
                     'detachment__region__name',
                     'junior_detachment__region__name')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    list_display = ('id',
                    'get_region',
                    'is_tandem',
                    'detachment',
                    'junior_detachment',
                    'created_at')
    ordering = ('detachment', 'junior_detachment', 'created_at')

    @admin.display(description='Регион')
    def get_region(self, obj):
        return obj.junior_detachment.region
    get_region.admin_order_field = 'junior_detachment__region__name'

    @admin.display(description='Тип заявки')
    def is_tandem(self, obj):
        return 'Тандем' if obj.detachment is not None else 'Старт'
