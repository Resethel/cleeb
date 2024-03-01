# -*- coding: utf-8 -*-
from __future__ import annotations

import re
import tempfile
import zipfile
from datetime import date, datetime
from pathlib import Path
from time import time

import django.contrib.gis.db.models as gis_models
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import Polygon
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.utils import timezone

from datasets.validators import validate_dataset_version_file

# ======================================================================================================================
# Module Constants
# ======================================================================================================================

# ----- Encoding -----
UTF8 = 'utf-8'
LATIN1 = 'latin-1'
ISO_8859_1 = 'iso-8859-1'
UTF16 = 'utf-16'
ASCII = 'ascii'
ENCODING_CHOICES = {
    UTF8: 'UTF-8',
    LATIN1: 'Latin-1',
    UTF16: 'UTF-16',
    ASCII: 'ASCII',
    ISO_8859_1: 'ISO-8859-1',
}

SVG_REGEX = re.compile(r'(?:<\?xml\b[^>]*>[^<]*)?(?:<!--.*?-->[^<]*)*(?:<svg|<!DOCTYPE svg)\b', re.DOTALL)


# ======================================================================================================================
# DatasetLayer & DatasetLayerField Models
# ======================================================================================================================

LAYER_FIELD_TYPE_MAP = {
    'OFTInteger'        : int,
    'OFTIntegerList'    : list[int],
    'OFTReal'           : float,
    'OFTRealList'       : list[float],
    'OFTString'         : str,
    'OFTStringList'     : list[str],
    'OFTWideString'     : str,
    'OFTWideStringList' : list[str],
    'OFTBinary'         : bytes,
    'OFTDate'           : date,
    'OFTTime'           : time,
    'OFTDateTime'       : datetime
}
LAYER_FIELD_TYPE_TYPE_CHOICES = [(k, k) for k in LAYER_FIELD_TYPE_MAP.keys()]

class DatasetLayerField(models.Model):
    """Represents a field of a dataset's layer."""

    # ------------------------------------------------------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------------------------------------------------------

    # ----- Identification -----

    id = models.AutoField(primary_key=True)

    # ----- Parent -----

    layer = models.ForeignKey(
        'DatasetLayer',
        related_name="fields",
        on_delete=models.CASCADE
    )

    # ----- Metadata -----

    name = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        default=None,
    )

    type = models.CharField(
        max_length=50,
        choices=LAYER_FIELD_TYPE_TYPE_CHOICES,
        blank=True,
        null=True,
        default=None,
    )

    max_length = models.IntegerField(
        blank=True,
        null=True,
        default=None,
        help_text="Longueur maximale du champ de texte.",
        validators=[MinValueValidator(0)]
    )

    precision = models.IntegerField(
        null=True,
        blank=True,
        default=None,
        help_text="Précision du champ numérique.",
        validators=[MinValueValidator(0)]
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def python_type(self) -> type:
        """Get the Python type of the field.

        The type is determined by the `type` field of the model.
        See `LAYER_FIELD_TYPE_MAP` for the mapping between the GDAL field types and the Python types.
        """
        return LAYER_FIELD_TYPE_MAP[self.type]
    # End def python_type

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        verbose_name = "Champ de couche de jeu de données"
        verbose_name_plural = "Champs de couche de jeu de données"
        unique_together = ['name', 'layer']
    # End class Meta
# End class DatasetLayerField

class DatasetLayer(models.Model):
    """Represents a layer of a dataset."""

    # ------------------------------------------------------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------------------------------------------------------

    # ----- Identification -----

    id   = models.AutoField(primary_key=True)

    # ----- Parent -----

    dataset = models.ForeignKey(
        'DatasetVersion',
        related_name="layers",
        on_delete=models.CASCADE
    )

    # ------ Metadata ------

    name = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        default=None,
        help_text="Nom de la couche de jeu de données."
    )

    srid = models.IntegerField(
        blank=True,
        null=True,
        default=None,
        help_text="SRID de la couche de jeu de données.",
    )

    bounding_box = gis_models.PolygonField(
        blank=True,
        null=True,
        default=None,
        help_text="Boîte englobante de la couche du jeu de données."
    )

    feature_count = models.IntegerField(
        blank=True,
        null=True,
        default=None,
        help_text="Nombre de géométries dans la couche du jeu de données.",
        validators=[MinValueValidator(0)]
    )

    geometry_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        default=None,
        help_text="Type de géométrie de la couche du jeu de données."
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        verbose_name = "Couche de jeu de données"
        verbose_name_plural = "Couches de jeux de données"
        unique_together = ['name', 'dataset']
    # End class Meta
# End class DatasetLayer


# ======================================================================================================================
# DatasetVersion Model
# ======================================================================================================================

def dataset_version_filepath(instance : DatasetVersion, filename : str) -> str:
    return f"datasets/{instance.dataset.slug}/{int(instance.date.timestamp())}{Path(filename).suffix}"
# End def dataset_version_filepath

class DatasetVersion(models.Model):
    """A version of a dataset file."""

    # ------------------------------------------------------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------------------------------------------------------

    # ------ Identification ------

    id = models.AutoField(primary_key=True)

    # ----- Parent -----

    dataset = models.ForeignKey(
        'Dataset',
        on_delete=models.CASCADE,
        related_name='versions'
    )

    # ----- Date -----

    date = models.DateTimeField(
        default=timezone.now,
        help_text="Date de la version du jeu de données."
    )

    # ----- File -----

    file = models.FileField(
        upload_to=dataset_version_filepath,
        verbose_name="Fichier",
        help_text="Fichier de la version du jeu de données.",
        default=None,
        null=True,
        blank=True,
        validators=[validate_dataset_version_file],
    )

    # ----- Metadata -----

    encoding = models.CharField(
        max_length=10,
        choices=ENCODING_CHOICES,
        default=UTF8,
        help_text="Encodage des propriétés du jeu de données."
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Non-persistent fields
    # ------------------------------------------------------------------------------------------------------------------

    def get_version_number(self) -> int:
        """Returns the version number of the dataset."""
        return self.dataset.versions.filter(date__lte=self.date).count()
    # End def version_number

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------
    def __str__(self):
        return f"Version of {self.dataset.name} from {self.date}"
    # End def __str__

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        verbose_name = "Version de jeu de données"
        verbose_name_plural = "Versions de jeux de données"
        ordering = ['-date']
    # End class Meta
# End class DatasetVersion


@receiver(post_save, sender=DatasetVersion)
def generate_layers(sender, instance, **kwargs):
    """Generate the layers of the dataset."""

    # 1. Open the zip file that contains the shapefile
    with zipfile.ZipFile(instance.file) as zip_file, tempfile.TemporaryDirectory() as tmp_dir:
        # 2. Extract the files in a temporary directory
        zip_file.extractall(tmp_dir)

        # 3. Find all the shapefiles contained in the zip file
        shapefiles = []
        for file_name in zip_file.namelist():
            # Discard hidden files and directories
            if file_name.endswith('.shp') and not file_name.startswith('__') and not file_name.startswith('.'):
                shapefiles.append(Path(tmp_dir) / Path(file_name))

        # 4. For each shapefile, generate a layer
        for shape_file in shapefiles:
            # 4.1 First, check if the shapefile is valid
            try:
                data_source : DataSource = DataSource(shape_file)
            except:
                print(f"Invalid shapefile: {shape_file}")
                continue

            # 4.2. If the shapefile is valid, generate the layer
            layer_names = []
            for layer in data_source:
                layer_names.append(layer.name)
                # 4.3. Check if the layer already exists, if so, use it instead of creating a new one
                layer_model = None
                if DatasetLayer.objects.filter(name=layer.name, dataset=instance).exists():
                    layer_model = DatasetLayer.objects.get(name=layer.name, dataset=instance)
                else:
                    layer_model = DatasetLayer(
                        name=layer.name,
                        dataset=instance
                    )

                # 4.4 Find the srid of the layer
                # Assume that the default projection is 2154, since most of the data is in France
                # Eventually, this should be replaced by a user-defined projection
                srid = layer.srs.srid if layer.srs.srid is not None else 2154

                # 4.4 Generate the bounding box
                bounding_box = Polygon.from_bbox(layer.extent.tuple)

                bounding_box.srid = srid
                layer_model.bounding_box = bounding_box

                # 4.5 Save the srid and the feature count
                layer_model.srid = srid
                layer_model.feature_count = layer.num_feat
                layer_model.geometry_type = layer.geom_type.name

                # 4.6 Save the layer object (which will trigger the regeneration of the layer's geometries)
                layer_model.save()

                # 4.7 Generate the fields of the layer
                # 4.7.1 First, delete all the fields of the layer
                layer_model.fields.all().delete()

                # 4.7.2 Then, generate the fields
                for field in layer.fields:
                    field_type  = layer.field_types[layer.fields.index(field)]
                    field_width = layer.field_widths[layer.fields.index(field)]
                    precision   = layer.field_precisions[layer.fields.index(field)]
                    geometry    = layer.geom_type.name

                    field_model = DatasetLayerField(
                        name=field,
                        type=field_type.__name__,
                        max_length=field_width,
                        precision=precision,
                        layer=layer_model
                    )
                    field_model.save()
# End def generate_layers

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
def generate_dataset_category_slug(sender, instance, **kwargs):
    """Generate the slug for the resource"""
    instance.slug = slugify(instance.name)
# End def generate_dataset_category_slug


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

    # ----- Identification -----

    id = models.AutoField(primary_key=True)
    slug = models.CharField(max_length=200, null=True, default=None)

    # ----- Description -----

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

    def get_absolute_url(self):
        return f"/dataset/{self.slug}"
    # End def get_absolute_url

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
def generate_dataset_slug(sender, instance, **kwargs):
    """Generate the slug for the resource"""
    instance.slug = slugify(instance.name)
# End def generate_dataset_slug


# ======================================================================================================================
# Helper methods
# ======================================================================================================================




