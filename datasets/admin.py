from django.contrib import admin
from django.db.models import QuerySet

from .models import Dataset, DatasetCategory, DatasetTechnicalInformation, DatasetVersion

# ======================================================================================================================
# Dataset Category Admin
# ======================================================================================================================

class DatasetCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    ordering = ('name',)
    exclude = ('id',)
# End class DatasetCategoryAdmin
admin.site.register(DatasetCategory, DatasetCategoryAdmin)

# ======================================================================================================================
# Dataset Admin
# ======================================================================================================================

class DatasetVersionInline(admin.TabularInline):
    model = DatasetVersion
    list_display = ('date', 'file')
    extra = 0
# End class DatasetVersionInline

class DatasetTechnicalInformationInline(admin.TabularInline):
    model = DatasetTechnicalInformation
    list_display = ('key', 'value')
    extra = 0

class CategoryFilter(admin.SimpleListFilter):
    title = 'categories'  # Human-readable title which will be displayed in the right admin sidebar just above the filter options.
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

    list_display = ('name', 'category', 'format', 'short_desc', 'file_size')
    list_filter = ('format', CategoryFilter)
    search_fields = ('name',)
    ordering = ('name', 'format')
    exclude = ('id', 'slug')

    # ------------------------------------------------------------------------------------------------------------------
    # Custom admin fields
    # ------------------------------------------------------------------------------------------------------------------

    def category(self, dataset : Dataset):
        if dataset.categories is None or dataset.categories.count() == 0:
            return "Non Défini"
        return ", ".join([category.name for category in dataset.categories.all()])
    # End def category

    def file_size(self, dataset : Dataset):
        # Get the latest version of the file of the dataset
        dataset_version = dataset.get_latest_version()

        if dataset_version is not None and dataset_version.file:
            return f"{dataset_version.file.size / 1024 / 1024:.2f} MB"
        return "-"

    file_size.short_description = 'File Size (MB)'

    # ------------------------------------------------------------------------------------------------------------------
    # Inlines
    # ------------------------------------------------------------------------------------------------------------------

    inlines = [DatasetVersionInline, DatasetTechnicalInformationInline]
# End class DatasetAdmin

admin.site.register(Dataset, DatasetAdmin)