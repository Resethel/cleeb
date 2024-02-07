from django.urls import path

from datasets.views import DatasetDetailView, DatasetsSearchView

urlpatterns = [
    path('jeux-de-donnees/', DatasetsSearchView.as_view(), name='datasets-search'),
    path('jeux-de-donnees/fiche/<slug:slug>/', DatasetDetailView.as_view(), name='dataset-detail'),
]