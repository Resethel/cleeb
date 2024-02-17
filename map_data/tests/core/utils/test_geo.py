# -*- coding: utf-8 -*-
"""
Tests for the layer_processing module.
"""
from django.test import TestCase

from map_data.core.utils.geo import clean_geojson


# ======================================================================================================================
# Helper functions
# ======================================================================================================================

def create_geojson(geometry_type, coordinates):
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": geometry_type,
                    "coordinates": coord
                },
                "properties": {}
            } for coord in coordinates
        ]
    }
# End def create_geojson

# ======================================================================================================================
# Tests
# ======================================================================================================================

class TestConvertShapefileToGeojson(TestCase):
    """Implements those tests once the tests datasets are available"""
    pass
# End class TestConvertShapefileToGeojson

class TestCleanGeojson(TestCase):
    def test_shouldRemoveEmptyPoints_givenPointWithEmptyCoordinates(self):
        geojson = create_geojson("Point", [[], [1.0, 2.0]])
        expected_output = create_geojson("Point", [[1.0, 2.0]])
        self.assertDictEqual(clean_geojson(geojson), expected_output)
    # End def test_shouldRemoveEmptyPoints_givenPointWithEmptyCoordinates

    def test_shouldRemoveEmptyPolygons_givenPolygonWithEmptyCoordinates(self):
        geojson = create_geojson("Polygon",
                                 [
                                     [],
                                     [[1, 2], [5, 6], [9, 10]],
                                     [[11, 12], [13, 14], [15, 16], [17, 18], [19, 20], [21, 22], [25, 26], [29, 30]]
                                 ])
        expected_output = create_geojson("Polygon",
                                         [
                                             [[1, 2], [5, 6], [9, 10]],
                                             [[11, 12], [13, 14], [15, 16], [17, 18], [19, 20], [21, 22], [25, 26], [29, 30]]
                                         ])

        self.assertDictEqual(clean_geojson(geojson), expected_output)
    # End def test_shouldRemoveEmptyPolygons_givenPolygonWithEmptyCoordinates

    def test_shouldRemoveEmptyPolygons_givenMultiPolygonWithEmptyPolygons(self):
        geojson = create_geojson("MultiPolygon",
                                 [
                                     [[[[1, 2], [3, 4], [5, 6], [7, 8], [9, 10]]]],
                                     [[[[]]]],
                                     [[[[], [], [], []], [[], [], [], []]]],
                                     [ # MultiPolygon with polygons with empty coordinates
                                         [
                                             [[11, 12], [13, 14], [15, 16], [17, 18], [19, 20]],
                                             [[21, 22], [], [25, 26], [29, 30]] # Missing coordinates in one of the rings

                                         ]
                                     ],
                                     [ # MultiPolygon with empty polygons
                                         [
                                             [[31, 32], [33, 34], [35, 36], [37, 38], [39, 40]],
                                             [[41, 42], [43, 44], [45, 46], [47, 48], [49, 50]]
                                         ],
                                         [ # Empty polygon
                                             [[], [], [], []],
                                         ]
                                     ]
                                 ])
        self.maxDiff = None
        expected_output = create_geojson("MultiPolygon",
                                         [
                                             [[[[1, 2], [3, 4], [5, 6], [7, 8], [9, 10]]]],
                                             [[[[11, 12], [13, 14], [15, 16], [17, 18], [19, 20]], [[21, 22], [25, 26], [29, 30]]]],
                                             [[[[31, 32], [33, 34], [35, 36], [37, 38], [39, 40]], [[41, 42], [43, 44], [45, 46], [47, 48], [49, 50]]]]
                                         ])
        self.assertDictEqual(clean_geojson(geojson), expected_output)
    # End def test_shouldRemoveEmptyPolygons_givenMultiPolygonWithEmptyPolygons
#  End Class TestCleanGeojson

