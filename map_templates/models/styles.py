# -*- coding: utf-8 -*-
"""
Models related to styles for the `map_templates` application.
"""
from colorfield.fields import ColorField
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from map_templates.validators import validate_dash_array


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
