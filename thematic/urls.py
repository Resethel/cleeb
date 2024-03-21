from django.urls import path
from .views import ThemeDetailView, theme_index_view

urlpatterns = [
    path('thematique/', theme_index_view, name='theme-index'),
    path('theme/<int:pk>/', ThemeDetailView.as_view(), name='theme'),
]