from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Maps the root URL to the home view in views.py
    path('themes/', views.themes_list, name='themes_list'),
    path('themes/<int:theme_id>/', views.theme_detail, name='theme_detail')
    # Add more paths for other views in the core app as needed
]