from django.urls import path

# import views from local directory
from . import views

app_name = 'my_app'

urlpatterns = [

    path('', views.get_my_form, name='my-form'),
    path('submit_form/', views.get_my_form, name='submit-form'),
    path('thank_you/', views.thank_you, name='thank-you'),
]