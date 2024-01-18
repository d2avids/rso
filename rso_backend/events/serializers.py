from datetime import date

from rest_framework import serializers

from api.serializers import ShortDetachmentSerializer
from events.models import Сompetition, СompetitionApplications, СompetitionParticipants
from headquarters.models import Detachment


class СompetitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Сompetition
        fields = '__all__'


class СompetitionApplicationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = СompetitionApplications
        fields = (
            'id',
            'competition',
            'detachment',
            'junior_detachment',
            'created_at',
            'is_confirmed_by_junior'
        )
        read_only_fields = (
            'id',
            'created_at',
            'competition',
            'detachment',
        )

    def validate(self, attrs):
        request = self.context.get('request')
        applications = СompetitionApplications.objects.all()
        participants = СompetitionParticipants.objects.all()
        if request.method == 'POST':
            competition = self.context.get('competition')
            detachment = self.context.get('detachment')
            junior_detachment = self.context.get('junior_detachment')

            if detachment.founding_date >= date(2023, 1, 25):
                raise serializers.ValidationError(
                    'Отряд-наставник должен быть основан до 25.01.2024'
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

            if junior_detachment:
                if junior_detachment.founding_date < date(2023, 1, 25):
                    raise serializers.ValidationError(
                        'Отряд-новичок основан ранее 25.01.2024, поэтому '
                        'его нельзя подать заявку как отряд-новичок'
                    )
                if applications.filter(
                    competition=competition,
                    junior_detachment=junior_detachment
                    ).exists() or participants.filter(
                        competition=competition,
                        junior_detachment=junior_detachment
                        ).exists():
                    raise serializers.ValidationError(
                        'Отряд-новичок уже подал заявку или участвует '
                        'в этом конкурсе'
                    )
        return attrs


class СompetitionParticipantsSerializer(serializers.ModelSerializer):
    class Meta:
        model = СompetitionParticipants
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
        attrs = super().validate(attrs)
        request = self.context.get('request')
        if request.method == 'POST':
            application = self.context.get('application')
            if (application.junior_detachment and not
                    application.is_confirmed_by_junior):
                raise serializers.ValidationError(
                    'Заявка еще не подтверждена младшим отрядом.'
                )
        return attrs

