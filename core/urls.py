from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Maps the root URL to the home view in views.py
    # Add more paths for other views in the core app as needed
]