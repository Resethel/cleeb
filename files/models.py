# -*- coding: utf-8 -*-
"""
Models for the `files` application.
"""
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from articles.models import Article
from common.utils import files as file_utils

# ======================================================================================================================
# Utility Functions
# ======================================================================================================================

def get_attachment_upload_path(instance, filename):
    # Get the extension of the file
    extension = filename.split('.')[-1]
    # Return the path
    return f"articles/{instance.article.slug}/attachments/{instance.slug}.{extension}"
# get_attachment_upload_path

# ======================================================================================================================
# Enums
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
# Main Class
# ======================================================================================================================

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

    short_description = models.CharField(
        max_length=50,
        verbose_name=_("Short Description"),
        help_text=_("Attachment's (very) short description (max 50 characters)"),
        blank=True,
        null=True,
    )

    # The type of file is enforced during upload.
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