import sys
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



from resources.models import BOBAanvraag, PvVerdenking, Verbalisant, RechtsPersoon, NatuurlijkPersoon, Persoon
from resources.forms import BOBAanvraagForm, BOBAanvraagStatusForm, BOBAanvraagFilterFormHelper, \
    PvVerdenkingForm, VerbalisantForm, PvMultiForm, RechtsPersoonForm, NatuurlijkPersoonForm
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
        initial['verbalisant'] = self.request.user.get_full_name()
        initial['verbalisant_email'] = self.request.user.email
        return initial

    def get_form(self, form_class=None):
        print("CreateView::get_form()")
        form = super().get_form()
        return form

    def form_valid(self, form):
        print('form_valid()')
        self.object = form.save(commit=False)
        self.object.created_by = self.request.user
        self.object.save()
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        print('form_invalid()')
        print(form.errors)
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('portal:portal-detail', args=[str(self.object.pk)])

class BOBAanvraagFormsView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        view = BOBAanvraagFormsListView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        print("BOBAanvraagFormsview::post()...")
        pass


class BOBAanvraagFormsListView(LoginRequiredMixin, View):
    model = BOBAanvraag
    template_name = 'portal/bobaanvraag_forms_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.object = self.get_object()
        form = BOBAanvraagStatusForm(available_transitions=available_transitions)
        form.helper.form_action = reverse('portal:portal-detail', args=[str(self.object.pk)])
        context['form'] = form
        return context



class BOBAanvraagDetailView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        view = BOBAanvraagDetailDisplayView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        #view = BOBAanvraagDetailStatusView.as_view()
        view = BOBAanvraagDetailFormView.as_view()
        return view(request, *args, **kwargs)



class BOBAanvraagDetailDisplayView(LoginRequiredMixin, DetailView, FormView):
    model = BOBAanvraag
    template_name = 'portal/bobaanvraag_detail.html'

    form_class = PvMultiForm

    def get(self, request, *args, **kwargs):
        print(f"{self.__class__.__name__}::get()")

        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


    def get_context_data(self, **kwargs):

        print(f"{self.__class__.__name__}::get_context_data()")
        context = super().get_context_data(**kwargs)

        # get fields
        fields = [field.name for field in self.object._meta.fields]
        print(fields)
        context['fields'] = fields

        # get PV verdenking details
        self.object = self.get_object()
        print(f"self.object: {self.object}")
        if self.object.pv_verdenking is None:
            form = PvVerdenkingForm()
        else:
            form = PvVerdenkingForm(instance=self.object.pv_verdenking)

        form.helper.form_action = reverse('portal:portal-detail', args=[str(self.object.pk)])
        context['form'] = form
        return context

        available_transitions = [(t.name, t.name) for t in self.object.get_available_user_status_transitions(user=self.request.user)]
        print(available_transitions)
        if len(available_transitions) > 0:
            form = BOBAanvraagStatusForm(available_transitions=available_transitions)
            form.helper.form_action = reverse('portal:portal-detail', args=[str(self.object.pk)])
            context['form'] = form
        return context


class BOBAanvraagDetailFormView(LoginRequiredMixin, FormView):
    template_name = 'portal/bobaanvraag_detail.html'
    form_class = BOBAanvraagStatusForm
    model = PvVerdenking

    def post(self, request, *args, **kwargs):
        """
        Update de aanvraag status
        :param request: HttpRequest object  containing POST parameters (eg.: next_status)
        :param args: positional arguments
        :param kwargs: keyword arguments (eg: pk)
        :return:
        """
        print(f"{self.__class__.__name__}::post()")
        print(f"POST: {self.request.POST}")
        pk = kwargs.get('pk', None)
        print(f"pk: {pk}")

        #next_status = self.request.POST.get('next_status', None)
        aanvraag = get_object_or_404(BOBAanvraag, pk=pk)

        verb_form = VerbalisantForm(self.request.POST, prefix='verbalisanten')
        print(verb_form)
        rp_form = RechtsPersoonForm(self.request.POST, prefix='rechtspersoon')
        print(rp_form)
        np_form = NatuurlijkPersoonForm(self.request.POST, prefix='natuurlijkpersoon')
        print(np_form)

        pv_form = PvVerdenkingForm(self.request.POST)
        print(f"\n----------\npv_form:\n{pv_form}\n---------\n")

        verb_valid = verb_form.is_valid()
        rp_valid = rp_form.is_valid()
        np_valid = np_form.is_valid()
        pv_valid = pv_form.is_valid()

        if verb_valid:
            print("verb_form is valid")
        else:
            print("verb_form is invalid")
            print(verb_form.errors)

        if rp_valid:
            print("rp_form is valid")
        else:
            print("rp_form is invalid")

        if np_valid:
            print("np_form is valid")
        else:
            print("np_form is invalid")

        if pv_valid:
            print("pv_form is valid")
        else:
            print("pv_form is invalid")
            print(pv_form.errors)

        pv_verdenking = None
        if verb_valid and np_valid and rp_valid and pv_form:
            verb = verb_form.save()
            np = np_form.save()
            rp = rp_form.save()

            pv = pv_form.save(commit=False)
            pv.rechtspersoon = rp
            pv.natuurlijkpersoon = np

            pv.save()
            pv.verbalisanten.add(verb)

            print(f"\npv: {pv}\n")
            pv_verdenking = pv

        self.object = aanvraag
        if not pv_verdenking is None:
            aanvraag.pv_verdenking = pv_verdenking
            aanvraag.save()
            messages.add_message(request, messages.SUCCESS, 'PV verdenking is successvol ingevuld.')
        else:
            print("pv verdenking is none")

        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('portal:portal-detail', kwargs={'pk': self.object.pk})



class BOBAanvraagDetailStatusView(LoginRequiredMixin, FormView):
    template_name = 'portal/bobaanvraag_detail.html'
    form_class = BOBAanvraagStatusForm
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

    def post(self, request, *args, **kwargs):
        print("UpdateView::get_form()")
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        print('UpdateView::form_valid()')
        self.object = form.save(commit=False)
        self.object.updated_by = self.request.user
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


