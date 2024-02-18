from datetime import date

from django.db import transaction
from django.conf import settings
from rest_framework import serializers

from competitions.models import (
    CompetitionApplications, CompetitionParticipants, Competitions,
    LinksOfParticipationInDistrAndInterregEvents,
    ParticipationInDistrAndInterregEvents,
    Score)
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


class LinksOfParticipationInDistrAndInterregEventsSerializer(
        serializers.ModelSerializer
):
    class Meta:
        model = LinksOfParticipationInDistrAndInterregEvents
        fields = (
            'id',
            'link'
        )

    def validate(self, attrs):
        request = self.context.get('request')
        if request.method == 'POST':
            event = self.context.get('event')
            if (
                LinksOfParticipationInDistrAndInterregEvents.objects
                .filter(
                    event=event,
                    link=attrs.get('link')
                )
            ).exists():
                raise serializers.ValidationError(
                    'Ссылка уже привязана к этому мероприятию.'
                )
        return attrs


class ParticipationInDistrAndInterregEventsSerializer(
        serializers.ModelSerializer
):
    links = LinksOfParticipationInDistrAndInterregEventsSerializer(
        many=True
    )

    class Meta:
        model = ParticipationInDistrAndInterregEvents
        fields = (
            'id',
            'competition',
            'detachment',
            'certificate_scans',
            'event_name',
            'number_of_participants',
            'links',
            'is_verified'
        )
        read_only_fields = (
            'id',
            'competition',
            'event_name',
            'detachment',
            'is_verified'
        )

    def validate(self, attrs):
        request = self.context.get('request')
        if not request.data.get('links'):
            raise serializers.ValidationError(
                'Добавьте хотя бы одну ссылку на фотоотчет.'
            )
        if len(attrs.get('links')) == 0:
            raise serializers.ValidationError(
                    'Добавьте хотя бы одну ссылку на фотоотчет.'
                )
        return attrs

    def update(self, instance, validated_data):
        links = validated_data.pop('links')
        if links:
            with transaction.atomic():
                event = super().update(instance, validated_data)
                event.links.all().delete()
                serializer = (
                    LinksOfParticipationInDistrAndInterregEventsSerializer(
                        many=True,
                        data=links,
                        context={'request': self.context.get('request'),
                                 'detachment': event.detachment,
                                 'event': event}
                    )
                )
                serializer.is_valid(raise_exception=True)
                serializer.save(event=event)
        else:
            event = super().update(instance, validated_data)
        return event


class ConfirmParticipationInDistrictAndInterregionalEventsSerializer(
        serializers.ModelSerializer
):
    links = LinksOfParticipationInDistrAndInterregEventsSerializer(
        many=True
    )

    class Meta:
        model = ParticipationInDistrAndInterregEvents
        fields = '__all__'
        read_only_fields = (
            'id',
            'competition',
            'detachment',
            'event_name',
            'certificate_scans',
            'number_of_participants',
            'links'
        )


class ParticipationInDistrAndInterregEventsCreateSerializer(
        serializers.ModelSerializer
):
    links = LinksOfParticipationInDistrAndInterregEventsSerializer(
        many=True
    )

    class Meta:
        model = ParticipationInDistrAndInterregEvents
        fields = (
            'id',
            'competition',
            'detachment',
            'event_name',
            'certificate_scans',
            'number_of_participants',
            'links',
            'is_verified'
        )
        read_only_fields = (
            'id',
            'competition',
            'detachment',
            'is_verified'
        )

    def validate(self, attrs):
        request = self.context.get('request')
        if not request.data.get('links'):
            raise serializers.ValidationError(
                'Добавьте хотя бы одну ссылку на фотоотчет.'
            )
        if not request.data.get('event_name'):
            raise serializers.ValidationError(
                'Укажите название мероприятия.'
            )
        if not request.data.get('number_of_participants'):
            raise serializers.ValidationError(
                'Укажите количество участников.'
            )
        if len(attrs.get('links')) == 0:
            raise serializers.ValidationError(
                    'Добавьте хотя бы одну ссылку на фотоотчет.'
            )
        if ParticipationInDistrAndInterregEvents.objects.filter(
            competition=self.context.get('competition'),
            detachment=self.context.get('detachment'),
            event_name=attrs.get('event_name')
        ).exists():
            raise serializers.ValidationError(
                'Отчетность по этому мероприятию уже подана.'
            )
        return attrs

    def create(self, validated_data):
        links = validated_data.pop('links')
        with transaction.atomic():
            event = super().create(validated_data)
            serializer = (
                LinksOfParticipationInDistrAndInterregEventsSerializer(
                    many=True,
                    data=links,
                    context={'request': self.context.get('request'),
                             'detachment': event.detachment,
                             'event': event}
                )
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(event=event)
        return event
