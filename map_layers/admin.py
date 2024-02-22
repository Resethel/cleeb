# -*- coding: utf-8 -*-
"""
Admin classes for the `map_layers` application.
"""
from django.contrib import admin
from django.utils.html import format_html

from map_layers.choices import GenerationStatus
from map_layers.models import MapLayer, MapLayerCustomProperty

# ======================================================================================================================
# Constants
# ======================================================================================================================

CLOCK_ICON_HTML = """
<span style="background-image: url('/static/admin/img/icon-clock.svg');
             background-repeat: no-repeat;
             background-position: 0 -16;
             position: relative;
             width: 16px;
             height: 16px;
             display: inline-block;
             vertical-align: middle;
             overflow: hidden;
             
             filter: brightness(0) saturate(100%) invert(51%) sepia(49%) saturate(4518%) hue-rotate(359deg) brightness(100%) contrast(107%);"
></span>
"""

# ======================================================================================================================
# MapLayer Admin
# ======================================================================================================================

class MapLayerCustomPropertyInline(admin.TabularInline):
    model = MapLayerCustomProperty
    extra = 0

class MapLayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'dataset', 'generation_status_icon', 'number_of_shapes')
    ordering = ('name',)
    readonly_fields = ('id', 'generation_status', 'task_id')

    inlines = [
        MapLayerCustomPropertyInline,
    ]

    # ------------------------------------------------------------------------------------------------------------------
    # Fieldset
    # ------------------------------------------------------------------------------------------------------------------

    fieldsets = (
        ('Generation Control', {
            'classes': ('collapse',),
            'fields': (
                ('generation_status', 'task_id'),
                'regenerate'
            )
        }),
        ('ID', {
            'classes': ('collapse',),
            'fields': ('id',)
        }),
        ('Description', {
            'fields': ('name', 'short_desc', 'description')
        }),
        ('Dataset and Layer configuration', {
            'fields': (
                ('dataset', 'shapefile'),
                ('max_polygons_points', 'max_multipolygons_polygons', 'max_multiolygons_points'),
                ('customize_properties',)
            )
        }),
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Non-Persistent Fields
    # ------------------------------------------------------------------------------------------------------------------

    def generation_status_icon(self, obj):
        match obj.generation_status:
            case GenerationStatus.COMPLETED:
                return format_html('<img src="/static/admin/img/icon-yes.svg" alt="True">')
            case GenerationStatus.FAILED:
                return format_html('<img src="/static/admin/img/icon-no.svg" alt="False">')
            case GenerationStatus.PENDING:
                return format_html('<img src="/static/admin/img/icon-unknown.svg" alt="Unknown">')
            case GenerationStatus.RUNNING:
                return format_html(CLOCK_ICON_HTML)
        return format_html('<img src="/static/admin/img/icon-alert.svg" alt="Invalid">')
    generation_status_icon.short_description = "Statut de Génération"

    def number_of_shapes(self, obj):
        if obj.shapes.count() == 0:
            return "-"
        return obj.shapes.count()
    number_of_shapes.short_description = "Nombre de Géométries"

admin.site.register(MapLayer, MapLayerAdmin)
