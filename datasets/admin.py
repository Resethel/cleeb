from django.contrib import admin

from .models import Dataset, DatasetVersion


# ======================================================================================================================
# Dataset Admin
# ======================================================================================================================

class DatasetVersionInline(admin.TabularInline):
    list_display = ('date', 'file')
    model = DatasetVersion
    extra = 0
# End class DatasetVersionInline

class DatasetAdmin(admin.ModelAdmin):

    # ------------------------------------------------------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------------------------------------------------------

    list_display = ('name', 'category', 'format', 'short_desc', 'file_size')
    list_filter = ('format', 'category')
    search_fields = ('name',)
    ordering = ('name', 'category')
    exclude = ('id',)

    # ------------------------------------------------------------------------------------------------------------------
    # Custom admin fields
    # ------------------------------------------------------------------------------------------------------------------

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

    inlines = [DatasetVersionInline]
# End class DatasetAdmin



admin.site.register(Dataset, DatasetAdmin)