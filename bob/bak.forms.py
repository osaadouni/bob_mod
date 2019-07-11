from django import forms

from .models import Onderzoek


class OnderzoekForm(forms.ModelForm):

    class Meta:
        model = Onderzoek
        exclude = ('dvom_onderzoekid',)
