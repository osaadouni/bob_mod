from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect


class InterceptionIndexView(LoginRequiredMixin, TemplateView):
    template_name = 'interception/index.html'

