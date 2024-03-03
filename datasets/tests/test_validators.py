# -*- coding: utf-8 -*-
"""
Tests for the `datasets` application validators.
"""
import tempfile
import zipfile
from pathlib import Path

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from datasets.validators import validate_dataset_version_file


class ValidateDatasetVersionFileTests(TestCase):

    def test_shouldNotThrowError_ifFileIsAZipFileContainingAShapefile(self):
        # Create a fake zip file
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_file_path = Path(temp_dir) / "file.zip"
            with zipfile.ZipFile(zip_file_path, "w") as zip_file:
                zip_file.writestr("file.shp", "Fake Data")
            file = SimpleUploadedFile("file.zip", open(zip_file_path, "rb").read())

        # Test the validator
        try:
            validate_dataset_version_file(file)
        except ValidationError:
            self.fail("validate_dataset_version_file() raised ValidationError unexpectedly!")
    # End def test_shouldNotThrowError_ifFileIsAZipFileContainingAShapefile

    def test_shouldThrowValidationError_ifFileIsNotAZipFile(self):
        file = SimpleUploadedFile("file.txt", b"Fake Data")
        with self.assertRaises(ValidationError):
            validate_dataset_version_file(file)
    # End def test_shouldThrowValidationError_ifFileIsNotAZipFile

    def test_shouldThrowValidationError_ifZipFileIsCorrupted(self):
        file = SimpleUploadedFile("file.zip", b"Fake Data")
        with self.assertRaises(ValidationError):
            validate_dataset_version_file(file)
    # End def test_shouldThrowValidationError_ifZipFileIsCorrupted

    def test_shouldThrowValidationError_ifZipFileDoesNotContainAShapefile(self):
        # Create a fake zip file
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_file_path = Path(temp_dir) / "file.zip"
            with zipfile.ZipFile(zip_file_path, "w") as zip_file:
                zip_file.writestr("file.txt", "Fake Data")
            file = SimpleUploadedFile("file.zip", open(zip_file_path, "rb").read())

        # Test the validator
        with self.assertRaises(ValidationError):
            validate_dataset_version_file(file)
    # End def test_shouldThrowValidationError_ifZipFileDoesNotContainAShapefile
# End class ValidateDatasetVersionFileTests