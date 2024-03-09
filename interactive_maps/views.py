"""
Views for the interactive maps application.
"""
from __future__ import annotations

from bs4 import BeautifulSoup
from django import urls
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.generic import DetailView

from core.models import Person
from interactive_maps.models import Map
from map_thematics.models import Thematic


# ======================================================================================================================
# Maps detail view
# ======================================================================================================================

class MapDetailView(DetailView):
    """Detail view for the interactive maps."""
    model = Map
    template_name = 'interactive_maps/map.html'
    context_object_name = 'interactive_maps'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        self.object : Map
        # Get the ThematicMapText related to the ThematicMap
        introduction   : str           = self.object.introduction
        text           : str           = self.object.text
        thematics      : set[Thematic] = self.object.thematics.all()
        authors        : set[Person]   = self.object.authors.all()
        title          : str           = self.object.title
        try:
            map_embed_html : str | None = self.object.render.embed_html.read().decode('utf-8')
            map_fs_link     : str | None = urls.reverse('map_fullscreen', kwargs={'slug': self.object.slug})
        except AttributeError:
            # If the map_render is None, then the map has not been generated yet
            map_embed_html = None
            map_fs_link     = None

        # Add the text and sections to the context
        context['title']         = title
        context['thematics']     = thematics
        context['created_at']    = self.object.created_at
        context['last_modified'] = self.object.last_modified
        context['authors']       = authors

        context['introduction']  = None if introduction is None else self.__format_introduction(introduction)
        context['sections']      = None if text is None else self.__split_text_sections(text)

        context['map_embed']     = map_embed_html
        context['map_fs_link']   = map_fs_link

        return context
    # End def get_context_data

    # ==================================================================================================================
    # Private methods
    # ==================================================================================================================

    @staticmethod
    def __format_introduction(introduction: str) -> str | None:
        """Format the introduction."""
        soup = BeautifulSoup(introduction, 'html.parser')

        # Remove unwrap unnecessary tags (<article>, <section>, <h1>, <h2>, <h3>, <h4>, <h5>, <h6>)
        for tag in soup.find_all(['article', 'section', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            tag.unwrap()

        # Check if the introduction is empty
        if soup.text == '':
            return None

        # Wrap the introduction in a <p> tag if it is not already wrapped
        if soup.p is None:
            soup.string.wrap(soup.new_tag('p'))

        return soup.decode_contents()

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
# End class MapDetailView

# ======================================================================================================================
# Interactive maps' full screen view
# ======================================================================================================================

def map_fullscreen_view(request, slug):
    # Get the map
    map_instance = get_object_or_404(Map, slug=slug)

    # Get the map's render
    map_render = map_instance.render

    if map_render is None or map_render.full_html is None:
        raise Http404(f"La vue plein écran de la carte '{map_instance.title}' n'est pas disponible.")

    # Return the html of the map's full screen view
    return FileResponse(map_render.full_html, as_attachment=False)
# End def interactive_map_fullscreen_view

# ======================================================================================================================
# Interactive maps' catalog view
# ======================================================================================================================

def maps_catalog_view(request):
    # List all the available maps
    map_objects  = Map.objects.all()


    context = []
    for m in map_objects:
        sub_context = {}
        sub_context['title']         = m.title
        sub_context['thematics']     = m.thematics.all()
        sub_context['created_at']    = m.created_at
        sub_context['last_modified'] = m.last_modified
        sub_context['authors']       = m.authors
        context.append(context)

    return render(request, 'interactive_maps/map_catalog.html', context={'maps' : map_objects})
