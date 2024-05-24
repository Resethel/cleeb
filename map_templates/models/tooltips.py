# -*- coding: utf-8 -*-
"""
Models related to tooltips for the `map_templates` application.
"""
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

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

