import django_filters

from .models import BOBAanvraag

class BOBAanvraagFilter(django_filters.FilterSet):
    class Meta:
        model = BOBAanvraag
        fields = ['verbalisant', 'verbalisant_email']