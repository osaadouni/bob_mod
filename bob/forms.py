import datetime
from bootstrap_datepicker_plus import DatePickerInput
from django import forms

from .models import BobHandeling


class BobHandelingForm(forms.ModelForm):
    dvom_datumpv = forms.DateField(
        label='Datum PV',
        widget=DatePickerInput(format='%d/%m/%Y'),
        initial=datetime.date.today()
    )

    dvom_verlengingingaandop = forms.DateField(
        label='Verlenging ingaand op',
        widget=DatePickerInput(format='%d/%m/%Y'),
    )
    dvom_verlengingeinddatum = forms.DateField(
        label='Verlenging einddatum',
        widget=DatePickerInput(format='%d/%m/%Y'),
    )
    #dvom_heterdaad = forms.TypedChoiceField(
    #    coerce=lambda x: x == 'True',
    #    choices=((False, 'False'), (True, 'True')),
    #    widget=forms.RadioSelect
    #)
    class Meta:
        model = BobHandeling
        exclude = ('dvom_bobhandelingid',)
        help_texts = {
            'dvom_datumpv': 'Datum van het PV',
            'dvom_aanvraagpv': 'PV nummer van het aanvraag PV',
            'dvom_heeftverlenging': 'Is deze bob handeling verlengd',
            'dvom_verlenging': 'Betreft het een verlenging van een eerdere bob handeling',
        }
        widgets = {
            'dvom_heterdaad': forms.RadioSelect,
            'dvom_heeftverlenging': forms.RadioSelect,
            'dvom_verlenging': forms.RadioSelect,
        }
