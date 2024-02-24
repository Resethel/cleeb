# -*- coding: utf-8 -*-
"""
Tests for the `BaseStyle` model of the `map_templates` application.
"""
from django.test import TestCase
from map_templates.models import BaseStyle
from django.core.exceptions import ValidationError

# ======================================================================================================================
# Concrete class for testing the abstract BaseStyle model
# ======================================================================================================================

class TestStyle(BaseStyle):
    class Meta:
        abstract = False

# ======================================================================================================================
# Test cases
# ======================================================================================================================

class TestDashArrayField(TestCase):
    def test_shouldNotRaiseValidationError_givenValidDashArray(self):
        correct_dash_arrays = [
            None,
            "10,5,32",
            "10,5",
            "10",
            "19, 4, 43, 3",
            "10 4 3 2",
        ]
        dash_array = None
        try:
            for dash_array in correct_dash_arrays:
                style = TestStyle(dash_array=dash_array)
                style.full_clean()
        except ValidationError:
            self.fail(f"ValidationError raised for valid dash_array: {dash_array}")
    # End def test_shouldNotRaiseValidationError_givenValidDashArray

    def test_invalid_dash_array(self):
        style = TestStyle(dash_array="invalid")
        with self.assertRaises(ValidationError):
            style.full_clean()
    # End def test_invalid_dash_array