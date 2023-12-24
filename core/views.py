from django.shortcuts import render

from core.models import Organization, Theme


# ======================================================================================================================
# Vue de la page d'accueil
# ======================================================================================================================

def home(request):
    return render(request, 'core/home.html')

# ======================================================================================================================
# Vues des thèmatiques de la cartographie
# ======================================================================================================================

def themes_list(request):
    themes = Theme.objects.all()
    return render(request, 'core/themes_list.html', {'themes': themes})

def theme_detail(request, theme_id):
    theme = Theme.objects.get(id=theme_id)
    return render(request, 'core/theme_detail.html', {'theme': theme})

# ======================================================================================================================
# Vues des acteurs de la cartographie
# ======================================================================================================================

def organizations_list(request):
    organizations = Organization.objects.all()
    return render(request, 'core/organizations_list.html', {'organizations': organizations})

def organization_detail(request, organization_id):
    organization = Organization.objects.get(id=organization_id)
    return render(request, 'organization_detail.html', {'organization': organization})
