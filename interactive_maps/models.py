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
        verbose_name=_("ID"),
        help_text=_("The unique identifier of the map render.")
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
        verbose_name=_("Template"),
        help_text=_("The template used to render the map.")
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Description
    # ------------------------------------------------------------------------------------------------------------------

    name = models.CharField(
        unique=True,
        max_length=255,
        verbose_name=_("Name"),
        help_text=_("The name of the map render.")
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Rendered files
    # ------------------------------------------------------------------------------------------------------------------

    embed_html = models.FileField(
        name="embed_html",
        verbose_name=_("Embedded HTML"),
        help_text=_("The embedded HTML code of the map. This file is used for the embedded display of the map."),
        upload_to=map_render_embed_path,
        null=True,
        default=None,
    )

    full_html = models.FileField(
        name="full_html",
        verbose_name=_("Full HTML"),
        help_text=_("The full HTML code of the map. This file is used for the fullscreen display of the map."),
        upload_to=map_render_full_path,
        null=True,
        default=None,
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        verbose_name = _("Map Render")
        verbose_name_plural = _("Map Renders")
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
        help_text=_("The slug of the map. This field is automatically generated from the title.")
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Metadata fields
    # ------------------------------------------------------------------------------------------------------------------

    created_at = models.DateField(
        auto_now_add=True,
        verbose_name=_("Created at"),
        help_text=_("The creation date of the interactive map."),
        editable=False
    )

    last_modified = models.DateField(
        auto_now=True,
        verbose_name=_("Last modified"),
        help_text=_("The last modification date of the interactive map."),
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
        verbose_name=_("Authors"),
        help_text=_("The authors of the map.")
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
        verbose_name=_("Render"),
        help_text=_("The render of the map."),
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Content fields
    # ------------------------------------------------------------------------------------------------------------------

    introduction = models.TextField(
        blank=True,
        null=True,
        default=None,
        verbose_name=_("Introduction text"),
        help_text=_(
            "The introduction of the interactive map. Formatted in HTML."
            "Only style tags (strong, em, etc.) will be kept."
            "All structure tags (section, article, h1, p, etc.) will be removed."
        )
    )

    body = tinymce_models.HTMLField(
        blank=True,
        null=True,
        default=None,
        verbose_name=_("Body text"),
        help_text=_("The body of the interactive map. Formatted in HTML.")
    )

    attachments = models.ManyToManyField(
        "files.File",
        verbose_name=_("Attached files"),
        related_name="interactive_maps",
        help_text=_("Files attached to the interactive map."),
        blank=True,
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------
    class Meta:
        ordering = ['id',]  # Order Thematic maps by 'title' field
        verbose_name = _("Interactive Map")
        verbose_name_plural = _("Interactive Maps")
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
