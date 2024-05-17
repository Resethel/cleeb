# -*- coding: utf-8 -*-
"""
Admin for the `article` application.
"""
from django.contrib import admin

from files.admin import FileInline
from .models import Article
from django.utils.translation import gettext_lazy as _

# ======================================================================================================================
# Article
# ======================================================================================================================

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """Admin for the `article` model."""

    # ------------------------------------------------------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------------------------------------------------------

    list_display = ("id", "title", "created_at", "last_modified_at")
    search_fields = ("id", "title")
    list_display_links = ("id", "title")
    readonly_fields = ("id", "slug", "created_at", "last_modified_at")
    radio_fields = {'status': admin.HORIZONTAL}
    inlines = (FileInline,)

    # ------------------------------------------------------------------------------------------------------------------
    # Fieldsets
    # ------------------------------------------------------------------------------------------------------------------

    fieldsets = (
        (_("ID"), {
            "classes": ("collapse",),
            "fields": (("id", "slug"),),
        }),
        (_("Metadata"), {
            "classes": ("collapse",),
            "fields": (("created_at", "last_modified_at"),),
        }),
        (_("Publication Status"), {
            "classes": ("wide",),
            "fields": ("status",),
        }),
        (_("Article"), {
            "fields": (
                "title",
                "authors",
                "themes",
                "cover_image",
                "body",
            ),
        }),
    )
# End class ArticleAdmin