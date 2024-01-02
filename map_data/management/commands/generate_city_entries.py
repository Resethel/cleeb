from django.core.management.base import BaseCommand

from map_data.core.processing import cities
from map_data.models import City


class Command(BaseCommand):
    help = "Regenerates the data linked to the cities datasets."

    def handle(self, *args, **options):
        # First, delete all the entries in the database.
        self.stdout.write(self.style.SUCCESS("Deleting all entries in the database..."))
        City.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("Done."))

        # Then, regenerate the data.
        city_entries = cities.generate_database_entries()
        self.stdout.write(self.style.SUCCESS(f"Creating {len(city_entries)} entries in the database..."))
        for city_entry in city_entries:
            # Create the shape entry
            city_instance = City.objects.create(
                name=city_entry["name"],
            )
            city_instance.save()
            city_instance.shape.create(
                feature_type=city_entry["type"],
                geometry_type=city_entry["geometry_type"],
                geometry_coordinates=city_entry["geometry_coordinates"],
                properties=city_entry["properties"],
            )

        self.stdout.write(self.style.SUCCESS("Done."))
# End class RegenerateCities