# -*- coding: utf-8 -*-
"""
Models related to fill patterns for the `map_templates` application.
"""
from colorfield.fields import ColorField
from django.contrib import admin
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


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