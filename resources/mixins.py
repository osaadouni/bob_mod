from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from resources.models import BOBAanvraag, VerbalisantProcesVerbaal
from resources.constants import NP_ENTITY_TYPE, RP_ENTITY_TYPE
from resources.forms import VerbalisantForm



############################################################
#  Verbalisanten mixin
############################################################
class VerbalisantMixin:
    def save_verbalisant(self, request, *args, **kwargs ):
        print(f"{self.__class__.__name__}::save_verbalisant()")
        verbalisanten = set()
        for i in range(1, 10):
            naam = request.POST.get('{}-naam-{}'.format(VerbalisantForm.prefix, i), None)
            rang = request.POST.get('{}-rang-{}'.format(VerbalisantForm.prefix, i), None)
            email = request.POST.get('{}-email-{}'.format(VerbalisantForm.prefix, i), None)
            if naam or email:
                print(f"==> verb {i}: {naam}, {rang}, {email}")
                verb = VerbalisantProcesVerbaal(naam=naam, rang=rang, email=email)
                verb.save()
                verbalisanten.add(verb)
        return verbalisanten

############################################################
#  Persoon Type mixin
############################################################
class PersoonTypeMixin:
    def save_persoon(self, request, *args, **kwargs):
        print(f"{self.__class__.__name__}::save_persoon()")
        pv = kwargs.get('pv', None)
        form = kwargs.get('form', None)
        if pv is None or form is None:
            print(f"pv is none or form is none")
            return None
        print(f"entity: {pv.entity_type}")
        if pv.entity_type == NP_ENTITY_TYPE:
            persoon_form = form['natuurlijk_persoon']
            if not persoon_form.is_valid():
                print(f"persoon_form not valid: {persoon_form.errors}")
                return JsonResponse({"error" : persoon_form.errors})
            persoon = persoon_form.save()
            pv.jegens_persoon = persoon

        elif pv.entity_type == RP_ENTITY_TYPE:
            persoon_form = form['rechtspersoon']
            if not persoon_form.is_valid():
                print(f"persoon_form not valid: {persoon_form.errors}")
                return JsonResponse({"error" : persoon_form.errors})
            persoon = persoon_form.save()
            pv.jegens_rechtspersoon = persoon
        return pv

############################################################
# PV Common Mixin
############################################################
class PVCommonMixin:

    def dispatch(self, request, *args, **kwargs):
        print(f"{self.__class__.__name__}::dispatch()")
        self.aanvraag_id = kwargs.get('aanvraag_id', None)
        self.aanvraag = get_object_or_404(BOBAanvraag, pk=self.aanvraag_id)
        print(f"==> aanvraag_id: {self.aanvraag_id}; aanvraag: {self.aanvraag}")
        return super().dispatch(request, *args, **kwargs)

    def render_to_response(self, context, **response_kwargs):
        print(f"{self.__class__.__name__}::render_to_response()")
        rendered = render_to_string(self.template_name, context, self.request)
        return JsonResponse({'html': rendered})


