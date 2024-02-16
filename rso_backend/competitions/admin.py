from django.contrib import admin

from competitions.models import (
    CompetitionApplications, CompetitionParticipants, Competitions,
    LinksOfParticipationInDistrAndInterregionalEvents,
    ParticipationInDistrAndInterregionalEvents,
    ParticipationInDistrAndInterregionalEventsReport, Score
)

admin.site.register(CompetitionParticipants)
admin.site.register(CompetitionApplications)
admin.site.register(Competitions)
admin.site.register(ParticipationInDistrAndInterregionalEventsReport)
admin.site.register(ParticipationInDistrAndInterregionalEvents)
admin.site.register(LinksOfParticipationInDistrAndInterregionalEvents)
admin.site.register(Score)
