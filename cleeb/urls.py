"""
URL configuration for cleeb project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.flatpages import views as flatpages_views

urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),

    # Flatpages
    path('mentions-legales/', flatpages_views.flatpage, {'url': '/mentions-legales/'}, name='mentions-legales'),
    path('donnees-personnelles/', flatpages_views.flatpage, {'url': '/donnees-personnelles/'}, name='donnees-personnelles'),
    path('conditions-d-utilisation/', flatpages_views.flatpage, {'url': '/conditions-d-utilisation/'}, name='conditions-d-utilisation'),

    # Apps
    path('', include('core.urls')),
    path('', include('interactive_maps.urls')),
    path('', include('thematic.urls')),
    path('', include('datasets.urls')),
    path('', include('articles.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
