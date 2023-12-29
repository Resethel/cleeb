# -*- coding: utf-8 -*-
"""
Module to process the data from the `communes` dataset.
"""
import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import shapefile
from pyproj import Transformer

# ======================================================================================================================
# Constants
# ======================================================================================================================

# Input files
PATH = Path(__file__).parent.parent.parent / "static/datasets/communes_emm"
SHAPEFILE = "communes_emm.shp"
INPUT_EPSG_PROJECTION = "2154"  # EPSG:2154 (Lambert 93)
OUTPUT_EPSG_PROJECTION = "4326" # EPSG:4326 (WGS84)

# ======================================================================================================================
# Functions
# ======================================================================================================================

def __convert_shapefile_to_geojson() -> dict:
    """Read a shapefile and return the data as a GeoJSON-like dict.

    Args:
        file_path (str | Path): The path to the shapefile to read.

    Returns:
        dict: The data of the shapefile as a GeoJSON-like dict.
    """

    reader = shapefile.Reader(PATH / SHAPEFILE, encoding='utf-8')

    # Create a transformer to convert between the two CRS
    transformer = Transformer.from_crs(
        INPUT_EPSG_PROJECTION,
        OUTPUT_EPSG_PROJECTION,
        always_xy=True
    )

    # Extract the field names of the shapefile to update the records
    field_names = [f[0] for f in reader.fields[1:]]

    # For each shape
    features = []
    n_shapes = len(reader.shapeRecords())

    shape_record : shapefile.ShapeRecord
    for shape_record in reader.shapeRecords():
        geometry = shape_record.shape.__geo_interface__
        coordinates = []

        if geometry['type'] == "MultiPolygon":
            # Reject multi-polygons with more than 2500 polygons
            n_polys = len(geometry['coordinates'])
            if n_polys > 2500:
                print(f"Rejecting {shape_record.record} with {n_polys} polygons (limit: 2500)")
                continue

            for polygon in geometry['coordinates']:
                sub_coordinates = []
                for sub_polygon in polygon:
                    # Limit the number of points in the sub-polygon to 100.
                    # This is to reduce the size of the GeoJSON file.
                    # If the sub_polygon has more than 100 points, only keep 1 point every len(polygon) // 100 points.
                    # In this case of multi-polygons, it's important to be more restrictive on the number of points

                    if len(sub_polygon) > 100:
                        sub_polygon = sub_polygon[::len(sub_polygon) // 100]

                    sub_coordinates.append(__convert_polygon_to_geojson(sub_polygon, transformer))
                coordinates.append(sub_coordinates)

        for polygon in geometry['coordinates']:
            # Limit the number of points in the polygon to 1000.
            # This is to reduce the size of the GeoJSON file.
            # If the polygon has more than 1000 points, only keep 1 point every len(polygon) // 1000 points.
            if len(polygon) > 1000:
                polygon = polygon[::len(polygon) // 1000]
            coordinates.append(__convert_polygon_to_geojson(polygon, transformer))

        # Create the GeoJSON entry with the correct interface
        properties = dict(zip(field_names, shape_record.record))
        feature = {
            "type": "Feature",
            "geometry": {
                "type": geometry['type'],
                "coordinates": coordinates,
            },
            "properties": properties,
        }
        features.append(feature)

    return {"type": "FeatureCollection", "features": features}
# End def read_shapefile

def __convert_polygon_to_geojson(polygon: list[tuple[Any, Any]], transformer: Transformer) -> list[tuple[Any, Any]]:

    new_polygon = []
    for point in polygon:
        if not isinstance(point, Sequence):
            continue
        if len(point) != 2:
            continue
        # NOTE: point[0] is the longitude and point[1] is the latitude, which is the opposite of what we would expect.
        #       This is because the shapefile is in the CRS EPSG:2154 (Lambert 93) which is a projected CRS.
        #       The coordinates are in meters and the order is (x, y) which is (longitude, latitude).
        point_coords = transformer.transform(point[0], point[1])

        new_polygon.append(point_coords)

    return new_polygon

def generate_database_entries() -> list[dict]:

    geojson = __convert_shapefile_to_geojson()
    database_entries = list()
    # Insert the data in the database
    for feature in geojson["features"]:
        database_entries.append(
            {
                "name": feature["properties"]["nom"],
                "type": feature["type"],
                "geometry_type": feature["geometry"]["type"],
                "geometry_coordinates": json.dumps(feature["geometry"]["coordinates"]),
                "properties": json.dumps(feature["properties"]),
            }
        )

    return database_entries
# End def generate_database_entries
