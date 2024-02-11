# -*- coding: utf-8 -*-
"""
Tests for the dataset_category model.
"""
from django.test import TestCase

from datasets.models import DatasetCategory

class DatasetCategoryModelSignalTests(TestCase):

    def test_slug_shouldBeSet_afterSaving(self):
        # Given
        dataset_category = DatasetCategory(name="My dataset category")
        # When
        dataset_category.save()
        # Then
        self.assertEqual(dataset_category.slug, "my-dataset-category")
    # End def test_slug_shouldBeSet_afterSaving
# End class DatasetCategoryModelSignalTests