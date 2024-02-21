from datetime import date

from django.db import transaction
from django.conf import settings
from django.urls import reverse
from rest_framework import serializers

from competitions.models import (
    CompetitionApplications, CompetitionParticipants, Competitions, LinksOfParticipationInAllRussianEvents,
    LinksOfParticipationInDistrAndInterregEvents, ParticipationInAllRussianEvents,
    ParticipationInDistrAndInterregEvents, PrizePlacesInAllRussianEvents, PrizePlacesInDistrAndInterregEvents,
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

    # def validate(self, attrs):
    #     request = self.context.get('request')
    #     if request.method == 'POST':
    #         event = self.context.get('event')
    #         if (
    #             self.Meta.model.objects
    #             .filter(
    #                 event=event,
    #                 link=attrs.get('link')
    #             )
    #         ).exists():
    #             raise serializers.ValidationError(
    #                 'Ссылка уже привязана к этому мероприятию.'
    #             )
    #     return attrs


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
        links = request.data.get('links')
        if not links or len(links) == 0:
            raise serializers.ValidationError(
                {'links': 'Добавьте хотя бы одну ссылку на фотоотчет.'}
            )
        link_values = [link['link'] for link in links]
        if len(link_values) != len(set(link_values)):
            raise serializers.ValidationError(
                {'links': 'Указаны одинаковые ссылки на фотоотчет.'}
            )
        return attrs

    def update(self, instance, validated_data):
        links = validated_data.pop('links')
        if links:
            try:
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
            except Exception as e:
                raise serializers.ValidationError(e)
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


class CreateParticipationInDistrAndInterregEventsSerializer(
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
        links = request.data.get('links')
        if not links:
            raise serializers.ValidationError(
                {"links": "Добавьте хотя бы одну ссылку на фотоотчет"}
            )
        if not request.data.get('event_name'):
            raise serializers.ValidationError(
                {'event_name': 'Укажите название мероприятия.'}
            )
        if not request.data.get('number_of_participants'):
            raise serializers.ValidationError(
                {'number_of_participants': 'Укажите количество участников.'}
            )
        if not links or len(links) == 0:
            raise serializers.ValidationError(
                {'links': 'Добавьте хотя бы одну ссылку на фотоотчет.'}
            )
        if self.Meta.model.objects.filter(
            competition=self.context.get('competition'),
            detachment=self.context.get('detachment'),
            event_name=attrs.get('event_name')
        ).exists():
            raise serializers.ValidationError(
                {'event_name': 'Отчетность по этому мероприятию уже подана.'}
            )
        link_values = [link['link'] for link in links]
        if len(link_values) != len(set(link_values)):
            raise serializers.ValidationError(
                {'links': 'Указаны одинаковые ссылки.'}
            )
        return attrs

    def create(self, validated_data):
        links = validated_data.pop('links')
        try:
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
        except Exception as e:
            raise serializers.ValidationError(e)
        return event


class LinksOfParticipationInAllRussianEventsSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = LinksOfParticipationInAllRussianEvents
        fields = (
            'id',
            'link'
        )


class ParticipationInAllRussianEventsSerializer(
    serializers.ModelSerializer
):
    links = LinksOfParticipationInAllRussianEventsSerializer(
        many=True
    )

    class Meta:
        model = ParticipationInAllRussianEvents
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
        links = attrs.get('links')
        if not links or len(links) == 0:
            raise serializers.ValidationError(
                    'Добавьте хотя бы одну ссылку на фотоотчет.'
                )
        link_values = [link['link'] for link in links]
        if len(link_values) != len(set(link_values)):
            raise serializers.ValidationError(
                'Ссылки должны быть уникальными.'
            )
        return attrs

    def update(self, instance, validated_data):
        links = validated_data.pop('links')
        if links:
            try:
                with transaction.atomic():
                    event = super().update(instance, validated_data)
                    event.links.all().delete()
                    serializer = (
                        LinksOfParticipationInAllRussianEventsSerializer(
                            many=True,
                            data=links,
                            context={'request': self.context.get('request'),
                                     'detachment': self.context.get('detachment'),
                                     'event': event}
                        )
                    )
                    serializer.is_valid(raise_exception=True)
                    serializer.save(event=event)
            except Exception as e:
                raise serializers.ValidationError(e)
        else:
            event = super().update(instance, validated_data)
        return event


class ConfirmParticipationInAllRussianEventsSerializer(
    serializers.ModelSerializer
):
    links = LinksOfParticipationInAllRussianEventsSerializer(
        many=True
    )

    class Meta:
        model = ParticipationInAllRussianEvents
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


class CreateParticipationInAllRussianEventsSerializer(
    serializers.ModelSerializer
):
    links = LinksOfParticipationInAllRussianEventsSerializer(
        many=True
    )

    class Meta:
        model = ParticipationInAllRussianEvents
        fields = (
            'id',
            'competition',
            'detachment',
            'event_name',
            'certificate_scans',
            'number_of_participants',
            'links',
            'is_verified',
        )
        read_only_fields = (
            'id',
            'competition',
            'detachment',
            'is_verified'
        )

    def validate(self, attrs):
        request = self.context.get('request')
        links = attrs.get('links')
        if not links:
            raise serializers.ValidationError(
                {'links': 'Добавьте хотя бы одну ссылку на фотоотчет.'}
            )
        if not request.data.get('event_name'):
            raise serializers.ValidationError(
                {'event_name': 'Укажите название мероприятия.'}
            )
        if not request.data.get('number_of_participants'):
            raise serializers.ValidationError(
                {'number_of_participants': 'Укажите количество участников.'}
            )
        if len(links) == 0:
            raise serializers.ValidationError(
                {'links': 'Добавьте хотя бы одну ссылку на фотоотчет.'}
            )
        if self.Meta.model.objects.filter(
            competition=self.context.get('competition'),
            detachment=self.context.get('detachment'),
            event_name=attrs.get('event_name')
        ).exists():
            raise serializers.ValidationError(
                {'event_name': 'Отчетность по этому мероприятию уже подана.'}
            )
        link_values = [link['link'] for link in links]
        if len(link_values) != len(set(link_values)):
            raise serializers.ValidationError(
                {'links': 'Ссылки должны быть уникальными.'}
            )
        return attrs

    def create(self, validated_data):
        try:
            links = validated_data.pop('links')
            with transaction.atomic():
                event = super().create(validated_data)
                serializer = (
                    LinksOfParticipationInAllRussianEventsSerializer(
                        many=True,
                        data=links,
                        context={'request': self.context.get('request'),
                                 'detachment': self.context.get('detachment'),
                                 'event': event}
                    )
                )
                serializer.is_valid(raise_exception=True)
                serializer.save(event=event)
        except Exception as e:
            raise serializers.ValidationError(e)
        return event


class PrizePlacesInDistrAndInterregEventsSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = PrizePlacesInDistrAndInterregEvents
        fields = (
            'id',
            'competition',
            'detachment',
            'certificate_scans',
            'event_name',
            'prize_place',
            'is_verified'
        )
        read_only_fields = (
            'id',
            'competition',
            'event_name',
            'detachment',
            'is_verified'
        )


class ConfirmPrizePlacesInDistrAndInterregEventsSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = PrizePlacesInDistrAndInterregEvents
        fields = '__all__'
        read_only_fields = (
            'id',
            'competition',
            'detachment',
            'event_name',
            'certificate_scans',
            'prize_place'
        )


class CreatePrizePlacesInDistrAndInterregEventsSerializer(
        serializers.ModelSerializer
):
    class Meta:
        model = PrizePlacesInDistrAndInterregEvents
        fields = (
            'id',
            'competition',
            'detachment',
            'event_name',
            'certificate_scans',
            'prize_place',
            'is_verified'
        )
        read_only_fields = (
            'id',
            'competition',
            'detachment',
            'is_verified'
        )

    def validate(self, attrs):
        prize_place = attrs.get('prize_place', None)
        if not attrs.get('event_name'):
            raise serializers.ValidationError(
                {'event_name': 'Укажите название мероприятия/конкурса.'}
            )
        if not prize_place:
            raise serializers.ValidationError(
                {'prize_place': 'Не указано призовое место.'}
            )
        if prize_place <= 0 or prize_place > 3:
            raise serializers.ValidationError(
                {'prize_place': 'Призовое место должно быть от 1 до 3.'}
            )
        if self.Meta.model.objects.filter(
            competition=self.context.get('competition'),
            detachment=self.context.get('detachment'),
            event_name=attrs.get('event_name')
        ).exists():
            raise serializers.ValidationError(
                {'event_name':
                 'Отчетность по этому мероприятию/конкурсу уже подана.'}
            )
        return attrs








class PrizePlacesInAllRussianEventsSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = PrizePlacesInAllRussianEvents
        fields = (
            'id',
            'competition',
            'detachment',
            'certificate_scans',
            'event_name',
            'prize_place',
            'is_verified'
        )
        read_only_fields = (
            'id',
            'competition',
            'event_name',
            'detachment',
            'is_verified'
        )


class ConfirmPrizePlacesInAllRussianEventsSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = PrizePlacesInAllRussianEvents
        fields = '__all__'
        read_only_fields = (
            'id',
            'competition',
            'detachment',
            'event_name',
            'certificate_scans',
            'prize_place'
        )


class CreatePrizePlacesInAllRussianEventsSerializer(
        serializers.ModelSerializer
):
    class Meta:
        model = PrizePlacesInAllRussianEvents
        fields = (
            'id',
            'competition',
            'detachment',
            'event_name',
            'certificate_scans',
            'prize_place',
            'is_verified'
        )
        read_only_fields = (
            'id',
            'competition',
            'detachment',
            'is_verified'
        )

    def validate(self, attrs):
        prize_place = attrs.get('prize_place', None)
        if not attrs.get('event_name'):
            raise serializers.ValidationError(
                {'event_name': 'Укажите название мероприятия/конкурса.'}
            )
        if not prize_place:
            raise serializers.ValidationError(
                {'prize_place': 'Не указано призовое место.'}
            )
        if prize_place <= 0 or prize_place > 3:
            raise serializers.ValidationError(
                {'prize_place': 'Призовое место должно быть от 1 до 3.'}
            )
        if self.Meta.model.objects.filter(
            competition=self.context.get('competition'),
            detachment=self.context.get('detachment'),
            event_name=attrs.get('event_name')
        ).exists():
            raise serializers.ValidationError(
                {'event_name':
                 'Отчетность по этому мероприятию/конкурсу уже подана.'}
            )
        return attrs
