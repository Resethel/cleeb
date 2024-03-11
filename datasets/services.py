# -*- coding: utf-8 -*-
"""
Service module for the `datasets` application.
It contains the business logic for the application needed to process the datasets.
"""
import datetime
import logging
import os
import shutil
import tempfile
import zipfile
from pathlib import Path
from uuid import uuid4

from django.apps import apps
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import GEOSGeometry
from django.core.files import File
from django.db.models import FileField

# ======================================================================================================================
# Constants
# ======================================================================================================================

logger = logging.getLogger(__name__)

# ======================================================================================================================
# Services
# ======================================================================================================================

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


# noinspection PyPep8Naming
def sanitize_shapefile_archive(dataset_version_id : int) -> int:
    """Sanitize the shapefile archive file by removing any files that are not supposed to be zipped with the shapefile.

    Files that are not supposed to be zipped with the shapefile are:
    - Resource fork files (i.e., __MACOSX folders, etc.)
    - Hidden files (i.e., files starting with a dot)
    - Executable files (i.e., .exe files)

    Args:
        dataset_version_id (int): The id of the dataset version to sanitize.

    Returns:
        int: The number of folders and files removed.
    """
    DatasetVersion = apps.get_model('datasets.DatasetVersion')

    # 0. Get the dataset version
    dataset_version = DatasetVersion.objects.get(id=dataset_version_id)
    n_removal = 0

    # 1. Open a temporary directory to perform the operations in
    with tempfile.TemporaryDirectory() as temp_dir:
        # 2. Open the zip file
        with dataset_version.file.open('rb') as file:
            with zipfile.ZipFile(file) as zip_file:
                # 2. Extract the contents of the zip file
                zip_file.extractall(temp_dir)

        # 3. Create a list of the files and folders
        file_list = []
        folder_list = []
        for path in Path(temp_dir).rglob('*'):
            if path.is_file():
                file_list.append(path)
            else:
                folder_list.append(path)

        # 4.1 Start by removing the folders that are not supposed to be zipped with the shapefile
        for folder in folder_list:
            if folder.name.startswith(('.', '__')):
                logger.debug(f"Removing hidden folder: {folder}")
                shutil.rmtree(folder)
                n_removal += 1
                # Update the file list so that it does not contain files from the removed folder
                file_list = [f for f in file_list if folder not in f.parents]

        # 4.2. Then, remove the files that are not supposed to be zipped with the shapefile
        for file in file_list:
            if file.name.startswith(('.', '__')):
                logger.debug(f"Removing hidden file: {file}")
                file.unlink()
                n_removal += 1
            # Remove executable files
            elif os.chmod(file, 0o777):
                n_removal += 1
                logger.debug(f"Removing executable file: {file}")
                file.unlink()

        # 4. Re-zip the contents of the temporary directory
        with dataset_version.file.open('wb') as file:
            with zipfile.ZipFile(file, 'w') as zip_file:
                for path in Path(temp_dir).rglob('*'):
                    zip_file.write(path, path.relative_to(temp_dir))

        # 5. Return the number of folders and files removed
        return n_removal
# End def sanitize_shapefile_zip