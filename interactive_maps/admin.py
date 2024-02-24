from django.contrib import admin
from django.utils.html import format_html

from .models import Map, MapRender


# ======================================================================================================================
# Admin classes for the MapRender model
# ======================================================================================================================

@admin.register(MapRender)
class MapRenderAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'linked_template', 'has_full_html', 'has_embed_html')
    search_fields = ('id', 'name')

    readonly_fields = ('id', 'slug', 'template')

    # ------------------------------------------------------------------------------------------------------------------
    # Fieldset
    # ------------------------------------------------------------------------------------------------------------------

    fieldsets = (
        ('ID', {
            'classes': ('collapse',),
            'fields': (('id','slug',), 'template'),
        }),
        ('Description', {
            'fields': ('name',),
        }),
        ('Render', {
            'fields': ('embed_html', 'full_html'),
        })
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Non-persistent fields
    # ------------------------------------------------------------------------------------------------------------------

    def linked_template(self, obj: MapRender):
        if obj.template is None:
            return "-"
        else:
            name = obj.template.name
            id_ = obj.template.id
            return format_html(f"<a href=/admin/map_templates/maptemplate/{id_}>{name}@{id_}</a>")
    linked_template.short_description = "Modèle Lié"

    def has_full_html(self, obj: MapRender):
        return obj.full_html is not None
    has_full_html.boolean = True
    has_full_html.short_description = "has full html?"

    def has_embed_html(self, obj: MapRender):
        return obj.embed_html is not None
    has_embed_html.boolean = True
    has_embed_html.short_description = "has embed html?"
# End class MapRenderAdmin

# ======================================================================================================================
# Admin classes for the Map model
# ======================================================================================================================

class AuthorInline(admin.TabularInline):
    """Inline class for the Person model."""
    model = Map.authors.through
    extra = 1

    show_change_link = True
# End class AuthorInline

@admin.register(Map)
class MapAdmin(admin.ModelAdmin):
    """Admin class for ThematicMap model."""

    inlines = [
        AuthorInline, # Inline for the Person model
    ]
# End class MapAdmin