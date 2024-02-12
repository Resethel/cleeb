# -*- coding: utf-8 -*-
"""
Command to regenerate the slugs for the core application.
"""
from django.core.management.base import BaseCommand
from core.models import Person, Organization


class Command(BaseCommand):
    """Command to regenerate the slugs for the core application."""
    help = "Regenerate the slugs for the core application."

    def handle(self, *args, **options):
        """Handle the command."""
        self.stdout.write("Regenerating the slugs for the core application.")
        for person in Person.objects.all():
            person.save()

        self.stdout.write("Regenerating the slugs for the organizations.")
        for organization in Organization.objects.all():
            organization.save()

        self.stdout.write("Done.")
    # End def handle
# End class Command