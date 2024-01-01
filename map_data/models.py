"""
Models for the `map_data` application.
"""
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
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
        help_text="L'ID du GeoJSON.",
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
        verbose_name = "GeoJSON"
        verbose_name_plural = "GeoJSONs"

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return f"{self.id}"
# End class Shape


# ======================================================================================================================
# City: represents a city of the metropolitan area
# ======================================================================================================================


class City(models.Model):
    """
    This class represents a city.
    """

    # ------------------------------------------------------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------------------------------------------------------

    id = models.AutoField(
        primary_key=True,
        verbose_name="ID",
        help_text="L'ID de la ville.",
    )

    name = models.CharField(
        max_length=255,
        verbose_name="Nom",
        help_text="Le nom de la ville.",
    )

    shape = GenericRelation(Shape)

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        verbose_name = "Ville"
        verbose_name_plural = "Villes"

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return self.name
# End class City

class MapLayer(models.Model):
    """
    This class represents a map layer.
    """

    # ------------------------------------------------------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------------------------------------------------------

    id = models.AutoField(
        primary_key=True,
        verbose_name="ID",
        help_text="L'ID de la couche de carte.",
    )

    name = models.CharField(
        max_length=255,
        verbose_name="Nom",
        help_text="Le nom de la couche de carte.",
    )

    shape = GenericRelation(Shape)

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        verbose_name = "Couche de carte"
        verbose_name_plural = "Couches de carte"

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return self.name


# ======================================================================================================================
# MapRender: represents a map render.
# ======================================================================================================================

class MapRender(models.Model):
    """This class represents a map render."""

    # ------------------------------------------------------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------------------------------------------------------

    id = models.AutoField(
        primary_key=True,
        verbose_name="ID",
        help_text="L'ID de la carte.",
    )

    name = models.CharField(
        max_length=255,
        verbose_name="Nom",
        help_text="Le nom de la carte.",
    )

    embed_html = models.FileField(
        name="embed_html",
        verbose_name="Code HTML de la carte qui peut être intégré dans une page web",
        upload_to="map_data/map_renders/embed",
        help_text="Le code HTML de la carte.",
        null=True,
        default=None,
    )

    full_html = models.FileField(
        name="full_html",
        verbose_name="Code HTML complet de la carte ouvrable dans un navigateur",
        upload_to="map_data/map_renders/full",
        help_text="Le code HTML complet de la carte.",
        null=True,
        default=None,
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        verbose_name = "Rendu de carte"
        verbose_name_plural = "Rendus de carte"

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return self.name