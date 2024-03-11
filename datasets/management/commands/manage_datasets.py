# -*- coding: utf-8 -*-
"""
Management command to manage the datasets.
"""
from django.core.management.base import BaseCommand

from datasets import services
from datasets.models import Dataset, DatasetVersion


class Command(BaseCommand):
    help = "Manage the datasets."

    def add_arguments(self, parser):
        action_parser = parser.add_subparsers(dest='action', help="The action to perform.")

        # --------------------------------------------------------------------------------------------------------------
        # parser for the 'list' action
        # --------------------------------------------------------------------------------------------------------------

        action_parser.add_parser('list', help="List the datasets.")

        # --------------------------------------------------------------------------------------------------------------
        # parser for the 'regen-features' action
        # --------------------------------------------------------------------------------------------------------------

        regen_feat_parser = action_parser.add_parser('regen-features', help="Regenerate the features of the datasets.")

        regen_feat_parser.add_argument(
            '--dataset', '-d',
            type=str,
            help="The name of the dataset to regenerate the features of."
                 "A specific version can be specified by appending the version number after a colon."
                 "For example: 'my_dataset:1'."
        )

        regen_feat_parser.add_argument(
            '--yes', '-y',
            action='store_true',
            help="Skip the confirmation prompt."
        )

        # --------------------------------------------------------------------------------------------------------------
        # parser for the 'sanitize' action
        # --------------------------------------------------------------------------------------------------------------

        sanitize_parser = action_parser.add_parser('sanitize', help="Sanitize the datasets.")

        sanitize_parser.add_argument(
            '--dataset', '-d',
            nargs='+', # 1 or more arguments
            type=str,
            help="The name of the dataset to sanitize."
                 "A specific version can be specified by appending the version number after a colon."
                 "For example: 'my_dataset:1'."
        )
    # End def add_arguments


    def handle(self, *args, **options):
        action = options.pop('action')

        if action == 'list':
            self.list_datasets(**options)
        elif action == 'regen-features':
            self.regenerate_features(**options)
        elif action == 'sanitize':
            self.sanitize(**options)
    # End def handle

    # ------------------------------------------------------------------------------------------------------------------
    # action methods
    # ------------------------------------------------------------------------------------------------------------------

    def list_datasets(self, **options):
        datasets = Dataset.objects.all()
        for dataset in datasets:
            str_ = f"{dataset.name}"
            version_count = dataset.versions.count()
            if version_count == 1:
                str_ += f" (1 version)"
            else:
                str_ += f" ({version_count} versions)"
            self.stdout.write(str_)

    # End def list_datasets

    def regenerate_features(self, **options):
        yes = options.pop('yes')
        dataset_args = options.pop('dataset')
        dataset_name, dataset_version = dataset_args.split(':')[:2] if dataset_args else (None, None)

        # Fetch the versions of the dataset
        if dataset_name is not None:
            if dataset_version is not None:
                dataset_versions = [Dataset.objects.get(name=dataset_name).get_version(int(dataset_version))]
                confirm_str = f"Are you sure you want to regenerate the features of the dataset '{dataset_name} (v{dataset_version})'? [y/N] "
            else:
                dataset = Dataset.objects.get(name=dataset_name)
                dataset_versions = dataset.versions.all()
                confirm_str = f"Are you sure you want to regenerate the features of {dataset_versions.count()} versions of the dataset '{dataset_name}'? [y/N] "
        else:
            dataset_versions = DatasetVersion.objects.all()
            confirm_str = f"Are you sure you want to regenerate the features of all the datasets [y/N] "

        # Confirm the action
        if not yes:
            confirm = input(confirm_str)
            if confirm.lower() not in ('y', 'yes'):
                self.stdout.write("Aborted.")
                return

        # Regenerate the features
        for dataset_version in dataset_versions:
            dataset_version.regenerate = True
            dataset_version.save()
            self.stdout.write(f"The regeneration of the features of the dataset '{dataset_version}' has been scheduled.")
    # End def regenerate_features

    def sanitize(self, **options):
        dataset_args = options.pop('dataset') if options.get('dataset') else []
        versions_to_sanitize = []
        for dataset_arg in dataset_args:
            if ':' in dataset_arg:
                dataset_name, dataset_version = dataset_arg.split(':')[:2] if dataset_args else (None, None)
            else:
                dataset_name, dataset_version = dataset_arg, None
            # Fetch the versions of the dataset
            if dataset_name is not None:
                if dataset_version is not None:
                    versions_to_sanitize.append(Dataset.objects.get(name=dataset_name).get_version(int(dataset_version)))
                else:
                    dataset = Dataset.objects.get(name=dataset_name)
                    versions_to_sanitize.extend(dataset.versions.all())

        if not versions_to_sanitize:
            versions_to_sanitize = DatasetVersion.objects.all()


        # Sanitize the datasets
        for dataset_version in versions_to_sanitize:
            self.stdout.write(f"Sanitizing the dataset '{dataset_version}'... ", ending='')
            try:
                n_removal = services.sanitize_shapefile_archive(dataset_version.id)
                self.stdout.write(self.style.SUCCESS(f"Removed {n_removal} unwanted files and folders."))
            except Exception as e:
                self.stdout.write(self.style.NOTICE(f"An error occurred while sanitizing the dataset '{dataset_version}': {e}"))
        self.stdout.write(f"Done.")
    # End def sanitize
# End class Command