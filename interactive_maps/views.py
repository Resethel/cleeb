"""
Views for the interactive maps application.
"""
from django.views.generic import DetailView

from map_thematics.models import Thematic
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

        self.object : Map
        # Get the ThematicMapText related to the ThematicMap
        text           : Text          = self.object.text
        thematics      : set[Thematic] = self.object.thematics.all()
        authors        : set[Author]   = self.object.authors.all()
        title          : str           = self.object.title
        try:
            map_embed_html : str | None = self.object.map_render.embed_html.read().decode('utf-8')
            map_fs_url     : str | None = self.object.map_render.full_html.url
        except AttributeError:
            # If the map_render is None, then the map has not been generated yet
            map_embed_html = None
            map_fs_url     = None

        # Filter the sections related to the ThematicMapText and order them by 'order'
        sections = text.section_set.all().order_by('order')

        # Add the text and sections to the context
        context['title']           = title
        context['thematics']       = thematics
        context['sections']        = sections
        context['authors']         = authors
        context['map_embed_html']  = map_embed_html
        context['map_fs_url']      = map_fs_url

        return context
# End class InteractiveMapDetailView
