from datetime import date

from django.conf import settings
from rest_framework import serializers

from competitions.models import (
    CompetitionApplications, CompetitionParticipants, Competitions,
    LinksOfParticipationInDistrAndInterregionalEvents,
    ParticipationInDistrAndInterregionalEvents,
    ParticipationInDistrAndInterregionalEventsReport
)
from headquarters.models import Detachment
from headquarters.serializers import BaseShortUnitSerializer


class ShortDetachmentCompetitionSerializer(BaseShortUnitSerializer):
    area = serializers.CharField(source='area.name')

    class Meta:
        model = Detachment
        fields = BaseShortUnitSerializer.Meta.fields + (
            'area',
        )


class CompetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Competitions
        fields = '__all__'


class CompetitionApplicationsObjectSerializer(serializers.ModelSerializer):
    competition = CompetitionSerializer()
    junior_detachment = ShortDetachmentCompetitionSerializer()
    detachment = ShortDetachmentCompetitionSerializer()

    class Meta:
        model = CompetitionApplications
        fields = (
            'id',
            'competition',
            'junior_detachment',
            'detachment',
            'created_at',
            'is_confirmed_by_junior'
        )


class CompetitionApplicationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetitionApplications
        fields = (
            'id',
            'competition',
            'junior_detachment',
            'detachment',
            'created_at',
            'is_confirmed_by_junior'
        )
        read_only_fields = (
            'id',
            'created_at',
            'competition',
            'junior_detachment',
        )

    def validate(self, attrs):
        request = self.context.get('request')
        applications = CompetitionApplications.objects.all()
        participants = CompetitionParticipants.objects.all()
        if request.method == 'POST':
            MIN_DATE = (f'{settings.DATE_JUNIOR_SQUAD[2]}'
                        f'.{settings.DATE_JUNIOR_SQUAD[1]}.'
                        f'{settings.DATE_JUNIOR_SQUAD[0]} года')
            competition = self.context.get('competition')
            detachment = self.context.get('detachment')
            junior_detachment = self.context.get('junior_detachment')

            if detachment:
                if not request.data.get('junior_detachment'):
                    raise serializers.ValidationError(
                        f'- дата основания основания отряда ранее {MIN_DATE}'
                    )
                if detachment.founding_date >= date(
                    *settings.DATE_JUNIOR_SQUAD
                ):
                    raise serializers.ValidationError(
                        f'- отряд-наставник должен быть основан до {MIN_DATE}'
                    )
                if applications.filter(
                    competition=competition,
                    detachment=detachment
                ).exists() or participants.filter(
                    competition=competition,
                    detachment=detachment
                ).exists():
                    raise serializers.ValidationError(
                        'Вы уже подали заявку или участвуете в этом конкурсе'
                    )

            if junior_detachment.founding_date < date(
                *settings.DATE_JUNIOR_SQUAD
            ):
                raise serializers.ValidationError(
                    f'- дата основания отряда ранее {MIN_DATE}'
                )
            if applications.filter(
                competition=competition,
                junior_detachment=junior_detachment
                ).exists() or participants.filter(
                    competition=competition,
                    junior_detachment=junior_detachment
                    ).exists():
                raise serializers.ValidationError(
                    '- отряд уже подал заявку или участвует '
                    'в этом конкурсе'
                )
        return attrs


class CompetitionParticipantsObjectSerializer(serializers.ModelSerializer):
    detachment = ShortDetachmentCompetitionSerializer()
    junior_detachment = ShortDetachmentCompetitionSerializer()

    class Meta:
        model = CompetitionParticipants
        fields = (
            'id',
            'competition',
            'detachment',
            'junior_detachment',
            'created_at'
        )


class CompetitionParticipantsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetitionParticipants
        fields = (
            'id',
            'competition',
            'detachment',
            'junior_detachment',
            'created_at'
        )
        read_only_fields = (
            'id',
            'competition',
            'detachment',
            'junior_detachment',
            'created_at'
        )

    def validate(self, attrs):
        request = self.context.get('request')
        if request.method == 'POST':
            application = self.context.get('application')
            if (application.detachment and not
                    application.is_confirmed_by_junior):
                raise serializers.ValidationError(
                    'Заявка еще не подтверждена младшим отрядом.'
                )
        return attrs


class LinksOfParticipationInDistrictAndInterregionalEventsSerializer(
        serializers.ModelSerializer
):
    class Meta:
        model = LinksOfParticipationInDistrAndInterregionalEvents
        fields = (
            'id',
            'link'
        )


class ParticipationInDistrictAndInterregionalEventsSerializer(
        serializers.ModelSerializer
):
    links = LinksOfParticipationInDistrictAndInterregionalEventsSerializer(
        many=True
    )

    class Meta:
        model = ParticipationInDistrAndInterregionalEvents
        fields = (
            'id',
            'event_name',
            'certificate_scans',
            'number_of_participants',
            'links'
        )

    def create(self, validated_data):
        links = validated_data.pop('links')
        event = super().create(validated_data)
        serializer = (
            LinksOfParticipationInDistrictAndInterregionalEventsSerializer(
                many=True,
                data=links,
                context={'request': self.context.get('request'),
                         'event': event}
            )
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(event=event)
        return event


class ParticipationInDistrictAndInterregionalEventsReportSerializer(
        serializers.ModelSerializer
):
    events = ParticipationInDistrictAndInterregionalEventsSerializer(
        many=True
    )

    class Meta:
        model = ParticipationInDistrAndInterregionalEventsReport
        fields = (
            'id',
            'is_verified',
            'competition',
            'detachment',
            'events'
        )
        read_only_fields = ('is_verified',
                            'competition',
                            'detachment')

    def create(self, validated_data):
        elements = validated_data.pop('events')
        report = super().create(validated_data)
        serializer = ParticipationInDistrictAndInterregionalEventsSerializer(
            many=True,
            data=elements,
            context={'report': report,
                     'request': self.context.get('request')}
        )
        serializer.is_valid(raise_exception=True)
        if serializer:
            serializer.save(report=report)
        return report


class ConfirmParticipationInDistrictAndInterregionalEventsReportSerializer(
        serializers.ModelSerializer
):
    class Meta:
        model = ParticipationInDistrAndInterregionalEventsReport
        fields = '__all__'
