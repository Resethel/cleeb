from django.core.management.base import BaseCommand, CommandError
from map_data.core.processing import cities
from map_data.models import City


class Command(BaseCommand):
    help = "Regenerates the data linked to the cities datasets."

    def handle(self, *args, **options):
        # First, delete all the entries in the database.
        City.objects.all().delete()

        # Then, regenerate the data.
        cities = towns.generate_database_entries()
        for city in cities:
            City.objects.create(
                name=city["name"],
                feature_type=city["type"],
                geometry_type=city["geometry_type"],
                geometry_coordinates=city["geometry_coordinates"],
                properties=city["properties"],
            )
        self.stdout.write(self.style.SUCCESS("Successfully regenerated the cities data."))
# End class RegenerateCities