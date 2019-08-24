from django.urls import path

from . import views


app_name = 'portal'

urlpatterns = [

    # portal handeling
    path('', views.PortalIndexView.as_view(), name='index'),
    path('add/', views.BOBAanvraagCreateView.as_view(), name='portal-create'),
    path('detail/<int:pk>', views.BOBAanvraagDetailView.as_view(), name='portal-detail'),


]
