from django.urls import path
from .views import MapThematicDetailView, thematic_list

urlpatterns = [
    path('thematiques/', thematic_list, name='thematic_list'),
    path('thematiques/<int:pk>/', MapThematicDetailView.as_view(), name='thematic_detail'),
]