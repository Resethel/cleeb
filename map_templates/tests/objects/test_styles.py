# -*- coding: utf-8 -*-
"""
Test for styles.py
"""
from django.test import TestCase
from map_templates.objects.styles import Style, PropertyStyle

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