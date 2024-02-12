from django.contrib import admin
from core.models import Author, Organization

# Register your models here.

# ======================================================================================================================
# Author
# ======================================================================================================================

class AuthorAdmin(admin.ModelAdmin):
    """Admin class for the Author model."""
# End class AuthorAdmin

admin.site.register(Author, AuthorAdmin)


# ======================================================================================================================
# Organization
# ======================================================================================================================

admin.site.register(Organization)