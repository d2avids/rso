from competitions.models import (CompetitionApplications,
                                 CompetitionParticipants, Competitions)
from django.contrib import admin

admin.site.register(CompetitionParticipants)
admin.site.register(CompetitionApplications)
admin.site.register(Competitions)

