"""
Models for the `map_data` application.
"""
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models

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