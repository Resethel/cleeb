# -*- coding: utf-8 -*-
"""
Models for the `interactive_maps` application.
"""
from django import urls
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import gettext_lazy as _
from tinymce import models as tinymce_models

from common.choices import PublicationStatus
from core.models import Organization
from thematic.models import Theme


# ======================================================================================================================
# Rendered Map
# ======================================================================================================================

def map_render_embed_path(instance, filename):
    # Get the extension of the file
    extension = filename.split('.')[-1]
    # Return the path
    return f"maps/{instance.slug}/embed.{extension}"
# End def map_render_embed_path

def map_render_full_path(instance, filename):
    # Get the extension of the file
    extension = filename.split('.')[-1]
    # Return the path
    return f"maps/{instance.slug}/full.{extension}"
# End def map_render_full_path

class MapRender(models.Model):
    """This class represents a map render."""

    # ------------------------------------------------------------------------------------------------------------------
    # ID fields
    # ------------------------------------------------------------------------------------------------------------------

    id = models.AutoField(
        primary_key=True,
        verbose_name="ID",
        help_text="L'ID de la carte.",
    )

    slug = models.SlugField(
        max_length=512,
        blank=True,
        null=True,
        default=None,
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Template
    # ------------------------------------------------------------------------------------------------------------------

    template = models.OneToOneField(
        to='map_templates.MapTemplate',
        related_name='render',
        on_delete=models.CASCADE,
        null=True,
        default=None,
        verbose_name='Modèle',
        help_text="Le modèle utilisé pour générer le rendu de la carte."
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Description
    # ------------------------------------------------------------------------------------------------------------------

    name = models.CharField(
        unique=True,
        max_length=255,
        verbose_name="Nom",
        help_text="Le nom du rendu."
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Rendered files
    # ------------------------------------------------------------------------------------------------------------------

    embed_html = models.FileField(
        name="embed_html",
        verbose_name="HTML intégrable",
        upload_to=map_render_embed_path,
        help_text="Le code HTML de la carte pouvant être intégré dans une page web.",
        null=True,
        default=None,
    )

    full_html = models.FileField(
        name="full_html",
        verbose_name="HTML complet",
        upload_to=map_render_full_path,
        help_text="Le code HTML d'une page web contenant la carte.",
        null=True,
        default=None,
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        verbose_name = "Rendu de carte"
        verbose_name_plural = "Rendus de carte"
    # End class Meta

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return self.name
    # End def __str__

    def clean(self, exclude=None):
        super().clean()
        self.slug = slugify(self.name)
    # End def clean_fields

    def get_absolute_url(self):
        # If the template is not linked, then the map is not supposed to be displayed.
        # Therefore, return None
        if self.is_linked_to_map() is False:
            return None

        # If the template is linked to a map, then the map is supposed to be displayed.
        if self.map.publication_status == PublicationStatus.DRAFT:
            return urls.reverse('map-draft-detail-fullscreen', kwargs={'slug': self.map.slug})

        return urls.reverse('map-detail-fullscreen', kwargs={'slug': self.map.slug})
    # End def get_absolute_url

    def is_linked_to_map(self):
        return hasattr(self, 'map') and self.map is not None
    # End def is_linked_to_map
# End class MapRender

# ======================================================================================================================
# Interactive Map
# ======================================================================================================================

class Map(models.Model):

    # ------------------------------------------------------------------------------------------------------------------
    # ID fields
    # ------------------------------------------------------------------------------------------------------------------

    id = models.AutoField(primary_key=True)

    slug = models.SlugField(
        max_length=100,
        blank=True,
        null=True,
        default=None,
        help_text="Le slug de la carte interactive. S'il n'est pas renseigné, il sera généré automatiquement."
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Metadata fields
    # ------------------------------------------------------------------------------------------------------------------

    created_at = models.DateField(
        auto_now_add=True,
        help_text="La date de création de la carte interactive.",
        editable=False
    )

    last_modified = models.DateField(
        auto_now=True,
        help_text="La date de dernière modification de la carte interactive.",
        editable=False
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Map fields
    # ------------------------------------------------------------------------------------------------------------------

    # Title of the thematic map
    title = models.CharField(max_length=100)

    # Author of the thematic map
    authors = models.ManyToManyField(
        'core.Person',
        blank=True,
        help_text="Les auteur.ice.s de la carte interactive."
    )

    themes = models.ManyToManyField(
        'thematic.Theme',
        related_name='maps',
        blank=True,
        verbose_name=_("Themes"),
        help_text=_("The themes of the map.")
    )

    publication_status = models.CharField(
        choices=PublicationStatus.choices,
        default=PublicationStatus.DRAFT,
        max_length=20,
        verbose_name=_("Publication status"),
        help_text=_("The publication status of the map.")
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Render field
    # ------------------------------------------------------------------------------------------------------------------

    render = models.OneToOneField(
        'MapRender',
        related_name='map',
        verbose_name="Rendu de carte",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text="Le rendu de la carte."
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Content fields
    # ------------------------------------------------------------------------------------------------------------------

    introduction = models.TextField(
        blank=True,
        null=True,
        default=None,
        help_text="L'introduction de la carte interactive. Formaté en HTML."
                  "Seuls les balises de style (strong, em, etc.) seront conservées."
                  "Toutes balises de structure (section, article, h1, p, etc.) seront supprimées."
    )

    body = tinymce_models.HTMLField(
        blank=True,
        null=True,
        default=None,
        help_text=_("The body of the interactive map.")
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------
    class Meta:
        ordering = ['id',]  # Order Thematic maps by 'title' field
        verbose_name = "Carte interactive"
        verbose_name_plural = "Cartes interactives"
    # End class Meta

    # ------------------------------------------------------------------------------------------------------------------
    # Magic methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return f"{self.title}"
    # End def __str__

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def clean(self, exclude=None):
        super().clean()
        self.slug = slugify(self.title)
    # End def clean_fields

    def get_absolute_url(self):
        if self.publication_status == PublicationStatus.DRAFT:
            return urls.reverse('map-draft-detail', kwargs={'slug': self.slug})
        return urls.reverse('map-detail', kwargs={'slug': self.slug})
    # End def get_absolute_url
# End class Map
