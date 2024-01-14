from django.contrib import admin

from map_layers.models import Dataset, MapLayer, MapLayerCustomProperty, MapLayerStatus


# ======================================================================================================================
# Dataset Admin
# ======================================================================================================================

class DatasetAdmin(admin.ModelAdmin):

    list_display = ('name', 'category', 'format', 'short_desc', 'file_size')
    list_filter = ('format', 'category')
    search_fields = ('name',)
    ordering = ('name', 'category')
    exclude = ('id',)

    def file_size(self, obj):
        if obj.file:
            return f"{obj.file.size / 1024 / 1024:.2f} MB"
        return "-"

    file_size.short_description = 'File Size (MB)'

# End class DatasetAdmin

admin.site.register(Dataset, DatasetAdmin)

# ======================================================================================================================
# MapLayer Admin
# ======================================================================================================================

class MapLayerCustomPropertyInline(admin.TabularInline):
    model = MapLayerCustomProperty
    extra = 0

class MapLayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'dataset', 'number_of_shapes', 'status')
    ordering = ('name',)
    exclude = ('id', 'status')

    inlines = [
        MapLayerCustomPropertyInline,
    ]

    def number_of_shapes(self, obj):
        if obj.shapes.count() == 0:
            return "-"
        return obj.shapes.count()

admin.site.register(MapLayer, MapLayerAdmin)