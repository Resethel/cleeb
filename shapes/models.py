import geojson
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
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

    # ----- Identification -----

    id = models.BigAutoField(
        primary_key=True,
        verbose_name="ID",
        help_text="L'ID de la géométrie GeoJSON.",
    )

    # ----- Parenthood -----

    parent_layer = models.ForeignKey(
        'map_layers.MapLayer',
        related_name="shapes",
        on_delete=models.SET_NULL, # Set to NULL if the parent layer is deleted,
                                   # unreferenced shape are periodically deleted
        verbose_name="Couche parent",
        help_text="La couche parent de la géométrie GeoJSON.",
        blank=True,
        default=None,
        null=True,
    )

    # ----- Geojson fields -----

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

    # ------------------------------------------------------------------------------------------------------------------
    # Non-persistent fields
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def parent(self):
        if self.parent_layer is not None:
            return self.parent_layer
    # End def parent

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
        return f"{self.geometry_type}@{self.id}"
    # End def __str__


    def clean(self):
        # Ensure that at most one parent is created
        n_parents = sum([
            self.parent_layer == True,
        ])

        if n_parents > 1:
            error_str = "Either remove this parent or another one"
            assigned_fields = dict()
            if self.parent_layer:
                assigned_fields["parent_layer"] = error_str
            raise ValidationError("This shape has more than one parent assigned.", params=assigned_fields)
    # End def clean


    def as_geojson(self) -> geojson.Feature:
        """Convert the shape to a GeoJSON feature."""
        match self.geometry_type.casefold():
            case "point":
                return geojson.Feature(
                    id=self.id,
                    geometry=geojson.Point(self.geometry_coordinates),
                    properties=self.properties,
                )
            case "linestring":
                return geojson.Feature(
                    id=self.id,
                    geometry=geojson.LineString(self.geometry_coordinates),
                    properties=self.properties,
                )
            case "polygon":
                return geojson.Feature(
                    id=self.id,
                    geometry=geojson.Polygon(self.geometry_coordinates),
                    properties=self.properties,
                )
            case "multipoint":
                return geojson.Feature(
                    id=self.id,
                    geometry=geojson.MultiPoint(self.geometry_coordinates),
                    properties=self.properties,
                )
            case "multilinestring":
                return geojson.Feature(
                    id=self.id,
                    geometry=geojson.MultiLineString(self.geometry_coordinates),
                    properties=self.properties,
                )
            case "multipolygon":
                return geojson.Feature(
                    id=self.id,
                    geometry=geojson.MultiPolygon(self.geometry_coordinates),
                    properties=self.properties,
                )
            case _:
                raise ValueError(f"Unknown geometry type: {self.geometry_type}")
    # End def as_geojson

# End class Shape
