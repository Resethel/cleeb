# -*- coding: utf-8 -*-
"""
Models for the `map_templates` application.
"""
from colorfield.fields import ColorField
from django.contrib import admin
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils.translation import gettext as _
from xyzservices import TileProvider

from common.utils.tasks import TaskStatus
from map_templates import tasks
from map_templates.services.templates import MapTemplate as MapTemplateObject
from map_templates.validators import validate_dash_array

# ======================================================================================================================
# Constants
# ======================================================================================================================

MIN_ZOOM = 5
MAX_ZOOM = 18

# ======================================================================================================================
# Tile
# ======================================================================================================================

class TileLayer(models.Model):
    """Represents a Leaflet/Folium tile layer."""

    # ID of the tile
    id = models.AutoField(primary_key=True)

    # Name of the tile
    name = models.CharField(
        unique=True,
        max_length=100,
        verbose_name=_("Name"),
        help_text=_("The name of the tile layer.")
    )

    verbose_name = models.CharField(
        unique=True,
        max_length=100,
        default=None,
        blank=True,
        null=True,
        verbose_name=_("Verbose Name"),
        help_text=_("The verbose name of the tile layer.")
    )

    transparent = models.BooleanField(
        default=False,
        verbose_name=_("Transparent"),
        help_text=_("Whether the tile layer is transparent, i.e., has an alpha channel.")
    )

    overlay = models.BooleanField(
        default=True,
        verbose_name=_("Overlay"),
        help_text=_("Whether the tile layer is an overlay, i.e., can be superimposed on other layers.")
    )

    control = models.BooleanField(
        default=True,
        verbose_name=_("Show in Layer Control"),
        help_text=_("Whether the tile layer should be shown in the layer control.")
    )

    type = models.CharField(
        max_length=7,
        choices=[
            ('builtin', _("Built-in")),
            ('xyz', 'XYZ')
        ],
        default='folium',
        verbose_name=_("Type"),
        help_text=_("The type of the tile layer. If 'folium', the tile is managed by Folium and the other fields are ignored.")
    )

    # URL of the tile
    url = models.URLField(
        max_length=500,
        default=None,
        blank=True,
        null=True,
        verbose_name=_("URL"),
        help_text=_("The XYZ URL of the tile layer.")
    )


    # Attribution of the tile
    attribution = models.CharField(
        max_length=200,
        default=None,
        blank=True,
        null=True,
        verbose_name=_("Attribution"),
        help_text=_("The attribution (credits) of the tile layer.")
    )

    # Access token of the tile (if any)
    access_token = models.CharField(
        max_length=100,
        default=None,
        blank=True,
        null=True,
        verbose_name=_("Access Token"),
        help_text=_(
            "Some tile providers require an access token to access their tiles. "
            "This field should be empty if no access token is required."
        )
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return self.name

    def clean(self):

        # First, call the parent clean method
        super().clean()

        # For built-in tiles, the URL and the attribution should be empty
        if self.type == "builtin":
            self.url = None
            self.attribution = None
            self.access_token = None
            return

        if self.url is None or self.url == "":
            raise ValidationError(_("An URL is required for XYZ tiles."))
        if self.attribution is None or self.attribution == "":
            raise ValidationError(_("An attribution is required for XYZ tiles."))

        # Check if the access token is required
        temp_provider : TileProvider = TileProvider(
            name=self.name,
            url=self.url,
            attribution=self.attribution
        )

        # Check if the access token is required
        requires_token = temp_provider.requires_token()
        if not requires_token:
            # If the access token is not required, it should be empty to avoid confusion
            self.access_token = None
        # If it is required, check if it is provided
        elif self.access_token is None or self.access_token == "":
            raise ValidationError(_("An access token is required for the tile '{name}@{url}'.").format(
                name=self.name,
                url=self.url
            ))
        # If it is provided, check if it is valid
        else:
            temp_provider["accessToken"] = self.access_token
            if temp_provider.requires_token(): # requires_token() should return False if the token is valid
                raise ValidationError(_("The access token provided is invalid for the tile '{name}@{url}'.").format(
                    name=self.name,
                    url=self.url
                ))

        # The url can be quite long, so it is splittable in multiple lines in the admin
        # So we must make sure that no line break is present in the URL
        if self.url is not None:
            self.url = self.url.replace("\n", "")
            self.url = self.url.replace("\r", "")
            self.url = self.url.replace("\t", "")
            self.url = self.url.strip()
            self.url = self.url.replace(" ", "")
    # End def clean

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        verbose_name = _("Tile Layer")
        verbose_name_plural = _("Tile Layers")
    # End class Meta
# End class TileLayer

@receiver(pre_save, sender=TileLayer)
def fill_missing_verbose_name(sender, instance, **kwargs):
    """If the verbose name is not set, fill it with the name."""
    if instance.verbose_name is None or instance.verbose_name == "":
        instance.verbose_name = instance.name.title()
# End def fill_missing_verbose_name

# ======================================================================================================================
# FillPatterns
# ======================================================================================================================

class FillPattern(models.Model):
    """Represent a Leaflet pattern."""

    # ------------------------------------------------------------------------------------------------------------------
    # Identification fields
    # ------------------------------------------------------------------------------------------------------------------

    id = models.AutoField(primary_key=True)

    # ------------------------------------------------------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------------------------------------------------------

    color = ColorField(
        default="#000000FF",
        format="hexa",
        verbose_name=_("Color"),
        help_text=_("The color of the fill pattern.")
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Non-persistent fields
    # ------------------------------------------------------------------------------------------------------------------

    @property
    @admin.display(description=_("Opacity"))
    def opacity(self) -> float:
        return int(self.color[7:9], 16) / 255
    # End def opacity

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        abstract = True
    # End class Meta
# End class FillPattern

class StripePattern(FillPattern):
    """ Represents a Leaflet stripe pattern. """

    # ------------------------------------------------------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------------------------------------------------------

    space_color = ColorField(
        default="#FFFFFFFF",
        format="hexa",
        verbose_name=_("Space Color"),
        help_text=_("The color of the spaces between the stripes.")
    )

    # Stripe width
    weight = models.IntegerField(
        default=4,
        validators=[
            MinValueValidator(0.0)
        ],
        verbose_name=_("Stripe Width"),
        help_text=_("The width of the stripes (in pixels).")
    )

    space_weight = models.IntegerField(
        default=4,
        validators=[
            MinValueValidator(0.0)
        ],
        verbose_name=_("Space Width"),
        help_text=_("The width of the spaces between the stripes (in pixels).")
    )

    angle = models.FloatField(
        default=0.5,
        validators=[
            MinValueValidator(-360.0),
            MaxValueValidator(360.0)
        ],
        verbose_name=_("Angle"),
        help_text=_("The angle of the stripes, in degrees, from an horizontal eastward line).")
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Non-persistent fields
    # ------------------------------------------------------------------------------------------------------------------

    @property
    @admin.display(description=_("Space Opacity"))
    def space_opacity(self) -> float:
        return int(self.space_color[7:9], 16) / 255
    # End def space_opacity

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return f"StripePattern@{self.id}"
    # End def __str__

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------
    class Meta:
        verbose_name = _("Stripe Pattern")
        verbose_name_plural = _("Stripe Patterns")
    # End class Meta
# End class StripePattern

class CirclePattern(FillPattern):

    # ------------------------------------------------------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------------------------------------------------------

    width = models.IntegerField(
        default=4,
        validators=[
            MinValueValidator(0.0)
        ],
        verbose_name=_("Horizontal Space"),
        help_text=_("The horizontal distance between the circles (in pixels).")
    )

    height = models.IntegerField(
        default=4,
        validators=[
            MinValueValidator(0.0)
        ],
        verbose_name=_("Vertical Space"),
        help_text=_("The vertical distance between the circles (in pixels).")
    )

    radius = models.IntegerField(
        default=12,
        validators=[
            MinValueValidator(0.0)
        ],
        verbose_name=_("Radius"),
        help_text=_("The radius of the circles (in pixels).")
    )

    fill_color = ColorField(
        default="#3388FF33",
        format="hexa",
        verbose_name=_("Fill Color"),
        help_text=_("The fill color of the circles.")
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Non-persistent fields
    # ------------------------------------------------------------------------------------------------------------------

    @property
    @admin.display(description=_("Fill Opacity"))
    def fill_opacity(self) -> float:
        return int(self.fill_color[7:9], 16) / 255
    # End def fill_opacity

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return f"CirclePattern@{self.id}"
    # End def __str__

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        verbose_name = _("Circle Pattern")
        verbose_name_plural = _("Circle Patterns")
    # End class Meta
# End class CirclePattern

# ======================================================================================================================
# Styles
# ======================================================================================================================

class BaseStyle(models.Model):
    """Represents a Leaflet style."""

    # ID of the style
    id = models.AutoField(primary_key=True)

    # ------------------------------------------------------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------------------------------------------------------

    stroke = models.BooleanField(
        default=True,
        verbose_name=_("Enable shape's borders"),
        help_text=_("Whether the shapes border should be drawn.")
    )

    # Color of the style
    color = ColorField(
        default='#3388ffff',
        format="hexa",
        verbose_name=_("Color"),
        help_text=_("The color of the shape.")
    )

    # Weight of the style
    weight = models.FloatField(
        default=3,
        validators=[
            MinValueValidator(0.0)
        ],
        verbose_name=_("Border Width"),
        help_text=_("The width of the shape's border (in pixels).")
    )

    # Line cap of the style
    line_cap = models.CharField(
        max_length=6,
        choices=[
            ("butt"  , _("Butt")),
            ("round" , _("Round")),
            ("square", _("Square"))
        ],
        default="round",
        verbose_name=_("Line Cap"),
        help_text=_("The cap of the shape's border. Butt: flat ends (i.e., no cap); Round: rounded ends; Square: square ends.")
    )

    # Line join of the style
    line_join = models.CharField(
        max_length=10,
        choices=[
            ("arcs"      , _("Arcs")),
            ("bevel"     , _("Bevel")),
            ("miter"     , _("Miter")),
            ("miter-clip", _("Miter-Clip")),
            ("round"     , _("Round"))
        ],
        default="round",
        verbose_name=_("Line Join"),
        help_text=_(
            "The join of the shape's border. "
            "Arcs: arcs between the lines; "
            "Bevel: beveled corners; "
            "Miter: mitered corners; "
            "Miter-Clip: mitered corners with clipping; "
            "Round: rounded corners."
        )
    )

    # Dash array of the style
    dash_array = models.CharField(
        max_length=50,
        default=None,
        blank=True,
        null=True,
        validators=[validate_dash_array],
        verbose_name=_("Border dashes"),
        help_text=_(
            "The dash pattern of the shape's border. "
            "A list of space-separated values that specify distances to alternately draw a line and a gap. "
        )
    )

    # Dash offset of the style
    dash_offset = models.CharField(
        max_length=5,
        default=None,
        blank=True,
        null=True,
        verbose_name=_("Border dashes' offset"),
        help_text=_("The offset between the dashes of the shape's border.")
    )

    # Fill of the style
    fill = models.BooleanField(
        default=True,
        verbose_name=_("Enable shape's fill"),
        help_text=_("Whether the shape should be filled.")
    )

    # Fill color of the style
    fill_color = ColorField(
        default='#3388ff33',
        format="hexa",
        blank=True,
        null=True,
        verbose_name=_("Fill Color"),
        help_text=_("The color of the shape's fill. If not set, the shape will use the color of the border.")
    )

    # Fill rule of the style
    fill_rule = models.CharField(
        max_length=100,
        choices=[
            ("nonzero", _("Nonzero")),
            ("evenodd", _("Even-Odd"))
        ],
        default='evenodd',
        verbose_name=_("Fill Rule"),
        help_text=_(
            "The fill rule of the shape. "
            "Nonzero: the shape is filled if the winding number is not zero; "
            "Even-Odd: the shape is filled if the winding number is odd."
        )
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Pattern fields
    # ------------------------------------------------------------------------------------------------------------------

    circle_pattern = models.OneToOneField(
        'CirclePattern',
        related_name='%(class)s',
        on_delete=models.SET_NULL,
        default=None,
        blank=True,
        null=True
    )

    stripe_pattern = models.OneToOneField(
        'StripePattern',
        related_name='%(class)s',
        on_delete=models.SET_NULL,
        default=None,
        blank=True,
        null=True
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Non-persistent fields
    # ------------------------------------------------------------------------------------------------------------------

    @property
    @admin.display(description=_("Opacity"))
    def opacity(self) -> float:
        return int(self.color[7:9], 16) / 255
    # End def opacity

    @property
    @admin.display(description=_("Fill Opacity"))
    def fill_opacity(self) -> float:
        return int(self.fill_color[7:9], 16) / 255
    # End def fill_opacity

    @property
    @admin.display(description=_("Fill Pattern"))
    def fill_pattern(self):
        if self.circle_pattern is not None:
            return self.circle_pattern
        if self.stripe_pattern is not None:
            return self.stripe_pattern
        return None
    # End def fill_pattern

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return f"Style@{self.id}"
    # End def __str__

    def clean(self):
        super().clean()
        if self.stroke is False and self.fill is False:
            raise ValidationError(_("The style cannot have both the stroke and the fill disabled."))

        if self.circle_pattern is not None and self.stripe_pattern is not None:
            raise ValidationError(
                _("The style cannot be filled by both a circle pattern and a stripe pattern."),
                params={
                    "circle_pattern": self.circle_pattern,
                    "stripe_pattern": self.stripe_pattern
                }
            )
    # End def clean

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        abstract = True
    # End class Meta
# End class BaseStyle

class Style(BaseStyle):

    # ------------------------------------------------------------------------------------------------------------------
    # Admin display
    # ------------------------------------------------------------------------------------------------------------------

    @admin.display(description=_("Type"))
    def style_type(self):
        if hasattr(self, "style_of") and self.style_of is not None:
            return _("Style")
        if hasattr(self, "highlight_of") and self.highlight_of is not None:
            return _("Highlight")
        return _("Unknown")
    # End def style_type

    @admin.display(description=_("Owner"))
    def owning_layer(self):
        if hasattr(self, "style_of") and isinstance(self.style_of, Layer):
            return str(self.style_of)
        if hasattr(self, "highlight_of") and isinstance(self.highlight_of, Layer):
            return str(self.highlight_of)
        return _("Orphaned")


    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return f"Style@{self.id}"
    # End def __str__

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        verbose_name = _("Style")
        verbose_name_plural = _("Styles")
# End class LayerStyle

class PropertyStyle(BaseStyle):

    # ------------------------------------------------------------------------------------------------------------------
    # Parent fields
    # ------------------------------------------------------------------------------------------------------------------

    style = models.ForeignKey(
        'Style',
        related_name='property_styles',
        on_delete=models.CASCADE,
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Filter fields
    # ------------------------------------------------------------------------------------------------------------------

    key = models.CharField(max_length=100)
    value = models.CharField(max_length=100)
    value_type = models.CharField(
        max_length=10,
        choices=[
            ("string", _("String")),
            ("number", _("Number")),
            ("boolean", _("Boolean"))
        ],
        default="string"
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return f"PropertyStyle[{self.key}={self.value}]@{self.id}"
    # End def __str__

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        verbose_name = _("Property's Style")
        verbose_name_plural = _("Properties' Styles")
# End class PropertyStyle


# ======================================================================================================================
# Filter
# ======================================================================================================================

class Filter(models.Model):

    # ID of the filter
    id = models.AutoField(primary_key=True)

    # ------------------------------------------------------------------------------------------------------------------
    # Ownership fields
    # ------------------------------------------------------------------------------------------------------------------

    layer = models.ForeignKey(
        'Layer',
        related_name='filters',
        on_delete=models.CASCADE,
        default=None,
        blank=True,
        null=True
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------------------------------------------------------

    key = models.CharField(max_length=100)

    # Operator of the filter
    operator = models.CharField(
        max_length=100,
        choices=[
            ("==", "=="),
            ("!=", "!="),
            (">", ">"),
            (">=", ">="),
            ("<", "<"),
            ("<=", "<=")
        ]
    )

    # Value of the filter
    value = models.CharField(max_length=100)
    value_type = models.CharField(
        max_length=10,
        choices=[
            ("string", _("String")),
            ("number", _("Number")),
            ("boolean", _("Boolean"))
        ],
        default="string"
    )


    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return f"Filter[{self.key}{self.operator}{self.value}]@{self.id}"
    # End def __str__

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        verbose_name = _("Filter")
        verbose_name_plural = _("Filters")
        unique_together = ('layer', 'key', 'operator', 'value')
    # End class Meta
# End class Filter

# ======================================================================================================================
# Tooltip
# ======================================================================================================================

class TooltipField(models.Model):

    # ------------------------------------------------------------------------------------------------------------------
    # Ownership field
    # ------------------------------------------------------------------------------------------------------------------

    tooltip = models.ForeignKey(
        'Tooltip',
        on_delete=models.CASCADE,
        related_name='fields'
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------------------------------------------------------

    field = models.ForeignKey(
        'datasets.DatasetLayerField',
        on_delete=models.CASCADE
    )

    alias = models.CharField(
        max_length=255,
        verbose_name=_("Alias"),
        help_text=_("The alias of the field in the tooltip."),
    )

    index = models.IntegerField(
        default=0,
        verbose_name=_("Index"),
        help_text=_("The index of the field in the tooltip."),
        validators=[
            MinValueValidator(0)
        ]
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        verbose_name = _("Tooltip Field")
        verbose_name_plural = _("Tooltip Fields")
        unique_together = ('tooltip', 'field')
    # End class Meta

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def clean(self):
        super().clean()
        if self.tooltip.layer.dataset_layer != self.field.layer:
            raise ValidationError(
                _("The tooltip field must belong to the same dataset layer as the tooltip."),
                params={
                    "tooltip_layer": self.tooltip.layer,
                    "field_layer": self.field.layer
                }
            )
    # End def clean
# End class TooltipField

class Tooltip(models.Model):

    # ------------------------------------------------------------------------------------------------------------------
    # Identification and ownership fields
    # ------------------------------------------------------------------------------------------------------------------

    id = models.AutoField(primary_key=True)

    layer = models.OneToOneField(
        'Layer',
        on_delete=models.CASCADE,
        related_name='tooltip'
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------------------------------------------------------

    # Relation to `TooltipField` is defined in the `TooltipField` model

    sticky = models.BooleanField(
        default=True,
        verbose_name=_("Sticky"),
        help_text=_("Whether the tooltip should stick to the mouse cursor.")
    )

    style = models.TextField(
        default=None,
        blank=True,
        null=True,
        verbose_name=_("Style"),
        help_text=_("The CSS style of the tooltip.")
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return f"Tooltip@{self.id}"
    # End def __str__

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        verbose_name = _("Tooltip")
        verbose_name_plural = _("Tooltips")
    # End class Meta
# End class Tooltip


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

# ======================================================================================================================
# Map template
# ======================================================================================================================

class MapTemplate(models.Model):
    """Represents a map template.

    Used by the map creator to render a Leaflet map with the desired layers and features.
    Once defined, the map template is validated and saved in the database.
    A routine then generates the corresponding HTML file to be used in the web application.
    """

    # ID of the map template
    id = models.AutoField(primary_key=True)

    # Name of the map template
    name = models.CharField(
        unique=True,
        max_length=100,
        verbose_name=_("Name"),
        help_text=_("The name of the map template.")
    )

    # Zoom start of the map template
    zoom_start = models.SmallIntegerField(
        default=int(MIN_ZOOM + 2/3 * (MAX_ZOOM - MIN_ZOOM)),
        validators=[
            MinValueValidator(MIN_ZOOM),
            MaxValueValidator(MAX_ZOOM)
        ],
        verbose_name=_("Zoom Level at startup"),
        help_text=_("The zoom level of the map at startup.")
    )

    # Center of the map template
    # Defaults to Metz, France: lat=49.119308, lon=6.175715 (because why not?)
    center = gis_models.PointField(
        default=Point(6.175715, 49.119308, srid=4326),
        srid=4326, # Keep the SRID to 4326 for compatibility with Leaflet
        verbose_name=_("Center"),
        help_text=_("The center of the map at startup.")
    )

    # Enable layer control of the map template
    layer_control = models.BooleanField(
        default=True,
        verbose_name=_("Enable Layer Control"),
        help_text=_("Whether the layer control should be enabled.")
    )

    # Enable zoom control of the map template
    zoom_control = models.BooleanField(
        default=True,
        verbose_name=_("Enable Zoom Control"),
        help_text=_("Whether the zoom control should be enabled.")
    )

    # Tiles to load on the map
    tiles = models.ManyToManyField(
        'TileLayer',
        verbose_name=_("Tiles"),
        help_text=_("The tiles to load on the map.")
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Task specific fields
    # ------------------------------------------------------------------------------------------------------------------

    task_id = models.UUIDField(
        blank=True,
        null=True,
        default=None,
        verbose_name=_("Task ID"),
        help_text=_("ID of the task generating the map render.")
    )

    task_status = models.CharField(
        max_length=25,
        blank=True,
        null=True,
        default=None,
        choices=TaskStatus,
        verbose_name=_("Task Status"),
        help_text=_("Status of the task generating the map render.")
    )

    regenerate = models.BooleanField(
        default=False,
        verbose_name=_("Regenerate"),
        help_text=_("Whether the map render should be regenerated.")
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return self.name

    def as_template_object(self) -> MapTemplateObject:
        """Returns the map template object."""
        return MapTemplateObject.from_model(self)
    # End def as_template_object

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        verbose_name = _("Map Template")
        verbose_name_plural = _("Map Templates")
    # End class Meta
# End class MapTemplate


@receiver(post_save, sender=MapTemplate)
def generate_map_render(sender, instance, created, **kwargs):
    """Generate the render of the map template."""
    if created:
        tasks.generate_maprender_from_maptemplate_task.delay(instance.id)
    elif instance.regenerate:
        # Revoke the previous task to avoid multiple renders
        if instance.task_id is not None:
            tasks.generate_maprender_from_maptemplate_task.AsyncResult(str(instance.task_id)).revoke()
        tasks.generate_maprender_from_maptemplate_task.delay(instance.id)
# End def generate_map_render