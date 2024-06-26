# -*- coding: utf-8 -*-
"""
Admin for the `files` application.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from files.models import File

# ======================================================================================================================
# AttachmentAdmin
# ======================================================================================================================

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    """Admin for the `File` model."""

    # ------------------------------------------------------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------------------------------------------------------

    list_display = ("id", "name", "short_description", "type")
    search_fields = ("id", "name")
    list_display_links = ("id", "name")
    readonly_fields = ("id", "slug")
    list_filter = ('type',)

    # ------------------------------------------------------------------------------------------------------------------
    # Fieldsets
    # ------------------------------------------------------------------------------------------------------------------

    fieldsets = (
        (_("ID"), {
            "classes": ("collapse",),
            "fields": (("id", "slug"),)
        }),
        (_("File"), {
            "fields": (
                ("name", "type",),
                "short_description",
                "file"
            ),
        }),
    )
# End class FileAdmin
