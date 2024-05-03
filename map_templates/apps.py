# -*- coding: utf-8 -*-
"""
Apps configuration for the `map_templates` application.
"""
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class MapTemplatesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'map_templates'
    verbose_name = _("Map Templates")
# End class MapTemplatesConfig
