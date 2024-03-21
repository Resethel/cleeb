from django.shortcuts import render
from django.views.generic import DetailView

from interactive_maps.models import Map
from thematic.models import Thematic


# ======================================================================================================================
# Vue des thèmatiques de la cartographie
# ======================================================================================================================

class MapThematicDetailView(DetailView):

    model = Thematic
    template_name = 'thematic/theme.html'
    context_object_name = 'thematic'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        self.object : Thematic
        # Get the ThematicMapText related to the ThematicMap
        maps : set[Map]   = self.object.map_set.all()
        name : str        = self.object.name
        description : str = self.object.long_desc if self.object.long_desc is not None else self.object.short_desc

        # Add the text and sections to the context
        context['thematic_name'] = name
        context['thematic_desc'] = description
        context['maps'] = maps

        return context


# ======================================================================================================================
# Vue listant les thèmes de la cartographie
# ======================================================================================================================

def thematic_list(request):
    thematics = Thematic.objects.all()
    return render(request, 'thematic/theme_catalog.html', {'thematics': thematics})

