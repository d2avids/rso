from dal import autocomplete
from django import forms

from headquarters.models import (CentralHeadquarter, Detachment,
                                 DistrictHeadquarter, EducationalHeadquarter,
                                 LocalHeadquarter, RegionalHeadquarter)


class CentralForm(forms.ModelForm):
    class Meta:
        model = CentralHeadquarter
        fields = '__all__'
        widgets = {
            'commander': autocomplete.ModelSelect2(url='user-autocomplete'),
        }


class DistrictForm(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = DistrictHeadquarter
        widgets = {
            'commander': autocomplete.ModelSelect2(url='user-autocomplete'),
        }


class RegionalForm(forms.ModelForm):
    class Meta:
        model = RegionalHeadquarter
        fields = '__all__'
        widgets = {
            'commander': autocomplete.ModelSelect2(url='user-autocomplete'),
            'region': autocomplete.ModelSelect2(url='region-autocomplete')
        }


class LocalForm(forms.ModelForm):
    class Meta:
        model = LocalHeadquarter
        fields = '__all__'
        widgets = {
            'commander': autocomplete.ModelSelect2(url='user-autocomplete'),
            'regional_headquarter': autocomplete.ModelSelect2(
                url='regional-autocomplete'
            )
        }


class EducationalForm(forms.ModelForm):
    class Meta:
        model = EducationalHeadquarter
        fields = '__all__'
        widgets = {
            'commander': autocomplete.ModelSelect2(url='user-autocomplete'),
            'educational_headquarter': autocomplete.ModelSelect2(
                url='educational-autocomplete'
            ),
            'local_headquarter': autocomplete.ModelSelect2(
                url='local-autocomplete'
            ),
            'educational_institution': autocomplete.ModelSelect2(
                url='educational-institution-autocomplete'
            ),
        }


class DetachmentForm(forms.ModelForm):
    class Meta:
        model = Detachment
        fields = '__all__'
        widgets = {
            'commander': autocomplete.ModelSelect2(url='user-autocomplete'),
            'region': autocomplete.ModelSelect2(url='region-autocomplete'),
            'educational_headquarter': autocomplete.ModelSelect2(
                url='educational-autocomplete'
            ),
            'local_headquarter': autocomplete.ModelSelect2(
                url='local-autocomplete'
            ),
            'regional_headquarter': autocomplete.ModelSelect2(
                url='regional-autocomplete'
            ),
            'educational_institution': autocomplete.ModelSelect2(
                url='educational-institution-autocomplete'
            ),
        }
