# -*- coding: utf-8 -*-
"""
Module to preprocess the data from the ZNIEFF (Zone naturelle d'intérêt écologique, faunistique et floristique) dataset.
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
DATASETS_PATH = Path(__file__).parent.parent.parent / "static/datasets"
LAYERS : list[dict] = [

    # ZNIEFF de type 1
    {
        "name"      : "znieff_type_1",
        "dataset"   : "dreal_grand_est",
        "shapefile" : "ZNIEFF1et2/ZNIEFF1_S_R44.shp",
        "properties"     : {
            "Categorie"  : "ZNIEFF de type 1",
            "Nom"        : "{NOM} ({ID_MNHN})",
            "Surface"    : "{SURF_ha} ha",
            "Fiche INPN" : "{Lien_INPN}",
            "Fiche DREAL": "{Lien_DREAL}"
        }
    },

    # ZNIEFF de type 2
    {
        "name"           : "znieff_type_2",
        "dataset"        : "dreal_grand_est",
        "shapefile"      : "ZNIEFF1et2/ZNIEFF2_S_R44.shp",
        "properties"     : {
            "Categorie"  : "ZNIEFF de type 1",
            "Nom"        : "{NOM} ({ID_MNHN})",
            "Surface"    : "{SURF_ha} ha",
            "Fiche INPN" : "{Lien_INPN}",
            "Fiche DREAL": "{Lien_DREAL}"
        }
    },

    # Trame verte
    {
        "name"     : "trame_verte",
        "dataset"   : "N_SRCE_CORRIDOR_S_000",
        "shapefile": "N_SRCE_CORRIDOR_S_000.shp",
        "properties": {
            "categorie": "Trame verte",
            "ID": "{ID_CORR}",
            "type": "{MILMAJ_NAT}"
        }
    },

    # Trame bleue
    {
        "name"        : "trame_bleue",
        "dataset"     : "N_SRCE_COURS_EAU_S_000",
        "shapefile"   : "N_SRCE_COURS_EAU_S_000.shp",
         "properties": {
            "categorie": "Trame verte",
            "ID": "{ID_CORR}",
            "type": "{MILMAJ_NAT}"
        }
    },

    # Reservoirs de biodiversite et reserves biologiques
    # {
    #     "name" : "reservoirs_biodiversite",
    #     "dataset"   : "N_SRCE_RESERVOIR_S_000",
    #     "shapefile"   : "N_SRCE_RESERVOIR_S_000.shp",
    #     "out_filename"  : "reservoirs_biodiversite.json",
    #     "properties": {
    #         "categorie": "Reservoir de biodiversité",
    #         "ID": "{ID_RESV}",
    #         "type": "{MILMAJ_NAT}"
    #     }
    # },


    # Reserves biologiques
    # {
    #     "name"    : "reserves_biologiques",
    #     "dataset" : "reserves_biologiques.zip",
    #     "shapefile": "reserves_biologiques.shp",
    #     "properties": {
    #         "categorie": "Reserve biologique",
    #         "nom" : "{NOM_SITE}",
    #         "surface" : "{SURF_OFF} ha",
    #         "fiche": "{URL_FICHE}"
    #     }
    # },

    # ZICO
    # "ZICO" : {
    #     "source_path"   : root_path() / "data/raw/zico.zip",
    #     "out_filename"  : "zico.json",
    #     "properties": {
    #         "categorie": "ZICO",
    #         "nom": "{NOM}",
    #     }
    # },

    # ZPS
    {
        "name"      : "reserves_naturelle_régionales",
        "dataset"   : "dreal_grand_est",
        "shapefile" : "N_ENP_RNR_S_R44/N_ENP_RNR_S_R44.shp",
        "encoding"      : "latin-1",
        "out_filename"  : "reserves_naturelles_regionales.json",
        "properties": {
            "Categorie": "Reserve naturelle régionale",
            "Nom": "{NOM_SITE}",
            "Gestionnaire": "{GEST_SITE}",
            "Operateur": "{OPERATEUR}",
            "Fiche": "{URL_FICHE}"
        }
    },

    # Zones boisées
    {
        "name"      : "zones_boisées",
        "dataset"   : "dreal_grand_est",
        "shapefile" : "Foret/Foret_BdcartoEd181_S_R44.shp",
        "encoding"      : "utf-8",
        "properties"    : {
            "ID": "{id}",
            "type": "{nature}"
        }
    },

    # Zones Humides probables
    {
        "name"      : "zones_humides_probables",
        "dataset"   : "dreal_grand_est",
        "shapefile" : "zhprobableseuillee_s_r44/ZHprobableSeuillee_S_R44.shp",
        "encoding"      : "utf-8",
    }

    # PLUi
    # "ZONAGE_GENERAL": {
    #     "source_path": root_path() / "data/raw/PLUi/Arreté_2023/zonage_général/zone_urba.shp",
    #     "shapefile_name": None,
    #     "out_filename": "zonage_general.json",
    #     "properties": {
    #         "Type de Zone": "{typezone}"
    #     }
    # }
]

METZ_LOCATION = (49.119309, 6.175716)
FILTER_LAT = 0.20
FILTER_LON = 0.20

INPUT_EPSG_PROJECTION = "2154"  # EPSG:2154 (Lambert 93)
OUTPUT_EPSG_PROJECTION = "4326" # EPSG:4326 (WGS84)

# ======================================================================================================================
# Functions
# ======================================================================================================================

def __convert_shapefile_to_geojson(file_path: str | Path, shapefile_name: str | None = None, encoding : str = 'utf-8') -> dict:
    """Read a shapefile and return the data as a GeoJSON-like dict.

    Args:
        file_path (str | Path): The path to the shapefile to read.

    Returns:
        dict: The data of the shapefile as a GeoJSON-like dict.
    """

    if shapefile_name is None:
        reader = shapefile.Reader(file_path, encoding=encoding)
    else:
        reader = shapefile.Reader(Path(file_path) / shapefile_name, encoding=encoding)

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
    print(f"Reading {n_shapes} shapes...")


    shape_record : shapefile.ShapeRecord
    for shape_record in reader.shapeRecords():

        geometry = shape_record.shape.__geo_interface__
        # print(geometry['type'], len(geometry['coordinates']))
        # Reproject the coordinates of the geometry
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

def generate_map_layer_entry(name : str, convert_properties: bool = True) -> list[dict]:

    # 1. Get the layer config
    layer_config = None
    try:
        layer_config = next(layer for layer in LAYERS if layer["name"] == name)
    except StopIteration:
        raise ValueError(f"Unknown layer name: {name}.")

    # 2. Find the dataset in the static folder
    dataset_path = DATASETS_PATH / f"{layer_config['dataset']}.zip"
    if not dataset_path.exists():
        raise ValueError(f"Unknown dataset name: {layer_config['dataset']}.")

    # 3. Read the shapefile
    print("Reading shapefile...")
    geojson = __convert_shapefile_to_geojson(dataset_path, layer_config.get("shapefile"),
                                             encoding=layer_config.get("encoding", "utf-8"))

    # 4. Filter the data to only include the data in the filter area.
    print("Filtering data...")
    geojson = __filter_data(geojson, METZ_LOCATION, FILTER_LAT, FILTER_LON)

    # 5. Convert the properties if needed
    if convert_properties:
        print("Converting properties...")
        for feature in geojson["features"]:
            if "properties" not in layer_config:
                continue
            feature["properties"] = {k: v.format(**feature["properties"]) for k, v in layer_config["properties"].items()}

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

def generate_all_map_layers_entries() -> dict:
    """Generate all the map layers entries."""
    return {layer["name"]: generate_map_layer_entry(layer["name"]) for layer in LAYERS}
