# -*- coding: utf-8 -*-
"""
Module to preprocess the data from the ZNIEFF (Zone naturelle d'intérêt écologique, faunistique et floristique) dataset.
"""
from __future__ import annotations

import json
from pathlib import Path

from map_data.core.processing import utils

# ======================================================================================================================
# Constants
# ======================================================================================================================

METZ_LOCATION = (49.119309, 6.175716)
FILTER_LAT = 0.20
FILTER_LON = 0.20

INPUT_EPSG_PROJECTION = "2154"  # EPSG:2154 (Lambert 93)
OUTPUT_EPSG_PROJECTION = "4326" # EPSG:4326 (WGS84)

# ======================================================================================================================
# Functions
# ======================================================================================================================

def __filter_data(data: dict, center : tuple[float, float], filter_lat : float, filter_lon : float) -> dict:
    """Filter the data to only include the data in the filter area.

    The filter area is a square centered on the center point and of size filter_lat x filter_lon.
    Any shape that intersects this square is included in the filtered data.
    """

    output = {"type": "FeatureCollection", "features": []}

    lat_min = center[0] - filter_lat
    lon_min = center[1] - filter_lon
    lat_max = center[0] + filter_lat
    lon_max = center[1] + filter_lon

    def match_polygon(polygon):
        for point in polygon:
            if lat_min <= point[1] <= lat_max and lon_min <= point[0] <= lon_max:
                return True
        return False

    # For each feature
    for feature in data["features"]:
        # For each polygon in the feature
        match = False

        if feature["geometry"]["type"] == "MultiPolygon":
            for polygon in feature["geometry"]["coordinates"]:
                for sub_polygon in polygon:
                    if match_polygon(sub_polygon):
                        match = True
                        break
                if match:
                    break
        else:
            for polygon in feature["geometry"]["coordinates"]:
                if match_polygon(polygon):
                    match = True
                    break

        if match:
            output["features"].append(feature)
    return output
# End def filter_data

# ======================================================================================================================
# Public functions
# ======================================================================================================================

def list_layers() -> list[str]:
    """List all the datasets that can be used in the map."""
    return [layer["name"] for layer in LAYERS]
# End def list_datasets

def generate_map_layer_database_entries(
        name : str,
        dataset_path : Path | str,
        shapefile_name : str,
        encoding : str = "utf-8",
        input_crs : str = INPUT_EPSG_PROJECTION,
        output_crs : str = OUTPUT_EPSG_PROJECTION,
        max_polygon_points : int | None = None,
        max_multipolygons : int | None = None,
        max_multipolygon_points : int | None = None,
        convert_properties: bool = True,
        properties: dict[str, str] | None = None,
) -> list[dict]:

    print(f"Generating map layer entry for '{name}'...")

    # 1. Convert the dataset path to a Path object
    dataset_path = Path(dataset_path)

    # 2. Find the dataset in the static folder
    if not dataset_path.exists():
        raise FileNotFoundError(f"No dataset found at '{dataset_path}'.")

    # 3. Read the shapefile
    print("Reading shapefile...")
    geojson = utils.convert_shapefile_to_geojson(
        file_path=dataset_path,
        shapefile_name=shapefile_name,
        encoding=encoding,
        input_crs=input_crs,
        output_crs=output_crs,
        max_polygon_points=max_polygon_points,
        max_multipolygons=max_multipolygons,
        max_multipolygon_points=max_multipolygon_points,
    )

    # 4. Filter the data to only include the data in the filter area.
    print("Filtering data...")
    geojson = __filter_data(geojson, METZ_LOCATION, FILTER_LAT, FILTER_LON)

    # 5. Convert the properties if needed
    if convert_properties:
        print("Converting properties...")
        for feature in geojson["features"]:
            if properties is None:
                continue
            feature["properties"] = {k: v.format(**feature["properties"]) for k, v in properties.items()}

    # 6. Create the list of features
    features = [
        {
            "type": feature["type"],
            "geometry": {
                "type": feature["geometry"]["type"],
                "coordinates": json.dumps(feature["geometry"]["coordinates"])
            },
            "properties": json.dumps(feature["properties"])
        }
        for feature in geojson["features"]
    ]

    # 7. Return the list of features
    return features
# End def generate_map_layer_entry
