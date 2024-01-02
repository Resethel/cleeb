from django.shortcuts import render

from core.models import Organization
from map_thematics.models import Thematic


# ======================================================================================================================
# Vue de la page d'accueil
# ======================================================================================================================

def home(request):
    return render(request, 'core/home.html')

# ======================================================================================================================
# Vues des acteurs de la cartographie
# ======================================================================================================================

def organizations_list(request):
    organizations = Organization.objects.all()
    return render(request, 'core/organizations_list.html', {'organizations': organizations})

def organization_detail(request, organization_id):
    organization = Organization.objects.get(id=organization_id)
    return render(request, 'organization_detail.html', {'organization': organization})
