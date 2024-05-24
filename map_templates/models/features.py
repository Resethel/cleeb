# -*- coding: utf-8 -*-
"""
Models related to features for the `map_templates` application.
"""
from django.contrib.gis.db import models as gis_models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

# ======================================================================================================================
# MapFeatures
# ======================================================================================================================

# TODO: Add an abstract class for the map features

class Layer(models.Model):
    """Represents a map layer.

    A map layer is a layer of data that can be shown or hidden on the map.
    The map layer to load is defined by its name in the database.
    """

    # ------------------------------------------------------------------------------------------------------------------
    # Identification fields
    # ------------------------------------------------------------------------------------------------------------------

    # ID of the layer
    id = models.AutoField(primary_key=True)

    # ------------------------------------------------------------------------------------------------------------------
    # Ownership fields
    # ------------------------------------------------------------------------------------------------------------------

    owner_feature_group = models.ForeignKey(
        'FeatureGroup',
        related_name='layers',
        on_delete=models.CASCADE,
        default=None,
        blank=True,
        null=True
    )

    owner_map_template = models.ForeignKey(
        'MapTemplate',
        related_name='layers',
        on_delete=models.CASCADE,
        default=None,
        blank=True,
        null=True
    )

    @property
    def owner(self):
        if self.owner_feature_group is not None:
            return self.owner_feature_group
        elif self.owner_map_template is not None:
            return self.owner_map_template
        else:
            return None
    # End def owner

    # ------------------------------------------------------------------------------------------------------------------
    # Metadata Fields
    # ------------------------------------------------------------------------------------------------------------------

    # Name of the layer
    name = models.CharField(
        max_length=100,
        verbose_name=_("Name"),
        help_text=_("The name of the layer.")
    )

    show = models.BooleanField(
        default=True,
        verbose_name=_("Show on Startup"),
        help_text=_("Whether the display of the layer should be enabled at startup.")
    )

    z_index = models.IntegerField(
        default=0,
        verbose_name=_("Z-index"),
        help_text=_(
            "The index defining the display order of the layers. "
            "The higher the index, the more the layer is displayed in the foreground."
        ),
        validators=[
            MinValueValidator(0)
        ]
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Dataset relations Fields
    # ------------------------------------------------------------------------------------------------------------------

    # Dataset Layer to load
    dataset_layer = models.ForeignKey(
        'datasets.DatasetLayer',
        on_delete=models.SET_NULL,
        default=None,
        blank=True,
        null=True,
        verbose_name=_("Dataset Layer"),
    )

    # Boundaries of the layer
    boundaries = gis_models.MultiPolygonField(
        blank=True,
        null=True,
        default=None,
        verbose_name=_("Boundaries"),
        help_text=_("The boundaries of the layer. Any feature outside these boundaries will not be processed.")
    )

    boundary_type = models.CharField(
        max_length=15,
        choices=[
            ("intersect", _("Intersect")),
            ("strict", _("Strict")),
            ("crop", _("Crop"))
        ],
        default="intersect",
        verbose_name=_("Boundary Type"),
        help_text=_(
            "Defines how the boundaries should be used. "
            "Intersect: any features intersecting or within the boundaries are kept in their entirety; "
            "Strict: only features completely within the boundaries are kept; "
            "Crop: any features intersecting the boundaries are cropped to fit within the boundaries, features outside are removed."
        )
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Style Fields
    # ------------------------------------------------------------------------------------------------------------------

    style = models.OneToOneField(
        'Style',
        related_name='style_of',
        on_delete=models.SET_NULL,
        default=None,
        blank=True,
        null=True
    )

    highlight = models.OneToOneField(
        'Style',
        related_name='highlight_of',
        on_delete=models.SET_NULL,
        default=None,
        blank=True,
        null=True
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        verbose_name = _("Layer")
        verbose_name_plural = _("Layers")

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
       return f"Layer[{self.name}]@{self.id}"
    # End def __str__

    def clean(self):
        if self.owner_feature_group is None and self.owner_map_template is None:
            raise ValidationError(_("The layer must belong to a feature group or a map template."))
        if self.owner_feature_group is not None and self.owner_map_template is not None:
            raise ValidationError(_("The layer cannot belong to both a feature group and a map template."))
    # End def clean

    def has_tooltip(self) -> bool:
        """Returns True if the layer has a tooltip, False otherwise."""
        return hasattr(self, "tooltip") and self.tooltip is not None
    # End def has_tooltip
# End class Layer

class FeatureGroup(models.Model):
    """Represents a group of features on the map.

    A feature group is a group of features that can be shown or hidden on the map.
    The feature group to load is defined by its name in the database.
    """

    # ID of the feature group
    id = models.AutoField(primary_key=True)

    # Name of the feature group
    name = models.CharField(
        max_length=100,
        verbose_name=_("Name"),
        help_text=_("The name of the feature group.")
    )

    # Related map template
    map_template = models.ForeignKey(
        'MapTemplate',
        related_name='feature_groups',
        on_delete=models.CASCADE,
        verbose_name=_("Parent Map Template"),
        help_text=_("The map template to which the feature group belongs.")
    )

    overlay = models.BooleanField(
        default=True,
        verbose_name=_("Is an Overlay"),
        help_text=_("Whether the feature group is an overlay, i.e., can be superimposed on other layers.")
    )

    control = models.BooleanField(
        default=True,
        verbose_name=_("Show in Layer Control"),
        help_text=_("Whether the feature group should be shown in the layer control.")
    )

    show_on_startup = models.BooleanField(
        default=False,
        verbose_name=_("Show on Startup"),
        help_text=_("Whether the display of the feature group should be enabled at startup.")
    )

    z_index = models.IntegerField(
        default=0,
        verbose_name=_("Z-index"),
        help_text=_(
            "The index defining the display order of the feature groups. "
            "The higher the index, the more the feature group is displayed in the foreground."
        ),
        validators=[
            MinValueValidator(0)
        ]
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return f"FeatureGroup[{self.name}]@{self.id}"

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        verbose_name = _("Feature Group")
        verbose_name_plural = _("Feature Groups")
    # End class Meta
# End class FeatureGroup