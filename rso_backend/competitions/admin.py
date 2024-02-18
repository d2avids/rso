from django.contrib import admin

from competitions.models import (
    CompetitionApplications, CompetitionParticipants, Competitions,
    LinksOfParticipationInDistrAndInterregEvents,
    ParticipationInDistrAndInterregEvents, Score
)

admin.site.register(CompetitionParticipants)
admin.site.register(CompetitionApplications)
admin.site.register(Competitions)
admin.site.register(ParticipationInDistrAndInterregEvents)
admin.site.register(LinksOfParticipationInDistrAndInterregEvents)
admin.site.register(Score)
