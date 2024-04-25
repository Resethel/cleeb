# -*- coding: utf-8 -*-
"""
Apps configuration for the `datasets` application.
"""
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DatasetsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'datasets'
    verbose_name = _('Datasets')
