from django.contrib import admin

from django.contrib import admin
from .models import City

class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'feature_type', 'geometry_type')
    search_fields = ('name',)

admin.site.register(City, CityAdmin)
