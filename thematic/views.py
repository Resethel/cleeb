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
        context['maps'] = self.object.map_set.all()

        return context
# End class ThemeDetailView


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
