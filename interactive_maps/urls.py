from django.urls import path

from .views import InteractiveMapDetailView

urlpatterns = [
    path('carte-interactives/<int:pk>/', InteractiveMapDetailView.as_view(), name='interactive_map_detail'),
]