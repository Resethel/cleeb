# -*- coding: utf-8 -*-
"""
Models for the `thematic` application.
"""
from colorfield.fields import ColorField
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


# ======================================================================================================================
# Theme
# ======================================================================================================================

def get_theme_cover_path(instance, filename):
    # Get the extension of the file
    extension = filename.split('.')[-1]
    # Return the path
    return f"thematic/theme/{instance.slug}/cover.{extension}"
# End def get_theme_cover_path

class Theme(models.Model):

    # ------------------------------------------------------------------------------------------------------------------
    # ID field
    # ------------------------------------------------------------------------------------------------------------------

    id = models.AutoField(primary_key=True)

    # ------------------------------------------------------------------------------------------------------------------
    # Slug and name
    # ------------------------------------------------------------------------------------------------------------------

    slug = models.SlugField(
        max_length=200,
        unique=True,
        blank=True,
        null=True,
        default=None,
        verbose_name=_("Slug"),
        help_text=_("Slug of the theme, used in urls.")
    )

    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_("Name"),
        help_text=_("Name of the theme.")
    )

    short_name = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        verbose_name=_("Short name"),
        help_text=_("Short name of the theme, used for tags.")
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Description and image
    # ------------------------------------------------------------------------------------------------------------------

    summary = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name=_("Summary"),
        help_text=_("Short description of the theme, displayed on the theme index page.")
    )

    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Description"),
        help_text=_("Long description of the theme, displayed on the theme page as an article.")
    )

    cover_image = models.ImageField(
        upload_to=get_theme_cover_path,
        blank=True,
        null=True,
        verbose_name=_("Cover image"),
        help_text=_("Image displayed on the theme page.")
    )

    color = ColorField(
        format='hex',
        default=None,
        blank=True,
        null=True,
        verbose_name=_("Color"),
        help_text=_("Color used to represent the theme.")
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        verbose_name = _("Theme")
        verbose_name_plural = _("Themes")

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return self.name
    # End def __str__

    def clean(self):
        super().clean()
        self.slug = slugify(self.name)
    # End def clean

    def get_absolute_url(self):
        return reverse('theme', kwargs={"pk" : self.id})
    # End def get_absolute_url
# End class Theme