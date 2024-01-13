from django.contrib import admin

from .models import City, MapLayer, MapRender


class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'id')
    search_fields = ('name', 'id')

admin.site.register(City, CityAdmin)

class MapLayerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('id', 'name')

admin.site.register(MapLayer, MapLayerAdmin)

class MapRenderAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'embed_html', 'full_html')
    search_fields = ('id', 'name')

admin.site.register(MapRender, MapRenderAdmin)