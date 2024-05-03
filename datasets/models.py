# -*- coding: utf-8 -*-
"""
Models for the `datasets` application.
"""
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
from django.utils.translation import gettext_lazy as _

from common.utils.tasks import TaskStatus
from datasets import tasks
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
# Feature Model
# ======================================================================================================================

class Feature(models.Model):
    """Represents a geographic feature in a dataset."""

    # ------------------------------------------------------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------------------------------------------------------

    # ----- Identification -----

    id = models.AutoField(primary_key=True)

    # ----- Parent -----

    layer = models.ForeignKey(
        'DatasetLayer',
        on_delete=models.CASCADE,
        related_name='features'
    )

    # ----- Properties -----

    geometry = gis_models.GeometryField()
    fields = models.JSONField()

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def type(self) -> str:
        """Get the type of the feature."""
        return self.layer.geometry_type
    # End def type

    def get_field(self, field_name : str, **kwargs) -> any:
        """Get the value of a field of the feature.

        Keyword Args:
            default (any): The default value to return if the field does not exist.
        """
        if 'default' in kwargs:
            raw_field = self.fields.get(field_name, kwargs['default'])
        else: # If no default value is provided, a missing field will raise a KeyError
            raw_field = self.fields.get(field_name)

        # If the field does not exist, return None
        if raw_field is None:
            return None

        # Else fetch the type of the field and convert it to the appropriate type
        field_type = self.layer.fields.get(name=field_name).python_type()
        return field_type(raw_field)
    # End def get_field

    def __str__(self):
        return f"Feature {self.id} of {self.layer.name}"
    # End def __str__

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        verbose_name = _("Geographic Feature")
        verbose_name_plural = _("Geographic Features")
    # End class Meta
# End class Feature

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
        max_length=255,
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
        verbose_name=_("Max length"),
        help_text=_("Maximum length of the text field."),
        validators=[MinValueValidator(0)]
    )

    precision = models.IntegerField(
        null=True,
        blank=True,
        default=None,
        verbose_name=_("Precision"),
        help_text=_("Number of decimal places."),
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
        verbose_name = _("Dataset Layer Field")
        verbose_name_plural = _("Dataset Layer Fields")
        unique_together = ['name', 'layer']
    # End class Meta

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return f"{self.layer} -> {self.name}"
    # End def __str__
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
        max_length=255,
        blank=True,
        null=True,
        default=None,
        verbose_name=_("Layer name"),
        help_text=_("Name of the layer of the dataset.")
    )

    srid = models.IntegerField(
        blank=True,
        null=True,
        default=None,
        verbose_name="SRID", # No need for translation
        help_text=_("SRID (SRS) of the layer of the dataset.")
    )

    bounding_box = gis_models.PolygonField(
        blank=True,
        null=True,
        default=None,
        verbose_name=_("Bounding box"),
        help_text=_("Bounding box of the layer of the dataset.")
    )

    feature_count = models.IntegerField(
        blank=True,
        null=True,
        default=None,
        verbose_name=_("Feature count"),
        help_text=_("Number of features in the layer."),
        validators=[MinValueValidator(0)]
    )

    geometry_type = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        default=None,
        verbose_name=_("Geometry type"),
        help_text=_("Type of the geometries in the layer.")
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return f"{self.dataset} - {self.name}"
    # End def __str__

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        verbose_name = _("Dataset Layer")
        verbose_name_plural = _("Dataset Layers")
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
        help_text=_("Date of the version of the dataset.")
    )

    # ----- File -----

    file = models.FileField(
        upload_to=dataset_version_filepath,
        verbose_name=_("File"),
        help_text=_("File containing the dataset."),
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
        verbose_name=_("Encoding"),
        help_text=_("Encoding of the dataset file.")
    )

    # ----- Task-related fields -----

    task_id = models.UUIDField(
        blank=True,
        null=True,
        default=None,
        verbose_name=_("Task ID"),
        help_text=_("ID of the task that generates the geographic features.")
    )

    task_status = models.CharField(
        max_length=25,
        blank=True,
        null=True,
        default=None,
        choices=TaskStatus,
        verbose_name=_("Task status"),
        help_text=_("Status of the task that generates the geographic features.")
    )

    regenerate = models.BooleanField(
        default=False,
        verbose_name=_("Regenerate"),
        help_text=_("Regenerate the geographic features of the dataset.")
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
        return f"{self.dataset.name} (v{self.get_version_number()})"
    # End def __str__

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        verbose_name = _("Dataset Version")
        verbose_name_plural = _("Dataset Versions")
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

                    field_model = DatasetLayerField(
                        name=field,
                        type=field_type.__name__,
                        max_length=field_width,
                        precision=precision,
                        layer=layer_model
                    )
                    field_model.save()

    # 4.8 Generate the features of the layer on creation, or if the `regenerate` field is set to True
    if instance.regenerate is True or kwargs.get('created', False) is True:
        # If there is already a task running, revoke it and start a new one
        if instance.task_id is not None:
            tasks.generate_features_task.AsyncResult(str(instance.task_id)).revoke()
        tasks.generate_features_task.delay(instance.id)
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

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_("Category name"),
        help_text=_("Name of the category of the dataset.")
    )

    icon = models.FileField(
        upload_to='datasets/category_icons',
        verbose_name=_("Icon"),
        help_text=_("Icon of the dataset category. Must be a monochromatic SVG file (black, transparent background).")
    )
    slug = models.SlugField(
        max_length=200,
        null=True,
        default=None
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return self.name
    # End def __str__

    def clean(self):
        if not SVG_REGEX.match(self.icon.file.read().decode('latin-1')):
            raise ValidationError(_("The icon must be a monochromatic SVG file."))

        # Set the slug
        self.slug = slugify(self.name)
    # End def clean

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        verbose_name = _("Dataset Category")
        verbose_name_plural = _("Dataset Categories")
        ordering = ['name']
    # End class Meta
# End class DatasetCategory


# ======================================================================================================================
# DatasetTechnicalInformation Model
# ======================================================================================================================

class DatasetTechnicalInformation(models.Model):
    """A piece of technical information about a dataset."""

    # ------------------------------------------------------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------------------------------------------------------

    id = models.AutoField(primary_key=True)

    key = models.CharField(
        max_length=100,
        verbose_name=_("Key"),
        help_text=_("Sorting key of the technical information.")
    )

    value = models.CharField(
        max_length=250,
        verbose_name=_("Value"),
        help_text="Valeur de l'information technique."
    )
    dataset = models.ForeignKey(
        'Dataset',
        on_delete=models.CASCADE,
        related_name='technical_information',
        verbose_name=_("Dataset"),
        help_text=_("Dataset to which the technical information is related.")
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
        verbose_name=_("Dataset Name"),
        help_text=_("Name of the dataset.")
    )

    public = models.BooleanField(
        default=True,
        verbose_name=_("Public"),
        help_text=_("Whether the dataset is public or not.")
    )

    categories = models.ManyToManyField(
        'DatasetCategory',
        blank=True,
        verbose_name=_("Categories"),
        help_text=_("Categories of the dataset.")
    )

    short_desc = models.TextField(
        max_length=400,
        blank=True,
        null=True,
        default=None,
        verbose_name=_("Short description"),
        help_text=_("Short description of the dataset, displayable as summary (max: 400 characters, optional).")
    )

    description = models.TextField(
        blank=True,
        null=True,
        default=None,
        verbose_name=_("Description"),
        help_text=_("Description of the dataset (optional).")
    )

    source = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        default=None,
        verbose_name=_("Source"),
        help_text=_("Source from which the dataset was obtained (optional).")
    )

    last_update = models.DateField(
        auto_now=True,
        verbose_name=_("Last update"),
        help_text=_("Date of the last update of the dataset.")
    )

    language = models.CharField(
        max_length=30,
        blank=True,
        null=True,
        default=None,
        verbose_name=_("Language"),
        help_text=_("Primary language of the dataset (optional).")
    )

    license = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        default=None,
        verbose_name=_("License"),
        help_text=_("License of the dataset (optional).")
    )

    usage_restrictions = models.TextField(
        blank=True,
        null=True,
        default=None,
        verbose_name=_("Usage restrictions"),
        help_text=_("Restrictions on the usage of the dataset (optional).")
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

    def get_version(self, version_number : int) -> DatasetVersion:
        """Return the version of the dataset file with the given version number."""
        if version_number < 1:
            raise ValueError("The version number must be greater than 0.")
        if version_number > self.versions.count():
            raise DatasetVersion.DoesNotExist(f"The dataset does not have a version number {version_number}.")

        return self.versions.order_by('date')[version_number - 1]
    # End def get_version

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
