from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

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
