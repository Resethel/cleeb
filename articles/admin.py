# -*- coding: utf-8 -*-
"""
Admin for the `article` application.
"""
from django.contrib import admin

from .models import Article
from django.utils.translation import gettext_lazy as _

# ======================================================================================================================
# AttachmentInline
# ======================================================================================================================

class AttachmentInline(admin.TabularInline):
    """Inline for the `File` model."""
    model = Article.attachments.through
    extra = 0

    def slug(self, obj):
        return obj.file.slug
    slug.short_description = _("Slug of the attachment")

    def description(self, obj):
        return obj.file.short_description
    description.verbose_name = _("Description")
    description.short_description = _("Description of the attachment")

    def download_url(self, obj):
        return obj.file.download_url
    download_url.verbose_name = _("Download URL")
    download_url.short_description = _("URL to download the attachment")

    def get_readonly_fields(self, request, obj=None):
        return list(super().get_readonly_fields(request, obj)) + ["slug", "description", "download_url"]
# End class AttachmentInline

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