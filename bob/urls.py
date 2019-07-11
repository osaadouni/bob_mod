from django.urls import path

# import views from local directory
from . import views


urlpatterns = [

    path('', views.CreateApplication.as_view(), name='index'),

]