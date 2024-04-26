# -*- coding: utf-8 -*-
"""
Context processors for the `core` application.
Provides context variables for all templates.
"""
from django.contrib.sites.shortcuts import get_current_site
from django.utils import translation

from cleeb import settings


def site(request):
    """
    Add site-wide context variables to the context.
    """
    return {
        'site': get_current_site(request),
    }
# End def site

def language(request):
    """
    Add language context variables to the context.
    """
    return {
        'available_languages': settings.LANGUAGES,
        'language_code': translation.get_language(),
        'language_name': dict(settings.LANGUAGES).get(translation.get_language(), ''),
    }