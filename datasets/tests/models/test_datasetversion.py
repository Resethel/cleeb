# -*- coding: utf-8 -*-
"""
Tests for the model `DatasetVersion` of the `datasets` application.
"""
from pathlib import Path

from django.contrib.gis.geos import Polygon
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from datasets.models import Dataset, DatasetLayer, DatasetVersion



class DatasetVersionModelParsingTests(TestCase):
    """Tests for the `DatasetVersion` model parsing methods.

    Upon save, the `DatasetVersion` model should parse the uploaded file and create the appropriate Model instances.
    """

    def setUp(self):
        self.test_data_path = Path(__file__).parent.parent / "resources" / "Test_shapefile_AO-shp.zip"
        self.test_dataset = Dataset.objects.create(name="Test Dataset")

    def test_shouldParseShapeFileIntoExpectedLayer_givenASingleShapefileInTheZipArchive(self):
        # Create a `DatasetVersion` instance
        dataset_version = DatasetVersion.objects.create(
            file=SimpleUploadedFile(self.test_data_path, open(self.test_data_path, "rb").read()),
            dataset=self.test_dataset
        )

        # Ensure that one `Layer` instance was created
        self.assertEqual(dataset_version.layers.count(), 1)

        # Ensure that the `Layer` instance is created as expected
        layer_instance : DatasetLayer = dataset_version.layers.first()
        self.assertEqual(layer_instance.name, "Test_shapefile_AO")
        self.assertEqual(layer_instance.srid, 4326)
        self.assertEqual(layer_instance.feature_count, 19)
        self.assertEqual(layer_instance.geometry_type, "Point")
        self.assertEqual(
            layer_instance.bounding_box,
            Polygon(
                (
                         (-171.184622586726, -83.741978950416),
                         (-171.184622586726, 88.0369969547271),
                         (145.257631204659, 88.0369969547271),
                         (145.257631204659, -83.741978950416),
                         (-171.184622586726, -83.741978950416)
                     ),
                     srid=4326
            )
        )

        # Ensure that the `LayerField` instances are created as expected
        self.assertEqual(layer_instance.fields.count(), 2)
        field_instances = layer_instance.fields.all()
        for field_instance in field_instances:
            if field_instance.name == "FID":
                self.assertEqual("OFTInteger", field_instance.type)
                self.assertEqual(2, field_instance.max_length)
                self.assertEqual(0, field_instance.precision)
            elif field_instance.name == "Id":
                self.assertEqual("OFTInteger", field_instance.type)
                self.assertEqual(1, field_instance.max_length)
                self.assertEqual(0, field_instance.precision)
            else:
                self.fail(f"Unexpected field name: {field_instance.name}")
    # End def test_shouldParseShapeFileIntoLayer
# End class DatasetVersionModelParsingTests
