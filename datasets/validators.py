# -*- coding: utf-8 -*-
"""
Validators for the `datasets` application.
"""
import zipfile

from django.core.exceptions import ValidationError
from django.core.files import File
from django.utils.translation import gettext_lazy as _


def validate_dataset_version_file(field: File):
    """Validator for the `file` attribute of a `DatasetVersion` object."""
    if not zipfile.is_zipfile(field.file):
        raise ValidationError(
            # message=f"'{field.name}' n'est pas un fichier ZIP valide.",
            message=_("{file} is not a valid ZIP file.").format(file=field.name),
            params={'file': field.name}
        )
    else:
        try:
            zip_file : zipfile.ZipFile
            with zipfile.ZipFile(field.file) as zip_file:
                if not zip_file.testzip() is None:
                    raise ValidationError(
                        message=_("{file} is corrupted.").format(file=field.name),
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
                            message=_("{file} does not contain a shapefile (.shp).").format(file=field.name),
                            params={'file': field.name}
                        )
        except zipfile.BadZipFile:
            raise ValidationError(
                message=_("{file} ZIP file seems to be corrupted.").format(file=field.name),
                params={'file': field.name}
            )
# End def validate_dataset_file