# -*- coding: utf-8 -*-
"""
Views for the `thematic` application.
"""
from django.db.models import Q
from django.views.generic import DetailView, ListView

from thematic.models import Theme


# ======================================================================================================================
# Theme view
# ======================================================================================================================

class ThemeView(DetailView):

    model = Theme
    template_name = 'thematic/theme.html'
    context_object_name = 'theme'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        self.object : Theme
        context['has_maps'] = self.object.maps.exists() # TODO: Filter by published maps once the status is implemented
        context['has_articles'] =  self.object.articles.filter(status='published').exists()

        return context
# End class ThemeView


# ======================================================================================================================
# Theme Index View (Thematic view)
# ======================================================================================================================

class ThemeIndexView(ListView):
    """View for the index of the `article` application."""
    model = Theme
    template_name = "thematic/theme_index.html"
    context_object_name = "themes"
    paginate_by = 10

    def get_queryset(self):
        themes = Theme.objects.order_by('name')
        # Filter by search query
        search = self.request.GET.get('search')
        if search:
            themes = themes.filter(
                Q(name__icontains=search) |
                Q(short_name__icontains=search) |
                Q(summary__icontains=search)
            ).distinct()
        return themes
    # End def get_queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add to the context the search query
        search = self.request.GET.get('search')
        context['search'] = search if search else None
        return context
    # End def get_context_data
# End class ThemeIndexView

