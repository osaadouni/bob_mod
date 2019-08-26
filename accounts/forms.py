from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column
from crispy_forms.bootstrap import PrependedText, PrependedAppendedText, AppendedText

from .models import User

class SignUpForm(UserCreationForm):
    username = forms.CharField(
        label="Gebruikersnaam",
        max_length=50,
        widget=forms.TextInput(attrs={'autofocus': True})
    )
    email = forms.EmailField(max_length=254, label='E-mail adres')

    password1 = forms.CharField(
        label="Wachtwoord",
        widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label="Bevestig Wachtwoord",
        widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')



class SignInForm(AuthenticationForm):
    username = forms.CharField(
        label="Gebruikersnaam",
        max_length=50,
        widget=forms.TextInput(attrs={'autofocus': True})
    )
    password = forms.CharField(
        label="Wachtwoord",
        max_length=100,
        widget=forms.PasswordInput
    )
    class Meta:
        model = User
        fields = ('username', 'password1')

    def __init__(self, *args, **kwargs):

        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.attrs={'novalidate':'true'}
        self.helper.form_show_labels = False
        self.helper.form_id = 'id-exampleForm'
        self.helper.form_class = 'blueForms'
        self.helper.form_method = 'post'
        self.helper.form_action = '.'
        self.helper.render_required_fields = True
        self.helper.render_hidden_fields = True
        self.helper.error_text_inline = True
        self.helper.help_text_inline = True

        self.helper.layout = Layout(
            Row(
                #Column('use'rname', css_class='form-group col mb-0'),
                Column(PrependedText('username', '<i class="fa fa-user"></i>', placeholder='username'), css_class='form-group col mb-0'),
                css_class='form-row'
            ),
            #PrependedText('username', '<i class="fa fa-user"></i>', placeholder='username'),

            Row(
                #Column('password', css_class='form-group col mb-0'),
                Column(PrependedText('password', '<i class="fa fa-lock"></i>', placeholder="Wachtwoord"), css_class='form-group col mb-0'),
                css_class='form-row'
            ),

            Submit('submit', 'Inloggen', css_class='btn btn-primary btn-block')

        )
        super().__init__(*args, **kwargs)

