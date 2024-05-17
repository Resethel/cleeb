# -*- coding: utf-8 -*-
"""
Models for the `files` application.
"""
from django import urls
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from articles.models import Article
from common.utils import files as file_utils

# ======================================================================================================================
# Utility Functions
# ======================================================================================================================

def get_upload_path(instance, filename):
    """Returns the path at which the file should be uploaded"""
    # Get the extension of the file
    extension = filename.split('.')[-1]
    # Return the path
    return f"files/{instance.slug}.{extension}"
# get_upload_path

def slugify_file_name(file_name : str) -> str:
    """Slugify the name of the file and avoid duplicates"""
    # Get the basic slug of the file
    slug = slugify(file_name)

    # Ensure that no other file as the same slug
    try:
        File.objects.get(slug=slug)
    # Case 1: There are no other files with the same slug
    except File.DoesNotExist:
        return slug

    # Case 2: There is already a file with the same slug.
    #         In that case, append the number of files with the same slug
    n = File.objects.filter(slug__contains=slug).count()
    return f"{slug}-{n:03d}"
# End def slugify_file_name

# ======================================================================================================================
# Enums
# ======================================================================================================================

class FileType(models.TextChoices):
    """Choices for the `File` model."""
    FILE  = "file" , _("File")  # Default, any kind of file
    PDF   = "pdf"  , _("PDF")   # PDF files
    IMAGE = "image", _("Image") # Image files can be embedded in the article
    VIDEO = "video", _("Video") # Video files can be embedded in the article
    AUDIO = "audio", _("Audio") # Audio files can be embedded in the article
# End class FileType

# ======================================================================================================================
# Main Class
# ======================================================================================================================

class File(models.Model):
    """Represent an attachment of an article (i.e. a file, an image, a video, etc.)."""

    # ------------------------------------------------------------------------------------------------------------------
    # Identification
    # ------------------------------------------------------------------------------------------------------------------

    id = models.AutoField(
        primary_key=True,
        verbose_name=_("ID"),
        help_text=_("File's ID")
    )

    slug = models.SlugField(unique=True)

    # ------------------------------------------------------------------------------------------------------------------
    # Data
    # ------------------------------------------------------------------------------------------------------------------

    name = models.CharField(
        max_length=100,
        verbose_name=_("Name"),
        help_text=_("Verbose name of the file")
    )

    short_description = models.CharField(
        max_length=50,
        verbose_name=_("Short Description"),
        help_text=_("A (very) short description of the file (max 50 characters, optional)"),
        blank=True,
        null=True,
    )

    # The type of file is enforced during upload.
    type = models.CharField(
        max_length=10,
        choices=FileType.choices,
        verbose_name=_("Type"),
        help_text=_("The type of file attached. Will be calculated automatically if left empty."),
        default=None,
        null=True,
    )

    file = models.FileField(
        max_length=500,
        upload_to=get_upload_path,
        verbose_name=_("File"),
        help_text=_("The file to upload to the website.")
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Non-persistent fields
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def download_url(self):
        """Return the URL to download the file."""
        return urls.reverse("files:download", kwargs={"slug": self.slug})
    # End def download_url

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        verbose_name = _("File")
        verbose_name_plural = _("Files")
    # End class Meta

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return self.name
    # End def __str__

    def clean(self):
        super().clean()
        self.slug = slugify_file_name(self.name)

        # If the type is `None`, infer the type of the file
        if self.type is None:
            if file_utils.is_pdf(self.file):
                self.type = FileType.PDF
            elif file_utils.is_image(self.file):
                self.type = FileType.IMAGE
            elif file_utils.is_video(self.file):
                self.type = FileType.VIDEO
            elif file_utils.is_audio(self.file):
                self.type = FileType.AUDIO
            else:
                self.type = FileType.FILE

        # Validate the file according to its type
        if self.type == FileType.PDF:
            if not file_utils.is_valid_pdf(self.file):
                raise ValidationError(_("The uploaded file is not a valid PDF file."))
        elif self.type == FileType.IMAGE:
            if not file_utils.is_valid_image(self.file):
                raise ValidationError(_("The uploaded file is not a valid image file."))
        # TODO: Add validation for other filetypes
    # End def clean
# End class File