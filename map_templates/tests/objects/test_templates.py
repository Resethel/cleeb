import operator

import django.test as djangotest

from map_templates import models
from map_templates.objects.templates import MAX_ZOOM, MIN_ZOOM, MapTemplate
from map_templates.objects.tiles import TileLayer
from map_templates.objects.features import Layer, FeatureGroup
from map_templates.objects.styles import Style
from map_templates.objects.filters import Filter

class TestMapTemplateObject(djangotest.TestCase):
    def setUp(self):
        self.tile = TileLayer(name="TestTile")
        self.style = Style(stroke=True, color="#000000")
        self.filter = Filter(key="test", operator="==", value="value")
        self.layer = Layer(name="TestLayer", map_layer="TestMapLayer", style=self.style, filters=[self.filter])
        self.feature_group = FeatureGroup(name="TestFeatureGroup", features=[self.layer])
        self.map_template = MapTemplate(name="TestMapTemplate", tiles=[self.tile],
                                        features=[self.layer, self.feature_group])

    def test_init(self):
        self.assertEqual(self.map_template.name, "TestMapTemplate")
        self.assertIn(self.tile, self.map_template.tiles)
        self.assertIn(self.layer, self.map_template.features)
        self.assertIn(self.feature_group, self.map_template.features)

    def test_addTile(self):
        new_tile = TileLayer(name="NewTile")
        self.map_template.add_tile(new_tile)
        self.assertIn(new_tile, self.map_template.tiles)
    # End def test_add_tile

    def test_addTile_shouldRaiseValueError_ifTileIsNotATileLayer(self):
        with self.assertRaises(ValueError):
            self.map_template.add_tile("NotATile")
    # End def test_validate_shouldRaiseValueError_ifZoomEndIsOutOfRange

    def test_addFeature_shouldAddLayer(self):
        new_layer = Layer(name="NewLayer", map_layer="NewMapLayer")
        new_feature_group = FeatureGroup(name="NewFeatureGroup", features=[new_layer])
        self.map_template.add_feature(new_layer)
        self.map_template.add_feature(new_feature_group)
        self.assertIn(new_layer, self.map_template.features)
        self.assertIn(new_feature_group, self.map_template.features)
    # End def test_addFeature_shouldAddLayer

    def test_addFeature_shouldRaiseValueError_ifFeatureIsNotAFeature(self):
        with self.assertRaises(ValueError):
            self.map_template.add_feature("NotAFeature")

    def test_removeFeature_shouldRemoveLayer(self):
        self.map_template.remove_feature("TestLayer", "Layer")
        self.assertNotIn(self.layer, self.map_template.features)
    # End def test_removeFeature_shouldRemoveLayer

    def test_removeFeature_shouldRaiseValueError_ifLayerDoesNotExist(self):
        with self.assertRaises(ValueError):
            self.map_template.remove_feature("NonExistentLayer", "Layer")
    # End def test_removeFeature_shouldRaiseValueError_ifLayerDoesNotExist

    def test_validate(self):
        self.map_template.validate()

    def test_validate_shouldRaiseValueError_ifZoomStartIsOutOfRange(self):
        self.map_template.zoom_start = MAX_ZOOM + 1
        with self.assertRaises(ValueError):
            self.map_template.validate()
        self.map_template.zoom_start = MIN_ZOOM - 1
        with self.assertRaises(ValueError):
            self.map_template.validate()
    # End def test_validate_shouldRaiseValueError_ifZoomStartIsOutOfRange


    def test_fromModel_shouldCreateMapTemplate(self):

        mt_mdl = models.MapTemplate.objects.create(name="TestMapTemplate")
        tile = models.TileLayer.objects.create(name="TestTile", url="http://test.com")

        mt_mdl.tiles.add(tile)
        mt_mdl.zoom_start = 5
        mt_mdl.layer_control = True
        mt_mdl.zoom_control = False


        feature_group = models.FeatureGroup.objects.create(map_template=mt_mdl, name="TestFeatureGroup")
        layer1 = models.Layer.objects.create(
            owner_map_template=mt_mdl,
            name="TestLayer1",
            style=models.Style.objects.create(stroke=True, color="#11111"),
            highlight=models.Style.objects.create(stroke=True, color="#111FFF")
        )

        layer2 = models.Layer.objects.create(
            owner_feature_group=feature_group,
            name="TestLayer2",
            style=models.Style.objects.create(stroke=False, color="#222222")
        )
        layer3 = models.Layer.objects.create(
            owner_feature_group=feature_group,
            name="TestLayer3",
            style=models.Style.objects.create(stroke=True, color="#444444"),
            highlight=models.Style.objects.create(stroke=True, color="#444FFF")
        )


        filter1 = models.Filter.objects.create(layer=layer3, key="test1", operator="==", value="value")
        filter2 = models.Filter.objects.create(layer=layer3, key="test2", operator="!=", value="notvalue")

        property_style1 = models.PropertyStyle.objects.create(style=layer1.style, key="test1", value="value", color="#FFF111")
        property_style2 = models.PropertyStyle.objects.create(style=layer3.style, key="test2", value="value", color="#FFF444")
        property_style3 = models.PropertyStyle.objects.create(style=layer3.style, key="test3", value="value", color="#EEE444")

        # Save the models
        mt_mdl.save()

        # Create the object
        mt_obj = MapTemplate.from_model(mt_mdl)

        # Assert the object
        self.assertEqual(mt_obj.name, "TestMapTemplate")
        self.assertEqual(mt_obj.zoom_start, 5)
        self.assertTrue(mt_obj.layer_control)
        self.assertFalse(mt_obj.zoom_control)
        self.assertEqual(len(mt_obj.tiles), 1)

        tile = mt_obj.tile("TestTile")
        self.assertEqual(tile.name, "TestTile")
        self.assertEqual(tile.url, "http://test.com")

        self.assertEqual(len(mt_obj.features), 2)

        # Get the layer and feature group
        layer = mt_obj.feature("TestLayer1")
        self.assertIsInstance(layer, Layer)
        layer : layer # Update type hint

        feature_group = mt_obj.feature("TestFeatureGroup")
        self.assertIsInstance(feature_group, FeatureGroup)
        feature_group : FeatureGroup # Update type hint

        self.assertEqual(feature_group.name, "TestFeatureGroup")
        self.assertEqual(len(feature_group), 2)
        fg_layer1 = feature_group["TestLayer2"]
        fg_layer2 = feature_group["TestLayer3"]
        self.assertIsInstance(fg_layer1, Layer)
        self.assertIsInstance(fg_layer2, Layer)
        self.assertEqual(fg_layer1.name, "TestLayer2")
        self.assertEqual(fg_layer2.name, "TestLayer3")
        fg_layer1 : Layer # Update type hint
        fg_layer2 : Layer

        # Assert the styles
        self.assertIsNotNone(layer.style)
        self.assertEqual(layer.style.color, "#11111")
        self.assertTrue(layer.style.stroke)
        self.assertEqual(len(layer.style.property_styles), 1)
        self.assertEqual(layer.style.property_styles[0].key, "test1")
        self.assertEqual(layer.style.property_styles[0].value, "value")
        self.assertEqual(layer.style.property_styles[0].color, "#FFF111")

        self.assertIsNotNone(layer.highlight)
        self.assertEqual(layer.highlight.color, "#111FFF")
        self.assertTrue(layer.highlight.stroke)

        self.assertIsNotNone(fg_layer1.style)
        self.assertIsNotNone(fg_layer2.style)
        self.assertEqual("TestLayer2", fg_layer1.name)
        self.assertEqual(fg_layer1.style.color, "#222222")
        self.assertFalse(fg_layer1.style.stroke)

        self.assertEqual("TestLayer3", fg_layer2.name)
        self.assertEqual(fg_layer2.style.color, "#444444")
        self.assertTrue(fg_layer2.style.stroke)
        self.assertEqual(len(fg_layer2.style.property_styles), 2)
        ps1 = fg_layer2.style.property_styles[0]
        ps2 = fg_layer2.style.property_styles[1]
        self.assertEqual(ps1.key, "test2")
        self.assertEqual(ps1.value, "value")
        self.assertEqual(ps1.color, "#FFF444")
        self.assertEqual(ps2.key, "test3")
        self.assertEqual(ps2.value, "value")
        self.assertEqual(ps2.color, "#EEE444")

        # Assert the filters
        self.assertEqual(len(fg_layer1.filters), 0)
        self.assertEqual(len(fg_layer2.filters), 2)
        self.assertEqual(fg_layer2.filters[0].key, "test1")
        self.assertEqual(fg_layer2.filters[0].operator, operator.eq)
        self.assertEqual(fg_layer2.filters[0].value, "value")
        self.assertEqual(fg_layer2.filters[1].key, "test2")
        self.assertEqual(fg_layer2.filters[1].operator, operator.ne)
        self.assertEqual(fg_layer2.filters[1].value, "notvalue")
    # End def test_fromModel_shouldCreateMapTemplate




