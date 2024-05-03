# -*- coding: utf-8 -*-
"""
Admin module for the `datasets` application.
"""
import django.contrib.gis.admin as gis_admin
from django.contrib import admin
from django.db.models import QuerySet
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from common.utils.admin import get_clock_icon_html
from common.utils.tasks import TaskStatus
from .models import Dataset, DatasetCategory, DatasetLayer, DatasetLayerField, DatasetTechnicalInformation, \
    DatasetVersion, Feature


# ======================================================================================================================
# Dataset Category Admin
# ======================================================================================================================

class DatasetCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    ordering = ('name',)
    exclude = ('id', 'slug')
# End class DatasetCategoryAdmin
admin.site.register(DatasetCategory, DatasetCategoryAdmin)

# ======================================================================================================================
# Feature Admin
# ======================================================================================================================

class FeatureAdmin(gis_admin.GISModelAdmin):
    list_display = ('id', 'layer')
    readonly_fields = ('id', 'layer')

# End class FeatureAdmin
admin.site.register(Feature, FeatureAdmin)

# ======================================================================================================================
# DatasetLayer Admin
# ======================================================================================================================

class DatasetLayerFieldAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent_dataset', 'parent_layer', 'type', 'max_length', 'precision')
    search_fields = ('name',)
    ordering = ('name',)
    readonly_fields = ('id',)

    # ------------------------------------------------------------------------------------------------------------------
    # Custom admin fields
    # ------------------------------------------------------------------------------------------------------------------

    def parent_dataset(self, field : DatasetLayerField):
        if field.layer is not None and field.layer.dataset is not None:
            parent_name = f"{field.layer.dataset.dataset} v{field.layer.dataset.get_version_number()}"
            return format_html(f'<a href="/admin/datasets/dataset/{field.layer.dataset.id}/change/">{parent_name}</a>')
        return "-"
    parent_dataset.short_description = _('Parent Dataset')

    def parent_layer(self, field : DatasetLayerField):
        if field.layer is not None:
            return format_html(f'<a href="/admin/datasets/datasetlayer/{field.layer.id}/change/">{field.layer.name}</a>')
        return "-"
    parent_layer.short_description = _('Parent Layer')
# End class DatasetLayerFieldAdmin

class DatasetLayerFieldInline(admin.TabularInline):
    model = DatasetLayerField
    list_display = ('name', 'type', 'max_length', 'precision')
    extra = 0
# End class DatasetLayerAdmin

class DatasetLayerAdmin(gis_admin.GISModelAdmin):
    list_display = ('id', 'name', 'dataset')
    search_fields = ('name', 'dataset__name')
    ordering = ('name',)
    exclude = ('id', 'slug')

    inlines = [DatasetLayerFieldInline]
# End class DatasetLayerAdmin

admin.site.register(DatasetLayerField, DatasetLayerFieldAdmin)
admin.site.register(DatasetLayer, DatasetLayerAdmin)

# ======================================================================================================================
# DatasetVersion Admin
# ======================================================================================================================

class DatasetVersionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'parent_dataset', 'date', 'file_size', 'encoding', 'generation_status')
    list_filter = ('dataset', 'date')
    list_display_links = ('id', 'name')
    search_fields = ('dataset__name',)
    ordering = ('-date',)
    readonly_fields = ('id', 'dataset', 'task_id', 'task_status')

    # ------------------------------------------------------------------------------------------------------------------
    # FieldSets
    # ------------------------------------------------------------------------------------------------------------------

    fieldsets = (
        (_("Task Information"), {  # Fieldset title (legend
            'classes': ('collapse',),  # Hide the fieldset by default
            'fields': (
                ('task_id', 'task_status'),
                'regenerate'
            )
        }),
        (_("Information"), {
            'fields': ('id', 'dataset')
        }),
        (_("Configuration"), {
            'fields': ('date', 'file', 'encoding')
        }),
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Custom admin fields
    # ------------------------------------------------------------------------------------------------------------------

    def name(self, version : DatasetVersion):
        return f"{version.dataset.name} (V{version.get_version_number()})"
    name.short_description = 'Name'

    def parent_dataset(self, version : DatasetVersion):
        if version.dataset is not None:
            parent_name = f"{version.dataset.name}"
            return format_html(f'<a href="/admin/datasets/dataset/{version.dataset.id}/change/">{parent_name}</a>')
        return "-"
    parent_dataset.short_description = _('Parent Dataset')

    def file_size(self, version : DatasetVersion):
        if version.file:
            return f"{version.file.size / 1024 / 1024:.2f} MB"
        return "-"
    file_size.short_description = _('File Size (MB)')


    def generation_status(self, version : DatasetVersion):
        match version.task_status:
            case TaskStatus.SUCCESS:
                return format_html('<img src="/static/admin/img/icon-yes.svg" alt="True">')
            case TaskStatus.FAILURE:
                return format_html('<img src="/static/admin/img/icon-no.svg" alt="False">')
            case TaskStatus.STARTED:
                return format_html(get_clock_icon_html("orange"))
            case TaskStatus.PENDING:
                return format_html(get_clock_icon_html("white"))
            case TaskStatus.REVOKED:
                return format_html('<img src="/static/admin/img/icon-no.svg" alt="False">')
            case _:
                return format_html('<img src="/static/admin/img/icon-alert.svg" alt="Invalid">')
    generation_status.short_description = _('Generation Status')
# End class DatasetVersionAdmin

admin.site.register(DatasetVersion, DatasetVersionAdmin)

# ======================================================================================================================
# Dataset Admin
# ======================================================================================================================

class DatasetVersionInline(admin.TabularInline):
    model = DatasetVersion
    list_display = ('date', 'file')
    fields = ('date', 'file', 'encoding')
    extra = 0
# End class DatasetVersionInline

class DatasetTechnicalInformationInline(admin.TabularInline):
    model = DatasetTechnicalInformation
    list_display = ('key', 'value')
    extra = 0

class CategoryFilter(admin.SimpleListFilter):
    title = _('categories')  # Human-readable title which will be displayed in the right admin sidebar just above the filter options.
    parameter_name = 'categories'  # Parameter for the filter that will be used in the URL query.

    def lookups(self, request, model_admin):
        categories = set([c for d in Dataset.objects.all() for c in d.categories.all()])
        return [(c.id, c.name) for c in categories]

    def queryset(self, request, queryset : QuerySet):
        if self.value():
            return queryset.filter(id=self.value())
        else:
            return queryset
# End class CategoryFilter

class DatasetAdmin(admin.ModelAdmin):

    # ------------------------------------------------------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------------------------------------------------------

    list_display = ('name', 'category', 'short_desc', 'file_size')
    list_filter = (CategoryFilter,)
    search_fields = ('name',)
    ordering = ('name',)
    exclude = ('id', 'slug')

    # ------------------------------------------------------------------------------------------------------------------
    # Custom admin fields
    # ------------------------------------------------------------------------------------------------------------------

    def category(self, dataset : Dataset):
        if dataset.categories is None or dataset.categories.count() == 0:
            return _("Undefined")
        return ", ".join([category.name for category in dataset.categories.all()])
    # End def category

    def file_size(self, dataset : Dataset):
        # Get the latest version of the file of the dataset
        dataset_version = dataset.get_latest_version()

        if dataset_version is not None and dataset_version.file:
            return f"{dataset_version.file.size / 1024 / 1024:.2f} MB"
        return "-"

    file_size.short_description = _('File Size (MB)')

    # ------------------------------------------------------------------------------------------------------------------
    # Inlines
    # ------------------------------------------------------------------------------------------------------------------

    inlines = [DatasetVersionInline, DatasetTechnicalInformationInline]
# End class DatasetAdmin

admin.site.register(Dataset, DatasetAdmin)