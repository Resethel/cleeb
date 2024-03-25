# -*- coding: utf-8 -*-
"""
URLs for the `interactive_maps` application.
"""
from django.urls import path

from .views import MapDetailView, map_fullscreen_view, MapIndexView, MapDraftDetailView, map_draft_fullscreen_view

urlpatterns = [
    path('cartes/', MapIndexView.as_view(), name='map-index'),
    path('carte/<slug:slug>/', MapDetailView.as_view(), name='map-detail'),
    path('carte/<slug:slug>/plein-ecran', map_fullscreen_view, name='map-detail-fullscreen'),
    path('carte/draft/<slug:slug>/', MapDraftDetailView.as_view(), name='map-draft-detail'),
    path('carte/draft/<slug:slug>/plein-ecran', map_draft_fullscreen_view, name='map-draft-detail-fullscreen')
]