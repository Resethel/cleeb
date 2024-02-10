# -*- coding: utf-8 -*-
from django.contrib import admin
from nested_admin.nested import NestedModelAdmin, NestedStackedInline, NestedTabularInline

from map_templates.models import FeatureGroup, Filter, Layer, MapTemplate, Style, PropertyStyle, TileLayer


# ======================================================================================================================
# TileLayer
# ======================================================================================================================

@admin.register(TileLayer)
class TileLayerAdmin(NestedModelAdmin):
    list_display = ('name',)
    list_display_links = ('name',)
    search_fields = ('name', )
    list_per_page = 25
# End class TileLayerAdmin

# ======================================================================================================================
# Style
# ======================================================================================================================

@admin.register(Style)
class StyleAdmin(NestedModelAdmin):
    list_display = ('id', 'color', 'dash_array', 'dash_offset', 'fill', 'fill_color', 'fill_opacity', 'fill_rule')
    list_display_links = ('id',)
    search_fields = ('color', 'dash_array', 'dash_offset', 'fill', 'fill_color', 'fill_opacity', 'fill_rule')
    list_per_page = 25
# End class StyleAdmin

@admin.register(PropertyStyle)
class PropertyStyleAdmin(NestedModelAdmin):
    list_display = ('id', 'key', 'value', 'style')
    list_display_links = ('id', 'key', 'value')
    search_fields = ('key', 'value', 'style')
    list_per_page = 25
# End class PropertyStyleAdmin

class PropertyStyleInline(NestedStackedInline):
    model = PropertyStyle
    extra = 0
    verbose_name = "Property Style"
    verbose_name_plural = "Property Styles"
# End class PropertyStyleInline


# Create an inline for the style, knowing it has a foreign key to a generic model
class StyleInline(NestedStackedInline):
    model = Style
    extra = 0
    verbose_name = "Style"
    verbose_name_plural = "Styles"

    inlines = [
        PropertyStyleInline
    ]
# End class StyleInline

# Create an inline for the property style, knowing it has a foreign key to a generic model

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
        # StyleInline,
    ]
# End class LayerAdmin

class LayerInline(NestedStackedInline):
    model = Layer
    extra = 0
    verbose_name = "Layer"
    verbose_name_plural = "Layers"
    # show_change_link = True

    inlines = [
        FilterInline,
        # StyleInline,
    ]
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
    list_display = ('name',)
    list_display_links = ('name',)
    search_fields = ('name',)
    list_per_page = 25

    inlines = [
        LayerInline,
        FeatureGroupInline,
    ]
# End class MapTemplateAdmin