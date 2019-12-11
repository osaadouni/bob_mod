import datetime
from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from bootstrap_datepicker_plus import DatePickerInput
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, ButtonHolder, Submit, Row, Column, Fieldset, Div, Field, Button, MultiField, HTML
from crispy_forms.utils import TEMPLATE_PACK
from crispy_forms.bootstrap import FieldWithButtons,StrictButton, AppendedText, PrependedText, PrependedAppendedText
from crispy_forms.bootstrap import InlineRadios

from betterforms.forms import BetterForm, BetterModelForm
from betterforms.multiform import MultiModelForm, MultiForm

from .models import BOBAanvraag, ProcesVerbaalVerdenking, ProcesVerbaalAanvraag, ProcesVerbaalHistorischeGegevens, \
    VerbalisantProcesVerbaal, RechtsPersoonProcesVerbaal, NatuurlijkPersoonProcesVerbaal, ProcesVerbaal
from .custom_layout_object import VerbalisantFormSection
from .constants import ENTITY_CHOICES


#################################
# Custom Crispy Field
#################################
class CustomCrispyField(Field):
    extra_context = {}

    def __init__(self, *args, **kwargs):
        self.extra_context = kwargs.pop('extra_context', self.extra_context)
        super(CustomCrispyField, self).__init__(*args, **kwargs)

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK, extra_context=None, **kwargs):
        if self.extra_context:
            extra_context = extra_context.update(self.extra_context) if extra_context else self.extra_context
        return super(CustomCrispyField, self).render(form, form_style, context, template_pack, extra_context, **kwargs)


########################################
# BOBAanvraag Form
########################################
class BOBAanvraagForm(forms.ModelForm):
    mondeling_aanvraag_datum = forms.DateField(
        label='Datum mondelinge aanvraag',
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
            'onderzoeksbelang_toelichting': forms.Textarea(attrs={'rows':3})
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
                    Field('mondeling_aanvraag_datum', css_class='bobaanvraag-mondeling-datum',
                          wrapper_class='col-md-6 mb-0'),
                    css_class='form-row'
                ),
                Field('naam_ovj', id="id_naam_ovj", css_class='bob-data-required', wrapper_class="col-sm-4 pl-0"),
                Row(
                    Field('parket_nummer', css_class='bob-data-required', wrapper_class='col-md-6 mb-0'),
                    Field('rc_nummer', css_class='bob-data-required', wrapper_class='col-md-6 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Field('naam_onderzoek', wrapper_class='col-md-6 mb-0', css_class='bob-data-required'),
                    Field('onderzoeksbelang_toelichting', wrapper_class='col-md-6 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Field('verstrekking_gegevens_aan', wrapper_class='col-md-3 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Field('verbalisant', wrapper_class='col-md-6 mb-0'),
                    Field('verbalisant_email', wrapper_class='col-md-6 mb-0'),
                    css_class='form-row'
                ),
                Row(
                    Field('bijlage_toevoegen', wrapper_class='col-md-6 mb-0'),
                    Field('bijlage', wrapper_class='col-md-6 mb-0'),
                    css_class='form-row'
                ),
            ),
            Submit('btn_submit_id', 'Opslaan &raquo;', id="id_btn_submit", css_class='btn-politie float-right btn-submit')
        )

    def clean(self):

        print('BOBAanvraagForm::clean()')

        cleaned_data = super().clean()

        return cleaned_data



###############################################
# BOBAanvraag Filter Form helpr
###############################################
class BOBAanvraagFilterFormHelper(FormHelper):
    form_method = 'GET'
    form_class = 'form-inline'
    form_show_labels = False
    field_template = 'bootstrap3/layout/inline_field.html'
    layout = Layout(
       Field('verbalisant', autocomplete="off", css_class='basicAutoComplete form-control-sm', placeholder="Naam verb..."),
       Field('verbalisant_email', autocomplete="off", css_class="basicAutoComplete form-control-sm", placeholder="Email verb..."),
       Field('pv_verdenking__bvh_nummer', autocomplete="off", css_class="basicAutoComplete form-control-sm", placeholder="BVH nummer..."),
       Submit('submit', 'Zoeken', css_class='btn-politie btn-sm'),
    )


###############################################
# BOBAanvraag Status Form
###############################################
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

################################
#  LAYPOUTS
################################

# VerbalisantLayout
class VerbalisantLayout(Layout):
    def __init__(self, *args, **kwargs):
        prefix = kwargs.get("prefix", VerbalisantForm.prefix)
        print(f"{self.__class__.__name__}::prefix={prefix}")
        super(VerbalisantLayout, self).__init__(
            CustomCrispyField('verbalisanten', template='resources/verbalisanten.html', extra_context={'prefix': prefix}),
        )

# EntitychoiceLayout
class EntityChoiceLayout(Layout):
    def __init__(self, *args, **kwargs):
        super(EntityChoiceLayout, self).__init__(
            CustomCrispyField('entity_type', template='resources/entity_type_select.html',
                              extra_context={'prefix': kwargs.get('prefix', None), 'choices': ENTITY_CHOICES})
        )

# PersoonLayout
class PersoonLayout(Layout):
    def __init__(self, *args, **kwargs):
        super(PersoonLayout, self).__init__(
            Field('jegens_rechtspersoon', template='resources/persoon_form.html'),

            Field('jegens_persoon',
                template='resources/persoon_form.html',
                title="Gegevens van de te onderzoeken persoon",
                class_wrapper='natuurlijkpersoon-wrapper'
            ),
        )


# PersoonLayout
#class PersoonLayout(Layout):
#    def __init__(self, *args, **kwargs):
#        prefix = kwargs.get("prefix")
#        super(PersoonLayout, self).__init__(
#            Field('rechtspersoon', template='resources/persoon_form.html'),
#            Field('natuurlijkpersoon', template='resources/persoon_form.html'),
#        )

# PVerdenkingLayout
class PvVerdenkingLayout(Layout):
    def __init__(self, *args, **kwargs):
        super(PvVerdenkingLayout,self).__init__(
            Fieldset('PV verdenking',
                     Row(
                         Field('pv_nummer', wrapper_class='col-sm-6'),
                         Field('bvh_nummer', wrapper_class='col-sm-6'),
                         Field('naam_ovj', wrapper_class='col-sm-6'),
                         Field('parket_nummer', wrapper_class='col-sm-6'),
                         Field('rc_nummer', wrapper_class='col-sm-6'),
                         css_class='form-row'
                     ),
                     css_class='border p-3 shadow-sm'
                     )
        )


###################################
# FORMS
###################################

# Verbalisant Form
class VerbalisantForm(forms.ModelForm):

    prefix = 'verbalisant'
    verbalisanten = forms.CharField(required=False)

    class Meta:
        model = VerbalisantProcesVerbaal
        fields = ('naam', 'rang', 'verbalisanten')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['verbalisanten'].help_text = "Verbalisanten  help text"
        self.fields['verbalisanten'].queryset = VerbalisantProcesVerbaal.objects.all()

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.attrs = {'novalidate': 'true'}
        self.helper.layout = Layout(
            VerbalisantLayout(),
        )


# EntityType Form ( NP, RP )
class EntityTypeForm(forms.ModelForm):

    prefix = 'entity'

    class Meta:
        model = ProcesVerbaal
        fields = ('entity_type',)

    def __init__(self, *args, **kwargs):
        self.prefix = kwargs.pop('prefix', self.prefix)
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.attrs = {'novalidate': 'true'}
        self.helper.layout = Layout(
            EntityChoiceLayout(prefix=self.prefix),
        )

# Rechtspersoon Form
class RechtsPersoonForm(forms.ModelForm):

    prefix = 'rechtspersoon'

    class Meta:
        model = RechtsPersoonProcesVerbaal
        fields = ('naam', 'rechtsvorm', 'statutaire_adres', 'vestiging_adres', 'post_adres', 'kvk_nummer',
                  'vertegenwoordiger', 'functie')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.attrs = {'novalidate': 'true'}
        self.helper.layout = Layout(
            Div(
                HTML(
                    '<p><strong>Gegevens van de te onderzoeken rechtspersoon</strong></p>'
                ),
                Row(
                    Field('naam', css_class='', wrapper_class='col-sm-6'),
                    Field('rechtsvorm', css_class='', wrapper_class='col-sm-6'),
                    css_class='',
                ),
                Row(
                    Field('statutaire_adres', css_class='', wrapper_class='col-sm-6'),
                    Field('vestiging_adres', css_class='', wrapper_class='col-sm-6'),
                    css_class='',
                ),
                Row(
                    Field('post_adres', css_class='', wrapper_class='col-sm-6'),
                    Field('kvk_nummer', css_class='', wrapper_class='col-sm-6'),
                    css_class=''
                ),
                Row(
                    Field('vertegenwoordiger', css_class='', wrapper_class='col-sm-6'),
                    Field('functie', css_class='', wrapper_class='col-sm-6'),
                    css_class='',
                ),
                css_class='pv-entity-type',data_entity_type="rp"
            )
        )

    def clean(self):
        print(f"{self.__class__.__name__}::clean()")
        cleaned_data = super().clean()
        print(f"value:{cleaned_data}")

# Nauurlijk persoon
class NatuurlijkPersoonForm(forms.ModelForm):
    prefix = 'natuurlijk_persoon'

    geboortedatum = forms.DateField(
        label='Geboortedatum',
        widget=DatePickerInput(format="%d/%m/%Y"),
        input_formats=settings.DATE_INPUT_FORMATS,
        required=False

    )

    class Meta:
        model = NatuurlijkPersoonProcesVerbaal
        fields = ('voornaam', 'voorvoegsel', 'achternaam', 'geslacht', 'geboortedatum', 'geboorteland', 'nationaliteit',
                  'adres', 'postcode', 'plaats', 'land', 'keno_nummer')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.attrs = {'novalidate': 'true'}
        self.helper.layout = Layout(
            Div(
                HTML(
                    '<p><strong>Gegevens van de te onderzoeken persoon</strong></p>'
                ),
                Row(
                    Field('voornaam', css_class='', wrapper_class='col-sm-5'),
                    Field('voorvoegsel', ccs_class='', wrapper_class='col-sm-2'),
                    Field('achternaam', css_class='', wrapper_class='col-sm-5'),
                    css_class=''
                ),
                Row(
                    Field('keno_nummer', wrapper_class='col-sm-4'),
                    Field('geslacht', css_class='custom-select', wrapper_class='col-sm-4'),
                    Field('geboortedatum', css_class='', wrapper_class='col-sm-4'),
                    css_class=''
                ),
                Row(
                    Field('geboorteland', css_class='custom-select', wrapper_class='col-sm-6'),
                    Field('nationaliteit', css_class='custom-select', wrapper_class='col-sm-6'),
                    css_class=''
                ),
                Row(
                    Field('adres', css_class='', wrapper_class='col-sm-6'),
                    Field('postcode', css_class='', wrapper_class='col-sm-6'),
                    css_class=''
                ),
                Row(
                    Field('plaats', css_class='', wrapper_class='col-sm-6'),
                    Field('land', css_class='', wrapper_class='col-sm-6'),
                    css_class=''
                ),
                css_class='pv-entity-type', data_entity_type="np"
            ),
        )


# validate pdf file
def validate_file(value):
    print(f"validate_file:: value={value}")


# Common PV form with common props
class PVCommonForm(forms.ModelForm):
    """
    Form class representing instances of select forms listing different BOB middelen to choose from.
    """
    pdf_document = forms.FileField(validators=[validate_file], required=False)
    hidden_pdf = forms.CharField(widget=forms.HiddenInput(), required=False)

    def clean(self):
        print(f"{self.__class__.__name__}::clean()")
        cleaned_data = super().clean()
        pdf_document = cleaned_data.get('pdf_document')
        hidden_pdf = cleaned_data.get('hidden_pdf')
        if pdf_document is None and hidden_pdf is not None:
            cleaned_data['pdf_document'] = hidden_pdf
            self.pdf_document = hidden_pdf
        elif pdf_document is None and hidden_pdf is None:
            raise forms.ValidationError("PDF bijlage is verplicht.")
        return cleaned_data

    def clean_entity_type(self):
        print(f"{self.__class__.__name__}::clean_entity_type()")
        value = self.cleaned_data['entity_type']
        print(f"value:{value}")
        return value


#################################################
# Form voor PV van Verdenking
#################################################
class ProcesVerbaalVerdenkingForm(PVCommonForm):
    """
    Form class representing instances of select forms listing different BOB middelen to choose from.
    """
    prefix = 'pv_verdenking'

    class Meta:
        model = ProcesVerbaalVerdenking
        fields = ('pv_nummer', 'bvh_nummer', 'naam_ovj', 'parket_nummer', 'rc_nummer',
                  'verbalisanten', 'jegens_rechtspersoon', 'jegens_persoon',
                  'toelichting', 'pdf_document', 'entity_type')
        widgets = {
            'toelichting': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'pdf_document': 'PDF Bijlage'
        }

    def __init__(self, *args, **kwargs):
        if 'prefix' in kwargs:
            self.prefix = kwargs.pop('prefix')
        super().__init__(*args, **kwargs)
        print(f"self.instance: {self.instance}")
        self.fields['verbalisanten'].help_text = "Verbalisanten  help text"
        if self.instance.pk is None:
            print(f"instance is none")
            self.fields['verbalisanten'].queryset = VerbalisantProcesVerbaal.objects.none()
        else:
            print("instance is not none")
            self.fields['verbalisanten'].queryset = self.instance.verbalisanten.all()

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.form_action = "."
        self.helper.form_id = 'pvVerdenkingFormId'
        self.helper.form_class = 'needs-validation pv-form-validate'
        self.helper.disable_csrf = True
        self.helper.attrs = {'novalidate': 'true'}
        self.helper.layout = Layout(
            Fieldset(
                'PV van verdenking',
                HTML(
                    '<p>Voeg de informatie toe zoals aangegeven op het PV van verdenking</p>'
                ),
                Row(
                    Field('pv_nummer', css_class='', wrapper_class='col-sm-6'),
                    Field('bvh_nummer', css_class='', wrapper_class='col-sm-6'),
                    css_class=''
                ),
                Row(
                    Field('naam_ovj', css_class='', wrapper_class='col-sm-6'),
                    Field('parket_nummer', css_class='', wrapper_class='col-sm-6'),
                    css_class=''
                ),
                Row(
                    Field('rc_nummer', css_class='', wrapper_class='col-sm-6'),
                    Field('toelichting', css_class='', wrapper_class='col-sm-6'),
                    css_class=''
                ),
                Row(
                    Field('pdf_document', css_class='', wrapper_class='col-sm-6'),
                    #CustomCrispyField('pdf_document', template='resources/includes/file_input.html',
                    #                  extra_context={'prefix': self.prefix})
                ),
                #VerbalisantLayout(),

                #VerbalisantForm().helper.layout,
                EntityChoiceLayout(prefix=self.prefix),

                #PersoonLayout(),

            ),
            #Submit('btn_submit_id', 'Opslaan &raquo;', css_id="id_btn_submit",
            #       css_class='btn-politie float-right btn-submit mt-3')
        )

##################################################
# PV voor Historische Gegevens
##################################################
class ProcesVerbaalHistorischeGegevensForm(PVCommonForm):

    prefix = 'pv_historische_gegevens'
    verbose_name = '126nd;  Vordering verstrekking historische financiele gegevens'

    entity_type = forms.ChoiceField(choices=ENTITY_CHOICES[:-1], label='Aanvraag richt zich op een', required=False)

    class Meta:
        model = ProcesVerbaalHistorischeGegevens
        fields = ('pv_nummer',  'bvh_nummer', 'naam_ovj', 'parket_nummer', 'rc_nummer',
                  'verbalisanten', 'jegens_rechtspersoon', 'jegens_persoon',
                  'toelichting', 'pdf_document', 'entity_type', 'jegens_verdachte', 'start_datum', 'eind_datum', 'rekeningnummer', 'financiele_instelling')
        widgets = {
            'toelichting': forms.Textarea(attrs={'rows':3}),
        }
        labels = {
            'pdf_document': 'PDF Bijlage'
        }

    start_datum = forms.DateField(
        label='Ingangsdatum van de bevrangingsperiode',
        widget=DatePickerInput(format="%d/%m/%Y"),
        input_formats=settings.DATE_INPUT_FORMATS
    )

    eind_datum = forms.DateField(
        label='Einddatum van bevragingsperiode',
        widget=DatePickerInput(format="%d/%m/%Y"),
        input_formats= settings.DATE_INPUT_FORMATS
    )


    def __init__(self, *args, **kwargs):
        verdachte_url = kwargs.pop("verdachte_url", "")
        prefix = kwargs.pop("prefix", self.prefix)

        super().__init__(*args, **kwargs)

        self.fields['verbalisanten'].help_text = "Verbalisanten  help text"
        self.fields['verbalisanten'].queryset = VerbalisantProcesVerbaal.objects.all()

        self.helper = FormHelper()
        self.helper.form_action = "."
        self.helper.form_id = 'pvhg'
        self.helper.form_class = 'needs-validation pv-form-validate'
        self.helper.disable_csrf = True
        self.helper.form_tag = False
        self.helper.attrs = {'novalidate': 'true'}
        self.helper.layout = Layout(
            Fieldset(
                '126nd;  Vordering verstrekking historische financiele gegevens',
                HTML(
                    '<p>Voeg de informatie toe zoals aangegeven op het PV van aanvraag</p>'
                ),
                Row(
                    Field('pv_nummer', css_class='', wrapper_class='col-sm-6'),
                    Field('bvh_nummer', css_class='', wrapper_class='col-sm-6'),
                    css_class=''
                ),
                Row(
                    Field('naam_ovj', css_class='', wrapper_class='col-sm-6'),
                    Field('parket_nummer', css_class='', wrapper_class='col-sm-6'),
                    css_class=''
                ),
                Row(
                    Field('rc_nummer', css_class='', wrapper_class='col-sm-6'),
                    Field('toelichting', css_class='', wrapper_class='col-sm-6'),
                    css_class=''
                ),
                Row(
                    Field('start_datum', css_class='', wrapper_class='col-sm-6'),
                    Field('eind_datum', css_class='', wrapper_class='col-sm-6'),
                    css_class=''
                ),
                Row(
                    Field('rekeningnummer', css_class='', wrapper_class='col-sm-6'),
                    Field('financiele_instelling', css_class='', wrapper_class='col-sm-6'),
                    css_class=''
                ),
                Row(
                    Field('jegens_verdachte', css_class='verdachte-input custom-select', wrapper_class='col-sm-6', data_url=verdachte_url),
                    css_class='',
                ),
                EntityChoiceLayout(prefix=self.prefix),
                PersoonLayout(),
                VerbalisantLayout(),
                Row(
                    CustomCrispyField('pdf_document', template='resources/includes/file_input.html',
                        extra_context={'prefix': self.prefix}
                    ),
                    css_class=""
                ),

            ),
            Submit('btn_submit_id', 'Opslaan &raquo;', css_id="id_btn_submit",
                   css_class='btn-politie float-right btn-submit mt-3')
        )


######################################
# PV Verdenking Multiple Form Class
######################################
class PVMultiForm(MultiModelForm):
    form_classes = {
        'pv_form': ProcesVerbaalVerdenkingForm,
        'natuurlijk_persoon': NatuurlijkPersoonForm,
        'rechtspersoon': RechtsPersoonForm,
        'verbalisant': VerbalisantForm,
    }

    def __init__(self, *args, **kwargs):
        print(f"{self.__class__.__name__}::__init__()")
        super().__init__(*args, **kwargs)

        #self.get_forms()

        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.form_class = "needs-validation pv-form-validate"
        self.helper.form_method = 'POST'
        self.helper.form_action = '.'
        self.helper.attrs = {'novalidate': 'true', 'enctype': 'multipart/form-data'}

        self.helper.layout = Layout(
        )

    #def save(self, commit=True):
    #    print(f"{self.__class__.__name__}::save()")
    #    objects = super().save(commit=False)

    #    if commit:
    #        user = objects['user']
    #        user.save()
    #        profile = objects['profile']
    #        profile.user = user
    #        profile.save()
    #        print(f"{self.__class__.__name__}::save() - profile saved.")
    #    return objects


###############################################
# PV Aanvraag Select Form
###############################################
class PVAanvraagSelectForm(forms.Form):
    form_type = forms.ChoiceField(label="Kies een BOB middel: ", widget=forms.Select(), choices=[], required=True)
    class Meta:
        fields = ('next_status',)

    def __init__(self, *args, **kwargs):
        available_forms = kwargs.pop('available_forms')
        print(f"available_forms: {available_forms}")
        super().__init__(*args, **kwargs)
        self.fields['form_type'].choices = available_forms
        self.helper = FormHelper()
        self.helper.form_class = 'inline-form'
        self.helper.form_action = "."
        self.helper.form_method = "GET"
        self.helper.form_id = 'pvAanvraagFormSelectId'
        self.helper.attrs = {'novalidate': 'true'}
        self.helper.layout = Layout(
            Row(
                Field('form_type', css_class='pv-aanvraag-form-select', wrapper_class="col-sm-6"),
               css_class='row'
            ),
        )



pv_aanvraag_forms = {
    'ProcesVerbaalHistorischeGegevens': ProcesVerbaalHistorischeGegevensForm
}
