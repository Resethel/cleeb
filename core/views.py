from django.shortcuts import render

from core.models import Theme


# ======================================================================================================================
# Vue de la page d'accueil
# ======================================================================================================================

def home(request):
    return render(request, 'home.html')

# ======================================================================================================================
# Vues des thèmes
# ======================================================================================================================

def themes_list(request):
    themes = Theme.objects.all()
    return render(request, 'themes_list.html', {'themes': themes})

def theme_detail(request, theme_id):
    theme = Theme.objects.get(id=theme_id)
    return render(request, 'theme_detail.html', {'theme': theme})