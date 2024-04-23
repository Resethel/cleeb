# -*- coding: utf-8 -*-
"""
Models for the `contact` application.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _


class Contact(models.Model):
    """
    Model to store contact messages.
    """

    # ------------------------------------------------------------------------------------------------------------------
    # ID Fields
    # ------------------------------------------------------------------------------------------------------------------

    id = models.AutoField(
        primary_key=True
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Data Fields
    # ------------------------------------------------------------------------------------------------------------------

    name = models.CharField(
        max_length=100,
        verbose_name=_("Name"),
        help_text=_("Name of the sender.")
    )

    email = models.EmailField(
        verbose_name=_("Email"),
        help_text=_("Email address of the sender.")
    )

    subject = models.CharField(
        max_length=100,
        verbose_name=_("Subject"),
        help_text=_("Subject of the message.")
    )

    message = models.TextField(
        verbose_name=_("Message"),
        help_text=_("Content of the message.")
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Metadata Fields
    # ------------------------------------------------------------------------------------------------------------------

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created at"),
        help_text=_("Date and time when the message was created.")
    )

    handled = models.BooleanField(
        default=False,
        verbose_name=_("Handled"),
        help_text=_("Flag to indicate if the message was handled by the team.")
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        verbose_name = _("Contact Message")
        verbose_name_plural = _("Contact Messages")
    # End class Meta

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return _("{name} - {subject} ({created_at})").format(
            name=self.name,
            subject=self.subject,
            created_at=self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        )
    # End def __str__

# End class Contact
