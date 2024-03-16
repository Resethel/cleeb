# -*- coding: utf-8 -*-
"""
Admin for the `article` application.
"""
from django.contrib import admin
from .models import Article
from django.utils.translation import gettext_lazy as _

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """Admin for the `article` application."""

    # ------------------------------------------------------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------------------------------------------------------

    list_display = ("id", "title", "created_at", "last_modified_at")
    search_fields = ("id", "title")
    list_display_links = ("id", "title")
    readonly_fields = ("id", "slug", "created_at", "last_modified_at")

    # ------------------------------------------------------------------------------------------------------------------
    # Fieldsets
    # ------------------------------------------------------------------------------------------------------------------

    fieldsets = (
        (_("ID"), {
            "classes": ("collapse",),
            "fields": ("id", "slug"),
        }),
        (_("Metadata"), {
            "classes": ("collapse",),
            "fields": (
                "created_at",
                "last_modified_at",
            ),
        }),
        (_("Article"), {
            "fields": (
                "title",
                "authors",
                "cover_image",
                "body",
            ),
        }),
    )
# End class ArticleAdmin

