import sys
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import TemplateView, DetailView, View, FormView, ListView
from django.views.generic.detail import SingleObjectMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy, resolve
from django.contrib import messages
from django.core import paginator
from django.core.paginator import Paginator, PageNotAnInteger
from django_tables2 import RequestConfig, SingleTableView, SingleTableMixin
from django_filters.views import FilterView
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.template import RequestContext
from django_fsm import TransitionNotAllowed

from resources.models import BOBAanvraag, ProcesVerbaalVerdenking, ProcesVerbaalHistorischeGegevens, ProcesVerbaalAanvraag, \
    VerbalisantProcesVerbaal, RechtsPersoonProcesVerbaal, NatuurlijkPersoonProcesVerbaal
from resources.forms import BOBAanvraagForm, BOBAanvraagStatusForm, BOBAanvraagFilterFormHelper, \
    ProcesVerbaalVerdenkingForm, VerbalisantForm, PVMultiForm, RechtsPersoonForm, NatuurlijkPersoonForm, \
    ProcesVerbaalHistorischeGegevensForm, PVAanvraagSelectForm,pv_aanvraag_forms
from resources.tables import BOBAanvraagTable
from resources.filters import BOBAanvraagFilter
from resources.constants import NP_ENTITY_TYPE, RP_ENTITY_TYPE, ENTITY_CHOICES
from resources.mixins import PVCommonMixin, VerbalisantMixin, PersoonTypeMixin


# Base Class
class BaseClassView(LoginRequiredMixin, View):
    app_name = None

    def dispatch(self, request, *args, **kwargs):
        print(f"{self.__class__.__name__}::dispatch()")
        self.app_name = resolve(request.path).app_name
        return super().dispatch(request, *args, **kwargs)


####################################
# Portal Index View
####################################
class PortalIndexView(LoginRequiredMixin, TemplateView):
    template_name = 'portal/index.html'


####################################
# BOB Aanvraag Views
####################################
# List aanvraag
class BOBAanvraagListView(BaseClassView, SingleTableView, FilterView):
    model = BOBAanvraag
    table_class = BOBAanvraagTable
    context_filter_name = 'filter'

    paginate_by = 5

    filterset_class = BOBAanvraagFilter
    formhelper_class = BOBAanvraagFilterFormHelper

    def get_queryset(self, **kwargs):
        qs = super().get_queryset()
        self.filter = self.filterset_class(self.request.GET, queryset=qs)
        self.filter.form.helper = self.formhelper_class()
        return self.filter.qs

    def get_template_names(self):
        return ['{}/bobaanvraag_list.html'.format(self.app_name)]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(f"{self.__class__.__name__}::get_context_data()")
        print(f"app_name:{self.app_name}")
        table = BOBAanvraagTable(self.get_queryset(**kwargs))
        RequestConfig(self.request, paginate={'per_page': self.paginate_by}).configure(table)
        context['object_list'] = table
        context[self.context_filter_name] = self.filter
        return context


# Create new aanvraag
class BOBAanvraagCreateView(BaseClassView, CreateView):
    model = BOBAanvraag
    template_name = None
    form_class = BOBAanvraagForm

    def get_template_names(self):
        return ['{}/bobaanvraag_form.html'.format(self.app_name)]

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
        return reverse_lazy('{}:{}-detail'.format(self.app_name, self.app_name), args=[str(self.object.pk)])


# BOB Aanvraag detail view
class BOBAanvraagDetailView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        view = BOBAanvraagDetailDisplayView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = BOBAanvraagDetailStatusView.as_view()
        #view = BOBAanvraagDetailFormView.as_view()
        return view(request, *args, **kwargs)



# BOB aanvraag detail view
class BOBAanvraagDetailDisplayView(BaseClassView, DetailView, FormView):
    model = BOBAanvraag
    form_class = PVMultiForm

    def get_template_names(self):
        return ['{}/bobaanvraag_detail.html'.format(self.app_name)]

    def get(self, request, *args, **kwargs):
        print(f"{self.__class__.__name__}::get()")

        self.object = self.get_object()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


    def get_context_data(self, **kwargs):

        print(f"{self.__class__.__name__}::get_context_data()")
        context = super().get_context_data(**kwargs)

        # set object
        self.object = self.get_object()
        print(f"self.object: {self.object}")

        # get fields
        fields = [{'name': field.name, 'label': field.verbose_name, 'value': field.value_from_object(self.object)} for field in self.object._meta.get_fields()]
        # fields = [field.name for field in self.object._meta.get_fields()]
        print(fields)
        context['fields'] = fields

        # check if PV verdenking exists
        pvv_url = None
        pva_url = None
        if self.object.pv_verdenking is not None:
            pvv_url = reverse('{}:{}-pvv-detail'.format(self.app_name, self.app_name), args=[str(self.object.pk), str(self.object.pv_verdenking.pk)])
        else:
            pvv_url = reverse('{}:{}-pvv-create'.format(self.app_name, self.app_name), args=[str(self.object.pk)])

        if self.object.pv_aanvraag is not None:
            pva_url = reverse('{}:{}-pva-detail'.format(self.app_name, self.app_name), args=[str(self.object.pk), str(self.object.pv_aanvraag.pk)])
        else:
            pva_url = reverse('{}:{}-pva-select'.format(self.app_name, self.app_name), args=[str(self.object.pk)])

        context['pvv_url'] = pvv_url
        context['pva_url'] = pva_url
        return context


class BOBAanvraagDetailStatusView(LoginRequiredMixin, FormView):
    template_name = 'portal/bobaanvraag_detail.html'
    form_class = BOBAanvraagStatusForm
    model = BOBAanvraag

    def dispatch(self, request, *args, **kwargs):
        print(f"{self.__class__.__name__}::dispatch()")
        print(f"kwargs: {self.kwargs}")
        print(f"self.request.POST: {self.request.POST}")
        self.pk = kwargs.get('pk', None)
        self.object = get_object_or_404(BOBAanvraag, pk=self.pk)
        print(f"==> pk: {self.pk}; self.object: {self.object}")
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Update de aanvraag status
        :param request: HttpRequest object  containing POST parameters (eg.: next_status)
        :param args: positional arguments
        :param kwargs: keyword arguments (eg: pk)
        :return:
        """
        print(f"{self.__class__.__name__}::post()")
        next_status = self.request.POST.get('next_status', None)
        print(f"==> pk: {self.pk}; self.object: {self.object}")
        print(f"next_status: {next_status}")
        if next_status is not None:
            transition = getattr(self.object, next_status)
            print(f"transition: {transition}")
            try:
                transition()
            except TransitionNotAllowed:
                print(f"Transition not allowed")
                sys.exit()

            self.object.save()
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



##########################################################
# PV verdenking Views
############################################################
class PvVerdenkingCreateView(BaseClassView, PVCommonMixin, VerbalisantMixin, PersoonTypeMixin,  CreateView):
    """
    View Class for creating an new instance of a PV van verdenking.
    """
    form_class = PVMultiForm

    def get_template_names(self):
        return ['{}/pv_verdenking_form.html'.format(self.app_name)]

    def get_context_data(self, **kwargs):
        print(f"{self.__class__.__name__}::get_context_data()")
        context = super().get_context_data(**kwargs)
        context['aanvraag_id'] = self.aanvraag_id
        context['aanvraag'] = self.aanvraag

        # set object
        form = self.form_class()
        form.helper.form_action = reverse('{}:{}-pvv-create'.format(self.app_name, self.app_name), args=[str(self.aanvraag_id)])
        context['form'] = form
        return context

    def post(self, request, *args, **kwargs):
        """
        Update de aanvraag status
        :param request: HttpRequest object  containing POST parameters (eg.: next_status)
        :param args: positional arguments
        :param kwargs: keyword arguments (eg: pk)
        :return:
        """
        print(f"{self.__class__.__name__}::post()")
        form = self.form_class(self.request.POST, self.request.FILES)
        pv_form = form['verdenking']
        pv_valid = pv_form.is_valid()
        print(f"pv_valid: {pv_valid}")
        if not pv_valid:
            print(f"pv_form is invalid: {pv_form.errors}")
            return JsonResponse({'error': 'PV form is not valid'})

        # save pv without commit
        pv = pv_form.save(commit=False)

        # save persoon type
        pv = self.save_persoon(request, pv=pv, form=form)
        pv.save()

        # save verbalisanten
        verbalisanten = self.save_verbalisant(request)
        pv.verbalisanten.set(verbalisanten)

        # add object
        self.object = pv

        # assign pv verdenking to aanvraag
        self.aanvraag.pv_verdenking = pv
        self.aanvraag.save()

        print("Done")
        return redirect(self.get_success_url())

    def render_to_response(self, context, **response_kwargs):
        print(f"{self.__class__.__name__}::render_to_response()")
        rendered = render_to_string(self.template_name, context, self.request)
        return JsonResponse({'html': rendered})

    def get_success_url(self):
        return reverse('{}:{}-pvv-detail'.format(self.app_name, self.app_name), kwargs={'aanvraag_id': self.aanvraag_id, 'pk': self.object.pk})


# PV Verdenking detail view
class PvVerdenkingDetailView(BaseClassView, DetailView):
    """
    View Class for displaying detail of an instance of PV van verdenking.
    """
    form_class = ProcesVerbaalVerdenkingForm
    model = ProcesVerbaalVerdenking
    template_name = 'portal/pv_verdenking_detail.html'

    def get_context_data(self, **kwargs):
        print(f"{self.__class__.__name__}::get_context_data()")
        context = super().get_context_data(**kwargs)

        # set object
        self.object = self.get_object()
        print(f"self.object: {self.object}")

        # get fields
        fields = [{'name': field.name, 'label': field.verbose_name, 'value': field.value_from_object(self.object)}
                  for field in self.object._meta.get_fields() if not field.is_relation]
        print(fields)
        context['fields'] = fields
        return context

    def render_to_response(self, context, **response_kwargs):
        print(f"{self.__class__.__name__}::render_to_response()")
        rendered = render_to_string(self.template_name, context, self.request)
        return JsonResponse({'html': rendered})


# PV verdenking Update View
class PvVerdenkingUpdateView(BaseClassView, PVCommonMixin, VerbalisantMixin, PersoonTypeMixin,  UpdateView):
    """
    View class for updating an instance of PV van verdenking.
    """
    form_class = PVMultiForm

    def get_template_names(self):
        return ['{}/pv_verdenking_form.html'.format(self.app_name)]

    def get_context_data(self, **kwargs):
        print(f"{self.__class__.__name__}::get_context_data()")
        context = super().get_context_data(**kwargs)
        context['aanvraag_id'] = self.aanvraag_id
        context['aanvraag'] = self.aanvraag

        # set object
        form = self.form_class()
        form.helper.form_action = reverse('{}:{}-pvv-create'.format(self.app_name), args=[str(self.aanvraag_id)])
        context['form'] = form
        return context

    def post(self, request, *args, **kwargs):
        """
        Update de aanvraag status
        :param request: HttpRequest object  containing POST parameters (eg.: next_status)
        :param args: positional arguments
        :param kwargs: keyword arguments (eg: pk)
        :return:
        """
        print(f"{self.__class__.__name__}::post()")
        form = self.form_class(self.request.POST, self.request.FILES)
        pv_form = form['verdenking']
        pv_valid = pv_form.is_valid()
        print(f"pv_valid: {pv_valid}")
        if not pv_valid:
            print(f"pv_form is invalid: {pv_form.errors}")
            return JsonResponse({'error': 'PV form is not valid'})

        # save pv without commit
        pv = pv_form.save(commit=False)

        # save persoon type
        pv = self.save_persoon(request, pv=pv, form=form)
        pv.save()

        # save verbalisanten
        verbalisanten = self.save_verbalisant(request)
        pv.verbalisanten.set(verbalisanten)

        # add object
        self.object = pv

        # assign pv verdenking to aanvraag
        self.aanvraag.pv_verdenking = pv
        self.aanvraag.save()

        print("Done")
        return redirect(self.get_success_url())

    def render_to_response(self, context, **response_kwargs):
        print(f"{self.__class__.__name__}::render_to_response()")
        rendered = render_to_string(self.template_name, context, self.request)
        return JsonResponse({'html': rendered})

    def get_success_url(self):
        return reverse('{}:{}-pvv-detail'.format(self.app_name, self.app_name), kwargs={'aanvraag_id': self.aanvraag_id, 'pk': self.object.pk})


####################################
# END Views PV van verdenking
####################################

####################################
# Select PV Aanvraag View
####################################
class PVAanvraagSelectView(BaseClassView, PVCommonMixin,  TemplateView):
    template_name = 'portal/pv_aanvraag_select.html'
    form_class = PVAanvraagSelectForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(f"self.aanvraag_id: {self.aanvraag_id}")
        available_forms = [('', '-- selecteer --')]
        available_forms.extend([(cls.__name__, cls.__name__) for cls in ProcesVerbaalAanvraag.__subclasses__()])
        form = self.form_class(available_forms=available_forms)
        form.helper.form_action = reverse('{}:{}-pva-create'.format(self.app_name, self.app_name), args=[str(self.aanvraag_id), '-1'])
        context['form'] = form
        return context

    def render_to_response(self, context, **response_kwargs):
        print(f"{self.__class__.__name__}::render_to_response()")
        rendered = render_to_string(self.template_name, context, self.request)
        return JsonResponse({'html': rendered})


##########################################################
# PV Aanvraag Views
############################################################
class PVAanvraagCreateView(BaseClassView, PVCommonMixin, VerbalisantMixin, PersoonTypeMixin,  CreateView):
    """
    View Class for creating an new instance of a PV van verdenking.
    """
    form_class = PVMultiForm
    template_name = 'portal/pv_verdenking_form.html'

    def get_context_data(self, **kwargs):
        print(f"{self.__class__.__name__}::get_context_data()")
        context = super().get_context_data(**kwargs)

        self.middel = self.kwargs.get('middel', '-1')
        context['aanvraag_id'] = self.aanvraag_id
        context['aanvraag'] = self.aanvraag

        print(f"middel: {self.middel}")

        # set object
        pv_form = pv_aanvraag_forms.get(self.middel, None)
        self.form_class.form_classes['pv_form'] = pv_form
        form = self.form_class()
        form.helper.form_action = reverse('{}:{}-pva-create'.format(self.app_name, self.app_name), args=[str(self.aanvraag_id), self.middel])
        context['form'] = form
        return context

    def post(self, request, *args, **kwargs):
        """
        Update de aanvraag status
        :param request: HttpRequest object  containing POST parameters (eg.: next_status)
        :param args: positional arguments
        :param kwargs: keyword arguments (eg: pk)
        :return:
        """
        print(f"{self.__class__.__name__}::post()")
        form = self.form_class(self.request.POST, self.request.FILES)
        pv_form = form['pv_form']
        pv_valid = pv_form.is_valid()
        print(f"pv_valid: {pv_valid}")
        if not pv_valid:
            print(f"pv_form is invalid: {pv_form.errors}")
            return JsonResponse({'error': 'PV form is not valid'})

        # save pv without commit
        pv = pv_form.save(commit=False)

        # save persoon type
        pv = self.save_persoon(request, pv=pv, form=form)
        pv.save()

        # save verbalisanten
        verbalisanten = self.save_verbalisant(request)
        pv.verbalisanten.set(verbalisanten)

        # add object
        self.object = pv

        # assign pv verdenking to aanvraag
        self.aanvraag.pv_verdenking = pv
        self.aanvraag.save()

        print("Done")
        return redirect(self.get_success_url())

    def render_to_response(self, context, **response_kwargs):
        print(f"{self.__class__.__name__}::render_to_response()")
        rendered = render_to_string(self.template_name, context, self.request)
        return JsonResponse({'html': rendered})

    def get_success_url(self):
        return reverse('{}:{}-pvv-detail'.format(self.app_name, self.app_name), kwargs={'aanvraag_id': self.aanvraag_id, 'pk': self.object.pk})


# PV Aanvraag detail view
class PVAanvraagDetailView(BaseClassView, DetailView):
    """
    View Class for displaying detail of an instance of PV van verdenking.
    """
    form_class = ProcesVerbaalVerdenkingForm
    model = ProcesVerbaalVerdenking
    template_name = 'portal/pv_verdenking_detail.html'

    def get_context_data(self, **kwargs):
        print(f"{self.__class__.__name__}::get_context_data()")
        context = super().get_context_data(**kwargs)

        # set object
        self.object = self.get_object()
        print(f"self.object: {self.object}")

        # get fields
        fields = [{'name': field.name, 'label': field.verbose_name, 'value': field.value_from_object(self.object)}
                  for field in self.object._meta.get_fields() if not field.is_relation]
        print(fields)
        context['fields'] = fields
        return context

    def render_to_response(self, context, **response_kwargs):
        print(f"{self.__class__.__name__}::render_to_response()")
        rendered = render_to_string(self.template_name, context, self.request)
        return JsonResponse({'html': rendered})


# PV verdenking Update View
class PVAanvraagUpdateView(BaseClassView, PVCommonMixin, VerbalisantMixin, PersoonTypeMixin,  UpdateView):
    """
    View class for updating an instance of PV van verdenking.
    """
    form_class = PVMultiForm

    def get_template_names(self):
        return ['{}/pv_verdenking_form.html'.format(self.app_name)]

    def get_context_data(self, **kwargs):
        print(f"{self.__class__.__name__}::get_context_data()")
        context = super().get_context_data(**kwargs)
        context['aanvraag_id'] = self.aanvraag_id
        context['aanvraag'] = self.aanvraag

        # set object
        form = self.form_class()
        form.helper.form_action = reverse('{}:{}-pvv-create'.format(self.app_name), args=[str(self.aanvraag_id)])
        context['form'] = form
        return context

    def post(self, request, *args, **kwargs):
        """
        Update de aanvraag status
        :param request: HttpRequest object  containing POST parameters (eg.: next_status)
        :param args: positional arguments
        :param kwargs: keyword arguments (eg: pk)
        :return:
        """
        print(f"{self.__class__.__name__}::post()")
        form = self.form_class(self.request.POST, self.request.FILES)
        pv_form = form['pv_form']
        pv_valid = pv_form.is_valid()
        print(f"pv_valid: {pv_valid}")
        if not pv_valid:
            print(f"pv_form is invalid: {pv_form.errors}")
            return JsonResponse({'error': 'PV form is not valid'})

        # save pv without commit
        pv = pv_form.save(commit=False)

        # save persoon type
        pv = self.save_persoon(request, pv=pv, form=form)
        pv.save()

        # save verbalisanten
        verbalisanten = self.save_verbalisant(request)
        pv.verbalisanten.set(verbalisanten)

        # add object
        self.object = pv

        # assign pv verdenking to aanvraag
        self.aanvraag.pv_verdenking = pv
        self.aanvraag.save()

        print("Done")
        return redirect(self.get_success_url())

    def render_to_response(self, context, **response_kwargs):
        print(f"{self.__class__.__name__}::render_to_response()")
        rendered = render_to_string(self.template_name, context, self.request)
        return JsonResponse({'html': rendered})

    def get_success_url(self):
        return reverse('{}:{}-pvv-detail'.format(self.app_name, self.app_name), kwargs={'aanvraag_id': self.aanvraag_id, 'pk': self.object.pk})


####################################
# END Views PV van aanvraag
####################################

################################################
# JSON response mixin
################################################
class JSONResponseMixin:
    """
    A mixin that can be used to render a JSON response.
    """
    def render_to_json_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        return JsonResponse(
            self.get_data(context),
            **response_kwargs
        )

    def get_data(self, context):
        """
        Returns an object that will be serialized as JSON by json.dumps().
        """
        # Note: This is *EXTREMELY* naive; in reality, you'll need
        # to do much more complex handling to ensure that arbitrary
        # objects -- such as Django model instances or querysets
        # -- can be serialized as JSON.
        return context

################################################
# VERBALISANT VIEWS                            #
################################################
class VerbalisantCreateView(JSONResponseMixin, CreateView):
    template_name = 'resources/verbalisant_part.html'
    form_class = VerbalisantForm

    def get_context_data(self, **kwargs):
        print(f"{self.__class__.__name__}::get_context_data()")
        context = super().get_context_data(**kwargs)
        row_index = self.request.GET.get('row_index', 1)
        print(f"{self.__class__.__name__}::row_index: {row_index}")

        form = self.form_class()
        context['index'] = row_index
        context['prefix'] = form.prefix
        return context

    def render_to_response(self, context, **response_kwargs):
        print(f"{self.__class__.__name__}::render_to_response()")
        rendered = render_to_string(self.template_name, context, self.request)
        return JsonResponse({'html': rendered})
