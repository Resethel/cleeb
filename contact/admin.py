# -*- coding: utf-8 -*-
"""
Admin for the `contact` application.
"""
from django.contrib import admin

from django.utils.translation import gettext_lazy as _
from contact.models import Contact

# ======================================================================================================================
# Contact
# ======================================================================================================================

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """
    Admin for the `Contact` model.
    """
    list_display       = ('name', 'email', 'subject', 'message')
    list_display_links = ('name', 'email', 'subject')
    search_fields      = ('name', 'email', 'subject', 'message')
    readonly_fields    = ('name', 'email', 'subject', 'message', 'created_at')

    # ------------------------------------------------------------------------------------------------------------------
    # Fieldsets
    # ------------------------------------------------------------------------------------------------------------------

    fieldsets = (
        (_('Contact'), {
            'fields': (
                'name',
                'email',
                'subject',
                'message',
            ),
        }),
        (_('Admin actions'), {
            'fields': (
                'created_at',
                'handled',
            ),
        })
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Permissions
    # ------------------------------------------------------------------------------------------------------------------

    def has_add_permission(self, request):
        return False
    # End def has_add_permission

# End class ContactAdmin
