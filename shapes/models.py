from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


# ======================================================================================================================
# Shape: represents a GeoJSON shape.
# ======================================================================================================================

class Shape(models.Model):
    """
    This class represents a GeoJSON shape.
    """

    # ------------------------------------------------------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------------------------------------------------------

    id = models.BigAutoField(
        primary_key=True,
        verbose_name="ID",
        help_text="L'ID de la géométrie GeoJSON.",
    )

    feature_type = models.CharField(
        max_length=255,
        verbose_name="Type de feature",
        help_text="Le type de feature du GeoJSON.",
    )

    geometry_type = models.CharField(
        max_length=255,
        verbose_name="Type de géométrie",
        help_text="Le type de géométrie du GeoJSON.",
        blank=True,
        null=True,
        default=None,
    )

    geometry_coordinates = models.JSONField(
        verbose_name="Coordonnées de la géométrie",
        help_text="Les coordonnées de la géométrie du GeoJSON.",
        blank=True,
        null=True,
        default=None,
    )

    properties = models.JSONField(
        verbose_name="Propriétés",
        help_text="Les propriétés du GeoJSON.",
        blank=True,
        null=True,
        default=None,
    )

    # Generic foreign key to link the GeoJSON to any model.
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        verbose_name = "Geometrie GeoJSON"
        verbose_name_plural = "Geometries GeoJSON"

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return f"{self.id}"
# End class Shape
