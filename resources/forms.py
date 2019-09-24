import datetime
from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from bootstrap_datepicker_plus import DatePickerInput
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit, Row, Column, Fieldset, Div, Field, Button
from crispy_forms.bootstrap import FieldWithButtons,StrictButton, AppendedText, PrependedText, PrependedAppendedText
from crispy_forms.bootstrap import InlineRadios

from .models import BOBAanvraag


class BOBAanvraagForm(forms.ModelForm):
    mondeling_aanvraag_datum = forms.DateField(
        label='Datum aanvraag',
        widget=DatePickerInput(format='%d/%m/%Y'),
        initial=datetime.date.today(),
        help_text='Datum v/d mondelinge vordering',
        input_formats=settings.DATE_INPUT_FORMATS
    )

    class Meta:
        model = BOBAanvraag
        exclude = ('unique_id', 'created_by', 'updated_by', 'status', 'created_at', 'updated_at')
        help_texts = {
            'dvom_aanvraagpv': 'PV nummer van het aanvraag PV',
            'mondeling_aanvraag_bevestiging': 'Betreft het een bevestiging van een mondelinge aanvraag',
        }
        widgets = {
            'mondeling_aanvraag_bevestiging': forms.RadioSelect,
            'bijlage_toevoegen': forms.RadioSelect,
        }

        error_messages = {
            "pv_nummer": {
                "required": _("Dit veld is verplicht.")
            },
            "verbalisant": {
                "required": _("Dit veld is verplicht.")
            },
            "verbalisant_email": {
                "required": _("Dit veld is verplicht.")
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = "."
        self.helper.form_id = 'aanvraagFormId'
        self.helper.attrs = {'novalidate': 'true'}

        self.helper.layout = Layout(
            Fieldset(
                'Algemeen',
                Row(
                    #Column('mondeling_aanvraag_bevestiging', css_class='bobaanvraag-mondeling-check col-md-6 mb-0'),
                    Div(InlineRadios('mondeling_aanvraag_bevestiging'), css_class='bobaanvraag-mondeling-check col-md-6 mb-0'),
                    Column('mondeling_aanvraag_datum', css_class='bobaanvraag-mondeling-datum col-md-6 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Div('naam_ovj', css_class='col-md-6 mb-0 bob-data-required'),
                    Div('parket_nummer', css_class='col-md-6 mb-0 bob-data-required'),
                    css_class='form-row'
                ),
                Row(
                    Div('naam_onderzoek', css_class='col-md-6 mb-0 bob-data-required'),
                    Div('rc_nummer', css_class='col-md-6 mb-0 bob-data-required'),
                    css_class='form-row'
                ),
                Row(
                    Column('pv_nummer', css_class='form-group col-sm-3 mb-0'),
                    Column('onderzoeksbelang_toelichting', css_class='form-group col-md-6 offset-md-3 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Column('verstrekking_gegevens_aan', css_class='form-group col-md-3 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Column('verbalisant', css_class='form-group col-md-6 mb-0'),
                    Column('verbalisant_email', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Column('bijlage_toevoegen', css_class='form-group col-md-6 mb-0'),
                    Column('bijlage', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
            ),
            Submit('btn_submit_id', 'Opslaan &raquo;', id="id_btn_submit", css_class='btn-politie float-right btn-submit')
        )

    def clean(self):

        print('BOBAanvraagForm::clean()')

        cleaned_data = super().clean()

        return cleaned_data



class BOBAanvraagFilterFormHelper(FormHelper):
    form_method = 'GET'
    form_class = 'form-inline'
    field_template = 'bootstrap3/layout/inline_field.html'
    layout = Layout(
       'verbalisant',
        'verbalisant_email',
        'pv_nummer',
        Submit('submit', 'Zoeken', css_class='btn-politie btn-sm'),

    )

    #layout = Layout(
    #    FieldWithButtons('dvom_verbalisant', StrictButton('Go!')),
    #)


class BOBAanvraagStatusForm(forms.Form):
    next_status = forms.ChoiceField(label="Ik wil deze aanvraag: ", widget=forms.Select(), choices=[], required=True)
    class Meta:
        fields = ('next_status',)

    def __init__(self, *args, **kwargs):

        available_transitions = kwargs.pop('available_transitions')

        super().__init__(*args, **kwargs)

        self.fields['next_status'].choices = available_transitions

        self.helper = FormHelper()
        self.helper.form_class = 'inline-form'
        self.helper.form_action = "."
        self.helper.form_id = 'aanvraagStatusFormId'
        self.helper.attrs = {'novalidate': 'true'}
        self.helper.layout = Layout(
            Row(
                Column('next_status', css_class="col-sm-4"),
                Column(Submit('btn_submit_id', 'Verzenden &raquo;', id="id_btn_submit",
               css_class='btn-politie  btn-submit ')),
                css_class="row-form d-flex justify-content-end align-items-end"
            )
        )

