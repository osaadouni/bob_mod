import datetime
from bootstrap_datepicker_plus import DatePickerInput
from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from .models import BobHandeling, Onderzoek





class BOBApplicationForm(forms.ModelForm):
    dvom_datumpv = forms.DateField(
        label='Datum PV',
        widget=DatePickerInput(format='%d/%m/%Y'),
        initial=datetime.date.today(),
        help_text='Datum van het PV',
        input_formats=settings.DATE_INPUT_FORMATS
    )

    dvom_verlengingingaandop = forms.DateField(
        label='Verlenging ingaand op',
        widget=DatePickerInput(format='%d/%m/%Y'),
        input_formats=settings.DATE_INPUT_FORMATS
    )
    dvom_verlengingeinddatum = forms.DateField(
        label='Verlenging einddatum',
        widget=DatePickerInput(format='%d/%m/%Y'),
        input_formats=settings.DATE_INPUT_FORMATS
    )
    dvom_vtmstartdatum = forms.DateField(
        label='VTMStartdatum / op',
        widget=DatePickerInput(format='%d/%m/%Y'),
        help_text='Startdatum vordering tot machtiging',
        input_formats=settings.DATE_INPUT_FORMATS
    )
    dvom_vtmeinddatum = forms.DateField(
        label='VTMEinddatum',
        widget=DatePickerInput(format='%d/%m/%Y'),
        help_text='Einddatum vordering tot machtiging',
        input_formats=settings.DATE_INPUT_FORMATS
    )

    dvom_machtigingop = forms.DateField(
        label='Machtiging op',
        widget=DatePickerInput(format='%d/%m/%Y'),
        help_text='Datum waarop de machtiging is afgegeven',
        input_formats=settings.DATE_INPUT_FORMATS,
        required=False
    )
    dvom_machtigingstartdatum = forms.DateField(
        label='Machtiging startdatum / op',
        widget=DatePickerInput(format='%d/%m/%Y'),
        help_text='Startdatum van de machtiging',
        input_formats=settings.DATE_INPUT_FORMATS,
        required=False
    )
    dvom_machtigingeinddatum = forms.DateField(
        label='Machtiging einddatum',
        widget=DatePickerInput(format='%d/%m/%Y'),
        help_text='Einddatum van de machtiging',
        input_formats=settings.DATE_INPUT_FORMATS,
        required=False
    )

    #dvom_heterdaad = forms.TypedChoiceField(
    #    coerce=lambda x: x == 'True',
    #    choices=((False, 'False'), (True, 'True')),
    #    widget=forms.RadioSelect
    #)
    class Meta:
        model = BobHandeling
        exclude = ('dvom_bobhandelingid', 'dvom_bobhandeling')
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

        error_messages = {
            "dvom_aanvraagpv": {
                "required": _("Dit veld is verplicht.")
            },
            "dvom_verbalisant": {
                "required": _("Dit veld is verplicht.")
            },
            "dvom_verbalisantcontactgegevens": {
                "required": _("Dit veld is verplicht.")
            },
            "dvom_strafvorderlijkebevoegdheidid": {
                "required": _("Dit veld is verplicht.")
            },

        }

    def clean(self):

        print('BOBApplicationForm::clean()')

        cleaned_data = super().clean()
        dvom_aanvraagpv = cleaned_data.get('dvom_aanvraagpv')
        dvom_datumpv = cleaned_data.get('dvom_datumpv')
        dvom_bobhandeling = f"BOB_handeling_{dvom_aanvraagpv}_{dvom_datumpv}"
        cleaned_data['dvom_bobhandeling'] = dvom_bobhandeling
        print(f"dvom_bobhandeling: {dvom_bobhandeling}")

        return cleaned_data


class OnderzoekForm(forms.ModelForm):

    class Meta:
        model = Onderzoek
        exclude = ('onderzoekid',)
