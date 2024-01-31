from django.urls import path

from .views import InteractiveMapDetailView
from .views import interactive_maps_catalog_view

urlpatterns = [
    path('carte-interactives/', interactive_maps_catalog_view, name='interactive_maps_catalog'),
    path('carte-interactives/<slug:slug>/', InteractiveMapDetailView.as_view(), name='interactive_map_detail'),
]