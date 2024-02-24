# -*- coding: utf-8 -*-
"""
Tests for the `TileLayer` model of the `map_templates` application.
"""
from unittest import mock

from django.test import TestCase
from django.core.exceptions import ValidationError
from xyzservices import TileProvider

from map_templates.models import TileLayer

class TileLayerModelTests(TestCase):
    def setUp(self):
        self.tile = TileLayer.objects.create(name="TestTile", type="builtin")

    def test_init_shouldCreateTileLayer(self):
        self.assertEqual(self.tile.name, "TestTile")
        self.assertEqual(self.tile.type, "builtin")
    # End def test_init_shouldCreateTileLayer

    def test_clean_shouldCleanUnnecessaryFields_ifTypeIsBuiltin(self):
        self.tile.type = "builtin"
        self.tile.url = "http://test.com"
        self.tile.attribution = "Test Attribution"
        self.tile.access_token = "testToken"
        self.tile.clean()

        self.assertIsNone(self.tile.url)
        self.assertIsNone(self.tile.attribution)
        self.assertIsNone(self.tile.access_token)
    # End def test_clean_shouldCleanUnnecessaryFields_ifTypeIsBuiltin

    @mock.patch.object(TileProvider, 'requires_token')
    def test_clean_shouldCleanAccessToken_ifTypeIsXYZ_andAccessTokenIsNotRequired(self, requires_token):
        requires_token.return_value = False
        self.tile.type = "xyz"
        self.tile.url = 'https://test.com'
        self.tile.attribution = "Test Attribution" # Does not matter for a test
        self.tile.clean()

        self.assertEqual(self.tile.url, 'https://test.com')
        self.assertEqual(self.tile.attribution, "Test Attribution")
        self.assertIsNone(self.tile.access_token)
    # End def test_clean_shouldCleanAccessToken_ifTypeIsXYZ_andAccessTokenIsNotRequired

    @mock.patch.object(TileProvider, 'requires_token')
    def test_clean_shouldRaiseValidationError_ifTypeIsXYZ_andAccessTokenIsRequired(self, requires_token):
        requires_token.return_value = True
        with self.assertRaises(ValidationError):
            self.tile.type = "xyz"
            self.tile.url = 'https://test.com'
            self.tile.attribution = "Test Attribution"
            # No access token provided
            self.tile.clean()
    # End def test_clean_shouldRaiseValidationError_ifTypeIsXYZ_andAccessTokenIsRequired

    @mock.patch.object(TileProvider, 'requires_token')
    def test_clean_shouldNotRaiseValidationError_ifTypeIsXYZ_andAccessTokenIsRequired_andAccessTokenIsValid(self, requires_token):
        requires_token.side_effect = [True, False]
        self.tile.type = "xyz"
        self.tile.url = 'https://test.com'
        self.tile.attribution = "Test Attribution"
        self.tile.access_token = "testToken"
        self.tile.clean()


    def test_shouldRaiseValidationError_ifTypeIsInvalid(self):
        with self.assertRaises(ValidationError):
            self.tile.type = "invalid"
            self.tile.full_clean()
    # End def test_shouldRaiseValidationError_ifTypeIsInvalid

    def test_shouldRaiseValidationError_ifUrlIsInvalid(self):
        with self.assertRaises(ValidationError):
            self.tile.type = "wms"
            self.tile.url = None
            self.tile.full_clean()
    # End def test_shouldRaiseValidationError_ifUrlIsInvalid

    def test_shouldRaiseValidationError_ifLayersIsInvalid(self):
        with self.assertRaises(ValidationError):
            self.tile.type = "wms"
            self.tile.layers = None
            self.tile.full_clean()
    # End def test_shouldRaiseValidationError_ifLayersIsInvalid
# End class TileLayerModelTests