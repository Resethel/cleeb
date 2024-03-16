# -*- coding: utf-8 -*-
"""
Views for the `article` application.
"""
from django.views.generic import DetailView

from article.models import Article


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

