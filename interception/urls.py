from django.urls import path

from . import views


app_name = 'interception'

urlpatterns = [

    path('', views.InterceptionIndexView.as_view(), name='index'),

]
