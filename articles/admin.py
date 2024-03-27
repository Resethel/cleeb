# -*- coding: utf-8 -*-
"""
Admin for the `article` application.
"""
from django.contrib import admin
from .models import Article, Attachment
from django.utils.translation import gettext_lazy as _

# ======================================================================================================================
# Article
# ======================================================================================================================

class AttachmentInline(admin.TabularInline):
    """Inline for the `Attachment` model."""
    model = Attachment
    extra = 0
    exclude = ('slug', 'type')
# End class AttachmentInline

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
    inlines = (AttachmentInline,)

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

# ======================================================================================================================
# AttachmentAdmin
# ======================================================================================================================

@admin.register(Attachment)
class Attachment(admin.ModelAdmin):
    """Admin for the `Attachment` model."""

    # ------------------------------------------------------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------------------------------------------------------

    list_display = ("id", "name", "article", "short_description", "type")
    search_fields = ("id", "name", "article")
    list_display_links = ("id", "name")
    readonly_fields = ("id", "slug")
    list_filter = ('type', 'article')

    # ------------------------------------------------------------------------------------------------------------------
    # Fieldsets
    # ------------------------------------------------------------------------------------------------------------------

    fieldsets = (
        (_("ID"), {
            "classes": ("collapse",),
            "fields": (("id", "slug"),)
        }),
        (_("Attachment"), {
            "fields": (
                "name",
                "type",
                "short_description",
                "article",
                "file"
            ),
        }),
    )

