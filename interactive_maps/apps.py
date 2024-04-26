# -*- coding: utf-8 -*-
"""
Apps configuration for the `interactive_maps` application.
"""
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class InteractiveMapsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'interactive_maps'
    verbose_name = _("Interactive Maps")
# End class InteractiveMapsConfig