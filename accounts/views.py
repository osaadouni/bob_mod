from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.detail import DetailView
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.models import User

from .forms import SignUpForm, SignInForm


class UserCreateView(CreateView):
    form_class = SignUpForm
    template_name = 'accounts/signup.html'
    success_url =  reverse_lazy('home')


    def form_valid(self, form):
        valid = super().form_valid(form)
        username, password = form.cleaned_data.get('username'), form.cleaned_data.get('password1')
        new_user = authenticate(username=username, password=password)
        auth_login(self.request, new_user)
        return valid

class UserLoginView(LoginView):
    model = User
    #form_class = SignInForm
    authentication_form = SignInForm
    template_name = 'accounts/login.html'



@method_decorator(login_required, name='dispatch')
class UserUpdateView(SuccessMessageMixin, UpdateView):
    model = User
    fields = ('first_name', 'last_name', 'email', )
    template_name = 'accounts/account_edit.html'
    success_url = reverse_lazy('accounts:account_edit')
    success_message = 'Account was updated successfully!'

    def get_object(self):
        return self.request.user


@method_decorator(login_required, name='dispatch')
class UserDetailView(DetailView):
    model = User
    template_name = 'accounts/account_detail.html'

    def get_object(self):
        return self.request.user




