from django.shortcuts import render, redirect
from django.views.generic import  TemplateView
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.urls import reverse, reverse_lazy
from django.core.exceptions import PermissionDenied


# Define groups
VERBLISANT_GROUPS       = set(['verbalisant'])
INTERCEPTIE_DESK_GROUPS = set(['interceptie_desk'])


class HomeIndex(LoginRequiredMixin, TemplateView):
    #template_name = 'home.html'

    def get(self, request):

        if self.is_verbalisant(self.request.user):
            return redirect(reverse('portal:index'))
        elif self.is_interceptie_desk(request.user):
            return redirect(reverse('interception:index'))
        else:
            raise PermissionDenied


    def is_verbalisant(self, user):
        return user.groups.filter(name__in=VERBLISANT_GROUPS).exists()

    def is_interceptie_desk(self, user):
        return user.groups.filter(name__in=INTERCEPTIE_DESK_GROUPS).exists()

