# -*- coding: utf-8 -*-
"""
Enumerations and choices used in the `map_layers` application.
"""
from django.db import models

class GenerationStatus(models.TextChoices):
    """Status of a map layer's geometry generation."""
    PENDING = "PENDING", "En attente"
    RUNNING = "RUNNING", "En cours"
    COMPLETED = "COMPLETED", "Terminé"
    FAILED = "FAILED", "Échoué"
# End class GenerationStatus