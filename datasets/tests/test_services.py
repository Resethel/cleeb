# -*- coding: utf-8 -*-
"""
Tests for the services of the `datasets` application.
"""
import os
import shutil
import tempfile
import zipfile
from pathlib import Path
from unittest import skip

from django.core.files.base import ContentFile, File
from django.test import TestCase

from datasets.models import Dataset, DatasetVersion
from datasets.services import sanitize_shapefile_archive


class TestSanitizeShapefileArchive(TestCase):

    temp_dir : tempfile.TemporaryDirectory | None = None
    _zip_path : Path | None = None

    # ==================================================================================================================
    # Setup and teardown
    # ==================================================================================================================
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls._zip_path = Path(cls.temp_dir.name) / "base_zip_archive.zip"

        # Write a bunch of fake data shapefile files
        with zipfile.ZipFile(cls._zip_path, "w") as zip_file:
            zip_file.writestr("file.cpg", "Fake Data")
            zip_file.writestr("file.dbf", "Fake Data")
            zip_file.writestr("file.prj", "Fake Data")
            zip_file.writestr("file.shp", "Fake Data")

        cls.dataset = Dataset.objects.create(name="Test Dataset", slug="test-dataset")
    # End def setUpClass

    @classmethod
    def tearDownClass(cls):
        if cls.temp_dir:
            del cls.temp_dir
    # End def tearDownClass

    def setUp(self):
        # Create a new zip datasetVersion object
        zip_file = File(open(self._zip_path, "rb"), name="test_zip.zip")
        self.dataset_version = DatasetVersion.objects.create(dataset=self.dataset, file=zip_file)
    # End def setUp

    def tearDown(self):
        # Delete the zip file
        DatasetVersion.objects.all().delete()
    # End def tearDown

    # ==================================================================================================================
    # Tests
    # ==================================================================================================================

    def test_shouldRemoveHiddenFilesAndFolders(self):
        hidden_files = [
            # Simple hidden files
            ".hidden_file-1",
            "__hidden_file-2",
            # Hidden files in a folder
            "folder/.hidden_file-3",
            "folder/__hidden_file-4",
            # Hidden folders
            ".hidden_folder/file1.txt",
            "__hidden_folder/file2.txt",
            # Hidden folders in a folder
            "folder/.hidden_folder/file3.txt",
            # Specific test for __MACOSX
            "__MACOSX/._file1.txt",
            "__MACOSX/._file2.txt",
            "folder/__MACOSX/._file1.txt",
            "folder/__MACOSX/._file2.txt",
        ]
        n_removed_objects = 9

        # 1. Add hidden files and folders to the zip file
        with zipfile.ZipFile(self.dataset_version.file.path, "a") as zip_file:
            for file in hidden_files:
                zip_file.writestr(file, "Fake Data")

        # 2. Call the function
        # 2.1 Wrap the file in a FileField to avoid the `PermissionError` when trying to remove the file
        n_rm = sanitize_shapefile_archive(self.dataset_version.id)

        # 3. Check that the number of removed files and folders is correct
        self.assertEqual(n_rm, n_removed_objects, f"Number of removed objects is not correct: {n_rm} != {n_removed_objects}")

        # 3. Check that the hidden files and folders were removed
        with zipfile.ZipFile(self.dataset_version.file.path, "r") as zip_file:
            for file in hidden_files:
                with self.assertRaises(KeyError, msg=f"Hidden file/folder '{file}' was not removed from the zip file"):
                    zip_file.getinfo(file)
    # End def test_shouldRemoveHiddenFilesAndFolders

    @skip("The writing of the executable file is not working properly. Need to fix it before running this test.")
    def test_shouldRemoveExecutableFiles(self):
        # 1. Create an executable file and add it to the zip file
        exec_file_path = self.temp_dir.name + "/exec_file.exe"
        with open(exec_file_path, "w") as file:
            file.write("#!/bin/bash\nFake Data")
        os.chmod(exec_file_path, 0o777)
        with zipfile.ZipFile(self.zip_path, "a") as zip_file:
            zip_file.write(exec_file_path, "exec_file.exe")

        # 2. Call the function
        sanitize_shapefile_archive(self.zip_path)

        # 3. Check that the executable file was removed
        with zipfile.ZipFile(self.zip_path, "r") as zip_file:
            with self.assertRaises(KeyError, msg="Executable file 'file.exe' was not removed from the zip file"):
                zip_file.getinfo("exec_file.exe")
# End class TestSanitizeShapefileArchive