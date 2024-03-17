from django.contrib import admin

from competitions.models import (
    CompetitionApplications, CompetitionParticipants, Competitions,
    Q7, Q7Report, LinksQ7
)

admin.site.register(CompetitionParticipants)
admin.site.register(CompetitionApplications)
admin.site.register(Competitions)
admin.site.register(Q7)
admin.site.register(Q7Report)
admin.site.register(LinksQ7)
