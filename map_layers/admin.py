from django.contrib import admin

from map_layers.models import MapLayer, MapLayerCustomProperty


# ======================================================================================================================
# MapLayer Admin
# ======================================================================================================================

class MapLayerCustomPropertyInline(admin.TabularInline):
    model = MapLayerCustomProperty
    extra = 0

class MapLayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'dataset', 'number_of_shapes')
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
