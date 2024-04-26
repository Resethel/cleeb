# -*- coding: utf-8 -*-
"""
Apps configuration for the `thematic` application.
"""
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ThematicConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'thematic'
    verbose_name = _("Thematic")
# End class ThematicConfig