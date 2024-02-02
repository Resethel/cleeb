# -*- coding: utf-8 -*-
"""
Module to process the data from the `communes` dataset.
"""
import json
from pathlib import Path

from map_data.core.processing import utils

# ======================================================================================================================
# Constants
# ======================================================================================================================

DEFAULT_INPUT_EPSG_PROJECTION = "2154"  # EPSG:2154 (Lambert 93)
DEFAULT_OUTPUT_EPSG_PROJECTION = "4326" # EPSG:4326 (WGS84)

# ======================================================================================================================
# Functions
# ======================================================================================================================

def generate_city_shape(dataset_path: Path, kv_pairs: dict[str, str], shapefile_name: str, encoding: str = "utf-8") -> dict:
    """Generate the shape of the cities dataset."""

    # 1. Generate the database entries for the cities
    geojson = utils.convert_shapefile_to_geojson(
        file_path=dataset_path,
        shapefile_name=shapefile_name,
        encoding=encoding,
        input_crs=DEFAULT_INPUT_EPSG_PROJECTION,
        output_crs=DEFAULT_OUTPUT_EPSG_PROJECTION,
        max_polygon_points = None,
        max_multipolygons = None,
        max_multipolygon_points = None,
    )

    # 2. Find the city in the geojson
    city_feature = None
    for feature in geojson["features"]:
        found = False
        for key, value in kv_pairs.items():
            if key not in feature["properties"]:
                break
            if feature["properties"][key] != value:
                break
        else:
            found = True

        if found:
            city_feature = feature
            break

    if city_feature is None:
        raise ValueError(f"Could not find a city in '{dataset_path}' with the following properties: {kv_pairs}")


    return city_feature



