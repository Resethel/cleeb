# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand

from datasets.models import Dataset, DatasetCategory


class Command(BaseCommand):
    help = "(Re-)generate the slugs of all the datasets in the database."

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Regenerating the slugs of all the datasets in the database..."))
        for dataset in Dataset.objects.all():
            dataset.save()
        self.stdout.write(self.style.SUCCESS("Regenerating the slugs of all the datasets categories in the database..."))
        for category in DatasetCategory.objects.all():
            category.save()
        self.stdout.write(self.style.SUCCESS("Done."))
# End class RegenerateCities