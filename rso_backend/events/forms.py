from dal import autocomplete
from django import forms

from events.models import (Event, EventApplications, EventOrganizationData,
                           EventParticipants, MultiEventApplication)


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = '__all__'
        widgets = {
            'author': autocomplete.ModelSelect2(url='user-autocomplete'),
        }


class EventOrganizationDataForm(forms.ModelForm):
    class Meta:
        model = EventOrganizationData
        fields = '__all__'
        widgets = {
            'organizer': autocomplete.ModelSelect2(url='user-autocomplete'),
        }


class EventParticipantDataForm(forms.ModelForm):
    class Meta:
        model = EventParticipants
        fields = '__all__'
        widgets = {
            'event': autocomplete.ModelSelect2(url='event-autocomplete'),
            'user': autocomplete.ModelSelect2(url='user-autocomplete'),
        }


class EventApplicationForm(forms.ModelForm):
    class Meta:
        model = EventApplications
        fields = '__all__'
        widgets = {
            'event': autocomplete.ModelSelect2(url='event-autocomplete'),
            'user': autocomplete.ModelSelect2(url='user-autocomplete'),
        }


class GroupEventApplicationForm(forms.ModelForm):
    class Meta:
        model = EventApplications
        fields = '__all__'
        widgets = {
            'event': autocomplete.ModelSelect2(url='event-autocomplete'),
            'author': autocomplete.ModelSelect2(url='user-autocomplete'),
        }


class MultiEventApplicationForm(forms.ModelForm):
    class Meta:
        model = MultiEventApplication
        fields = '__all__'
        widgets = {
            'event': autocomplete.ModelSelect2(url='event-autocomplete'),
            'detachment': autocomplete.ModelSelect2(
                url='detachment-autocomplete'
            ),
            'educational_headquarter': autocomplete.ModelSelect2(
                url='educational-autocomplete'
            ),
            'local_headquarter': autocomplete.ModelSelect2(
                url='local-autocomplete'
            ),
            'regional_headquarter': autocomplete.ModelSelect2(
                url='regional-autocomplete'
            )
        }
