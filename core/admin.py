# -*- coding: utf-8 -*-
"""
Admin for the `core` application.
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from core.filters import PersonFullNameFilter, PersonOrganizationsFilter
from core.models import Person, Organization


# ======================================================================================================================
# Person
# ======================================================================================================================

class PersonAdmin(admin.ModelAdmin):
    """Admin class for the Person model."""

    list_display       = ('id', 'full_name', 'email', 'member_of', 'has_picture')
    list_display_links = ('id', 'full_name')
    list_filter        = (PersonFullNameFilter, PersonOrganizationsFilter)
    search_fields      = ('id', 'full_name')
    list_per_page      = 25

    readonly_fields = ('id', 'slug')

    # ------------------------------------------------------------------------------------------------------------------
    # Fieldsets
    # ------------------------------------------------------------------------------------------------------------------

    fieldsets = (
        (_('ID'), {
            'classes': ('collapse',),
            'fields': (('id', 'slug'),)
        }),
        (_('Nom'), {
            'description': _("Name of the person. The last name and first name or the pseudonym are required. All 3 can be filled in simultaneously."),
            'fields': (('lastname', 'firstname'), 'pseudonym')
        }),
        (_('Contact and Social medias'), {
            'fields': ('email', 'facebook', 'instagram', 'twitter_x', 'website')
        }),
        (_('Picture'), {
            'fields': ('picture',)
        }),
        (_("Organization affiliations"), {
            'fields': ('organizations',)
        }),
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Non-persistent fields
    # ------------------------------------------------------------------------------------------------------------------

    def has_picture(self, obj):
        return bool(obj.picture)
    has_picture.boolean = True
    has_picture.short_description = _("Has picture")

    def member_of(self, obj):
        if obj.organizations.count() == 0:
            return "-"
        return ", ".join([organization.name for organization in obj.organizations.all()])
    member_of.short_description = _("Organization affiliations")
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
        (_('ID'), {
            'classes': ('collapse',),
            'fields': (('id', 'slug'),)
        }),
        (_('Nom'), {
            'fields': ('name',)
        }),
        (_('Logo and other images'), {
            'fields': ('logo',)
        }),
        (_('Contact and Social medias'), {
            'fields': ('email', 'facebook', 'instagram', 'twitter_x', 'website')
        }),
        (_('Description'), {
            'fields': ('type', 'description')
        }),
    )


admin.site.register(Organization, OrganizationAdmin)