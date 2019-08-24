from django.urls import path

from . import views


app_name = 'portal'

urlpatterns = [

    # portal handeling
    path('', views.PortalIndexView.as_view(), name='index'),

]
