from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Maps the root URL to the home view in views.py
    path('organizations/', views.organizations_list, name='organizations_list'),
    path('organizations/<int:organization_id>/', views.organization_detail, name='organization_detail'),
]