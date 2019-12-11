from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect


class InterceptionIndexView(LoginRequiredMixin, TemplateView):
    template_name = 'interception/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        context['room_name_json'] = 'bobmod'
        return context






