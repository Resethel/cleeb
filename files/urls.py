# -*- coding: utf-8 -*-
"""
URLs for the `files` application.
"""
from django.urls import path

from . import views

urlpatterns = [
    path('files/download/<slug:slug>', views.download_file_view, name='download')
]
