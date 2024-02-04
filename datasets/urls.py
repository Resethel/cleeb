from django.urls import path

from datasets.views import DatasetDetailView

urlpatterns = [
    path('jeux-de-donnees/fiche/<slug:slug>/', DatasetDetailView.as_view(), name='dataset-detail'),
]