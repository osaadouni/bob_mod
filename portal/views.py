from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import TemplateView, DetailView, View, FormView, ListView
from django.views.generic.detail import SingleObjectMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.core import paginator
from django.core.paginator import Paginator, PageNotAnInteger
from django_tables2 import RequestConfig, SingleTableView, SingleTableMixin
from django_filters.views import FilterView



from resources.models import BOBAanvraag
from resources.forms import BOBAanvraagForm, BOBAanvraagStatusForm, BOBAanvraagFilterFormHelper
from resources.tables import BOBAanvraagTable
from resources.filters import BOBAanvraagFilter


# Create your views here.
class PortalIndexView(LoginRequiredMixin, TemplateView):
    template_name = 'portal/index.html'


class BOBAanvraagCreateView(LoginRequiredMixin,CreateView):
    model = BOBAanvraag
    template_name = 'portal/bobaanvraag_form.html'
    form_class = BOBAanvraagForm


    def get_initial(self):
        """
        Get the initial dictionary from the superclass method
        :return:
        """
        initial = super().get_initial()
        # Copy the dictionary so we don't accidently change a mutable dict
        initial = initial.copy()
        initial['dvom_verbalisant'] = self.request.user.get_full_name()
        initial['dvom_verbalisantcontactgegevens'] = self.request.user.email
        return initial

    def get_form(self, form_class=None):
        print("CreateView::get_form()")
        form = super().get_form()
        return form

    def form_valid(self, form):
        print('form_valid()')
        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        self.object.save()
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        print('form_invalid()')
        print(form.errors)
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('portal:portal-detail', args=[str(self.object.pk)])


class BOBAanvraagDetailView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        view = BOBAanvraagDetailDisplayView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = BOBAanvraagDetailStatusView.as_view()
        return view(request, *args, **kwargs)



class BOBAanvraagDetailDisplayView(LoginRequiredMixin, DetailView):
    model = BOBAanvraag
    template_name = 'portal/bobaanvraag_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fields = [field.name for field in self.object._meta.fields]
        print(fields)
        context['fields'] = fields
        self.object = self.get_object()
        available_transitions = [(t.name, t.name) for t in self.object.get_available_user_status_transitions(user=self.request.user)]
        print(self.object)
        print(available_transitions)
        if len(available_transitions) > 0:
            form = BOBAanvraagStatusForm(available_transitions=available_transitions)
            form.helper.form_action = reverse('portal:portal-detail', args=[str(self.object.pk)])
            context['form'] = form
        return context


class BOBAanvraagDetailStatusView(LoginRequiredMixin, FormView):
    template_name = 'portal/bobaanvraag_detail.html'
    form_classs = BOBAanvraagStatusForm
    model = BOBAanvraag

    def post(self, request, *args, **kwargs):
        """
        Update de aanvraag status
        :param request: HttpRequest object  containing POST parameters (eg.: next_status)
        :param args: positional arguments
        :param kwargs: keyword arguments (eg: pk)
        :return:
        """
        next_status = self.request.POST.get('next_status', None)
        pk = kwargs.get('pk', None)
        aanvraag = get_object_or_404(BOBAanvraag, pk=pk)
        self.object = aanvraag
        if next_status is not None:
            print(f"next_status: {next_status}")
            transition = getattr(aanvraag, next_status)
            print(f"transition: {transition}")
            transition()
            aanvraag.save()

            messages.add_message(request, messages.SUCCESS, 'Aanvraag is successvol ingediend.')

        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('portal:portal-detail', kwargs={'pk': self.object.pk})


class BOBAanvraagUpdateView(UpdateView):
    model = BOBAanvraag
    form_class = BOBAanvraagForm
    template_name = 'portal/bobaanvraag_form.html'

    def get_form(self, form_class=None):
        print("UpdateView::get_form()")
        form = super().get_form()
        form.helper.form_action = reverse('portal:portal-edit', kwargs={'pk': self.object.pk})
        return form

    def form_valid(self, form):
        print('UpdateView::form_valid()')
        self.object = form.save(commit=False)
        self.object.owner = self.request.user
        self.object.save()
        messages.success(self.request, 'Aanvraag is successvol geupdate.')
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('portal:portal-detail', args=[str(self.object.pk)])


class BOBAanvraagDeleteView(DeleteView):
    model = BOBAanvraag
    template_name = 'portal/bobaanvraag_confirm_delete.html'
    success_url = reverse_lazy('portal:portal-list')


class BOBAanvraagListView(LoginRequiredMixin, SingleTableView, FilterView):
    model = BOBAanvraag
    template_name = 'portal/bobaanvraag_list.html'
    table_class = BOBAanvraagTable
    context_filter_name = 'filter'


    #ordering = ['-pk']
    paginate_by = 5

    filterset_class = BOBAanvraagFilter
    formhelper_class = BOBAanvraagFilterFormHelper

    def get_queryset(self, **kwargs):
        qs = super().get_queryset()
        self.filter = self.filterset_class(self.request.GET, queryset=qs)
        self.filter.form.helper = self.formhelper_class()
        return self.filter.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        table = BOBAanvraagTable(self.get_queryset(**kwargs))
        RequestConfig(self.request, paginate={'per_page': self.paginate_by}).configure(table)
        context['object_list'] = table
        context[self.context_filter_name] = self.filter
        return context


