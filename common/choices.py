# -*- coding: utf-8 -*-
"""
Common choices for the models of the website.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _

class PublicationStatus(models.TextChoices):
    """Choices for the `Article` model."""
    DRAFT = "draft", _("Draft")
    PUBLISHED = "published", _("Published")
# End class PublicationStatus
