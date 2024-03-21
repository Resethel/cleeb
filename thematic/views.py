from django.shortcuts import render
from django.views.generic import DetailView

from interactive_maps.models import Map
from thematic.models import Theme


# ======================================================================================================================
# Vue des thèmatiques de la cartographie
# ======================================================================================================================

class ThemeDetailView(DetailView):

    model = Theme
    template_name = 'thematic/theme.html'
    context_object_name = 'theme'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        self.object : Theme
        # Get the ThematicMapText related to the ThematicMap
        maps : set[Map]   = self.object.map_set.all()
        name : str        = self.object.name
        description : str = self.object.long_desc if self.object.long_desc is not None else self.object.short_desc

        # Add the text and sections to the context
        context['theme_name'] = name
        context['theme_desc'] = description
        context['maps'] = maps

        return context


# ======================================================================================================================
# Vue listant les thèmes de la cartographie
# ======================================================================================================================

def theme_index_view(request):
    return render(
        request,
        'thematic/theme_index.html',
        {'themes': Theme.objects.all()}
    )
# End def theme_index_view
