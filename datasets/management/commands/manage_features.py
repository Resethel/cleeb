# -*- coding: utf-8 -*-
"""
Management command to manage the features.
"""
from django.core.management.base import BaseCommand
from django.db import connection

from datasets.models import Dataset, Feature


class Command(BaseCommand):
    help = "Manage the features of the datasets."

    def add_arguments(self, parser):
        action_parser = parser.add_subparsers(dest='action', help="The action to perform.")

        # --------------------------------------------------------------------------------------------------------------
        # parser for the 'count' action
        # --------------------------------------------------------------------------------------------------------------

        count_parser = action_parser.add_parser('count', help="Count the number of features.")
        count_parser.add_argument(
            '--layer', '-l',
            type=str,
            help="The name of the layer to count the features of. If not provided, all layers will be counted."
        )

        # --------------------------------------------------------------------------------------------------------------
        # parser for the 'clear' action
        # --------------------------------------------------------------------------------------------------------------

        clear_parser = action_parser.add_parser('clear', help="Clear the features.")
        target_group = clear_parser.add_mutually_exclusive_group()

        target_group.add_argument(
            '--layer', '-l',
            type=str,
            help="The name of the layer to clear the features of."
        )
        target_group.add_argument(
            '--dataset', '-d',
            type=str,
            help="The name of the dataset to clear the features of."
                 "A specific version can be specified by appending the version number after a colon."
                 "For example: 'my_dataset:1'."
        )

        clear_parser.add_argument(
            '--yes', '-y',
            action='store_true',
            help="Skip the confirmation prompt."
        )
    # End def add_arguments

    def handle(self, *args, **options):
        action = options.pop('action')

        if action == 'count':
            self.count_features(**options)
        elif action == 'clear':
            self.clear_features(**options)
    # End def handle

    def count_features(self, layer=None, **kwargs):
        """Count the number of features."""
        if layer is not None:
            features = Feature.objects.filter(layer__name=layer)
            count = features.count()
            self.stdout.write(self.style.SUCCESS(f"{count} features found in the layer '{layer}'."))
            return

        features = Feature.objects.all()
        count = features.count()
        self.stdout.write(self.style.SUCCESS(f"{count} features found in total."))
    # End def count_features

    def clear_features(self, layer=None, dataset=None, yes=False, **kwargs):
        """Clear the features."""
        if layer is not None:
            features = Feature.objects.filter(layer__name=layer)
            confirm_str = f"Are you sure you want to delete {features.count()} features from the layer '{layer}'? [y/N] "
        elif dataset is not None:
            dataset_name, version_number = dataset.split(":")[:2] if ':' in dataset else (dataset, None)

            if version_number is None:
                features = Feature.objects.filter(layer__dataset__name=dataset_name, layer__version__version_number=version_number)
                confirm_str = f"Are you sure you want to delete {features.count()} features from the dataset '{dataset_name}'? [y/N] "
            else:
                dataset_version = Dataset.objects.get(name=dataset_name).get_version(int(version_number))
                features = Feature.objects.filter(layer__dataset=dataset_version)
                confirm_str = f"Are you sure you want to delete {features.count()} features from the dataset '{dataset_name}' version {version_number}? [y/N] "
        else:
            features = Feature.objects.all()
            confirm_str = f"Are you sure you want to delete all the {features.count()} features from the database? [y/N] "


        if not yes:
            confirm = input(confirm_str)
            if confirm.lower() not in ('y', 'yes'):
                self.stdout.write(self.style.WARNING("Action cancelled."))
                return

        # Delete the features
        deleted = features.delete()
        count = deleted[0]
        self.stdout.write(self.style.SUCCESS(f"{count} features deleted."))

        # Reset the primary key sequence if all features were deleted
        if Feature.objects.count() > 0:
            return
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT setval(pg_get_serial_sequence('datasets_feature', 'id'), coalesce(max(id), 1), max(id) IS NOT null) FROM datasets_feature;"
            )
    # End def clear_features
# End class Command