from dal import autocomplete
from django import forms

from users.models import RSOUser


class RSOUserForm(forms.ModelForm):
    class Meta:
        model = RSOUser
        fields = '__all__'
        widgets = {
            'region': autocomplete.ModelSelect2(url='region-autocomplete'),
        }
