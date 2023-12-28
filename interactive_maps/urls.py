from django.urls import path
from . import views
from .views import InteractiveMapDetailView

urlpatterns = [
    path('carte-interactives/<int:pk>/', InteractiveMapDetailView.as_view(), name='thematic_map_detail'),
]