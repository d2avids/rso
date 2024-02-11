from dal import autocomplete
from django import forms

from events.models import (Event, EventApplications, EventOrganizationData,
                           EventParticipants)


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
