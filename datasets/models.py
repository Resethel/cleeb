# -*- coding: utf-8 -*-
from __future__ import annotations

import re
import uuid
import zipfile
from pathlib import Path

import geojson
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.template.defaultfilters import slugify

# ======================================================================================================================
# Constants
# ======================================================================================================================

SHAPEFILE = 'shapefile'
GEOJSON = 'geojson'
DATASET_FORMAT_CHOICES = {
    SHAPEFILE: 'Shapefile',
    GEOJSON: 'GeoJSON'
}

SVG_REGEX = re.compile(r'(?:<\?xml\b[^>]*>[^<]*)?(?:<!--.*?-->[^<]*)*(?:<svg|<!DOCTYPE svg)\b', re.DOTALL)


# ======================================================================================================================
# DatasetVersion Model
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
# DatasetCategory Model
# ======================================================================================================================

class DatasetCategory(models.Model):
    """A category for a dataset."""

    # ------------------------------------------------------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------------------------------------------------------

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True, help_text="Nom de la catégorie du jeu de données.")
    icon = models.FileField(upload_to='datasets/category_icons', help_text="Icône de la catégorie du jeu de données. Doit être un fichier SVG monochrome (noir, fond transparent).")
    slug = models.SlugField(max_length=200, null=True, default=None)

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return self.name
    # End def __str__

    def clean(self):
        if not SVG_REGEX.match(self.icon.file.read().decode('latin-1')):
            raise ValidationError('Le fichier doit être un fichier SVG valide.')
    # End def clean

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        verbose_name = "Catégorie d'un jeu de données"
        verbose_name_plural = "Catégories de jeux de données"
        ordering = ['name']
    # End class Meta
# End class DatasetCategory

@receiver(pre_save, sender=DatasetCategory)
def generate_slug(sender, instance, **kwargs):
    """Generate the slug for the resource"""
    instance.slug = slugify(instance.name)
# End def generate_slug


# ======================================================================================================================
# DatasetTechnicalInformation Model
# ======================================================================================================================

class DatasetTechnicalInformation(models.Model):
    """A piece of technical information about a dataset."""

    # ------------------------------------------------------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------------------------------------------------------

    id = models.AutoField(primary_key=True)
    key = models.CharField(max_length=100, help_text="Clé de l'information technique.")
    value = models.CharField(max_length=250, help_text="Valeur de l'information technique.")
    dataset = models.ForeignKey(
        'Dataset',
        on_delete=models.CASCADE,
        related_name='technical_information',
        help_text="Jeu de données associé à l'information technique."
    )
# End class DatasetTechnicalInformation


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
    slug = models.CharField(max_length=200, null=True, default=None)

    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Nom du jeu de données"
    )

    public = models.BooleanField(
        default=True,
        help_text="Indique si le jeu de données peut être partagé publiquement."
    )

    categories = models.ManyToManyField(
        'DatasetCategory',
        blank=True,
        help_text="Catégories du jeu de données."
    )

    short_desc = models.TextField(
        max_length=400,
        blank=True,
        null=True,
        default=None,
        help_text="Description courte du jeu de données affichée dans les listes (max: 400 caractères, optionnel)."
    )

    description = models.TextField(
        blank=True,
        null=True,
        default=None,
        help_text="Description du jeu de données. Optionnel."
    )

    # ----- Metadata fields -----

    source = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        default=None,
        help_text="Source du jeu de données. Optionnel."
    )

    last_update = models.DateField(
        auto_now=True,
        help_text="Date de dernière mise à jour du jeu de données.")

    language = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        default=None,
        help_text="Langue du jeu de données. Optionnel."
    )

    license = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        default=None,
        help_text="Licence du jeu de données. Optionnel."
    )

    usage_restrictions = models.TextField(
        blank=True,
        null=True,
        default=None,
        help_text="Restrictions d'utilisation du jeu de données. Optionnel."
    )

    # ----- Technical fields -----

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
# End def dataset_pre_save

@receiver(pre_save, sender=Dataset)
def generate_slug(sender, instance, **kwargs):
    """Generate the slug for the resource"""
    instance.slug = slugify(instance.name)
# End def generate_slug

@receiver(post_save, sender=Dataset)
def set_up_format_technical_information(sender, instance, created, **kwargs):
    """Create a piece of technical information about the dataset format."""
    # If the format is already set, simply update the technical information
    if instance.technical_information.filter(key='format').exists():
        instance.technical_information.filter(key='format').update(value=instance.format)

    else:
        DatasetTechnicalInformation.objects.create(
            key='format',
            value=instance.format,
            dataset=instance
        ).save()
# End def create_format_technical_information



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

