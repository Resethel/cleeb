# -*- coding: utf-8 -*-
"""
Validators for the `datasets` application.
"""
import zipfile

from django.core.files import File
from django.core.exceptions import ValidationError


def validate_dataset_version_file(field: File):
    """Validator for the `file` attribute of a `DatasetVersion` object."""
    if not zipfile.is_zipfile(field.file):
        raise ValidationError(
            message=f"'{field.name}' n'est pas un fichier ZIP valide.",
            params={'file': field.name}
        )
    else:
        try:
            zip_file : zipfile.ZipFile
            with zipfile.ZipFile(field.file) as zip_file:
                if not zip_file.testzip() is None:
                    raise ValidationError(
                        message=f"Le fichier ZIP '{field.name}' est corrompu.",
                        params={'file': field.name}
                    )
                else:
                    # Check that the zip file contains at least one file with a .shp extension
                    shapefile_found = False
                    for file_name in zip_file.namelist():
                        if file_name.endswith('.shp'):
                            shapefile_found = True
                            break
                    if not shapefile_found:
                        raise ValidationError(
                            message=f"Le fichier ZIP '{field.name}' ne contient pas de fichier shapefile (.shp).",
                            params={'file': field.name}
                        )
        except zipfile.BadZipFile:
            raise ValidationError(
                message='Le fichier ZIP est corrompu.',
                params={'file': field.name}
            )
# End def validate_dataset_file