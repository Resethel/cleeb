from __future__ import annotations

import enum
import json
from abc import ABC, abstractmethod
from typing import Collection, Iterable, Literal, MutableSet

from map_templates import models
from map_templates.objects.filters import Filter
from map_templates.objects.styles import Style
from map_templates.utils import repr_str


class FeatureType(enum.Enum):
    """The type of the feature."""
    MARKER = enum.auto()
    LAYER = enum.auto()
    FEATURE_GROUP = enum.auto()


class Feature(ABC):
    """Represents a feature on the map.

    May be a Layer, a FeatureGroup, or a Marker.
    """
    def __init__(self, name : str, type_ : FeatureType) -> None:
        if not isinstance(name, str):
            raise TypeError(f"Expected 'name' to be of type 'str', not '{type(name)}'")
        if not isinstance(type_, FeatureType):
            raise TypeError(f"Expected 'type' to be of type 'FeatureType', not '{type(type_)}'")
        self.name : str = name
        self.type : FeatureType = type_
    # End def __init__

    @abstractmethod
    def validate(self):
        """Validate the shape."""
        pass
    # End def validate

    # ------------------------------------------------------------------------------------------------------------------
    # Model conversion
    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    @abstractmethod
    def from_model(model) -> Feature:
        """Convert a model to a Feature object"""
        pass
    # End def from_model

    @abstractmethod
    def to_model(self):
        """Convert the Feature object to a model"""
        pass
    # End def to_model

    # ------------------------------------------------------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------------------------------------------------------

    @abstractmethod
    def serialize(self, method: Literal['json', 'dict'] = 'json', **kwargs) -> str | dict:
        """Serialize the feature."""
        pass
    # End def serialize

    @staticmethod
    @abstractmethod
    def deserialize(data: str | dict, method: Literal['json', 'dict'] = 'json', **kwargs) -> Feature:
        """Deserialize the feature."""
        pass
    # End def deserialize


class Layer(Feature):
    """Represents a map layer.

    A map layer is a layer of data that can be shown or hidden on the map.
    The map layer to load is defined by its name in the database.
    """
    def __init__(
            self,
            name : str,
            map_layer: str,
            style : Style | None = None,
            highlight : Style | None = None,
            filters : Filter | Collection[Filter] | Iterable[Filter] | None = None,
            show_on_startup : bool = True
    ) -> None:
        super().__init__(name, FeatureType.LAYER)
        self.map_layer       : str           = map_layer
        self.filters         : list[Filter]  = []
        self.style           : Style | None  = style
        self.highlight       : Style | None  = highlight
        self.show_on_startup : bool          = show_on_startup

        # add filters
        if filters is not None:
            if not isinstance(filters, (Collection, Iterable)):
                self.add_filter(filters)

            for i, filter_ in enumerate(filters):
                self.add_filter(filter_)
    # End def __init__

    # ------------------------------------------------------------------------------------------------------------------
    # Magic Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __eq__(self, other):
        if not isinstance(other, Layer):
            return False
        return all([
            self.name == other.name,
            self.map_layer == other.map_layer,
            self.style == other.style,
            self.highlight == other.highlight,
            self.filters == other.filters,
            self.show_on_startup == other.show_on_startup])
    # End def __eq__

    def __hash__(self):
        return hash((self.name, self.map_layer, self.style, self.highlight, frozenset(self.filters), self.show_on_startup))
    # End def __hash__

    def __repr__(self):
        return repr_str(self)
    # End def __repr__

    # ------------------------------------------------------------------------------------------------------------------
    # Add filters
    # ------------------------------------------------------------------------------------------------------------------

    def add_filter(self, filter_ : Filter):
        """Add a filter to the layer."""
        self.filters.append(filter_)
    # End def add_filter

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def validate(self):
        """Validate the layer."""
        # Validate that the zoom start is valid
        if self.style is not None:
            self.style.validate()
        if self.highlight is not None:
            self.highlight.validate()

        for idx, filter_ in enumerate(self.filters):
            if not isinstance(filter_, Filter):
                raise ValueError(f"Expected 'filters@{idx}' to be of type 'Filter', not '{type(filter_)}'")
            filter_.validate()
    # End def validate

    # ------------------------------------------------------------------------------------------------------------------
    # Model conversion
    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def from_model(model: models.Layer) -> Layer:
        """Convert a model to a Layer object"""
        if not isinstance(model, models.Layer):
            raise ValueError(f"Expected 'model' to be of a 'Layer' model, not '{type(model)}'")

        return Layer(
            name=model.name,
            map_layer=model.map_layer.name if model.map_layer else None,
            style=Style.from_model(model.style) if model.style else None,
            highlight=Style.from_model(model.highlight) if model.highlight else None,
            filters=[Filter(key=f.key, operator=f.operator, value=f.value) for f in model.filters.all()],
            show_on_startup=model.show
        )

    def to_model(self) -> models.Layer:
        """Convert the Layer object to a model"""
        raise NotImplementedError("This method has not been implemented yet")
    # End def to_model

    # ------------------------------------------------------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------------------------------------------------------

    def serialize(self, method: Literal['json', 'dict'] = 'json', **kwargs) -> str | dict:
        """Serialize the layer.

        Args:
            method (Literal['json', 'dict']): The method to use to serialize the layer.
                Default is 'json'.
        """
        if method == 'json':
            return json.dumps(self._to_dict(), **kwargs)
        if method == 'dict':
            return self._to_dict()
        raise ValueError(f"Invalid method '{method}'")
    # End def serialize

    @staticmethod
    def deserialize(data: str | dict, method: Literal['json', 'dict'] = 'json', **kwargs) -> Layer:
        """Deserialize the layer."""
        if method == 'json':
            return Layer._from_dict(json.loads(data, **kwargs))
        if method == 'dict':
            return Layer._from_dict(data)
        raise ValueError(f"Invalid method '{method}'")
    # End def deserialize

    def _to_dict(self) -> dict:
        return {
            "__type__"    : "__Layer__",
            "name"      : self.name,
            "map_layer" : self.map_layer,
            "style"     : self.style.serialize('dict') if self.style else None,
            "highlight" : self.highlight.serialize('dict') if self.highlight else None,
            "filters"   : [f.serialize('dict') for f in self.filters],
            "show" : self.show_on_startup
        }
    # End def to_dict

    @staticmethod
    def _from_dict(data: dict) -> Layer:
        if data.get("__type__", None) != "__Layer__":
            raise ValueError(f"Invalid type '{data.get('__type__', None)}'")
        return Layer(
            name=data["name"],
            map_layer=data["map_layer"],
            style=Style.deserialize(data["style"], 'dict') if data["style"] else None,
            highlight=Style.deserialize(data["highlight"], 'dict') if data["highlight"] else None,
            filters=[Filter.deserialize(f, 'dict') for f in data["filters"]],
            show_on_startup=data["show"]
        )


class FeatureGroup(MutableSet, Feature):
    """Represents a map feature group.

    A feature group is a group of features that can be shown or hidden on the map.
    It may contain multiple layers, markers, etc.
    """

    def __init__(
            self,
            name : str,
            show_on_startup : bool = True,
            *,
            features : Collection[Feature] | Iterable[Feature] | None = None
    ) -> None:
        super().__init__(name, FeatureType.FEATURE_GROUP)
        self.name : str | None = name
        self.show_on_startup : bool = show_on_startup
        self.__features : set[Feature] = set()

        if features is None:
            return
        if not isinstance(features, (Collection, Iterable)):
            raise ValueError(f"Expected 'layers' to be a `Collection` or an `Iterable`, not `{type(features)}`")

        for feature in features:
            if not isinstance(feature, Feature):
                raise ValueError(f"Expected 'feature' to be of type 'Feature', not '{type(feature)}'")
            self.add(feature)
    # End def __init__

    # ==================================================================================================================
    # Magic Methods
    # ==================================================================================================================

    def __getitem__(self, name: str) -> Feature:
        if not isinstance(name, str):
            raise TypeError(f"Expected 'name' to be of type 'str', not '{type(name)}'")
        try:
            return next((l for l in self.__features if l.name == name))
        except StopIteration:
            raise ValueError(f"Feature '{name}' does not exist in feature group")
    # End def __getitem__

    def __contains__(self, name: str) -> bool:
        if not isinstance(name, str):
            raise TypeError(f"Expected 'name' to be of type 'str', not '{type(name)}'")
        return next((l for l in self.__features if l.name == name), None) is not None
    # End def __contains__

    def __iter__(self):
        return iter(self.__features)
    # End def __iter__

    def __len__(self):
        return len(self.__features)
    # End def __len__

    def __eq__(self, other):
        if not isinstance(other, FeatureGroup):
            return False
        return self.__features == other.__features
    # End def __eq__

    def __hash__(self):
        return hash((self.name, self.show_on_startup, frozenset(self.__features)))
    # End def __hash__

    def __repr__(self):
        return repr_str(self)
    # End def __repr__

    # ------------------------------------------------------------------------------------------------------------------
    # Setters
    # ------------------------------------------------------------------------------------------------------------------

    def add(self, feature: Feature):
        """Add a layer to the feature group."""
        if not isinstance(feature, Feature):
            raise ValueError(f"Expected 'layer' to be of type 'Layer', not '{type(feature)}'")
        self.__features.add(feature)
    # End def add

    def discard(self, feature: Feature):
        """Remove a layer from the feature group."""
        if not isinstance(feature, Feature):
            raise ValueError(f"Expected 'layer' to be of type 'Layer', not '{type(feature)}'")
        self.__features.discard(feature)
    # End def discard

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def validate(self):
        """Validate the feature group."""
        for feature in self.__features:
            feature.validate()
    # End def validate

    # ------------------------------------------------------------------------------------------------------------------
    # Model conversion
    # ------------------------------------------------------------------------------------------------------------------

    @staticmethod
    def from_model(model: models.FeatureGroup) -> FeatureGroup:
        """Convert a model to a FeatureGroup object"""
        if not isinstance(model, models.FeatureGroup):
            raise ValueError(f"Expected 'model' to be of a 'FeatureGroup' model, not '{type(model)}'")

        return FeatureGroup(
            name=model.name,
            show_on_startup=model.show_on_startup,
            features=[Layer.from_model(layer) for layer in model.layers.all()]
        )
    # End def from_model

    def to_model(self) -> models.FeatureGroup:
        """Convert the FeatureGroup object to a model"""
        raise NotImplementedError("This method has not been implemented yet")
    # End def to_model

    # ------------------------------------------------------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------------------------------------------------------

    def serialize(self, method: Literal['json', 'dict'] = 'json', **kwargs) -> str | dict:
        """Serialize the feature group.

        Args:
            method (Literal['json', 'dict']): The method to use to serialize the feature group.
                Default is 'json'.
        """
        if method == 'json':
            return json.dumps(self.__to_dict(), **kwargs)
        if method == 'dict':
            return self.__to_dict()
        raise ValueError(f"Invalid method '{method}'")
    # End def serialize

    def deserialize(self, data: str | dict, method: Literal['json', 'dict'] = 'json', **kwargs) -> FeatureGroup:
        """Deserialize the feature group."""
        if method == 'json':
            return FeatureGroup.__from_dict(json.loads(data, **kwargs))
        if method == 'dict':
            return FeatureGroup.__from_dict(data)
        raise ValueError(f"Invalid method '{method}'")

    def __to_dict(self) -> dict:
        return {
            "__type__" : "__FeatureGroup__",
            "name" : self.name,
            "show_on_startup" : self.show_on_startup,
            "features" : [feature.serialize('dict') for feature in self.__features]
        }
    # End def to_dict

    @staticmethod
    def __from_dict(data: dict) -> FeatureGroup:
        if data.get("__type__", None) != "__FeatureGroup__":
            raise ValueError(f"Expected '__type__' to be '__FeatureGroup__', not '{data.get('__type__', None)}'")

        features = []
        for feature in data["features"]:
            if feature.get("__type__", None) == "__Layer__":
                features.append(Layer.deserialize(feature, 'dict'))
            elif feature.get("__type__", None) == "__FeatureGroup__":
                features.append(FeatureGroup.deserialize(feature, 'dict'))
            else:
                raise ValueError(f"Invalid type '{feature.get('__type__', None)}'")


        return FeatureGroup(
            name=data["name"],
            show_on_startup=data["show_on_startup"],
            features=features
        )
    # End def from_dict
# End class FeatureGroup