from django.db import models


# ======================================================================================================================
# City model
# ======================================================================================================================

class City(models.Model):
    """
    This class represents a city.
    """

    # ------------------------------------------------------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------------------------------------------------------

    name = models.CharField(
        max_length=255,
        verbose_name="Nom",
        help_text="Le nom de la ville.",
    )

    feature_type = models.CharField(
        max_length=255,
        verbose_name="Type de feature",
        help_text="Le type de feature de la ville.",
    )

    geometry_type = models.CharField(
        max_length=255,
        verbose_name="Type de géométrie",
        help_text="Le type de géométrie de la ville.",
        blank=True,
        null=True,
        default=None,
    )

    geometry_coordinates = models.JSONField(
        verbose_name="Coordonnées de la géométrie",
        help_text="Les coordonnées de la géométrie de la ville.",
        blank=True,
        null=True,
        default=None,
    )

    properties = models.JSONField(
        verbose_name="Propriétés",
        help_text="Les propriétés de la ville.",
        blank=True,
        null=True,
        default=None,
    )

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
