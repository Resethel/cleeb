# -*- coding: utf-8 -*-
from __future__ import annotations
import uuid
import zipfile
from pathlib import Path

import geojson
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone

# ======================================================================================================================
# Constants
# ======================================================================================================================

SHAPEFILE = 'shapefile'
GEOJSON = 'geojson'
DATASET_FORMAT_CHOICES = {
    SHAPEFILE: 'Shapefile',
    GEOJSON: 'GeoJSON'
}

# ======================================================================================================================
# DatasetFile Model
# ======================================================================================================================

def dataset_version_filepath(instance : DatasetVersion, filename : str) -> str:
    return f"datasets/{instance.dataset.id}_{uuid.uuid4()}{Path(filename).suffix}"
# End def dataset_version_filepath

class DatasetVersion(models.Model):
    """A version of a dataset file."""

    # ------------------------------------------------------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------------------------------------------------------

    id      = models.AutoField(primary_key=True)
    dataset = models.ForeignKey('Dataset', on_delete=models.CASCADE, related_name='versions')
    date    = models.DateTimeField(default=timezone.now, help_text="Date de la version du jeu de données.")
    file    = models.FileField(upload_to=dataset_version_filepath, help_text="Fichier de la version du jeu de données.")

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------
    def __str__(self):
        return f"Version of {self.dataset.name} from {self.date}"
    # End def __str__

    def clean(self):
        validate_dataset_version_file(self)

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------
    class Meta:
        verbose_name = "Version de jeu de données"
        verbose_name_plural = "Versions de jeux de données"
        ordering = ['-date']
    # End class Meta
# End class DatasetVersion


# ======================================================================================================================
# Dataset Model
# ======================================================================================================================


class Dataset(models.Model):
    """A dataset is a file containing geographic data.

    It can be either a ZIP file containing a shapefile, or a GeoJSON.
    """

    # ------------------------------------------------------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------------------------------------------------------

    id = models.AutoField(primary_key=True)

    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Nom du jeu de données"
    )

    category = models.CharField(
        max_length=100,
        blank=True,
        help_text="Catégorie du jeu de données. Optionnel."
    )

    short_desc = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        default=None,
        help_text="Description courte du jeu de données. Optionnel. Utilisé pour générer l'aide contextuelle."
    )

    description = models.TextField(
        blank=True,
        null=True,
        default=None,
        help_text="Description du jeu de données. Optionnel."
    )

    format = models.CharField(
        max_length=10,
        choices=DATASET_FORMAT_CHOICES,
        help_text="Format du jeu de données. Soit un fichier ZIP contenant un fichier shapefile, soit un fichier GeoJSON."
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return self.name
    # End def __str__

    def get_latest_version(self) -> DatasetVersion | None:
        """Return the latest version of the dataset file."""
        return self.versions.latest('date') if  self.versions.exists() else None
    # End def get_latest_version

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        verbose_name = "Jeu de données"
        verbose_name_plural = "Jeux de données"
        ordering = ['name']
    # End class Meta
# End class Dataset

@receiver(pre_save, sender=Dataset)
def dataset_pre_save(sender, instance, **kwargs):
    """Validate the dataset file format and complete the description field if it is empty."""

    # 1. Nullify empty descriptions
    if instance.short_desc is not None and instance.short_desc.strip() == '':
        instance.short_desc = None
    if instance.description is not None and instance.description.strip() == '':
        instance.description = None

    # 2. Complete the category field if it is empty
    if instance.category is None or instance.category.strip() == '':
        instance.category = 'Non classé'
    instance.category = instance.category.strip()
# End def dataset_pre_save

# ======================================================================================================================
# Helper methods
# ======================================================================================================================


def validate_dataset_version_file(instance : DatasetVersion):
    if instance.dataset.format == SHAPEFILE:
        if not zipfile.is_zipfile(instance.file):
            raise ValidationError('Le fichier doit être un fichier ZIP.')
        else:
            try:
                zip_file : zipfile.ZipFile
                with zipfile.ZipFile(instance.file) as zip_file:
                    if not zip_file.testzip() is None:
                        raise ValidationError('Le fichier ZIP est corrompu.')
                    else:
                        # Check that the zip file contains at least one file with a .shp extension
                        shapefile_found = False
                        for file_name in zip_file.namelist():
                            if file_name.endswith('.shp'):
                                shapefile_found = True
                                break
                        if not shapefile_found:
                            raise ValidationError('Le fichier ZIP doit contenir au moins un fichier avec une extension .shp.')
            except zipfile.BadZipFile:
                raise ValidationError('Le fichier ZIP est corrompu.')

    elif instance.dataset.format == GEOJSON:
        try:
            obj : geojson.GeoJSON = geojson.loads(instance.file.read())
            if not obj.is_valid:
                raise ValidationError('Le fichier doit être un fichier GeoJSON valide. (erreur: {})'.format(obj.errors()))
        except ValueError:
            raise ValidationError('Le fichier doit être un fichier GeoJSON.')

        finally:
            # Reset the file pointer to the beginning of the file
            instance.file.seek(0)

    else:
        raise ValidationError('Le format du jeu de données est invalide.')
# End def validate_dataset_file

