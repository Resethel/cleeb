# -*- coding: utf-8 -*-
"""
Utility functions for geographic data.
"""
from pathlib import Path
from typing import Any, Sequence

import geojson
import shapefile
from pyproj import Transformer

from map_data.core.utils.enums import EPSGProjection, Encoding


# ======================================================================================================================
# Convert Shapefile to Geojson
# ======================================================================================================================

def convert_shapefile_to_geojson(file_path: str | Path,
                                 input_epsg_projection: EPSGProjection,
                                 output_epsg_projection: EPSGProjection | None = None,
                                 shapefile_name: str | None = None,
                                 **kwargs: Any) -> geojson.FeatureCollection:
    """Read a shapefile and return the data as a GeoJSON-like dict.

    Args:
        file_path (str | Path): The path to the shapefile.
        input_epsg_projection (EPSGProjection): The EPSG projection of the shapefile.
        output_epsg_projection (EPSGProjection): The EPSG projection to convert the coordinates to.
        shapefile_name (str | None, optional): The name of the shapefile.
            If None, the file_path is the full path to the shapefile.
            Defaults to None.
        
    Keyword Args:
        encoding (Encoding, optional): The encoding of the shapefile.
            Defaults to Encoding.UTF_8.
        polygon_point_limit (int, optional): The maximum number of points to keep in a polygon
            If set to None, no limit is applied.
            Defaults to 1000.
        sub_polygon_limit (int, optional): The maximum number of polygons to keep in a multipolygon.
            If set to None, no limit is applied.
            Defaults to 2500.
        sub_polygon_point_limit (int, optional): The maximum number of points to keep in a sub-polygon of a multipolygon.
            If set to None, no limit is applied.
            Defaults to 1000.    

    Returns:
        dict: The data of the shapefile as a GeoJSON-like dict.
    """
    # Get the kwargs
    encoding = kwargs.get("encoding", Encoding.UTF_8)
    polygon_point_limit = kwargs.get("polygon_point_limit", 1000)
    sub_polygon_limit = kwargs.get("sub_polygon_limit", 2500)
    sub_polygon_point_limit = kwargs.get("sub_polygon_point_limit", 1000)
    

    if shapefile_name is None:
        reader = shapefile.Reader(file_path, encoding=encoding.value)
    else:
        reader = shapefile.Reader(Path(file_path) / shapefile_name, encoding=encoding.value)

    # Create a transformer to convert between the two CRS
    transformer = Transformer.from_crs(
        input_epsg_projection.value,
        output_epsg_projection.value if output_epsg_projection is not None else input_epsg_projection.value,
        always_xy=True
    )

    # Extract the field names of the shapefile to update the records
    field_names = [f[0] for f in reader.fields[1:]]

    # For each shape
    features = []
    n_shapes = len(reader.shapeRecords())
    print(f"Reading {n_shapes} shapes...")


    shape_record : shapefile.ShapeRecord
    for i, shape_record in enumerate(reader.shapeRecords()):

        geometry = shape_record.shape.__geo_interface__
        coordinates = []

        if geometry['type'] == "MultiPolygon":
            # Reject multi-polygons with more than 2500 polygons
            n_polys = len(geometry['coordinates'])
            if sub_polygon_limit is not None and n_polys > sub_polygon_limit:
                print(f"Rejecting {shape_record.record} with {n_polys} polygons (limit: 2500)")
                continue

            for polygon in geometry['coordinates']:
                sub_coordinates = []
                for sub_polygon in polygon:
                    # Limit the number of points in the sub-polygon to `sub_polygon_point_limit`.
                    # This is to reduce the size of the GeoJSON file.
                    # If the sub_polygon has more than `sub_polygon_point_limit` points, only keep 1 point every len(polygon) // `sub_polygon_point_limit` points.
                    # In this case of multi-polygons, it's important to be more restrictive on the number of points
                    if sub_polygon_point_limit is not None and len(sub_polygon) > sub_polygon_point_limit:
                        sub_polygon = sub_polygon[::len(sub_polygon) // sub_polygon_point_limit]

                    sub_coordinates.append(_convert_polygon_to_geojson(sub_polygon, transformer))
                coordinates.append(sub_coordinates)

        for polygon in geometry['coordinates']:
            # Limit the number of points in the polygon to `polygon_point_limit`.
            # This is to reduce the size of the GeoJSON file.
            # If the polygon has more than `polygon_point_limit` points, only keep 1 point
            # every len(polygon) // `polygon_point_limit` points.
            if len(polygon) > polygon_point_limit:
                polygon = polygon[::len(polygon) // 1000]
            coordinates.append(_convert_polygon_to_geojson(polygon, transformer))

        # Create the GeoJSON entry with the correct interface
        properties = dict(zip(field_names, shape_record.record))

        feature_geometry = None
        match geometry['type'].casefold():
            case "polygon":
                feature_geometry = geojson.Polygon(coordinates=coordinates)
            case "multipolygon":
                feature_geometry = geojson.MultiPolygon(coordinates=coordinates)
            case "point":
                feature_geometry = geojson.Point(coordinates=coordinates)
            case _:
                raise ValueError(f"Unknown geometry of type {feature_geometry}")

        features.append(geojson.Feature(id=i, geometry=feature_geometry, properties=properties))

    return geojson.FeatureCollection(features=features)
# End def convert_shapefile_to_geojson

def _convert_polygon_to_geojson(polygon: list[tuple[Any, Any]], transformer: Transformer) -> list[tuple[Any, Any]]:
    """Helper function to convert a polygon to a GeoJSON-like polygon."""
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

# ======================================================================================================================
# Filter & operations on Geojson Features
# ======================================================================================================================

def filter_data(feature_collection: geojson.FeatureCollection,
                center : tuple[float, float],
                filter_lat : float,
                filter_lon : float) -> dict:
    """Filter the data to only include the data in the filter area.

    The filter area is a square centered on the center point and of size filter_lat x filter_lon.
    Any shape that intersects this square is included in the filtered data.
    """
    if not isinstance(feature_collection, geojson.FeatureCollection):
        raise TypeError(f"Expected features type to be 'FeatureCollection', not '{type(filter_data)}")




    lat_min = center[0] - filter_lat
    lon_min = center[1] - filter_lon
    lat_max = center[0] + filter_lat
    lon_max = center[1] + filter_lon

    # 1. Helper function to match a
    def match_polygon(polygon):
        for point in polygon:
            if lat_min <= point[1] <= lat_max and lon_min <= point[0] <= lon_max:
                return True
        return False

    # For each feature
    features = []
    for feature in feature_collection.features:
        # For each polygon in the feature
        match = False

        if isinstance(feature, geojson.MultiPolygon):
            for polygon in feature.geometry.coordinates:
                for sub_polygon in polygon:
                    if match_polygon(sub_polygon):
                        match = True
                        break
                if match:
                    break
        else:
            for polygon in feature.geometry.coordinates:
                if match_polygon(polygon):
                    match = True
                    break

        if match:
            features.append(feature)
    return geojson.FeatureCollection(features=features)
# End def filter_data

# ======================================================================================================================
# Cleaning Functions
# ======================================================================================================================

# TODO: Implement function to rewind Polygons and Multipolygons (i.e., follow the right-end rule)

def clean_geojson(geojson: dict) -> dict:
    """Clean the geojson by removing empty features or coordinates.

    Args:
        geojson (dict): The geojson to clean.
    """
    output = {"type": "FeatureCollection", "features": []}

    for feature in geojson["features"]:
        # If the feature is a Polygon...
        new_feature = {"type": "Feature",
                       "geometry": {"type": feature["geometry"]["type"], "coordinates": []},
                       "properties": feature["properties"]}

        match feature["geometry"]["type"]:
            case "Polygon":
                cleaned_polygon = __clean_polygon_coordinates(feature["geometry"]["coordinates"])
                if cleaned_polygon:
                    new_feature["geometry"]["coordinates"] = cleaned_polygon
                else:
                    continue

            case "MultiPolygon":
                cleaned_polygons = []
                # Clean each polygon in the multi-polygon
                for polygon in feature["geometry"]["coordinates"]:
                    cleaned_polygon = __clean_polygon_coordinates(polygon)
                    if cleaned_polygon:
                        cleaned_polygons.append(cleaned_polygon)
                # Append the cleaned multi-polygon if not empty
                if cleaned_polygons:
                    new_feature["geometry"]["coordinates"] = cleaned_polygons
                else:
                    continue

            case "Point":
                if feature["geometry"]["coordinates"]:
                    new_feature["geometry"]["coordinates"] = feature["geometry"]["coordinates"]
                else:
                    continue

            case _:
                ValueError(f"Unsupported geometry type: {feature['geometry']['type']}")

        if new_feature["geometry"]["coordinates"]:
            output["features"].append(new_feature)

    return output
# End def clean_geojson


def __clean_polygon_coordinates(coordinates: list[list[tuple[float, float]]]) -> list[list[tuple[float, float]]] | None:
    """Clean a polygon by removing empty points.

    Returns:
        list[list[tuple[float, float]]] | None: The cleaned polygon or None if the polygon is empty.
    """
    out_coords = []
    for rings in coordinates:
        out_ring = [point for point in rings if point]
        if out_ring:
            out_coords.append(out_ring)

    if out_coords:
        return out_coords
    return None
