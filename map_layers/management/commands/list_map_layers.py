# -*- coding: utf-8 -*-
"""
Commands for the map_layers app.
"""
from django.core.management import BaseCommand

from map_layers.models import MapLayer


class Command(BaseCommand):
    """A Django command to generate the map layers."""

    help = "Énumère les couches de la carte."


    def handle(self, *args, **options):
        """Handle the command."""
        # Load all the map layers from the database.
        available_layers = MapLayer.objects.all()
        self.stdout.write(self.style.SUCCESS(f"{len(available_layers)} couches disponibles:"))
        for layer in available_layers:
            self.stdout.write(self.style.SUCCESS(f"- {layer.name}"))