# -*- coding: utf-8 -*-
"""
Views for the `article` application.
"""
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView

from common.choices import PublicationStatus
from thematic.models import Theme
from .models import Article
from files.models import FileType


# ======================================================================================================================
# Index view
# ======================================================================================================================

class ArticleIndexView(ListView):
    """View for the index of the `article` application."""
    model = Article
    template_name = "articles/article_index.html"
    context_object_name = "articles"
    paginate_by = 10

    def get_queryset(self):
        articles = Article.objects.filter(status=PublicationStatus.PUBLISHED).order_by('-created_at')

        # 1. Filter by theme
        theme_slug = self.request.GET.get('theme')
        if theme_slug:
            theme = Theme.objects.filter(slug=theme_slug)
            articles = articles.filter(themes__in=theme)

        # 2. Filter by search query
        search = self.request.GET.get('search')
        if search:
            articles = articles.filter(
                Q(title__icontains=search) |
                Q(authors__firstname__icontains=search) |
                Q(authors__lastname__icontains=search)
            ).distinct()
        return articles
    # End def get_queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add to the context which theme
        context['themes'] = Theme.objects.all()
        theme_slug = self.request.GET.get('theme')
        context['selected_theme'] = Theme.objects.get(slug=theme_slug) if theme_slug else None
        # Add to the context the search query
        search = self.request.GET.get('search')
        context['search'] = search if search else None
        return context
    # End def get_context_data
# End class ArticleIndexView

# ======================================================================================================================
# Article view
# ======================================================================================================================

class ArticleView(DetailView):
    """View for the `Article` model."""
    object: Article
    model = Article
    template_name = "articles/article.html"
    queryset = Article.objects.filter(status=PublicationStatus.PUBLISHED)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.title
        context['authors'] = self.object.authors.all()
        context['cover_image'] = self.object.cover_image
        context['created_at'] = self.object.created_at
        context['last_modified_at'] = self.object.last_modified_at
        context['body'] = self.object.body

        # Add the downloadable attachments (pdf or file)
        context['attachments'] = None
        attachments = self.object.attachments.filter(type__in=[FileType.PDF, FileType.FILE]).order_by('slug')
        if attachments.exists():
            context['attachments'] = attachments.all()

        return context
    # End def get_context_data
# End class ArticleView

@method_decorator(staff_member_required, name='dispatch')
class DraftArticleView(ArticleView):
    """View for the `Article` model."""
    queryset = Article.objects.filter(status=PublicationStatus.DRAFT)
# End class ArticleDraftView