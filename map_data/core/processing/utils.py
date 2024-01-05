from pathlib import Path
from typing import Any, Sequence

import shapefile
from pyproj import Transformer


def convert_shapefile_to_geojson(
        file_path: str | Path,
        shapefile_name: str | None = None,
        encoding : str = 'utf-8',
        input_crs: str = "2154",
        output_crs: str = "4326",
        max_polygon_points: int = 1000,
        max_multipolygons: int = 2500,
        max_multipolygon_points: int = 100,
) -> dict:
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
    transformer = Transformer.from_crs(input_crs, output_crs, always_xy=True)

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
            if n_polys > max_multipolygons:
                print(f"Rejecting {shape_record.record} with {n_polys} polygons (limit: 2500)")
                continue

            for polygon in geometry['coordinates']:
                sub_coordinates = []
                for sub_polygon in polygon:
                    # Limit the number of points in the sub-polygon to 100.
                    # This is to reduce the size of the GeoJSON file.
                    # If the sub_polygon has more than `max_multipolygon_points` points, only keep 1 point every len(polygon) // 100 points.
                    # In this case of multi-polygons, it's important to be more restrictive on the number of points

                    if len(sub_polygon) > max_multipolygon_points:
                        sub_polygon = sub_polygon[::len(sub_polygon) // max_multipolygon_points]

                    sub_coordinates.append(_convert_polygon_to_geojson(sub_polygon, transformer))
                coordinates.append(sub_coordinates)

        for polygon in geometry['coordinates']:
            # Limit the number of points in the polygon to 1000.
            # This is to reduce the size of the GeoJSON file.
            # If the polygon has more than `max_polygon_points` points, only keep 1 point every len(polygon) // 1000 points.
            if len(polygon) > max_polygon_points:
                polygon = polygon[::len(polygon) // max_polygon_points]
            coordinates.append(_convert_polygon_to_geojson(polygon, transformer))

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

def _convert_polygon_to_geojson(polygon: list[tuple[Any, Any]], transformer: Transformer) -> list[tuple[Any, Any]]:

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
# End def _convert_polygon_to_geojson