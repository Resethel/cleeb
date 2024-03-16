# -*- coding: utf-8 -*-
"""
URLs for the `article` application.
"""
from django.urls import path

from article import views

urlpatterns = [
    path('article/<slug:slug>', views.ArticleView.as_view(), name='article_view'),
]
