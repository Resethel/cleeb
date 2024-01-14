import shutil
import tempfile
from pathlib import Path

from celery import shared_task

from .models import MapLayer, MapLayerStatus
from map_layers.processing import map_layers as map_layers_processing

# ======================================================================================================================
# Task to generate the map layer shapes
# ======================================================================================================================

@shared_task(name="generate_map_layers_shapes")
def generate_map_layers_shapes(map_layer_id):
    # 1. Get the map layer
    map_layer : MapLayer = MapLayer.objects.get(id=map_layer_id)

    # 2. Update the map layer status
    map_layer.status = MapLayerStatus.GENERATING
    map_layer.save()

    # 3. If there are any shapes linked to this map layer, delete them
    map_layer.shapes.all().delete()

    # 4. Gather all the properties that should be converted
    properties = None
    if map_layer.customize_properties is True:
        properties = {p.name: str(p.value) for p in map_layer.maplayercustomproperty_set.all()}


    # 4. copy the map layer dataset to the temporary folder as a zip file
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        zip_path = tmp_path / "dataset.zip"
        shutil.copy(map_layer.dataset.file.path, zip_path)

        # 4. Generate the map layer shapes
        try:
            shape_entries = map_layers_processing.generate_map_layer_database_entries(
                name=map_layer.name,
                dataset_path=zip_path,
                shapefile_name=map_layer.shapefile,
                encoding=map_layer.encoding,
                max_polygon_points=map_layer.max_polygons_points,
                max_multipolygons=map_layer.max_multipolygons_polygons,
                max_multipolygon_points=map_layer.max_multiolygons_points,
                properties=properties
            )

            # 5. Save the map layer shapes in the database
            for shape_entry in shape_entries:
                map_layer.shapes.create(
                    feature_type=shape_entry["type"],
                    geometry_type=shape_entry["geometry"]["type"],
                    geometry_coordinates=shape_entry["geometry"]["coordinates"],
                    properties=shape_entry["properties"],
                )


            # 6. Update the map layer status
            map_layer.status = MapLayerStatus.DONE
        except Exception as e:
            # 7. Update the map layer status
            print("Error generating map layer shapes: {}".format(e))
            map_layer.status = MapLayerStatus.ERROR
        finally:
            map_layer.save()
