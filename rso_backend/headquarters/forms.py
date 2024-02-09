from dal import autocomplete
from django import forms

from headquarters.models import (CentralHeadquarter, Detachment,
                                 DistrictHeadquarter, EducationalHeadquarter,
                                 LocalHeadquarter, RegionalHeadquarter, UserCentralHeadquarterPosition, UserDetachmentPosition, UserDistrictHeadquarterPosition, UserEducationalHeadquarterPosition, UserLocalHeadquarterPosition, UserRegionalHeadquarterPosition)


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


class BasePositionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'instance' in kwargs:
            self.fields['user'].disabled = True
            self.fields['user'].widget = forms.TextInput(attrs={
                'readonly': True,
                'style': 'background-color: #e9ecef; cursor: not-allowed;',
            })
            self.fields['headquarter'].disabled = True
            self.fields['headquarter'].widget = forms.TextInput(attrs={
                'readonly': True,
                'style': 'background-color: #e9ecef; cursor: not-allowed;',
            })


class CentralPositionForm(BasePositionForm):
    class Meta:
        model = UserCentralHeadquarterPosition
        fields = '__all__'
        widgets = {
            'position': autocomplete.ModelSelect2(url='position-autocomplete'),
        }


class DistrictPositionForm(BasePositionForm):
    class Meta:
        model = UserDistrictHeadquarterPosition
        fields = '__all__'
        widgets = {
            'position': autocomplete.ModelSelect2(url='position-autocomplete'),
        }


class RegionalPositionForm(BasePositionForm):
    class Meta:
        model = UserRegionalHeadquarterPosition
        fields = '__all__'
        widgets = {
            'position': autocomplete.ModelSelect2(url='position-autocomplete'),
            'headquarter': autocomplete.ModelSelect2(
                url='regional-autocomplete'
            )
        }


class LocalPositionForm(BasePositionForm):
    class Meta:
        model = UserLocalHeadquarterPosition
        fields = '__all__'
        widgets = {
            'position': autocomplete.ModelSelect2(url='position-autocomplete'),
            'headquarter': autocomplete.ModelSelect2(
                url='local-autocomplete'
            )
        }


class EducationalPositionForm(BasePositionForm):
    class Meta:
        model = UserEducationalHeadquarterPosition
        fields = '__all__'
        widgets = {
            'position': autocomplete.ModelSelect2(url='position-autocomplete'),
            'headquarter': autocomplete.ModelSelect2(
                url='educational-autocomplete'
            )
        }


class DetachmentPositionForm(BasePositionForm):
    class Meta:
        model = UserDetachmentPosition
        fields = '__all__'
        widgets = {
            'user': autocomplete.ModelSelect2(url='user-autocomplete'),
            'position': autocomplete.ModelSelect2(url='position-autocomplete'),
            'headquarter': autocomplete.ModelSelect2(
                url='detachment-autocomplete'
            )
        }
