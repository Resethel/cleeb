"""
Module that generates the map data from a template definition.
"""
from __future__ import annotations

import folium
from django.db.models import QuerySet

from map_data.core.map.template import CityLimits, Filter, MapTemplate
from map_data.models import City, MapLayer
from shapes.models import Shape

# ======================================================================================================================
# Constants
# ======================================================================================================================

LOCATION_OF_METZ = (49.119309, 6.175716)
DEFAULT_ZOOM_START = 12
MIN_ZOOM = 2
MAX_ZOOM = 10

# ======================================================================================================================
# Custom Tile Layers
# ======================================================================================================================

CUSTOM_TILE_LAYERS = {
    "PLAN_IGN": {
        "url": ('https://wxs.ign.fr/choisirgeoportail/geoportail/wmts?'
             'REQUEST=GetTile'
             '&SERVICE=WMTS'
             '&VERSION=1.0.0'
             '&STYLE=normal'
             '&TILEMATRIXSET=PM'
             '&FORMAT=image/png'
             '&LAYER=GEOGRAPHICALGRIDSYSTEMS.PLANIGNV2'
             '&TILEMATRIX={z}'
             '&TILEROW={y}'
             '&TILECOL={x}'),
        "attribution": (
            '&copy; <a target="_blank" href="https://www.geoportail.gouv.fr/">Geoportail France</a>'
        )
    }
}

# ======================================================================================================================
# Map Generator
# ======================================================================================================================

class MapBuilder:
    def __init__(self, template : MapTemplate | None):
        self._template : MapTemplate | None = None
        if template is not None:
            self.template = template
    # End def __init__

    # ------------------------------------------------------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def template(self) -> MapTemplate:
        return self._template

    @template.setter
    def template(self, value: MapTemplate):
        # 1. Check if the value is a MapTemplate
        if not isinstance(value, MapTemplate):
            raise ValueError(f"Value must be a MapTemplate, not {type(value)}")

        # 2. Validate the template. If it is not valid, an exception will be raised by the template
        value.validate()

        # 3. Set the template
        self._template = value
    # End def template

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def build(self) -> folium.Map:
        """Generate the map data from the template."""

        map_ = folium.Map(
            tiles=self.template.tile.value[0] if self.template.tile.value[1] is False else None,
            location=LOCATION_OF_METZ,
            zoom_start=DEFAULT_ZOOM_START if self.template.zoom_start is None else self.template.zoom_start,
            min_zoom=MIN_ZOOM,
            max_zoom=MAX_ZOOM,
            min_lat=LOCATION_OF_METZ[0] - 1.5,
            max_lat=LOCATION_OF_METZ[0] + 1.5,
            min_lon=LOCATION_OF_METZ[1] - 1.5,
            max_lon=LOCATION_OF_METZ[1] + 1.5,
            max_bounds_viscosity=2.0,
            max_bounds=True,
            control_scale=True,
            zoom_control=self.template.enable_zoom_control,
        )

        # 1. Add the custom tile layer if needed
        if self.template.tile.value[1] is True:
            folium.TileLayer(
                tiles=CUSTOM_TILE_LAYERS[self.template.tile.value[0]]["url"],
                attr=CUSTOM_TILE_LAYERS[self.template.tile.value[0]]["attribution"],
                name=self.template.tile.value,
                overlay=False,
                control=True,
            ).add_to(map_)

        # 2. Build the city limits feature group
        if self.template.show_city_limits:
            city_limits_config = self.template.city_limits
            if city_limits_config.show_emm_limits is True:
                # Fetch the geojson that represent the limits of the EMM
                geojson = self.__fetch_emm_limits_geojson()

                # Create the feature group and add it to the map
                folium.GeoJson(
                    geojson,
                    name="Limites de l'EMM",
                    style_function=lambda x: {
                        "color": "black",
                        "weight": 3,
                        "fillOpacity": 0.0,
                    },
                    highlight_function=None,
                    tooltip=None,
                    show=True,
                ).add_to(map_)

            # Add the city limits if the mode is not 'only_emm'
            if city_limits_config.mode in ('all', 'exclude', 'include'):
                feature_group = folium.FeatureGroup(
                    name="Limites des communes",
                    show=True,
                )

                # Fetch the geojson that represent the limits of the cities
                geojson = self.__fetch_cities_limits_geojson(city_limits_config)
                folium.GeoJson(
                    geojson,
                    name="Limites des communes",
                    style_function=lambda x: {
                        "color": "black",
                        "weight": 1,
                        "fillOpacity": 0.0,
                    },
                    highlight_function=None,
                    tooltip=None,
                    show=True,
                ).add_to(map_)


        # 3. Build the feature groups of the map
        for fg in self.template.get_feature_groups():

            # 2.1 Add the basic feature group parameters
            feature_group = folium.FeatureGroup(
                name=fg.name,
                show=fg.show_on_startup
            )
            print(f"Adding feature group '{fg.name}' to the map...")

            # 2.2 Add the layers
            for layer in fg.get_layers():
                print(f"Adding layer '{layer.name}' to the feature group '{fg.name}'...")

                # 2.2.1 Fetch the data from the MapLayer model and add it to the feature group
                geojson = self.__fetch_layer_geojson(layer.map_layer)
                print(f"Layer '{layer.name}' contains {len(geojson['features'])} features.")

                if layer.filters is not None and len(layer.filters) > 0:
                    geojson = self.__filter_geojson(geojson, *layer.filters)

                # 2.2.3. Add the feature group to the map
                folium.GeoJson(
                    geojson,
                    name=layer.name,
                    style_function=layer.style.function_style if layer.style is not None else None,
                    highlight_function=layer.highlight.function_style if layer.highlight is not None else None,
                    # TODO: Add the popup once the template class for a tooltip is implemented
                    tooltip=None,
                    show=layer.show_on_startup,
                ).add_to(feature_group)

            # 2.3. Finally, add the feature group to the map
            feature_group.add_to(map_)


        # 3. Enable the layer control if needed
        print(f"Setting the layer control to {self.template.enable_layer_control}...")
        if self.template.enable_layer_control:
            folium.LayerControl().add_to(map_)

        # 4. Return the folium map object
        print(f"Map '{self.template.name}' generated successfully.")
        return map_
    # End def build_map

    @staticmethod
    def __fetch_layer_geojson(layer: str) -> dict:
        """Fetch the geojson features from the MapLayer model."""
        # 1. Check if the layer exists in the database
        if not MapLayer.objects.filter(name=layer).exists():
            raise ValueError(f"Layer {layer} does not exist in the database.")

        # 2. Fetch the data from the database
        layer_query: QuerySet = MapLayer.objects.filter(name=layer)
        # 2.1 Check if there is any data,
        if layer_query is None or layer_query.count() == 0:
            raise RuntimeError(f"Layer {layer} does not contain any data.")
        if layer_query.count() > 1:
            raise RuntimeWarning(f"Layer {layer} contains more than one entry. Only the first one will be used.")

        # 2.1. Fetch the data from the database
        feature_set = layer_query.first().shape.all()

        # 3. Convert the data into a GeoJSON format
        geojson = {"type": "FeatureCollection", "features": []}
        feature: Shape
        for feature in feature_set:
            geojson["features"].append(
                {
                    "type": feature.feature_type,
                    "geometry": {
                        "type": feature.geometry_type,
                        "coordinates": eval(feature.geometry_coordinates),
                    },
                    "properties": eval(feature.properties)
                }
            )

        return geojson
    # End def __fetch_layer_geojson

    @staticmethod
    def __fetch_emm_limits_geojson() -> dict:
        """Fetch the geojson features from the MapLayer model."""
        # 1. Check if the layer exists in the database
        if not City.objects.filter(name="Limites de l'EMM").exists():
            raise ValueError(f"Cannot find the limits of the EMM in the database.")

        # 2. Fetch the data from the database
        limit_query: QuerySet = City.objects.filter(name="Limites de l'EMM")
        # 2.1 Check if there is any data,
        if limit_query is None or limit_query.count() == 0:
            raise RuntimeError(f"Cannot find the limits of the EMM in the database.")
        if limit_query.count() > 1:
            raise RuntimeWarning(f"There are several limits for the EMM. Only the first one will be used.")

        # 2.1. Fetch the data from the database
        feature_set = limit_query.first().shape.all()

        # 3. Convert the data into a GeoJSON format
        geojson = {"type": "FeatureCollection", "features": []}
        feature: Shape
        for feature in feature_set:
            geojson["features"].append(
                {
                    "type": feature.feature_type,
                    "geometry": {
                        "type": feature.geometry_type,
                        "coordinates": eval(feature.geometry_coordinates),
                    },
                    "properties": {}
                }
            )

        return geojson

    @staticmethod
    def __fetch_cities_limits_geojson(config: CityLimits) -> dict:
        """Fetch the geojson features from the MapLayer model."""


        cities = City.objects.all()

        # 1. If the mode is 'all', fetch all the cities
        if config.mode == "all":
            geojson = {"type": "FeatureCollection", "features": []}
            for city in cities:
                if city.name == "Limites de l'EMM":
                    continue
                feature_set = city.shape.all()
                for feature in feature_set:
                    geojson["features"].append(
                        {
                            "type": feature.feature_type,
                            "geometry": {
                                "type": feature.geometry_type,
                                "coordinates": eval(feature.geometry_coordinates),
                            },
                            "properties": {}
                        }
                    )
            return geojson

        elif config.mode == "exclude":
            geojson = {"type": "FeatureCollection", "features": []}
            for city in cities:
                if city.name not in config.cities:
                    feature_set = city.shape.all()
                    for feature in feature_set:
                        geojson["features"].append(
                            {
                                "type": feature.feature_type,
                                "geometry": {
                                    "type": feature.geometry_type,
                                    "coordinates": eval(feature.geometry_coordinates),
                                },
                                "properties": {}
                            }
                        )
            return geojson

        elif config.mode == "include":
            geojson = {"type": "FeatureCollection", "features": []}
            for city in cities:
                if city.name in config.cities:
                    feature_set = city.shape.all()
                    for feature in feature_set:
                        geojson["features"].append(
                            {
                                "type": feature.feature_type,
                                "geometry": {
                                    "type": feature.geometry_type,
                                    "coordinates": eval(feature.geometry_coordinates),
                                },
                                "properties": {}
                            }
                        )
            return geojson
    # End def __fetch_layer_geojson

    @staticmethod
    def __filter_geojson(geojson: dict, *filters: Filter) -> dict:
        """Filter the geojson features based on the filters provided."""
        # 1. Check if the geojson is valid
        if geojson is None or "features" not in geojson.keys():
            raise ValueError("The geojson is invalid.")

        # 2. Filter the geojson
        filtered_features : list[dict] = geojson["features"]
        initial_length = len(filtered_features)
        for filter_ in filters:
            temp_features = []
            for feature in filtered_features:
                properties = feature["properties"]
                if filter_.property_name not in properties.keys():
                    continue

                if filter_.op(properties[filter_.property_name], filter_.property_value) is True:
                    # print(properties[filter_.property_name], f"operator: {filter_.op}({type(filter_.op)})",
                    #                           filter_.property_value)
                    temp_features.append(feature)

            filtered_features = temp_features

        print(f"Filtering: kept {len(filtered_features)}/{initial_length} features")
        return {"type": "FeatureCollection", "features": filtered_features}
# End class MapBuilder