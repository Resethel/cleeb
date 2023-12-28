"""
Views for the interactive maps application.
"""
from django.views.generic import DetailView

from core.models import Theme
from interactive_maps.models import Author, Map, Text

# ======================================================================================================================
# Vue pour les cartes interactives
# ======================================================================================================================

class InteractiveMapDetailView(DetailView):
    """Detail view for thematic maps."""
    model = Map
    template_name = 'interactive_maps/interactive_map.html'
    context_object_name = 'interactive_maps'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get the ThematicMapText related to the ThematicMap
        text    : Text        = self.object.text
        themes  : set[Theme]  = self.object.themes.all()
        authors : set[Author] = self.object.authors.all()
        title   : str         = self.object.title

        # Filter the sections related to the ThematicMapText and order them by 'order'
        sections = text.section_set.all().order_by('order')

        # Add the text and sections to the context
        context['title']    = title
        context['themes']   = themes
        context['sections'] = sections
        context['authors']  = authors

        return context
# End class InteractiveMapDetailView
