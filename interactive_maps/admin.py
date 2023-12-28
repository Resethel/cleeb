from django.contrib import admin

from .models import Author, Map, Section, Text


# ======================================================================================================================
# Admin classes for the Section model
# ======================================================================================================================

class SectionAdmin(admin.ModelAdmin):
    """Admin class for the ThematicMapTextSection model."""
# End class SectionAdmin

admin.site.register(Section, SectionAdmin)

# ======================================================================================================================
# Admin classes for the Text
# ======================================================================================================================

class SectionInline(admin.StackedInline):
    """Inline class for the ThematicMapTextSection model."""
    model = Section
    extra = 1
    show_change_link = True
# End class SectionInline

class TextAdmin(admin.ModelAdmin):
    """Admin class for the Text model."""

    inlines = [
        SectionInline, # Inline for the ThematicMapTextSection model
    ]
# End class TextAdmin

admin.site.register(Text, TextAdmin)

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

class TextInline(admin.StackedInline):
    """Inline class for the Text model."""
    model = Text
    extra = 1
    show_change_link = True
# End class TextInline

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
        TextInline, # Inline for the Text model
    ]
# End class MapAdmin

admin.site.register(Map, MapAdmin)