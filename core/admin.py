from django.contrib import admin
from core.models import Person, Organization


# ======================================================================================================================
# Person
# ======================================================================================================================

class PersonAdmin(admin.ModelAdmin):
    """Admin class for the Person model."""
# End class AuthorAdmin

admin.site.register(Person, PersonAdmin)


# ======================================================================================================================
# Organization
# ======================================================================================================================

admin.site.register(Organization)