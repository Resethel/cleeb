# -*- coding: utf-8 -*-
"""
Views for the `files` application.
"""
from django.http import Http404, FileResponse
from django.shortcuts import render

from files.models import File


def download_file_view(request, slug):
    """View for downloading a file.

    This view prevents the exposition of the server's file system structure.
    Returns a

    Args:
        slug (str): the slug of the file.
    Raises:
        An HTTP404 response if the file is not found.
    """
    file_object = File.objects.get(slug=slug)
    if not file_object:
        raise Http404
    file = file_object.file
    response = FileResponse(file)
    file_name = f"{file_object.slug}.{file.name.split('.')[-1]}".replace('-', '_')
    response['Content-Disposition'] = f'attachment; filename="{file_name}"'
    return response
# End def download_file_view
