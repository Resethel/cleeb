from django.contrib import admin

from .models import Shape


class ShapeAdmin(admin.ModelAdmin):
    list_display = ('id', 'feature_type', 'properties')
    search_fields = ('id', 'feature_type', 'properties')

admin.site.register(Shape, ShapeAdmin)
