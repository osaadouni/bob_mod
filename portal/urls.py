from django.urls import path
from django.views.generic import RedirectView

from . import views


app_name = 'portal'

urlpatterns = [

    # portal handeling
    #path('', views.PortalIndexView.as_view(), name='index'),
    path('',  RedirectView.as_view(url='list/'), name='index'),
    path('add/', views.BOBAanvraagCreateView.as_view(), name='portal-create'),
    path('detail/<int:pk>', views.BOBAanvraagDetailView.as_view(), name='portal-detail'),
    path('forms/<int:pk>', views.BOBAanvraagFormsView.as_view(), name='portal-forms'),
    path('edit/<int:pk>', views.BOBAanvraagUpdateView.as_view(), name='portal-edit'),
    path('delete/<int:pk>', views.BOBAanvraagDeleteView.as_view(), name='portal-delete'),
    path('list/', views.BOBAanvraagListView.as_view(), name='portal-list'),


    # PV verdenking
    path('detail/<int:aanvraag_id>/pvv/add', views.PvVerdenkingCreateView.as_view(), name='portal-pvv-create'),
    path('detail/<int:aanvraag_id>/pvv/detail/<int:pk>', views.PvVerdenkingDetailView.as_view(), name='portal-pvv-detail'),
    # verbalisant
    path('verbalisant/add', views.VerbalisantCreateView.as_view(), name='verbalisant-create'),

]
