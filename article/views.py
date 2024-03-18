# -*- coding: utf-8 -*-
"""
Views for the `article` application.
"""
from django.db.models import Q
from django.views.generic import DetailView, ListView

from article.models import Article


# ======================================================================================================================
# Index view
# ======================================================================================================================

class ArticleIndexView(ListView):
    """View for the index of the `article` application."""
    model = Article
    template_name = "article/article_index.html"
    context_object_name = "articles"
    paginate_by = 10

    def get_queryset(self):
        articles = Article.objects.order_by('-created_at')
        # Filter by search query
        search = self.request.GET.get('search')
        if search:
            articles = articles.filter(
                Q(title__icontains=search) |
                Q(authors__firstname__icontains=search) |
                Q(authors__lastname__icontains=search)
            ).distinct()
        print(articles)
        return articles
    # End def get_queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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
    template_name = "article/article.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.object.title
        context['authors'] = self.object.authors.all()
        context['cover_image'] = self.object.cover_image
        context['created_at'] = self.object.created_at
        context['last_modified_at'] = self.object.last_modified_at
        context['body'] = self.object.body

        return context
    # End def get_context_data
# End class ArticleView

