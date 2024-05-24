# -*- coding: utf-8 -*-
"""
Models related to filters for the `map_templates` application.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _

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