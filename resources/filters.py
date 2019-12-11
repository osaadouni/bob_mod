import django_filters

from .models import BOBAanvraag

class BOBAanvraagFilter(django_filters.FilterSet):

    pv_verdenking__bvh_nummer = django_filters.CharFilter(lookup_expr='icontains')
    verbalisant = django_filters.CharFilter(lookup_expr='icontains')
    verbalisant_email = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = BOBAanvraag
        fields = ['verbalisant', 'verbalisant_email', 'pv_verdenking__bvh_nummer']