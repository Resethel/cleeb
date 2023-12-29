from django.contrib import admin

from .models import City


class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'id')
    search_fields = ('name', 'id')

admin.site.register(City, CityAdmin)
