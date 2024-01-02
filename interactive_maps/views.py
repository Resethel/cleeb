"""
Views for the interactive maps application.
"""
from __future__ import annotations

from django.views.generic import DetailView

from map_thematics.models import Thematic
from interactive_maps.models import Author, Map
from bs4 import BeautifulSoup

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
        text           : str           = self.object.text
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

        # Add the text and sections to the context
        context['title']           = title
        context['thematics']       = thematics
        context['sections']        = None if text is None else self.__split_text_sections(text)
        context['authors']         = authors
        context['map_embed_html']  = map_embed_html
        context['map_fs_url']      = map_fs_url

        return context

    @staticmethod
    def __split_text_sections(text: str) -> list | None:
        """Split the text into sections."""
        soup = BeautifulSoup(text, 'html.parser')

        sections = []
        for section in soup.find_all('section'):
            # Get the content of the section.
            # The section tag is removed from the content as it is handled by the template.
            section_content = section.decode_contents()

            sections.append(section_content)

        return sections


    # End def __split_text_sections
# End class InteractiveMapDetailView



