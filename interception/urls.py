from django.urls import path

from . import views


app_name = 'interception'

urlpatterns = [

    # interception handeling
    path('', views.InterceptionIndexView.as_view(), name='index'),
    path('add/', views.BOBAanvraagCreateView.as_view(), name='interception-create'),
    path('detail/<int:pk>', views.BOBAanvraagDetailView.as_view(), name='interception-detail'),
    path('edit/<int:pk>', views.BOBAanvraagUpdateView.as_view(), name='interception-edit'),
    path('delete/<int:pk>', views.BOBAanvraagDeleteView.as_view(), name='interception-delete'),



]
