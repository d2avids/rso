from django.contrib import admin
from competitions.models import CompetitionApplications, CompetitionParticipants, Competitions


admin.site.register(CompetitionParticipants)
admin.site.register(CompetitionApplications)
admin.site.register(Competitions)

