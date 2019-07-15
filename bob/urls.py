from django.urls import path

# import views from local directory
from . import views

app_name = 'bob'

urlpatterns = [

    # bob handeling
    path('', views.BOBApplicationListView.as_view(), name='bob-index'),
    path('add', views.BOBApplicationCreateView.as_view(), name='bob-create'),
    path('<int:pk>', views.BOBApplicationDetailView.as_view(), name='bob-detail'),
    path('edit/<int:pk>', views.BOBApplicationUpdateView.as_view(), name='bob-edit'),
    path('delete/<int:pk>', views.BOBApplicationDeleteView.as_view(), name='bob-delete'),

    # onderzoek
    path('onderzoek/', views.OnderzoekListView.as_view(), name='onderzoek-index'),
    path('onderzoek/add/', views.OnderzoekCreateView.as_view(), name='onderzoek-create'),
]