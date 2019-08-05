"""bob_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

from .views import HomePage


urlpatterns = [
    path('admin/', admin.site.urls),
]

urlpatterns += [
    path('bob/', include('bob.urls')),
    path('', RedirectView.as_view(url='/bob/', permanent=True)),
    # HomePage.as_view(), name='home'),
]

urlpatterns += [
    path('accounts/',  include('accounts.urls')),
    #path('accounts/',  include('django.contrib.auth.urls')),
]

urlpatterns += [
    path('my_form/',  include('my_app.urls')),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
