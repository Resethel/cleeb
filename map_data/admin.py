from django.contrib import admin

from .models import MapRender

class MapRenderAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'embed_html', 'full_html')
    search_fields = ('id', 'name')

admin.site.register(MapRender, MapRenderAdmin)