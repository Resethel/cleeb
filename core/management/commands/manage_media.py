# -*- coding: utf-8 -*-
"""
Command to manage the media files of the project.
"""
import os

from django.apps import apps
from django.conf import settings
from django.core.management import BaseCommand
from django.db.models import FileField, Q


class Command(BaseCommand):
    """Command to manage the media files of the project."""

    # ------------------------------------------------------------------------------------------------------------------
    # Help string
    # ------------------------------------------------------------------------------------------------------------------

    help = "Manage the media files of the project."

    # ------------------------------------------------------------------------------------------------------------------
    # Argument parser
    # ------------------------------------------------------------------------------------------------------------------

    def add_arguments(self, parser):
        """Add arguments to the parser."""
        action_parser = parser.add_subparsers(
            dest='action',
            help="The action to perform."
        )

        # --------------------------------------------------------------------------------------------------------------
        # 'clean-orphaned' action
        # --------------------------------------------------------------------------------------------------------------

        clean_orphaned_parser = action_parser.add_parser(
            'clean-orphaned',
            help="Clean the orphaned media files."
        )

        clean_orphaned_parser.add_argument(
            '--dry-run',
            action='store_true',
            help="Perform a dry run of the operation."
        )

        clean_orphaned_parser.add_argument(
            '--exclude',
            nargs='+',
            type=str,
            help="Exclude the specified directories from the operation."
        )
    # End def add_arguments

    def handle(self, *args, **options):
        """Handle the command."""
        action = options['action']
        if action == 'clean-orphaned':
            clean_orphaned(self, options)
        else:
            self.stderr.write(f"Unknown action '{action}'.")
# End class Command

# ======================================================================================================================
# Functions
# ======================================================================================================================

def clean_orphaned(cmd : BaseCommand, options : dict):
    """Clean the orphaned media files."""
    dry_run = options['dry_run']
    exclude = options['exclude'] if options['exclude'] else []
    if dry_run:
        cmd.stdout.write("Performing a dry run.")
    else:
        cmd.stdout.write("Cleaning the orphaned media files.")

    dry_run = True if options['dry_run'] else False

    # Get all files in the database
    all_models = apps.get_models()
    physical_files = set()
    db_files = set()
    for model in all_models:
        file_fields = []
        filters = Q()
        for f_ in model._meta.fields:
            if isinstance(f_, FileField):
                file_fields.append(f_.name)
                is_null = {'{}__isnull'.format(f_.name): True}
                is_empty = {'{}__exact'.format(f_.name): ''}
                filters &= Q(**is_null) | Q(**is_empty)
        # only retrieve the models which have non-empty, non-null file fields
        if file_fields:
            try:
                files = model.objects.exclude(filters).values_list(*file_fields, flat=True).distinct()
            except TypeError:
                # When a model has several file fields, the values_list method returns a list of tuples
                # which is not handled by the flat=True argument.
                files = model.objects.exclude(filters).values_list(*file_fields).distinct()
                files = [file_ for file_tuple in files for file_ in file_tuple]
            db_files.update(files)

    # Get all files from the MEDIA_ROOT, recursively
    media_root = getattr(settings, 'MEDIA_ROOT', None)
    if media_root is not None:
        for relative_root, dirs, files in os.walk(media_root):
            for file_ in files:
                # Compute the relative file path to the media directory, so it can be compared to the values from the db
                relative_file = os.path.join(os.path.relpath(relative_root, media_root), file_)
                physical_files.add(relative_file)

    # Compute the difference and delete those files
    deletables = physical_files - db_files
    if not deletables:
        cmd.stdout.write("No orphaned files found.")
        return

    n_fd = 0
    size_fd = 0
    for file_ in deletables:
        if file_ in exclude:
            cmd.stdout.write(f"Skipped: {file_}")
            continue

        if dry_run:
            n_fd += 1
            size_fd += os.path.getsize(os.path.join(media_root, file_))
            cmd.stdout.write(f"Would delete: {file_}")
        else:
            n_fd += 1
            size_fd += os.path.getsize(os.path.join(media_root, file_))
            os.remove(os.path.join(media_root, file_))
            cmd.stdout.write(f"Deleted: {file_}")


    # If `dry_run` is True, simply list the files that would be deleted
    if dry_run:
        cmd.stdout.write(cmd.style.SUCCESS(f"Would have deleted {n_fd} files, freeing {size_fd / 1024 / 1024 / 1024} GB"))
        return

    # Bottom-up - delete empty directories
    for relative_root, dirs, files in os.walk(media_root, topdown=False):
        for dir_ in dirs:
            if not os.listdir(os.path.join(relative_root, dir_)):
                os.rmdir(os.path.join(relative_root, dir_))

    cmd.stdout.write(cmd.style.SUCCESS(f"Deleted {n_fd} files, freeing {size_fd / 1024 / 1024 / 1024} GB"))
# End def clean_orphaned