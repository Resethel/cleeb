# -*- coding: utf-8 -*-
"""
Models for the `article` application.
"""
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from common.choices import PublicationStatus
from common.utils import files as file_utils


# ======================================================================================================================
# Choices
# ======================================================================================================================

class AttachmentType(models.TextChoices):
    """Choices for the `Attachment` model."""
    FILE  = "file", _("File")   # Default, any kind of file
    PDF   = "pdf", _("PDF")     # PDF files
    IMAGE = "image", _("Image") # Image files can be embedded in the article
    VIDEO = "video", _("Video") # Video files can be embedded in the article
    AUDIO = "audio", _("Audio") # Audio files can be embedded in the article
# End class AttachmentType

# ======================================================================================================================
# Article
# ======================================================================================================================

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

    status = models.CharField(
        max_length=10,
        choices=PublicationStatus.choices,
        default=PublicationStatus.DRAFT,
        verbose_name=_("Status"),
        help_text=_("The status of the article."),
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

    def get_absolute_url(self):
        # If the article is a draft, return the draft URL, which is different from the published URL and
        # requires special permissions to access.
        if self.status == PublicationStatus.DRAFT:
            return reverse('draft-article', args=[self.slug])
        return reverse('article', args=[self.slug])
    # End def get_absolute_url
# End class Article

# ======================================================================================================================
# Attachment
# ======================================================================================================================

def get_attachment_upload_path(instance, filename):
    # Get the extension of the file
    extension = filename.split('.')[-1]
    # Return the path
    return f"articles/{instance.article.slug}/attachments/{instance.slug}.{extension}"
# End def get_attachment_upload_path

class Attachment(models.Model):
    """Represent an attachment of an article (i.e. a file, an image, a video, etc.)."""

    # ------------------------------------------------------------------------------------------------------------------
    # Identification
    # ------------------------------------------------------------------------------------------------------------------

    id = models.AutoField(
        primary_key=True,
        verbose_name=_("ID"),
        help_text=_("Attachment ID")
    )

    slug = models.SlugField()

    # ------------------------------------------------------------------------------------------------------------------
    # Parent article
    # ------------------------------------------------------------------------------------------------------------------

    article = models.ForeignKey(
        Article,
        related_name="attachments",
        on_delete=models.CASCADE,
        verbose_name=_("Article"),
        help_text=_("Article to which the attachment belongs to")
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Data
    # ------------------------------------------------------------------------------------------------------------------

    name = models.CharField(
        max_length=100,
        verbose_name=_("Name"),
        help_text=_("Attachment's Name")
    )

    # The type of a file is enforced during upload.
    type = models.CharField(
        max_length=10,
        choices=AttachmentType.choices,
        verbose_name=_("Type"),
        help_text=_("Attachment's Type"),
        default=None,
        null=True,
    )

    file = models.FileField(
        max_length=500,
        upload_to=get_attachment_upload_path,
        verbose_name=_("File"),
        help_text=_("Attachment's File")
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        verbose_name = _("Attachment")
        verbose_name_plural = _("Attachments")
        unique_together = ["article", "slug"]
    # End class Meta

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return self.name
    # End def __str__

    def clean(self):
        super().clean()
        self.slug = slugify(self.name)

        # If the type is `None`, infer the type of the file
        if self.type is None:
            if file_utils.is_pdf(self.file):
                self.type = AttachmentType.PDF
            elif file_utils.is_image(self.file):
                self.type = AttachmentType.IMAGE
            elif file_utils.is_video(self.file):
                self.type = AttachmentType.VIDEO
            elif file_utils.is_audio(self.file):
                self.type = AttachmentType.AUDIO
            else:
                self.type = AttachmentType.FILE

        # Validate the file according to its type
        if self.type == AttachmentType.PDF:
            if not file_utils.is_valid_pdf(self.file):
                raise ValidationError(_("The file is not a valid PDF file."))
        elif self.type == AttachmentType.IMAGE:
            if not file_utils.is_valid_image(self.file):
                raise ValidationError(_("The file is not a valid image file."))
        # TODO: Add validation for other filetypes
    # End def clean
# End class Attachment
