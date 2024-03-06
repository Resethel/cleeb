# -*- coding: utf-8 -*-
"""
Processor service module for the `map_templates` application.
"""
from __future__ import annotations

import json
import logging
from typing import Iterable, Iterator

import folium
import geojson
import xyzservices
from django.apps import apps
from django.contrib.gis.geos import GEOSGeometry
from django.core.files.base import ContentFile
from django.templatetags.static import static
from django.utils.text import slugify

from datasets.models import DatasetLayer, Feature
from interactive_maps.models import MapRender
from map_templates.services.features import BoundaryType, FeatureGroup as FeatureGroupObject, Layer as LayerObject
from map_templates.services.filters import Filter
from map_templates.services.styles import Style
from map_templates.services.templates import MapTemplate as MapTemplateObject

# ======================================================================================================================
# Constants
# ======================================================================================================================

logger = logging.getLogger(__name__)
MAX_ZOOM = 18
MIN_ZOOM = 1

# ======================================================================================================================
# Map Generator
# ======================================================================================================================

class TemplateProcessor:
    """Class that generates a map from a MapTemplate object or model."""

    def __init__(self, template) -> None:
        self.map: folium.Map | None = None
        self.__template_model = None
        self.__template : MapTemplateObject | None = None
        if template is not None:
            self.template = template
    # End def __init__

    # ------------------------------------------------------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def template(self) -> MapTemplateObject:
        return self.__template

    @template.setter
    def template(self, value):
        map_template_model = apps.get_model("map_templates", "MapTemplate")
        # 1. Check if the value is a MapTemplate
        if isinstance(value, map_template_model):
            store_model = True
            obj = value.as_template_object()
        elif isinstance(value, MapTemplateObject):
            store_model = False
            obj = value
        else: # Invalid type
            raise ValueError(f"Invalid type for template: {type(value)}. Expected a 'MapTemplate' object or model.")

        # 2. Validate the template.
        # If it is not valid, an exception will be raised by the template
        try:
            obj.validate()
        except Exception as e:
            raise ValueError(f"The template provided is invalid") from e

        # 3. Set the template
        self.__template_model = value if store_model is True else None
        self.__template = obj
    # End def template

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def build(self) -> None:
        """Generate the map data from the template."""
        logger.info(f"Generating map '{self.template.name}'...")

        # 0. Create the folium map object
        map_ = folium.Map(
            tiles=None,
            # Invert the coordinates as folium uses (lat, lon) and not (lon, lat)
            location=(self.template.center.y, self.template.center.x),
            zoom_start=self.template.zoom_start,
            min_zoom=MIN_ZOOM,
            max_zoom=MAX_ZOOM,
            min_lat=self.template.center.y - 1.5,
            max_lat=self.template.center.y + 1.5,
            min_lon=self.template.center.x - 1.5,
            max_lon=self.template.center.x + 1.5,
            max_bounds_viscosity=2.0,
            max_bounds=True,
            control_scale=True,
            zoom_control=self.template.zoom_control,
        )

        # 1. Add the tiles
        for tile in self.__generate_tile_layers():
            logger.debug(f"Adding tile '{tile.tile_name}' to the map...")
            tile.add_to(map_)

        # 2. Build the feature of the map
        # 2.1. Sort the features by their z-index.
        #      Lower z-index means the features are added first.
        #      If two features have the same z_index, then the order is undefined.
        sorted_features = sorted(self.template.features, key=lambda f: f.z_index)
        keep_in_front = []
        legend_entries = []
        # 2.2. Add the features to the map
        for feature in sorted_features:
            # 2.2.1. If the feature is a layer, add it to the map
            if isinstance(feature, LayerObject):
                logger.debug(f"Adding layer '{feature.name}' to the map...")
                legend_entries.append((feature.name, feature.style))
                feature = self.__generate_layer(feature)
                keep_in_front.append(feature)
                feature.add_to(map_)

            # 2.2.2. If the feature is a feature group, process its sub-features
            elif isinstance(feature, FeatureGroupObject):
                # 2.2.2.1. Create a feature group
                logger.debug(f"Adding feature group '{feature.name}' to the map...")
                feature_group = folium.FeatureGroup(
                    name=feature.name,
                    show=feature.show_on_startup
                )

                # 2.2.2.2. Process the sub-features by their z-index
                sorted_sub_features = sorted(feature, key=lambda f: f.z_index)
                for sub_feature in sorted_sub_features:
                    legend_entries.append((sub_feature.name, sub_feature.style))
                    sub_feature = self.__generate_layer(sub_feature)
                    keep_in_front.append(sub_feature)
                    sub_feature.add_to(feature_group)

                # 2.2.2.3. Add the feature group to the map
                feature_group.add_to(map_)

        # 3. Create a layer control
        logger.debug(f"Setting the layer control to {self.template.layer_control}...")
        if self.template.layer_control:
            folium.LayerControl().add_to(map_)

        # 4. Set the layer order
        map_.keep_in_front(*keep_in_front)

        # 5. Generate the legend
        #    Reverse the legend entries to have the lowest z-index at the bottom
        generate_legend(map_, reversed(legend_entries))

        # 5. Return the folium map object
        self.map = map_
        logger.info(f"Map '{self.template.name}' generated successfully.")
    # End def build

    def save(self) -> None:
        """Save the generated map in the database as a MapRender.

        Raises:
            RuntimeError: If no map has been generated yet.
        """
        # 1. Ensure that a map has been generated before
        if self.map is None:
            logger.warning("Trying to save while no map has been generated.")
            raise RuntimeError("No map has been generated yet.")

        # 2. Get or create the map render object
        try:
            map_render = self.__template_model.render
            logger.debug(f"Updating {self.__template_model}'s render")
        except Exception:
            i = 0
            found_name = False
            while i < 100:
                render_name = f"{self.template.name}" if i == 0 else f"{self.template.name}-{i}"
                if not MapRender.objects.filter(name=render_name).exists():
                    found_name = True
                    break
                i += 1
            if not found_name:
                raise RuntimeError("Map Name Finding loop limit reached")

            map_render = MapRender(name=render_name)
            logger.debug(f"Creating new map render '{render_name}'...")

        # 3. Save the map data
        # The content is unescaped to as it is meant to be displayed in a browser
        embed_content = ContentFile(name=f"{slugify(self.template.name)}.html", content=self.map._repr_html_())
        full_content  = ContentFile(name=f"{slugify(self.template.name)}.html", content=self.map.get_root().render())
        map_render.embed_html.save(embed_content.name, embed_content, save=False)
        map_render.full_html.save(full_content.name, full_content, save=False)
        if self.__template_model:
            map_render.template = self.__template_model
        map_render.clean()
        map_render.save()
        logger.info(f"Map '{self.template.name}' saved successfully.")
    # End def save


    # ------------------------------------------------------------------------------------------------------------------
    # Private Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __generate_tile_layers(self) -> Iterator[folium.TileLayer]:
        for tile in self.template.tiles:
            if tile.type == 'builtin':
                yield folium.TileLayer(
                    name=tile.display_name,
                    tiles=tile.name,
                    attr=f"(c) {tile.name.title()}",
                    overlay=False,
                    control=tile.control
                )
            else:
                yield folium.TileLayer(
                    name=tile.display_name,
                    tiles=xyzservices.TileProvider(
                        name=tile.name,
                        url=tile.url,
                        attribution=tile.attribution,
                        access_token=tile.access_token
                    ),
                    attr=tile.attribution,
                    overlay=False,
                    control=True,
                )
    # End def __generate_tile_layers

    def __generate_layer(self, map_layer : LayerObject) -> folium.GeoJson:
        """Generate a layer from a MapLayer object."""

        # 2.2.1 Fetch the data from the MapLayer model and add it to the feature group
        feature_collection = self.__layer_to_geojson(map_layer)
        logger.debug(f"Layer '{map_layer.name}' contains {len(feature_collection.get('features'))} features.")

        if map_layer.filters is not None and len(map_layer.filters) > 0:
            feature_collection = self.__filter_geojson(feature_collection, map_layer.filters)

        # 2.2.2. Create a tooltip for the layer if it exists
        tooltip = None
        if map_layer.tooltip is not None:
            tooltip = folium.GeoJsonTooltip(
                fields=map_layer.tooltip.fields,
                aliases=map_layer.tooltip.aliases,
                labels=True,
                sticky=map_layer.tooltip.sticky,
            )

        # 2.2.3. Create the layer
        return folium.GeoJson(
            feature_collection.__geo_interface__,
            name=map_layer.name,
            style_function=map_layer.style.function if map_layer.style is not None else None,
            highlight_function=map_layer.highlight.function if map_layer.highlight is not None else None,
            # TODO: Add the popup once the template class for a popup is implemented
            tooltip=tooltip,
            show=map_layer.show_on_startup,
        )
    # End def __generate_layer

    @staticmethod
    def __layer_to_geojson(layer: LayerObject) -> geojson.FeatureCollection:
        """Fetch the geojson features from the MapLayer model."""
        # 1. Check if the layer exists in the database
        if not DatasetLayer.objects.filter(id=layer.dataset_layer_id).exists():
            raise ValueError(f"Layer {layer} does not exist in the database.")

        # 2. Fetch the data from the database
        dataset_layer: DatasetLayer = DatasetLayer.objects.filter(id=layer.dataset_layer_id).first()

        # 3.1. If the layer has no boundaries, fetch all the features
        if layer.boundaries is None:
            features_query = Feature.objects.filter(layer=dataset_layer)
        # 3.2. Otherwise, fetch the features that intersect the boundaries
        elif layer.boundary_type == BoundaryType.INTERSECT or layer.boundary_type == BoundaryType.CROP:
            features_query = Feature.objects.filter(layer=dataset_layer, geometry__intersects=layer.boundaries)
        # 3.3. Otherwise, fetch the features that are within the boundaries
        elif layer.boundary_type == BoundaryType.STRICT:
            features_query = Feature.objects.filter(layer=dataset_layer, geometry__within=layer.boundaries)
        else:
            raise ValueError(f"Invalid boundary type for layer {layer}")

        # 4. Convert the data into a geojson object
        features = []
        for feature in features_query:
            if layer.boundary_type == BoundaryType.CROP:
                geometry = GEOSGeometry(feature.geometry.intersection(layer.boundaries))
            else:
                geometry = feature.geometry
            properties = feature.fields
            features.append(
                geojson.Feature(
                    geometry=json.loads(str(geometry.geojson)),
                    properties=properties,
                )
            )

        return geojson.FeatureCollection(features)
    # End def __fetch_layer_geojson

    @staticmethod
    def __filter_geojson(feature_collection: geojson.FeatureCollection,
                         filters: Iterable[Filter],
                         *,
                         strict: bool = False) -> geojson.FeatureCollection:
        """Filter the geojson features based on the filters provided."""

        # 2. Filter the geojson
        filtered_features : list[geojson.Feature] = feature_collection.get('features')
        initial_length = len(filtered_features)
        for filter_ in filters:
            logger.debug(f"Applying filter '{filter_!r}' to the layer...")
            temp_features = []
            for feature in filtered_features:
                properties = feature.get('properties')

                # If the key is not in the properties, the feature is kept
                # unless `strict` is set to True. In that case, the feature
                # is discarded.
                if filter_.key not in properties.keys():
                    if strict is False:
                        temp_features.append(feature)
                    else:
                        logger.debug(f"Discarding feature {feature!r} (strict mode).")
                    continue

                if filter_.operator(properties[filter_.key], filter_.value) is True:
                    logger.debug(f"Keeping feature {feature!r} (match filter)")
                    temp_features.append(feature)
                else:
                    logger.debug(f"Discarding feature {feature!r} (does not match filter)")

            filtered_features = temp_features

        logger.debug(f"Filtering done: kept {len(filtered_features)}/{initial_length} features")
        return geojson.FeatureCollection(features=filtered_features)
    # End def __filter_geojson
# End class MapBuilder


# ======================================================================================================================
# Legend Generation
# ======================================================================================================================

LEGEND_TEMPLATE = """
    <div class="legend --collapsed">
        <img class="collapsed-icon" src="{icon}" alt="Collapse icon"></img>
        {entries}
    </div>
"""

ENTRY_TEMPLATE = """
    <div class="legend-entry">
        <div class="square" style="--fill-color: {fill_color}; --stroke-color: {stroke_color};"></div>
        <p>{label}</p>
    </div>
"""


def generate_legend(map_ : folium.Map, entries : Iterable[tuple[str, Style]]) -> None:
    """Generate a legend from the entries provided."""
    # Fill the template with the entries
    legend_html = LEGEND_TEMPLATE

    # Add the entries
    html_entries = []
    for entry in entries:
        stroke_color, fill_color = convert_style_color_to_legend_colors(entry[1])
        html_entries.append(ENTRY_TEMPLATE.format(
            fill_color=fill_color,
            stroke_color=stroke_color,
            label=entry[0]
        ))

    # Add the entries and the icon to the legend
    legend_html = legend_html.format(
        icon=static('assets/icons/help_FILL0_wght500_GRAD200_opsz24.svg'),
        entries="".join(html_entries)
    )

    # Add the legend to the map
    map_.get_root().html.add_child(folium.CssLink(static('map_templates/css/legend.css')))
    map_.get_root().html.add_child(folium.Element(legend_html))
    map_.get_root().html.add_child(folium.JavascriptLink(static('map_templates/js/legend-toggle.js')))
# End def generate_legend


def convert_style_color_to_legend_colors(style: Style) -> tuple[str, str]:
    fill_color_hex = style.fill_color
    fill_color_opacity = style.fill_opacity
    stroke_color_hex = style.color
    stroke_color_opacity = style.opacity

    stroke_color = (f"rgba("
                    f"{int(stroke_color_hex[1:3], 16)},"  # Red
                    f"{int(stroke_color_hex[3:5], 16)},"  # Green
                    f"{int(stroke_color_hex[5:7], 16)},"  # Blue
                    f"{stroke_color_opacity})")  # Opacity

    fill_color = (f"rgba("
                  f"{int(fill_color_hex[1:3], 16)},"  # Red
                  f"{int(fill_color_hex[3:5], 16)},"  # Green
                  f"{int(fill_color_hex[5:7], 16)},"  # Blue
                  f"{fill_color_opacity})")  # Opacity

    return stroke_color, fill_color
# End def convert_style_color_to_legend_colors







    
