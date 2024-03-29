# -*- coding: utf-8 -*-
"""
Views for the interactive maps application.
"""
from __future__ import annotations

from bs4 import BeautifulSoup
from django import urls
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView

from common.choices import PublicationStatus
from core.models import Person
from interactive_maps.models import Map
from thematic.models import Theme


# ======================================================================================================================
# Interactive maps' index view
# ======================================================================================================================

class MapIndexView(ListView):
    """Index view for the interactive maps."""
    model = Map
    template_name = 'interactive_maps/map_index.html'
    context_object_name = 'maps'

    def get_queryset(self):
        # 1. Get the maps
        maps = Map.objects.filter(publication_status=PublicationStatus.PUBLISHED).order_by('-created_at')

        # 2. Filter by theme
        theme_slug = self.request.GET.get('theme')
        if theme_slug:
            theme = Theme.objects.filter(slug=theme_slug)
            maps = maps.filter(themes__in=theme)

        # 2. Filter by search query
        search = self.request.GET.get('search')
        if search:
            maps = maps.filter(
                Q(title__icontains=search) |
                Q(authors__firstname__icontains=search) |
                Q(authors__lastname__icontains=search)
            ).distinct()
        return maps
    # End def get_queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 1. Add to the context which theme is selected
        context['themes'] = Theme.objects.all()
        theme_slug = self.request.GET.get('theme')
        context['selected_theme'] = Theme.objects.get(slug=theme_slug) if theme_slug else None
        # Add to the context the search query
        search = self.request.GET.get('search')
        context['search'] = search if search else None
        return context
    # End def get_context_data
# End class MapIndexView

# ======================================================================================================================
# Maps detail view
# ======================================================================================================================

class MapDetailView(DetailView):
    """Detail view for the interactive maps."""
    model = Map
    template_name = 'interactive_maps/map.html'
    context_object_name = 'interactive_maps'
    queryset = Map.objects.filter(publication_status=PublicationStatus.PUBLISHED)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        self.object : Map
        # Get the ThematicMapText related to the ThematicMap
        introduction : str         = self.object.introduction
        body         : str         = self.object.body
        themes       : set[Theme]  = self.object.themes.all()
        authors      : set[Person] = self.object.authors.all()
        title        : str         = self.object.title
        try:
            map_embed_html : str | None = self.object.render.embed_html.read().decode('utf-8')
            map_fs_link    : str | None = urls.reverse('map-detail-fullscreen', kwargs={'slug': self.object.slug})
        except AttributeError:
            # If the map_render is None, then the map has not been generated yet
            map_embed_html = None
            map_fs_link     = None

        # Add the body and sections to the context
        context['title']         = title
        context['themes']        = themes
        context['created_at']    = self.object.created_at
        context['last_modified'] = self.object.last_modified
        context['authors']       = authors

        context['introduction']  = None if introduction is None else self.__format_introduction(introduction)
        context['body']          = body

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


@method_decorator(staff_member_required, name='dispatch')
class MapDraftDetailView(MapDetailView):
    queryset = Map.objects.filter(publication_status=PublicationStatus.DRAFT)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if context['map_fs_link'] is not None:
            context['map_fs_link'] = urls.reverse('map-draft-detail-fullscreen', kwargs={'slug': self.object.slug})
        return context
# End class MapDraftDetailView


# ======================================================================================================================
# Interactive maps' full screen view
# ======================================================================================================================

def map_fullscreen_view(request, slug):
    # Get the map
    map_instance = get_object_or_404(Map, slug=slug, publication_status=PublicationStatus.PUBLISHED)

    # Get the map's render
    map_render = map_instance.render

    if map_render is None or map_render.full_html is None:
        raise Http404(f"La vue plein écran de la carte '{map_instance.title}' n'est pas disponible.")

    # Return the html of the map's fullscreen view
    return FileResponse(map_render.full_html, as_attachment=False)
# End def interactive_map_fullscreen_view

@staff_member_required
def map_draft_fullscreen_view(request, slug):
    # Get the map
    map_instance = get_object_or_404(Map, slug=slug, publication_status=PublicationStatus.DRAFT)

    # Get the map's render
    map_render = map_instance.render

    if map_render is None or map_render.full_html is None:
        raise Http404(f"La vue plein écran de la carte '{map_instance.title}' n'est pas disponible.")

    # Return the html of the map's fullscreen view
    return FileResponse(map_render.full_html, as_attachment=False)
# End def interactive_map_draft_fullscreen_view
