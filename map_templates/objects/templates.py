from __future__ import annotations

import json
from typing import Collection, Iterable, Literal

from map_templates import models
from map_templates.objects.features import Feature, FeatureGroup, Layer
from map_templates.objects.tiles import TileLayer
from map_templates.utils import repr_str

MIN_ZOOM = 5
MAX_ZOOM = 18


class MapTemplate:
    """Represents a map template."""
    def __init__(self,
                 name : str = None,
                 *,
                 zoom_start : int | None = None,
                 layer_control : bool = True,
                 zoom_control : bool = True,
                 tiles : Collection[TileLayer] = None,
                 features : Collection[Feature] | None = None) -> None:

        self.name          : str = name
        self.zoom_start    : int = zoom_start if zoom_start is not None else MIN_ZOOM + (MAX_ZOOM - MIN_ZOOM)*(2/3)
        self.layer_control : bool = layer_control
        self.zoom_control  : bool = zoom_control

        # Private properties
        self.__tiles   : set[TileLayer] = set()
        self.__features: set[Feature] = set()

        # Add the tiles
        if tiles not in (None, []):
            if not isinstance(tiles, (Collection, Iterable)):
                raise ValueError(
                    f"Expected 'tiles' to be of type 'TileLayer' or a collection of 'TileLayer', not '{type(tiles)}'"
                )
            for tile in tiles:
                self.add_tile(tile)

        # Add the features
        if features not in (None, []):
            if not isinstance(features, (Collection, Iterable)):
                raise ValueError(
                    f"Expected 'features' to be a collection of 'Feature', not '{type(features)}'"
                )
            for feature in features:
                if not isinstance(feature, Feature):
                    raise ValueError(f"Expected 'feature' to be of type 'Layer' or 'FeatureGroup', not '{type(feature)}'")
                self.add_feature(feature)


    # End def __init__

    # ------------------------------------------------------------------------------------------------------------------
    # Magic Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return "MapTemplate:{}".format(self.__hash__() if self.name.strip() in ("", None) else self.name)
    # End def __str__

    def __repr__(self):
       return repr_str(self)
    # End def __repr__

    # ------------------------------------------------------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def features(self) -> frozenset[Feature]:
        """Get the features of the template."""
        return frozenset(self.__features)
    # End def features

    @property
    def tiles(self) -> frozenset[TileLayer]:
        """Get the tiles of the template."""
        return frozenset(self.__tiles)
    # End def tiles

    # ------------------------------------------------------------------------------------------------------------------
    # Getters
    # ------------------------------------------------------------------------------------------------------------------

    def feature(self, name: str) -> Feature:
        """Get the features of the template."""
        try:
            return next((f for f in self.__features if f.name == name))
        except StopIteration:
            raise ValueError(f"Feature '{name}' does not exist in the template")
    # End def feature

    def tile(self, name) -> TileLayer:
        """Get the tiles of the template."""
        try:
            return next((t for t in self.__tiles if t.name == name))
        except StopIteration:
            raise ValueError(f"Tile '{name}' does not exist in the template")
    # End def tile

    # ------------------------------------------------------------------------------------------------------------------
    # Setters
    # ------------------------------------------------------------------------------------------------------------------

    def add_tile(self, tile: TileLayer):
        """Add a tile to the template."""
        if not isinstance(tile, TileLayer):
            raise ValueError(f"Expected 'tile' to be of type 'TileLayer', not '{type(tile)}'")
        self.__tiles.add(tile)
    # End def add_tile

    def add_feature(self, feature: Feature):
        """Add a layer to the template."""
        if not isinstance(feature, Feature):
            raise ValueError(f"Expected 'feature' to be of type 'Layer' or 'FeatureGroup', not '{type(feature)}'")
        self.__features.add(feature)
    # End def add_feature

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def remove_feature(self, fg_or_name : Feature | str, type : Literal['Layer', 'FeatureGroup'] | None = None):
        """Remove a layer from the template."""
        if isinstance(fg_or_name, str):
            if type is None:
                raise ValueError("If 'fg_or_name' is of type 'str', 'type' must be specified")
            if type not in ('Layer', 'FeatureGroup'):
                raise ValueError(f"Invalid type '{type}'")
            try:
                feature = next((f for f in self.__features if f.name == fg_or_name and f.type == type))
            except StopIteration:
                raise ValueError(f"Feature '{fg_or_name}' does not exist in the template")

        elif isinstance(fg_or_name, Feature):
            if fg_or_name not in self.__features:
                raise ValueError(f"Feature '{fg_or_name}' does not exist in the template")
            feature = fg_or_name
        else:
            raise ValueError(f"Expected 'fg_or_name' to be of type 'str' or 'Feature', not '{builtins.type(fg_or_name)}'")

        self.__features.remove(feature)
    # End def remove_layer

    def validate(self):
        """Validate the template."""
        # Validate that the zoom start is valid
        if self.zoom_start is not None and (self.zoom_start < MIN_ZOOM or self.zoom_start > MAX_ZOOM):
            raise ValueError(f"Zoom start must be between {MIN_ZOOM} and {MAX_ZOOM} (got {self.zoom_start})")
        for tile in self.__tiles:
            tile.validate()
        for feature in self.__features:
            feature.validate()
    # End def validate

    # ------------------------------------------------------------------------------------------------------------------
    # Model conversion
    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def from_model(model: models.MapTemplate) -> MapTemplate:
        """Convert a model to a MapTemplate object"""

        features = []
        for feature in model.layers.all():
            features.append(Layer.from_model(feature))
        for feature in model.feature_groups.all():
            features.append(FeatureGroup.from_model(feature))


        template = MapTemplate(name=model.name, zoom_start=model.zoom_start, layer_control=model.layer_control,
                               zoom_control=model.zoom_control, tiles=[
                TileLayer.from_model(tile) for tile in model.tiles.all()
            ], features=features)

        # Validate the template
        template.validate()

        # Return the template
        return template

    # End def from_model

    def to_model(self) -> models.MapTemplate:
        """Convert the MapTemplate object to a model"""
        raise NotImplementedError("This method has not been implemented yet")
    # End def to_model

    # ------------------------------------------------------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------------------------------------------------------

    def serialize(self, method: Literal['json', 'dict'] = 'json', **kwargs) -> str | dict:
        """Serialize the template.

        Args:
            method (Literal['json']): The method to use to serialize the template.
                Default is 'json'.
        """
        if method == 'json':
            return json.dumps(self._to_dict(), **kwargs)
        if method == 'dict':
            return self._to_dict()

        raise ValueError(f"Invalid method '{method}'")
    # End def serialize

    @staticmethod
    def deserialize(data: str | dict, method: Literal['json', 'kwargs'] = 'json', **kwargs) -> MapTemplate:
        """Deserialize the template."""
        if method == 'json':
            return MapTemplate._from_dict(json.loads(data, **kwargs))
        if method == 'dict':
            return MapTemplate._from_dict(data)
        raise ValueError(f"Invalid method '{method}'")
    # End def deserialize

    def _to_dict(self) -> dict:
        """Convert the template to a JSON string."""
        return {
            "__type__" : "__MapTemplate__",
            "name" : self.name,
            "zoom_start" : self.zoom_start,
            "layer_control" : self.layer_control,
            "zoom_control" : self.zoom_control,
            "tiles" : [tile.serialize(method='dict') for tile in self.__tiles],
            "features" : [feature.serialize(method='dict') for feature in self.__features]
        }

    # End def to_json

    @staticmethod
    def _from_dict(data: dict) -> MapTemplate:
        """Convert the template to a JSON string."""
        if data.get("__type__", None) != "__MapTemplate__":
            raise ValueError(f"Invalid type '{data.get('__type__', None)}'")

        return MapTemplate(name=data["name"], zoom_start=data["zoom_start"], layer_control=data["layer_control"],
                           zoom_control=data["zoom_control"],
                           tiles=[TileLayer.deserialize(tile, method='dict') for tile in data["tiles"]],
                           features=[Layer.deserialize(feature, method='dict') for feature in data["features"]])
    # End def to_json
