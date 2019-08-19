from django.urls import path
from django.views.generic import RedirectView

# import views from local directory
from . import views

app_name = 'portal'

urlpatterns = [

    # portal handeling
    #path('', views.PortalIndexView.as_view(), name='index'),
    path('',  RedirectView.as_view(url='list/'), name='index'),

    path('list/', views.BOBAanvraagListView.as_view(), name='portal-list'),
    path('add/', views.BOBAanvraagCreateView.as_view(), name='portal-create'),
    path('detail/<int:pk>', views.BOBAanvraagDetailView.as_view(), name='portal-detail'),
    path('edit/<int:pk>', views.BOBAanvraagUpdateView.as_view(), name='portal-edit'),
    path('delete/<int:pk>', views.BOBAanvraagDeleteView.as_view(), name='portal-delete'),

]