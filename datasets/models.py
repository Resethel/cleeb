# -*- coding: utf-8 -*-
from __future__ import annotations
import uuid
import zipfile

import geojson
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver

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

    def get_file_path(self, _):
        return f'datasets/{uuid.uuid4()}'
    # End def get_file_path

    file = models.FileField(
        upload_to=get_file_path,
        help_text="Fichier du jeu de données. Le fichier doit correspondre au format choisi.",
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return self.name
    # End def __str__

    def clean(self):
        validate_dataset_file(self)
    # End def clean

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


def validate_dataset_file(instance : Dataset):
    if instance.format == SHAPEFILE:
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

    elif instance.format == GEOJSON:
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

