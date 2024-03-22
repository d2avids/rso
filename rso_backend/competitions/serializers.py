from datetime import date
import logging

from django.db import transaction
from django.conf import settings
from rest_framework import serializers

from competitions.models import (
    Q10, Q11, Q12, Q7, Q8, Q9, CompetitionApplications, CompetitionParticipants, Competitions,
    LinksQ7, LinksQ8, Q10Report, Q11Report, Q12Report,
    Q13EventOrganization, Q13DetachmentReport,
    Q18DetachmentReport, Q19Report, Q7Report, Q8Report, Q9Report)
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


class LinksQ7Serializer(
        serializers.ModelSerializer
):
    class Meta:
        model = LinksQ7
        fields = (
            'id',
            'link'
        )


class Q7Serializer(
        serializers.ModelSerializer
):
    links = LinksQ7Serializer(
        many=True
    )

    class Meta:
        model = Q7
        fields = (
            'id',
            'certificate_scans',
            'event_name',
            'number_of_participants',
            'links',
            'is_verified',
            'detachment_report'
        )
        read_only_fields = (
            'id',
            'event_name',
            'detachment',
            'is_verified',
            'detachment_report'
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
                        LinksQ7Serializer(
                            many=True,
                            data=links,
                            context={'request': self.context.get('request'),
                                     'detachment_report': event.detachment_report,
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


class CreateQ7Serializer(
        serializers.ModelSerializer
):
    links = LinksQ7Serializer(
        many=True
    )

    class Meta:
        model = Q7
        fields = (
            'id',
            'event_name',
            'certificate_scans',
            'number_of_participants',
            'links',
            'is_verified',
            'detachment_report'
        )
        read_only_fields = (
            'id',
            'detachment',
            'is_verified',
            'detachment_report'
        )

    def validate(self, attrs):
        event = self.context.get('event')
        links = event.get('links')
        if not links:
            raise serializers.ValidationError(
                {"links": "Добавьте хотя бы одну ссылку на фотоотчет"}
            )
        if not event.get('event_name'):
            raise serializers.ValidationError(
                {'event_name': 'Укажите название мероприятия.'}
            )
        if not event.get('number_of_participants'):
            raise serializers.ValidationError(
                {'number_of_participants': 'Укажите количество участников.'}
            )
        if not links or len(links) == 0:
            raise serializers.ValidationError(
                {'links': 'Добавьте хотя бы одну ссылку на фотоотчет.'}
            )
        if self.Meta.model.objects.filter(
            detachment_report=self.context.get('detachment_report'),
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
                    LinksQ7Serializer(
                        many=True,
                        data=links,
                        context={'request': self.context.get('request'),
                                 'detachment_report': event.detachment_report,
                                 'event': event}
                    )
                )
                serializer.is_valid(raise_exception=True)
                serializer.save(event=event)
        except Exception as e:
            raise serializers.ValidationError(e)
        return event


class Q7ReportSerializer(
    serializers.ModelSerializer
):
    participation_data = Q7Serializer(many=True)
    detachment = ShortDetachmentCompetitionSerializer()
    competition = CompetitionSerializer()

    class Meta:
        model = Q7Report
        fields = '__all__'


class LinksQ8Serializer(
        serializers.ModelSerializer
):
    class Meta:
        model = LinksQ8
        fields = (
            'id',
            'link'
        )


class Q8Serializer(
        serializers.ModelSerializer
):
    links = LinksQ8Serializer(
        many=True
    )

    class Meta:
        model = Q8
        fields = (
            'id',
            'certificate_scans',
            'event_name',
            'number_of_participants',
            'links',
            'is_verified',
            'detachment_report'
        )
        read_only_fields = (
            'id',
            'event_name',
            'detachment',
            'is_verified',
            'detachment_report'
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
                        LinksQ8Serializer(
                            many=True,
                            data=links,
                            context={'request': self.context.get('request'),
                                     'detachment_report': event.detachment_report,
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


class CreateQ8Serializer(
        serializers.ModelSerializer
):
    links = LinksQ8Serializer(
        many=True
    )

    class Meta:
        model = Q8
        fields = (
            'id',
            'event_name',
            'certificate_scans',
            'number_of_participants',
            'links',
            'is_verified',
            'detachment_report'
        )
        read_only_fields = (
            'id',
            'detachment',
            'is_verified',
            'detachment_report'
        )

    def validate(self, attrs):
        event = self.context.get('event')
        links = event.get('links')
        if not links:
            raise serializers.ValidationError(
                {"links": "Добавьте хотя бы одну ссылку на фотоотчет"}
            )
        if not event.get('event_name'):
            raise serializers.ValidationError(
                {'event_name': 'Укажите название мероприятия.'}
            )
        if not event.get('number_of_participants'):
            raise serializers.ValidationError(
                {'number_of_participants': 'Укажите количество участников.'}
            )
        if not links or len(links) == 0:
            raise serializers.ValidationError(
                {'links': 'Добавьте хотя бы одну ссылку на фотоотчет.'}
            )
        if self.Meta.model.objects.filter(
            detachment_report=self.context.get('detachment_report'),
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
                    LinksQ8Serializer(
                        many=True,
                        data=links,
                        context={'request': self.context.get('request'),
                                 'detachment_report': event.detachment_report,
                                 'event': event}
                    )
                )
                serializer.is_valid(raise_exception=True)
                serializer.save(event=event)
        except Exception as e:
            raise serializers.ValidationError(e)
        return event


class Q8ReportSerializer(
    serializers.ModelSerializer
):
    participation_data = Q8Serializer(many=True)
    detachment = ShortDetachmentCompetitionSerializer()
    competition = CompetitionSerializer()

    class Meta:
        model = Q8Report
        fields = '__all__'


class Q9Serializer(
    serializers.ModelSerializer
):
    class Meta:
        model = Q9
        fields = (
            'id',
            'detachment_report',
            'certificate_scans',
            'event_name',
            'prize_place',
            'is_verified'
        )
        read_only_fields = (
            'id',
            'event_name',
            'detachment_report',
            'is_verified'
        )


class CreateQ9Serializer(
        serializers.ModelSerializer
):
    # certificate_scans = serializers.FileField()
    class Meta:
        model = Q9
        fields = (
            'id',
            'detachment_report',
            'event_name',
            'certificate_scans',
            'prize_place',
            'is_verified'
        )
        read_only_fields = (
            'id',
            'detachment_report',
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
            detachment_report=self.context.get('detachment_report'),
            event_name=attrs.get('event_name')
        ).exists():
            raise serializers.ValidationError(
                {'event_name':
                 'Отчетность по этому мероприятию/конкурсу уже подана.'}
            )
        return attrs


class Q9ReportSerializer(
    serializers.ModelSerializer
):
    participation_data = Q9Serializer(many=True)
    detachment = ShortDetachmentCompetitionSerializer()
    competition = CompetitionSerializer()

    class Meta:
        model = Q9Report
        fields = '__all__'


class Q10Serializer(
    serializers.ModelSerializer
):
    class Meta:
        model = Q10
        fields = (
            'id',
            'detachment_report',
            'certificate_scans',
            'event_name',
            'prize_place',
            'is_verified'
        )
        read_only_fields = (
            'id',
            'event_name',
            'detachment_report',
            'is_verified'
        )


class CreateQ10Serializer(
        serializers.ModelSerializer
):
    class Meta:
        model = Q10
        fields = (
            'id',
            'detachment_report',
            'event_name',
            'certificate_scans',
            'prize_place',
            'is_verified'
        )
        read_only_fields = (
            'id',
            'detachment_report',
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
            detachment_report=self.context.get('detachment_report'),
            event_name=attrs.get('event_name')
        ).exists():
            raise serializers.ValidationError(
                {'event_name':
                 'Отчетность по этому мероприятию/конкурсу уже подана.'}
            )
        return attrs


class Q10ReportSerializer(
    serializers.ModelSerializer
):
    participation_data = Q10Serializer(many=True)
    detachment = ShortDetachmentCompetitionSerializer()
    competition = CompetitionSerializer()

    class Meta:
        model = Q10Report
        fields = '__all__'


class Q11Serializer(
    serializers.ModelSerializer
):
    class Meta:
        model = Q11
        fields = (
            'id',
            'detachment_report',
            'certificate_scans',
            'event_name',
            'prize_place',
            'is_verified'
        )
        read_only_fields = (
            'id',
            'event_name',
            'detachment_report',
            'is_verified'
        )


class CreateQ11Serializer(
        serializers.ModelSerializer
):
    class Meta:
        model = Q11
        fields = (
            'id',
            'detachment_report',
            'event_name',
            'certificate_scans',
            'prize_place',
            'is_verified'
        )
        read_only_fields = (
            'id',
            'detachment_report',
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
            detachment_report=self.context.get('detachment_report'),
            event_name=attrs.get('event_name')
        ).exists():
            raise serializers.ValidationError(
                {'event_name':
                 'Отчетность по этому мероприятию/конкурсу уже подана.'}
            )
        return attrs


class Q11ReportSerializer(
    serializers.ModelSerializer
):
    participation_data = Q11Serializer(many=True)
    detachment = ShortDetachmentCompetitionSerializer()
    competition = CompetitionSerializer()

    class Meta:
        model = Q11Report
        fields = '__all__'


class Q12Serializer(
    serializers.ModelSerializer
):
    class Meta:
        model = Q12
        fields = (
            'id',
            'detachment_report',
            'certificate_scans',
            'event_name',
            'prize_place',
            'is_verified'
        )
        read_only_fields = (
            'id',
            'event_name',
            'detachment_report',
            'is_verified'
        )


class CreateQ12Serializer(
        serializers.ModelSerializer
):
    class Meta:
        model = Q12
        fields = (
            'id',
            'detachment_report',
            'event_name',
            'certificate_scans',
            'prize_place',
            'is_verified'
        )
        read_only_fields = (
            'id',
            'detachment_report',
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
            detachment_report=self.context.get('detachment_report'),
            event_name=attrs.get('event_name')
        ).exists():
            raise serializers.ValidationError(
                {'event_name':
                 'Отчетность по этому мероприятию/конкурсу уже подана.'}
            )
        return attrs


class Q12ReportSerializer(
    serializers.ModelSerializer
):
    participation_data = Q12Serializer(many=True)
    detachment = ShortDetachmentCompetitionSerializer()
    competition = CompetitionSerializer()

    class Meta:
        model = Q12Report
        fields = '__all__'


class Q13EventOrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Q13EventOrganization
        fields = (
            'id',
            'event_type',
            'event_link',
            'detachment_report',
            'is_verified'
        )
        read_only_fields = ('is_verified', 'detachment_report')


class Q13DetachmentReportSerializer(serializers.ModelSerializer):
    organization_data = serializers.ListField(
        child=Q13EventOrganizationSerializer(),
        write_only=True
    )
    organized_events = serializers.SerializerMethodField()

    class Meta:
        model = Q13DetachmentReport
        fields = (
            'id',
            'competition',
            'detachment',
            'organization_data',
            'organized_events',
        )
        read_only_fields = ('competition', 'detachment')

    @staticmethod
    def get_organized_events(instance):
        organized_events = Q13EventOrganization.objects.filter(
            detachment_report=instance
        )
        return Q13EventOrganizationSerializer(organized_events, many=True).data


class Q18DetachmentReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Q18DetachmentReport
        fields = (
            'id',
            'detachment',
            'competition',
            'participants_number',
            'is_verified'
        )
        read_only_fields = ('is_verified', 'detachment', 'competition',)

    def validate(self, attrs):
        competition = self.context.get('competition')
        detachment = self.context.get('detachment')
        if Q18DetachmentReport.objects.filter(
                competition=competition, detachment=detachment
        ).exists():
            raise serializers.ValidationError(
                {'error': 'Отчет по данному показателю уже существует'}
            )
        if not CompetitionParticipants.objects.filter(
                competition=competition,
                junior_detachment=detachment
        ).exists() and not CompetitionParticipants.objects.filter(
            competition=competition,
            detachment=detachment
        ).exists():
            raise serializers.ValidationError(
                {
                    'error': 'Отряд подающего пользователя не '
                             'участвует в конкурсе.'
                },
            )
        return attrs

logger = logging.getLogger('tasks')
class Q19ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Q19Report
        fields = (
            'id',
            'detachment',
            'competition',
            'is_verified',
            'safety_violations'
        )
        read_only_fields = (
            'is_verified',
            'detachment',
            'competition'
        )

    def validate(self, attrs):
        request = self.context.get('request')
        if not attrs.get('safety_violations'):
            raise serializers.ValidationError(
                {'safety_violations': 'Не указано количество нарушений.'}
            )
        if attrs.get('safety_violations') not in ['Имеются', 'Отсутствуют']:
            raise serializers.ValidationError(
                {'safety_violations': 'Некорректное значение.'}
            )
        if request.method == 'POST':
            competition = self.context.get('competition')
            detachment = self.context.get('detachment')
            if Q19Report.objects.filter(
                    competition=competition, detachment=detachment
            ).exists():
                raise serializers.ValidationError(
                    {'error': 'Отчет по данному показателю уже существует'}
                )
        return attrs
