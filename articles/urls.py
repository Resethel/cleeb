# -*- coding: utf-8 -*-
"""
URLs for the `article` application.
"""
from django.urls import path

from . import views

urlpatterns = [
    path('articles/', views.ArticleIndexView.as_view(), name='article-index'),
    path('article/<slug:slug>', views.ArticleView.as_view(), name='article'),
    path('article/draft/<slug:slug>', views.DraftArticleView.as_view(), name='draft-article'),
]
