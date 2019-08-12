import django_filters

from .models import BOBAanvraag

class BOBAanvraagFilter(django_filters.FilterSet):
    class Meta:
        model = BOBAanvraag
        fields = ['dvom_verbalisant', 'dvom_verbalisantcontactgegevens', 'dvom_aanvraagpv']