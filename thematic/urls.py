# -*- coding: utf-8 -*-
"""
URLs for the `thematic` application.
"""
from django.urls import path
from .views import ThemeView, ThemeIndexView

urlpatterns = [
    path('thematique/', ThemeIndexView.as_view(), name='theme-index'),
    path('theme/<slug:slug>/', ThemeView.as_view(), name='theme'),
]