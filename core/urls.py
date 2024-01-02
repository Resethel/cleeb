from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Maps the root URL to the home view in views.py
    path('organizations/', views.organizations_list, name='organizations_list'),
    path('organizations/<slug:slug>/', views.OrganizationDetailView.as_view(), name='organization_detail'),
]