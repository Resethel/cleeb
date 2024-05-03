# -*- coding: utf-8 -*-
"""
Apps configuration for the `core` application.
"""
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = _('Core')
# End class CoreConfig
