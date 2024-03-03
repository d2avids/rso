from competitions.models import (CompetitionApplications,
                                 CompetitionParticipants)
from dal import autocomplete
from django import forms


class CompetitionApplicationsForm(forms.ModelForm):
    class Meta:
        model = CompetitionApplications
        fields = '__all__'
        widgets = {
            'detachment': autocomplete.ModelSelect2(
                url='competition-detachment-autocomplete'
            ),
            'junior_detachment': autocomplete.ModelSelect2(
                url='competition-junior-detachment-autocomplete'
            )
        }


class CompetitionParticipantsForm(forms.ModelForm):
    class Meta:
        model = CompetitionParticipants
        fields = '__all__'
        widgets = {
            'detachment': autocomplete.ModelSelect2(
                url='competition-detachment-autocomplete'
            ),
            'junior_detachment': autocomplete.ModelSelect2(
                url='competition-junior-detachment-autocomplete'
            )
        }
