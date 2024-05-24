# -*- coding: utf-8 -*-
"""
Models related to tiles and tile layers for the `map_templates` application.
"""
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from xyzservices import TileProvider

# ======================================================================================================================
# Tile Layer
# ======================================================================================================================

class TileLayer(models.Model):
    """Represents a Leaflet/Folium tile layer."""

    # ID of the tile
    id = models.AutoField(primary_key=True)

    # Name of the tile
    name = models.CharField(
        unique=True,
        max_length=100,
        verbose_name=_("Name"),
        help_text=_("The name of the tile layer.")
    )

    verbose_name = models.CharField(
        unique=True,
        max_length=100,
        default=None,
        blank=True,
        null=True,
        verbose_name=_("Verbose Name"),
        help_text=_("The verbose name of the tile layer.")
    )

    transparent = models.BooleanField(
        default=False,
        verbose_name=_("Transparent"),
        help_text=_("Whether the tile layer is transparent, i.e., has an alpha channel.")
    )

    overlay = models.BooleanField(
        default=True,
        verbose_name=_("Overlay"),
        help_text=_("Whether the tile layer is an overlay, i.e., can be superimposed on other layers.")
    )

    control = models.BooleanField(
        default=True,
        verbose_name=_("Show in Layer Control"),
        help_text=_("Whether the tile layer should be shown in the layer control.")
    )

    type = models.CharField(
        max_length=7,
        choices=[
            ('builtin', _("Built-in")),
            ('xyz', 'XYZ')
        ],
        default='folium',
        verbose_name=_("Type"),
        help_text=_("The type of the tile layer. If 'folium', the tile is managed by Folium and the other fields are ignored.")
    )

    # URL of the tile
    url = models.URLField(
        max_length=500,
        default=None,
        blank=True,
        null=True,
        verbose_name=_("URL"),
        help_text=_("The XYZ URL of the tile layer.")
    )


    # Attribution of the tile
    attribution = models.CharField(
        max_length=200,
        default=None,
        blank=True,
        null=True,
        verbose_name=_("Attribution"),
        help_text=_("The attribution (credits) of the tile layer.")
    )

    # Access token of the tile (if any)
    access_token = models.CharField(
        max_length=100,
        default=None,
        blank=True,
        null=True,
        verbose_name=_("Access Token"),
        help_text=_(
            "Some tile providers require an access token to access their tiles. "
            "This field should be empty if no access token is required."
        )
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return self.name

    def clean(self):

        # First, call the parent clean method
        super().clean()

        # For built-in tiles, the URL and the attribution should be empty
        if self.type == "builtin":
            self.url = None
            self.attribution = None
            self.access_token = None
            return

        if self.url is None or self.url == "":
            raise ValidationError(_("An URL is required for XYZ tiles."))
        if self.attribution is None or self.attribution == "":
            raise ValidationError(_("An attribution is required for XYZ tiles."))

        # Check if the access token is required
        temp_provider : TileProvider = TileProvider(
            name=self.name,
            url=self.url,
            attribution=self.attribution
        )

        # Check if the access token is required
        requires_token = temp_provider.requires_token()
        if not requires_token:
            # If the access token is not required, it should be empty to avoid confusion
            self.access_token = None
        # If it is required, check if it is provided
        elif self.access_token is None or self.access_token == "":
            raise ValidationError(_("An access token is required for the tile '{name}@{url}'.").format(
                name=self.name,
                url=self.url
            ))
        # If it is provided, check if it is valid
        else:
            temp_provider["accessToken"] = self.access_token
            if temp_provider.requires_token(): # requires_token() should return False if the token is valid
                raise ValidationError(_("The access token provided is invalid for the tile '{name}@{url}'.").format(
                    name=self.name,
                    url=self.url
                ))

        # The url can be quite long, so it is splittable in multiple lines in the admin
        # So we must make sure that no line break is present in the URL
        if self.url is not None:
            self.url = self.url.replace("\n", "")
            self.url = self.url.replace("\r", "")
            self.url = self.url.replace("\t", "")
            self.url = self.url.strip()
            self.url = self.url.replace(" ", "")
    # End def clean

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        verbose_name = _("Tile Layer")
        verbose_name_plural = _("Tile Layers")
    # End class Meta
# End class TileLayer

# ======================================================================================================================
# Signals
# ======================================================================================================================

@receiver(pre_save, sender=TileLayer)
def fill_missing_verbose_name(sender, instance, **kwargs):
    """If the verbose name is not set, fill it with the name."""
    if instance.verbose_name is None or instance.verbose_name == "":
        instance.verbose_name = instance.name.title()
# End def fill_missing_verbose_name
