from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, TemplateView, View, FormView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.detail import SingleObjectMixin
from django.contrib.auth.decorators import login_required, user_passes_test, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.core import paginator
from django.core.paginator import Paginator, PageNotAnInteger
from django_tables2 import RequestConfig, SingleTableView, SingleTableMixin
from django_filters.views import FilterView

from resources.models import BOBAanvraag
from resources.forms import BOBAanvraagForm, BOBAanvraagFilterFormHelper, BOBAanvraagStatusForm
from resources.tables import BOBAanvraagTable
from resources.filters import BOBAanvraagFilter

# Create your views here.
class PortalIndexView(LoginRequiredMixin, TemplateView):
    template_name = 'portal/index.html'



class PagedFilteredTableView(SingleTableView):
    filter_class = None
    formhelper_class = None
    context_filter_name = 'filter'

    def get_queryset(self, **kwargs):
        qs = super(PagedFilteredTableView, self).get_queryset()
        self.filter = self.filter_class(self.request.GET, queryset=qs)
        #self.filter.form.helper = self.formhelper_class()
        return self.filter.qs

    def get_table(self, **kwargs):
        table = super(PagedFilteredTableView, self).get_table()
        RequestConfig(self.request, paginate={'page': self.request.GET.get('page',1),
                                              "per_page": self.paginate_by}).configure(table)
        return table

    def get_context_data(self, **kwargs):
        context = super(PagedFilteredTableView, self).get_context_data()
        context[self.context_filter_name] = self.filter
        return context

class XBOBAanvraagListView(LoginRequiredMixin, PagedFilteredTableView):
    model = BOBAanvraag
    table_class = BOBAanvraagTable
    template_name = 'portal/bobaanvraag_list.html'
    paginate_by = 2
    filter_class = BOBAanvraagFilter

    #formhelper_class = FooFilterFormHelper



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

        #initial={'dvom_verbalisant': self.request.user.get_full_name(),
        #         'dvom_verbalisantcontactgegevens': self.request.user.email,
        #         }
        #form = self.form_class(initial=initial)
        #form.helper.form_action = reverse('portal:portal-create')
        return form

    def form_valid(self, form):
        print('form_valid()')
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()

        return redirect(self.get_success_url())
        #return super().form_valid(form)

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
        context['form'] = BOBAanvraagStatusForm(available_transitions=available_transitions)

        return context

class BOBAanvraagDetailStatusView(LoginRequiredMixin, SingleTableView, FormView):
    template_name = 'portal/bobaanvraag_detail.html'
    form_classs = BOBAanvraagStatusForm
    model = BOBAanvraag

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('portal:portal-detail', kwargs={'pk': self.object.pk})


class BOBAanvraagUpdateView(UpdateView):
    model = BOBAanvraag
    form_class = BOBAanvraagForm
    template_name = 'portal/bobaanvraag_form.html'
    success_url = reverse_lazy('portal:portal-list')


class BOBAanvraagDeleteView(DeleteView):
    model = BOBAanvraag
    template_name = 'portal/bobaanvraag_confirm_delete.html'
    success_url = reverse_lazy('portal:portal-list')


