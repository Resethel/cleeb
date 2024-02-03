from django.contrib import admin

from map_layers.models import City, CityDatasetKeyValue, MapLayer, MapLayerCustomProperty, GenerationStatus


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

# ======================================================================================================================
# City Admin
# ======================================================================================================================

class CityDatasetKeyValueInline(admin.TabularInline):
    model = CityDatasetKeyValue
    extra = 1  # Number of extra forms to display
# End class CityDatasetKeyValueInline


class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'limits_dataset', 'generation_status')
    ordering = ('name',)
    exclude = ('id', 'status')

    inlines = [
        CityDatasetKeyValueInline,
    ]
# End class CityAdmin

admin.site.register(City, CityAdmin)
