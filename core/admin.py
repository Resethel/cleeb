from django.contrib import admin
from core.models import Organization, Theme

# Register your models here.
admin.site.register(Theme)
admin.site.register(Organization)