from django.shortcuts import render, redirect
from django.views.generic import  TemplateView
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.urls import reverse, reverse_lazy
from django.core.exceptions import PermissionDenied



class HomeIndex(LoginRequiredMixin, TemplateView):
    #template_name = 'home.html'

    def get(self, request):
        """
        Checks the type of user and redirects to the appropriate 
        page accordingly 
        """

        if self.request.user.is_verbalisant:
            return redirect(reverse('portal:index'))
        elif self.request.user.is_idesk_member:
            return redirect(reverse('interception:index'))
        else:
            raise PermissionDenied


