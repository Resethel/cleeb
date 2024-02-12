from django.contrib import admin

from .models import Map



# ======================================================================================================================
# Admin classes for the Map model
# ======================================================================================================================

class AuthorInline(admin.TabularInline):
    """Inline class for the Person model."""
    model = Map.authors.through
    extra = 1

    show_change_link = True
# End class AuthorInline

class MapAdmin(admin.ModelAdmin):
    """Admin class for ThematicMap model."""

    inlines = [
        AuthorInline, # Inline for the Person model
    ]
# End class MapAdmin

admin.site.register(Map, MapAdmin)