# -*- coding: utf-8 -*-
"""
URLs for the `datasets` application.
"""
from django.urls import path

from datasets import views
from datasets.views import DatasetDetailView, DatasetsIndexView

urlpatterns = [
    path('jeux-de-donnees/', DatasetsIndexView.as_view(), name='datasets-index'),
    path('jeux-de-donnees/fiche/<slug:slug>/', DatasetDetailView.as_view(), name='dataset'),
    path('jeux-de-donnees/fiche/<slug:slug>/telecharger/<int:pk>', views.dataset_version_download_view, name='dataset-download'),
]