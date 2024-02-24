# -*- coding: utf-8 -*-
"""
Test for styles.py
"""
from django.test import TestCase

from map_templates.objects.styles import PropertyStyle, Style, validate_style_attributes


class TestStyle(TestCase):
    def setUp(self):
        self.style = Style()

    def test_serialize_shouldReturnCorrectDict(self):
        self.style.stroke = True
        result = self.style._to_dict()
        self.assertEqual(result, {"__type__": "Style", "stroke": True})
    # End def test_serialize_shouldReturnCorrectDict

    def test_deserialize_shouldReturnCorrectStyle(self):
        data = {"__type__": "Style", "stroke": True}
        result = Style._from_dict(data)
        self.assertEqual(result.stroke, True)
    # End def test_deserialize_shouldReturnCorrectStyle
# End class TestStyle


class TestPropertyStyle(TestCase):
    def setUp(self):
        self.property_style = PropertyStyle("key", "value")

    def test_serialize_shouldReturnCorrectDict(self):
        self.property_style.key = "testKey"
        self.property_style.value = "testValue"
        self.property_style.stroke = True
        result = self.property_style.serialize('dict')

        self.assertEqual(result, {"__type__": "__PropertyStyle__", "key": "testKey", "value": "testValue", "stroke": True})
    # End def test_serialize_shouldReturnCorrectDict

    def test_deserialize_shouldReturnCorrectPropertyStyle(self):
        data = {"__type__": "__PropertyStyle__", "key": "testKey", "value": "testValue", "stroke": True}
        result = PropertyStyle.deserialize(data, 'dict')

        self.assertIsInstance(result, PropertyStyle)
        self.assertEqual(result.key, "testKey")
        self.assertEqual(result.value, "testValue")
        self.assertEqual(result.stroke, True)
    # End def test_deserialize_shouldReturnCorrectPropertyStyle
# End class TestPropertyStyle


class TestValidateStyleAttributes(TestCase):

    def test_shouldNotRaiseError_givenCorrectAttributes(self):
        attributes = {
            "stroke": True,
            "color": "#ffffff",
            "weight": 1.0,
            "opacity": 0.5,
            "line_cap": 'round',
            "line_join": 'round',
            "dash_array": None,
            "dash_offset": None,
            "fill": True,
            "fill_color": "#ffffff",
            "fill_opacity": 0.5,
            "fill_rule": 'evenodd',
            "fill_pattern": None
        }
        validate_style_attributes(attributes)

    # test_shouldNotRaiseValidationError_givenCorrectAttributes

    def test_shouldRaiseValueError_givenInvalidColor(self):
        with self.assertRaises(ValueError):
            validate_style_attributes({"color": "invalid_color"})
    # End def test_raiseValueError_givenInvalidColor

    def test_shouldRaiseValueError_givenInvalidOpacity(self):
        invalid_opacities = [-5, 1.3, "invalid"]
        for invalid_opacity in invalid_opacities:
            with self.assertRaises(ValueError):
                validate_style_attributes({"opacity": invalid_opacity})
    # test_shouldRaiseValueError_givenInvalidOpacity

    def test_shouldRaiseValueError_givenInvalidLineCap(self):
        with self.assertRaises(ValueError):
            validate_style_attributes({"line_cap": 'invalid_line_cap'})
    # test_shouldRaiseValueError_givenInvalidLineCap

    def test_shouldRaiseValueError_givenInvalidLineJoin(self):
        with self.assertRaises(ValueError):
            validate_style_attributes({"line_join": 'invalid_line_join'})
    # test_shouldRaiseValueError_givenInvalidLineJoin

    def test_shouldRaiseValueError_givenInvalidFillRule(self):
        with self.assertRaises(ValueError):
            validate_style_attributes({"fill_rule": 'invalid_fill_rule'})
    # test_shouldRaiseValueError_givenInvalidFillRule

    def test_shouldNotRaiseValueError_givenValidDashArray(self):
        correct_dash_arrays = [
            "10%",
            "10",
            "10,5,32",
            "10,5",
            "19.6%, 34.4314314%",
            "19, 4, 43, 3",
            "10 4 3 2",
        ]
        dash_array = None
        try:
            for dash_array in correct_dash_arrays:
                attributes = {"dash_array": dash_array}
                validate_style_attributes(attributes)
        except ValueError:
            self.fail(f"ValueError raised for valid dash_array: `{dash_array}`")
    # End def test_shouldNotRaiseValueError_givenCorrectDashArray

    def test_shouldRaiseValueError_givenInvalidDashArray(self):
        invalid_dash_array = {"dash_array": "invalid_dash_array"}
        with self.assertRaises(ValueError):
            validate_style_attributes(invalid_dash_array)
    # test_shouldRaiseValueError_givenInvalidDashArray
# End class TestValidateStyleAttributes