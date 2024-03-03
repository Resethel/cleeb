# -*- coding: utf-8 -*-
"""
Utility module for the celery tasks.
"""
from enum import Enum

from django.db import models
from django.db.models import Choices, TextChoices


# ======================================================================================================================
# Enums
# ======================================================================================================================

class TaskStatus(models.TextChoices):
    """Enum to represent the status of a task."""
    PENDING = "PENDING", "Pending"
    STARTED = "STARTED", "Started"
    SUCCESS = "SUCCESS", "Success"
    FAILURE = "FAILURE", "Failure"
    REVOKED = "REVOKED", "Revoked"
# End class TaskStatus