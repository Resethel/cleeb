from django.urls import path

from .views import MapDetailView, map_fullscreen_view
from .views import maps_catalog_view

urlpatterns = [
    path('cartes/', maps_catalog_view, name='interactive_maps_catalog'),
    path('cartes/<slug:slug>/', MapDetailView.as_view(), name='interactive_map_detail'),
    path('cartes/<slug:slug>/plein-ecran', map_fullscreen_view, name='map_fullscreen'),
]