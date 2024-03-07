# -*- coding: utf-8 -*-
"""
Service module for the `datasets` application.
It contains the business logic for the application needed to process the datasets.
"""
import datetime
import tempfile
import zipfile
from pathlib import Path

from django.apps import apps
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import GEOSGeometry


# noinspection PyPep8Naming
def generate_features(dataset_version_id: int) -> None:
    """Process the dataset into a geojson layer."""

    # Get the required models. This is done inside the function to avoid circular imports
    DatasetLayer   = apps.get_model('datasets.DatasetLayer')
    DatasetVersion = apps.get_model('datasets.DatasetVersion')
    Feature        = apps.get_model('datasets.Feature')

    # 1. Get the dataset version
    dataset_version = DatasetVersion.objects.get(id=dataset_version_id)

    with zipfile.ZipFile(dataset_version.file.path) as zip_file, tempfile.TemporaryDirectory() as temp_dir:
        # 2. Extract the contents of the zip file
        zip_file.extractall(temp_dir)

        # 3. Find all the shapefiles in the zip file
        shapefiles = []
        for file_name in zip_file.namelist():
            if file_name.endswith('.shp') and not file_name.startswith(('.', '__')):
                shapefiles.append(Path(temp_dir) / file_name)

        for shapefile_path in shapefiles:
            data_source = DataSource(shapefile_path)

            # 4. Iterate over all layers in the shapefile
            for layer in data_source:
                # 4.1. Get the corresponding DatasetLayer instance
                dataset_layer = DatasetLayer.objects.filter(name=layer.name, dataset=dataset_version).first()

                # 4.2. If the layer does not exist, it means that it is part of another shapefile in the same zip file
                if not dataset_layer:
                    continue

                # 4.3. Clean the features of the layer
                dataset_layer.features.all().delete()

                # 4.3 Iterate over all features in the layer and save them to the database
                for feature in layer:
                    # Convert the feature's geometry to a GEOSGeometry instance
                    geometry = GEOSGeometry(feature.geom.wkt, srid = dataset_layer.srid)

                    fields = {}
                    for field in feature.fields:
                        in_field = feature.get(field)
                        # Convert date and time fields to ISO format
                        if isinstance(in_field, (datetime.date, datetime.time, datetime.datetime)):
                            fields[field] = in_field.isoformat()
                        else:
                            fields[field] = feature.get(field)

                    # Create a Feature instance for the feature and save it to the database
                    # immediately so that memory is not exhausted
                    Feature.objects.create(
                        layer=dataset_layer,
                        geometry=geometry,
                        fields=fields
                    ).save()
# End def generate_features
