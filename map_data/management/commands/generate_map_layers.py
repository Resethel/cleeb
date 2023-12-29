from django.core.management.base import BaseCommand

from map_data.core.processing import cities, map_layers
from map_data.models import City, MapLayer


class Command(BaseCommand):
    help = "Regenerates the data linked to the map layers."

    def add_arguments(self, parser):

        parser.add_argument(
            "--list",
            action="store_true",
            help="List all the map layers.",
        )


        layer_or_all_group = parser.add_mutually_exclusive_group()

        layer_or_all_group.add_argument(
            "--all",
            action="store_true",
            help="Regenerate all the map layers.",
        )

        layer_or_all_group.add_argument(
            '--layer',
            nargs='+',
            type=str,
            help="Regenerate the specified map layers.",
        )
    # End def add_arguments

    def handle(self, *args, **options):

        if options["list"]:
            available_layers = map_layers.list_layers()
            self.stdout.write(self.style.SUCCESS(f"{len(available_layers)} available layers:"))
            for layer in available_layers:
                self.stdout.write(self.style.SUCCESS(f"- {layer}"))

        elif options["layer"]:
            # 1. Ensure that the layer is valid.
            for layer in options["layer"]:
                self.stdout.write(self.style.SUCCESS(f"Processing layer {layer}..."))
                try:
                    self.__handle_single_layer(layer)
                except ValueError:
                    self.stdout.write(self.style.WARNING(f"Layer {layer} does not exist... Skipping."))

        elif options["all"]:
            self.stdout.write(self.style.SUCCESS("Processing all layers..."))
            self.__handle_all_layer()

        self.stdout.write(self.style.SUCCESS("Done."))


    # ------------------------------------------------------------------------------------------------------------------
    # Private methods
    # ------------------------------------------------------------------------------------------------------------------

    def __handle_single_layer(self, layer: str):
        # 1. Ensure that the layer exists.
        available_layers = map_layers.list_layers()
        if layer not in available_layers:
            self.stdout.write(self.style.ERROR(f"Layer {layer} does not exist."))
            raise ValueError(f"Layer {layer} does not exist.")

        # 2. Remove the entry in the database for this map layer
        if MapLayer.objects.filter(name=layer).exists():
            self.stdout.write(self.style.SUCCESS(f"Deleting all entries in the database for {layer}..."))
            MapLayer.objects.filter(name=layer).delete()

        # 3. Generate the entry to be added in the database for this map layer
        self.stdout.write(self.style.SUCCESS(f"Creating entries in the database for {layer}..."))
        map_layer_entry = map_layers.generate_map_layer_entry(layer)

        # 4. Add the entry in the database for this map layer
        map_layer_instance = MapLayer.objects.create(
            name=layer,
        )
        map_layer_instance.save()
        for shape_entry in map_layer_entry:
            map_layer_instance.shape.create(
                feature_type=shape_entry["type"],
                geometry_type=shape_entry["geometry"]["type"],
                geometry_coordinates=shape_entry["geometry"]["coordinates"],
                properties=shape_entry["properties"],
            )
    # End def __handle_single_layer


    def __handle_all_layer(self):
        # 1. First, delete all the entries in the database.
        self.stdout.write(self.style.SUCCESS("Deleting all `MapLayer` entries in the database..."))
        MapLayer.objects.all().delete()

        # 2. Then, regenerate the data.
        layers_entries = map_layers.generate_all_map_layers_entries()
        for layer_name, layer_entry in layers_entries.items():
            self.stdout.write(self.style.SUCCESS(f"Creating {len(layer_entry)} entries in the database for {layer_name}..."))
            # Create the shape entry
            map_layer_instance = MapLayer.objects.create(
                name=layer_name,
            )
            map_layer_instance.save()
            for shape_entry in layer_entry:
                map_layer_instance.shape.create(
                    geometry_type=shape_entry["geometry"]["type"],
                    geometry_coordinates=shape_entry["geometry"]["coordinates"],
                    properties=shape_entry["properties"],
                )


# End class RegenerateCities