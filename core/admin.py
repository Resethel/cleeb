from django.contrib import admin

from core.filters import PersonFullNameFilter, PersonOrganizationsFilter
from core.models import Person, Organization


# ======================================================================================================================
# Person
# ======================================================================================================================

class PersonAdmin(admin.ModelAdmin):
    """Admin class for the Person model."""

    list_display = ('id', 'full_name', 'email', 'member_of', 'has_picture')
    list_display_links = ('id', 'full_name')
    list_filter = (PersonFullNameFilter, PersonOrganizationsFilter)
    search_fields = ('id', 'full_name')
    list_per_page = 25

    readonly_fields = ('id', 'slug')

    # ------------------------------------------------------------------------------------------------------------------
    # Fieldsets
    # ------------------------------------------------------------------------------------------------------------------

    fieldsets = (
        ('ID', {
            'classes': ('collapse',),
            'fields': (('id', 'slug'),)
        }),
        ('Dénomination', {
            'description': "Le nom de la personne. Le nom et prénom ou le pseudonyme sont requis. Les 3 peuvent être renseignés simultanément.",
            'fields': (('lastname', 'firstname'), 'pseudonym')
        }),
        ('Médias sociaux', {
            'fields': ('email', 'facebook', 'instagram', 'twitter_x', 'website')
        }),
        ('Image', {
            'fields': ('picture',)
        }),
        ('Lien avec des organisations', {
            'fields': ('organizations',)
        }),
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Non-persistent fields
    # ------------------------------------------------------------------------------------------------------------------

    def has_picture(self, obj):
        return bool(obj.picture)
    has_picture.boolean = True
    has_picture.short_description = "Possède une photo"

    def member_of(self, obj):
        if obj.organizations.count() == 0:
            return "-"
        return ", ".join([organization.name for organization in obj.organizations.all()])
    member_of.short_description = "Lien avec des organisations"
admin.site.register(Person, PersonAdmin)


# ======================================================================================================================
# Organization
# ======================================================================================================================

class OrganizationAdmin(admin.ModelAdmin):

    list_display = ('id', 'name', 'email')
    list_display_links = ('id', 'name')
    search_fields = ('id', 'name')
    list_per_page = 25

    readonly_fields = ('id', 'slug')

    # ------------------------------------------------------------------------------------------------------------------
    # Fieldsets
    # ------------------------------------------------------------------------------------------------------------------

    fieldsets = (
        ('ID', {
            'classes': ('collapse',),
            'fields': (('id', 'slug'),)
        }),
        ('Dénomination', {
            'fields': ('name',)
        }),
        ('Identité visuelle', {
            'fields': ('logo',)
        }),
        ('Contact et réseaux sociaux', {
            'fields': ('email', 'facebook', 'instagram', 'twitter_x', 'website')
        }),
        ('Description', {
            'fields': ('type', 'description')
        }),
    )


admin.site.register(Organization, OrganizationAdmin)