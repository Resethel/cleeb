# -*- coding: utf-8 -*-
"""
Models for the `article` application.
"""
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


def get_cover_image_upload_path(instance, filename):
    # Get the extension of the file
    extension = filename.split('.')[-1]
    # Return the path
    return f"articles/{instance.slug}/cover.{extension}"
# End def get_splash_image_upload_path

class Article(models.Model):
    """Represent an article about a specific topic.

    Articles are not bound to a specific theme or interactive map.
    They are used to provide additional information about a more specific topic.
    """

    # ------------------------------------------------------------------------------------------------------------------
    # ID fields
    # ------------------------------------------------------------------------------------------------------------------

    id = models.AutoField(
        primary_key=True,
        verbose_name="ID",
        help_text="L'ID de l'article.",
    )

    slug = models.SlugField(
        max_length=512,
        blank=True,
        null=True,
        default=None,
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Metadata
    # ------------------------------------------------------------------------------------------------------------------

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created at"),
        help_text=_("The date of creation of the article."),
    )

    last_modified_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Last modified at"),
        help_text=_("The date of the last modification of the article."),
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Article fields
    # ------------------------------------------------------------------------------------------------------------------

    title = models.CharField(
        max_length=512,
        verbose_name=_("Title"),
        help_text=_("The title of the article."),
    )

    authors = models.ManyToManyField(
        "core.Person",
        verbose_name=_("Authors"),
        help_text=_("Authors of the article."),
        blank=True
    )

    cover_image = models.ImageField(
        upload_to=get_cover_image_upload_path,
        verbose_name=_("Splash image"),
        help_text=_("The splash image of the article."),
        null=True,
        blank=True,
    )

    body = models.TextField(
        verbose_name=_("Article body"),
        help_text=_("The body of the article."),
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        verbose_name = _("Article")
        verbose_name_plural = _("Articles")
    # End class Meta

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return self.title
    # End def __str__

    def clean(self):
        self.slug = slugify(self.title)
    # End def clean
# End class Article
