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

# Input files
CITIES_PATH = Path(__file__).parent.parent.parent / "static/datasets/communes_emm.zip"
CITIES_SHAPEFILE = "Communes_emm.shp"
CITIES_INPUT_EPSG_PROJECTION = "2154"  # EPSG:2154 (Lambert 93)
CITIES_OUTPUT_EPSG_PROJECTION = "4326" # EPSG:4326 (WGS84)

EMM_LIMITS_PATH = Path(__file__).parent.parent.parent / "static/datasets/limites_emm.zip"
EMM_LIMITS_SHAPEFILE = "limites_emm.shp"
EMM_LIMITS_INPUT_EPSG_PROJECTION = "2154"  # EPSG:2154 (Lambert 93)
EMM_LIMITS_OUTPUT_EPSG_PROJECTION = "4326" # EPSG:4326 (WGS84)

# ======================================================================================================================
# Functions
# ======================================================================================================================


def generate_database_entries() -> list[dict]:

    # 1. Prepare the list of database entries
    database_entries = []

    # 2. Generate the database entries for the cities
    geojson = utils.convert_shapefile_to_geojson(
        file_path=CITIES_PATH,
        shapefile_name=CITIES_SHAPEFILE,
        encoding="utf-8",
        input_crs=CITIES_INPUT_EPSG_PROJECTION,
        output_crs=CITIES_OUTPUT_EPSG_PROJECTION
    )

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

    # 3. Generate the database entries for the EMM limits
    geojson = utils.convert_shapefile_to_geojson(
        file_path=EMM_LIMITS_PATH,
        shapefile_name=EMM_LIMITS_SHAPEFILE,
        encoding="utf-8",
        input_crs=EMM_LIMITS_INPUT_EPSG_PROJECTION,
        output_crs=EMM_LIMITS_OUTPUT_EPSG_PROJECTION
    )

    for feature in geojson["features"]:
        database_entries.append(
            {
                "name": "Limites de l'EMM",
                "type": feature["type"],
                "geometry_type": feature["geometry"]["type"],
                "geometry_coordinates": json.dumps(feature["geometry"]["coordinates"]),
                "properties": {},
            }
        )

    return database_entries
# End def generate_database_entries
