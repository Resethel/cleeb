# -*- coding: utf-8 -*-
"""
Tests for the `files` application
"""
from django.test import TestCase

from files.models import File


class FileModelSlugTest(TestCase):

    # ------------------------------------------------------------------------------------------------------------------
    # Setup and teardown
    # ------------------------------------------------------------------------------------------------------------------

    def setUp(self):
        self.file1 = File.objects.create(name="Test File 1", file="test_file_1.txt")
        self.file2 = File.objects.create(name="Test File 2", file="test_file_2.txt")
    # End def setUp

    # ------------------------------------------------------------------------------------------------------------------
    # Tests
    # ------------------------------------------------------------------------------------------------------------------

    def test_slug_shouldBeCreated_onFileCreation(self):
        self.assertEqual(self.file1.slug, "test-file-1")

    def test_slug_shouldBeUpdated_givenNameChange(self):
        self.file1.name = "Updated Test File 1"
        self.file1.save()
        self.assertEqual(self.file1.slug, "updated-test-file-1")
    # End def test_slug_shouldBeUpdated_givenNameChange

    def test_slug_shouldNotBeUpdated_givenNoNameChange(self):
        old_slug = self.file2.slug
        self.file2.short_description = "Updated description"
        self.file2.save()
        self.assertEqual(self.file2.slug, old_slug)
    # End def test_slug_shouldNotBeUpdated_givenNoNameChange

    def test_slug_shouldBeDifferent_givenSeveralFilesWithTheSameName(self):
        self.file1.name = "Same Name"
        self.file1.save()
        self.file2.name = "Same Name"
        self.file2.save()
        file3 = File.objects.create(name="Same Name", file="test_file_3.txt")
        self.assertNotEqual(self.file1.slug, self.file2.slug)
        self.assertNotEqual(self.file1.slug, file3.slug)
        self.assertNotEqual(self.file2.slug, file3.slug)
        self.assertEqual(self.file1.slug, "same-name")
        self.assertEqual(self.file2.slug, "same-name-001")
        self.assertEqual(file3.slug, "same-name-002")
    # End def test_slug_shouldBeDifferent_givenSeveralFilesWithTheSameName

    def test_slug_shouldAlwaysTakeTheHighestSuffix(self):
        # Create a file and check its slug
        self.file1.name = "Same Name"
        self.file1.save()
        self.assertEqual(self.file1.slug, "same-name")

        self.file2.name = "Same Name"
        self.file2.save()
        self.assertEqual(self.file2.slug, "same-name-001")

        # Delete the first file
        self.file1.delete()

        # Create a new file with the same name, and ensure it does not take the slug of the deleted file
        file3 = File.objects.create(name="Same Name", file="test_file_3.txt")
        file3.save()
        self.assertNotEqual(self.file2.slug, file3.slug)
        self.assertEqual(file3.slug, "same-name-002")
    # End def test_slug_shouldAlwaysTakeTheHighestSuffix
# End class FileModelSlugTest


