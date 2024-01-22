# -*- coding: utf-8 -*-
"""
Commands for the map_layers app.
"""
from django.core.management import BaseCommand

from map_layers.models import MapLayer
from map_layers.models import GenerationStatus


class Command(BaseCommand):
    """A Django command to generate the map layers."""

    help = "Regénère les couches de la carte."

    def add_arguments(self, parser):

        # The command to execute
        parser.add_argument(
            "target",
            type=str,
            nargs="*",
            help="La cible de la commande. "
                 "Si omis, la commande s'applique à toutes les couches. "
                 "Plusieurs cibles peuvent être spécifiées en les séparant par des espaces."
        )


    def handle(self, *args, **options):
        """Handle the command."""
        # Check if a target was specified
        available_layers = MapLayer.objects.all()
        if not options["target"] or options["target"]is None:
            # Load all the map layers from the database.
            self.stdout.write(self.style.SUCCESS(f"{len(available_layers)} couches marquées pour regénération"))
            for layer in available_layers:
                layer.status = GenerationStatus.PENDING
                layer.save()
            self.stdout.write(self.style.SUCCESS("Done."))
            return

        for target in options["target"]:
            if target not in [layer.name for layer in available_layers]:
                self.stdout.write(self.style.ERROR(f"La couche '{target}' n'existe pas."))
                continue

            layer = MapLayer.objects.get(name=target)
            layer.status = GenerationStatus.PENDING
            layer.save()

        self.stdout.write(self.style.SUCCESS("Done."))