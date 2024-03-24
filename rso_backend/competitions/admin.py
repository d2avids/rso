from django.contrib import admin

from competitions.models import (
    Q10, Q9, CompetitionApplications, CompetitionParticipants, Competitions,
    Q7, Q10Ranking, Q10Report, Q10TandemRanking, Q18Ranking, Q19Ranking, Q19Report, Q19TandemRanking, Q1Ranking, Q1Report, Q1TandemRanking, Q20Ranking, Q20Report, Q20TandemRanking, Q7Ranking,
    Q7Report, LinksQ7, Q13TandemRanking, Q18TandemRanking, Q13Ranking,
    Q7TandemRanking, Q9Ranking, Q9Report, Q9TandemRanking
)


@admin.register(Q13Ranking)
class Q13RankingAdmin(admin.ModelAdmin):
    list_display = ('id', 'detachment', 'place')
    search_fields = ('detachment__name', 'place')


@admin.register(Q13TandemRanking)
class Q13TandemRankingAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'detachment', 'junior_detachment', 'place'
    )
    search_fields = ('detachment__name', 'junior_detachment__name', 'place')


@admin.register(Q18Ranking)
class Q18RankingAdmin(admin.ModelAdmin):
    list_display = ('id', 'detachment', 'place')
    search_fields = ('detachment__name', 'place')


@admin.register(Q18TandemRanking)
class Q18TandemRankingAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'detachment', 'junior_detachment', 'place'
    )
    search_fields = ('detachment__name', 'junior_detachment__name', 'place')


admin.site.register(CompetitionParticipants)
admin.site.register(CompetitionApplications)
admin.site.register(Competitions)


@admin.register(Q7)
class Q7Admin(admin.ModelAdmin):
    list_display = (
        'id', 'event_name', 'detachment_report', 'is_verified',
        'number_of_participants'
    )


admin.site.register(Q7Report)
admin.site.register(Q7Ranking)
admin.site.register(Q7TandemRanking)


@admin.register(Q9)
class Q9Admin(admin.ModelAdmin):
    list_display = (
        'id', 'event_name', 'detachment_report', 'is_verified',
        'prize_place'
    )


admin.site.register(Q9Report)
admin.site.register(Q9Ranking)
admin.site.register(Q9TandemRanking)


@admin.register(Q10)
class Q10Admin(admin.ModelAdmin):
    list_display = ('id', 'event_name', 'is_verified', 'prize_place')


admin.site.register(Q10Report)
admin.site.register(Q10Ranking)
admin.site.register(Q10TandemRanking)


@admin.register(Q1Report)
class Q1ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'detachment', 'score')


admin.site.register(Q1TandemRanking)
admin.site.register(Q1Ranking)

@admin.register(Q19Report)
class Q19ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'detachment', 'is_verified', 'safety_violations')


admin.site.register(Q19TandemRanking)
admin.site.register(Q19Ranking)

@admin.register(Q20Report)
class Q20ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'detachment', 'is_verified')


admin.site.register(Q20TandemRanking)
admin.site.register(Q20Ranking)
