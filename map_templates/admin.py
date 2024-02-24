# -*- coding: utf-8 -*-
"""
Admin module for the `map_templates` application.
"""
from __future__ import annotations
from django.contrib import admin
from django import forms
from django.utils.html import format_html
from nested_admin.nested import NestedModelAdmin, NestedStackedInline, NestedTabularInline

from map_templates.choices import GenerationStatus
from map_templates.models import FeatureGroup, Filter, Layer, MapTemplate, Style, PropertyStyle, TileLayer

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
# TileLayer
# ======================================================================================================================

@admin.register(TileLayer)
class TileLayerAdmin(NestedModelAdmin):
    list_display = ('verbose_name', 'name', 'type', 'display_url')
    list_display_links = ('verbose_name', 'name')
    list_filter = ('type',)
    search_fields = ('name', 'type')
    ordering = ('verbose_name', 'type')
    list_per_page = 25

    # Add a custom display for the URL
    def display_url(self, obj):
        if obj.url is None:
            return 'N/A'

        # If the URL is too long, display only the first 50 characters
        if len(obj.url) > 50:
            return obj.url[:50] + "..."
        return obj.url
    display_url.short_description = 'URL'

    def formfield_for_dbfield(self, db_field, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == 'url':
            formfield.widget = forms.Textarea(attrs={'rows': 4, 'cols': 100})
        return formfield
# End class TileLayerAdmin

# ======================================================================================================================
# Style
# ======================================================================================================================

@admin.register(PropertyStyle)
class PropertyStyleAdmin(NestedModelAdmin):
    list_display = ('style', 'key', 'value')
    list_display_links = ('style', 'key', 'value')
    list_filter = ('style',)
    list_per_page = 25

    search_fields = ('style', 'key', 'value')
    ordering = ('style', 'key')

    fieldsets = (
        ("Style lié", {
            'fields': ('style',)
        }),
        ("Clé et valeur", {
            'fields': (('key', 'value'),)
        }),
        ("Style", {
            'fields': ('color', 'weight', 'opacity', 'fill', 'fill_color', 'fill_rule', 'fill_opacity', 'dash_array',
                       'dash_offset', 'line_cap', 'line_join')
        }),
    )


# End class PropertyStyleAdmin

class PropertyStyleInline(NestedStackedInline):
    model = PropertyStyle
    extra = 0
    verbose_name = "Style des propriétés"
    verbose_name_plural = "Styles des propriétés"

    fieldsets = (
        ("Clé et valeur", {
            'fields': (('key', 'value'),)
        }),
        ("Style", {
            'fields': ('color', 'weight', 'opacity', 'fill', 'fill_color', 'fill_rule', 'fill_opacity', 'dash_array',
                       'dash_offset', 'line_cap', 'line_join')
        }),
    )
# End class PropertyStyleInline


@admin.register(Style)
class StyleAdmin(NestedModelAdmin):
    list_display = (
        'style_type',
        'owning_layer',
        'id',
        'color',
        'weight',
        'opacity',
        'fill',
        'fill_color',
        'fill_opacity',
        'fill_rule',
        'line_cap',
        'line_join',
        'dash_array',
        'dash_offset',
    )
    list_display_links = ('id',)
    readonly_fields = ('style_type', 'owning_layer', 'id')
    search_fields = ('style_type', 'owning_layer', 'id')
    list_per_page = 25


    inlines = [
        PropertyStyleInline
    ]

    # ------------------------------------------------------------------------------------------------------------------
    # FieldSets
    # ------------------------------------------------------------------------------------------------------------------

    fieldsets = (
        ("Appartenance", {
            'classes': ('collapse',),  # Hide the fieldset by default
            'description': "L'appartenance d'un style à une couche.",
            'fields': (('style_type', 'owning_layer', 'id'),)
        }),
        ("Bordures", {
            'description': "Les bordures sont les lignes qui délimitent les formes géométriques.",
            'fields': ('stroke', ('color', 'weight', 'opacity', 'dash_array', 'dash_offset', 'line_cap', 'line_join'))
        }),
        ("Remplissage", {
            'description': "Le remplissage est la couleur qui remplit les formes géométriques.",
            'fields': ('fill', ('fill_color', 'fill_opacity', 'fill_rule'))
        }),

    )
# End class StyleAdmin


class StyleInline(NestedStackedInline):
    model = Style
    extra = 0
    verbose_name = "Style"
    verbose_name_plural = "Styles"

    inlines = [
        PropertyStyleInline
    ]
# End class StyleInline


# ======================================================================================================================
# Filter
# ======================================================================================================================

@admin.register(Filter)
class FilterAdmin(NestedModelAdmin):
    list_display = ('id', 'key', 'operator', 'value')
    list_display_links = ('id', 'key', 'operator', 'value')
    search_fields = ('key',)
    list_per_page = 25
# End class FilterAdmin

class FilterInline(NestedTabularInline):
    model = Filter
    extra = 0
    # show_change_link = True

    verbose_name = "Filter"
    verbose_name_plural = "Filters"
# End class FilterInline

# ======================================================================================================================
# Layer
# ======================================================================================================================

@admin.register(Layer)
class LayerAdmin(NestedModelAdmin):
    list_display = ('id', 'map_layer', 'show')
    list_display_links = ('id', 'map_layer', 'show')
    search_fields = ('name', 'map_layer', 'show')
    list_per_page = 25

    inlines = [
        FilterInline,
    ]
# End class LayerAdmin

class LayerInline(NestedStackedInline):
    model = Layer
    extra = 0
    verbose_name = "Layer"
    verbose_name_plural = "Layers"

    inlines = [
        FilterInline,
    ]

    # Hide the foreign keys to the map template and the feature group in the admin.
    # If direct alteration is needed, it should be done through the map template or the feature group
    # admin pages and not through the layer admin page
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ['owner_map_template', 'owner_feature_group']:
            return None
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
# End class LayerInline

# ======================================================================================================================
# FeatureGroup
# ======================================================================================================================

@admin.register(FeatureGroup)
class FeatureGroupAdmin(NestedModelAdmin):
    list_display = ('id', 'show_on_startup')
    list_display_links = ('id', 'show_on_startup')
    search_fields = ('id', 'show_on_startup')
    list_per_page = 25

    inlines = [
        LayerInline,
    ]
# End class FeatureGroupAdmin

class FeatureGroupInline(NestedStackedInline):
    model = FeatureGroup
    extra = 0
    verbose_name = "Feature Group"
    verbose_name_plural = "Feature Groups"

    inlines = [
        LayerInline,
    ]
# End class FeatureGroupInline

# ======================================================================================================================
# Map template
# ======================================================================================================================

@admin.register(MapTemplate)
class MapTemplateAdmin(NestedModelAdmin):
    list_display = ('id', 'name', 'generation_status_icon', 'linked_map_render')
    list_display_links = ('id', 'name',)
    search_fields = ('id', 'name',)
    list_per_page = 25

    readonly_fields = ('id', 'generation_status', 'task_id')

    inlines = [
        LayerInline,
        FeatureGroupInline,
    ]

    # ------------------------------------------------------------------------------------------------------------------
    # FieldSets
    # ------------------------------------------------------------------------------------------------------------------

    fieldsets = (
        ('ID', {
            'classes': ('collapse',),
            'fields': ('id',),
        }),
        ('Generation Control', {
            'classes': ('collapse',),
            'fields': (
                ('generation_status', 'task_id'),
                'regenerate'
            )
        }),
        ('Description', {
            'fields': ('name',)
        }),
        ('Tiles and Controls', {
            'fields': ('tiles','zoom_start', 'layer_control', 'zoom_control')
        }),
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Non-Persistent Fields
    # ------------------------------------------------------------------------------------------------------------------

    def generation_status_icon(self, obj : MapTemplate):
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

    def linked_map_render(self, obj : MapTemplate):
        if obj.render is None:
            return "-"
        else:
            name = obj.render.name
            id_ = obj.render.id
            return format_html(f'<a href="/admin/interactive_maps/maprender/{id_}/change/">{name}@{id_}</a>')
    linked_map_render.short_description = "Rendu Lié"
# End class MapTemplateAdmin