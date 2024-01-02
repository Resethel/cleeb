from django.contrib import admin

from .models import Author, Map

# ======================================================================================================================
# Admin classes for the Author model
# ======================================================================================================================

class AuthorAdmin(admin.ModelAdmin):
    """Admin class for the Author model."""
# End class AuthorAdmin

admin.site.register(Author, AuthorAdmin)


# ======================================================================================================================
# Admin classes for the Map model
# ======================================================================================================================

class AuthorInline(admin.TabularInline):
    """Inline class for the Author model."""
    model = Map.authors.through
    extra = 1

    show_change_link = True
# End class AuthorInline

class MapAdmin(admin.ModelAdmin):
    """Admin class for ThematicMap model."""

    inlines = [
        AuthorInline, # Inline for the Author model
    ]
# End class MapAdmin

admin.site.register(Map, MapAdmin)