# -*- coding: utf-8 -*-
"""
Admin for the `contact` application.
"""
from django.contrib import admin

from contact.models import Contact

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    """
    Admin for the `Contact` model.
    """
    list_display = ('name', 'email', 'subject', 'message')
    search_fields = ('name', 'email', 'subject', 'message')

    # ------------------------------------------------------------------------------------------------------------------
    # Fieldsets
    # ------------------------------------------------------------------------------------------------------------------

    # fieldsets = (
    #     (None, {
    #         'fields': ('name', 'email', 'subject', 'message')
    #     }),
    #     ('Dates', {
    #         'fields': ('created', 'modified'),
    #         'classes': ('collapse',),
    #     }),
    # )
# End class ContactAdmin
