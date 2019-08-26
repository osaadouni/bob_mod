import django_filters
from django import forms

from .models import BOBAanvraag
from .forms import BOBAanvraagFilterForm
from .transitions import STATE_HUMAN

class BOBAanvraagFilter(django_filters.FilterSet):
    states = [(k,v) for k,v in STATE_HUMAN.items()]
    choices = [ ('', '-- Status --') ]
    choices.extend(states)
    status = django_filters.ChoiceFilter(choices=choices,required=False)

    class Meta:
        model = BOBAanvraag
        fields = ['dvom_verbalisant', 'dvom_verbalisantcontactgegevens', 'dvom_aanvraagpv', 'status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #self.filters['status'].extra['choices'] = choices
