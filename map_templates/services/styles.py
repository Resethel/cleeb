# -*- coding: utf-8 -*-
"""
Styles service module for the `map_templates` application.
"""
from __future__ import annotations

import json
from typing import Literal

from folium.plugins import CirclePattern, StripePattern

from map_templates import models
from map_templates.utils import repr_str, snake_to_camel

# ======================================================================================================================
# Constants
# ======================================================================================================================

DEFAULT_STYLE = {
    "stroke"       : True,
    "color"        : "#3388ff",
    "weight"       : 3,
    "opacity"      : 1,
    "line_cap"     : 'round',
    "line_join"    : 'round',
    "dash_array"   : None,
    "dash_offset"  : None,
    "fill"         : True,
    "fill_color"   : "#3388ff",
    "fill_opacity" : 0.2,
    "fill_rule"    : 'evenodd',
    "fill_pattern" : None
}

STYLE_ATTRIBUTES = [
    "stroke",
    "color",
    "weight",
    "opacity",
    "line_cap",
    "line_join",
    "dash_array",
    "dash_offset",
    "fill",
    "fill_color",
    "fill_opacity",
    "fill_rule",
    "fill_pattern"
]


# ======================================================================================================================
# Style
# ======================================================================================================================

class Style:
    """Represent a style of the data.

    A style can either be applied to a layer or to an element which match a given property.
    """

    # ------------------------------------------------------------------------------------------------------------------
    # Magic Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __init__(self, **kwargs):

        # Style properties
        self.stroke       : bool | None        = kwargs.get("stroke", None)
        self.color        : str | None         = kwargs.get("color", None)
        self.weight       : float | int | None = kwargs.get("weight", None)
        self.opacity      : float | int | None = kwargs.get("opacity", None)
        self.line_cap     : str | None         = kwargs.get("line_cap", None)
        self.line_join    : str | None         = kwargs.get("line_join", None)
        self.dash_array   : str | None         = kwargs.get("dash_array", None)
        self.dash_offset  : str | None         = kwargs.get("dash_offset", None)
        self.fill         : bool | None        = kwargs.get("fill", None)
        self.fill_color   : str | None         = kwargs.get("fill_color", None)
        self.fill_opacity : int | float | None = kwargs.get("fill_opacity", None)
        self.fill_rule    : str | None         = kwargs.get("fill_rule", None)
        self.fill_pattern : StripePattern | CirclePattern | None = kwargs.get("fill_pattern", None)

        self.property_styles : list[PropertyStyle] = []
    # End def __init__

    # ------------------------------------------------------------------------------------------------------------------
    # Magic Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        attrs = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items() if v is not None and not k.startswith('_'))
        return f"{self.__class__.__name__}({attrs})"
    # End def __str__

    def __repr__(self):
        return repr_str(self)
    # End def __repr__

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def validate(self):
        """Validate the style."""
        validate_style_attributes({k: v for k, v in self.__dict__.items() if k in STYLE_ATTRIBUTES})
        for property_style in self.property_styles:
            property_style.validate()
    # End def validate

    def function(self, x : dict) -> dict:
        """Function used to style the data.

        Args:
            x (dict): The data to style.
        """

        rstyle = {}
        # Get the style for the layer
        for attr in STYLE_ATTRIBUTES:
            value = getattr(self, attr)
            if value is not None:
                rstyle[snake_to_camel(attr, capitalize_first=False)] = value

        # For each property style, check if the property value matches the value of the property in the data
        # If it does, add the style to the style
        for property_style in self.property_styles:
            try:
                if x["properties"].get(property_style.key, None) == property_style.value:
                    for attr in STYLE_ATTRIBUTES:
                        value = getattr(property_style, attr)
                        if value is not None:
                            rstyle[snake_to_camel(attr, capitalize_first=False)] = value
            except Exception:
                pass

        return rstyle
    # End def function_style

    # ------------------------------------------------------------------------------------------------------------------
    # Private methods
    # ------------------------------------------------------------------------------------------------------------------

    def __fill_defaults(self):
        """Fills the style with the default values."""
        for attr, default_value in DEFAULT_STYLE.items():
            if getattr(self, attr) is None:
                setattr(self, attr, default_value)
    # End def __fill_defaults

    # ------------------------------------------------------------------------------------------------------------------
    # Model Conversion
    # ------------------------------------------------------------------------------------------------------------------

    def to_model(self) -> models.BaseStyle:
        """Convert the Style object to a model"""
        raise NotImplementedError("This method has not been implemented yet")
    # End def to_model

    @staticmethod
    def from_model(model: models.Style) -> Style:
        attributes = {attr: getattr(model, attr) for attr in STYLE_ATTRIBUTES if hasattr(model, attr)}

        # TODO: The conversion of fill patterns is not yet supported
        if hasattr(model, "fill_pattern"):
            attributes["fill_pattern"] = None

        style = Style(**attributes)

        for property_style in model.property_styles.all():
            style.property_styles.append(PropertyStyle.from_model(property_style))

        return style
    # End def from_model

    # ------------------------------------------------------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------------------------------------------------------

    def serialize(self, method: Literal['json', 'dict'] = 'json', **kwargs) -> str | dict:
        """Serialize the style.

        Args:
            method (Literal['json', 'dict']): The method to use to serialize the style.
                If 'json', the style is serialized to a JSON string (see `json.dumps` for kwargs).
                If 'dict', the style is serialized to a dictionary.
                Default is 'json'.
        """
        if method == 'json':
            return json.dumps(self._to_dict(), **kwargs)
        if method == 'dict':
            return self._to_dict()
        raise ValueError(f"Invalid method '{method}'")
    # End def serialize

    @staticmethod
    def deserialize(data: str | dict, method: Literal['json', 'dict'] = 'json', **kwargs) -> Style:
        """Deserialize the style.

        Args:
            data (str | dict): The data to deserialize.
            method (Literal['json', 'dict']): The method to use to deserialize the style.
                If 'json', the data is deserialized from a JSON string (see `json.loads` for kwargs).
                If 'dict', the data is deserialized from a dictionary.
                Default is 'json'.
        """

        if method == 'json':
            return Style._from_dict(json.loads(data, **kwargs))
        if method == 'dict':
            return Style._from_dict(data)
        raise ValueError(f"Invalid method '{method}'")
    # End def deserialize

    def _to_dict(self) -> dict:

        dict_ = {"__type__" : "Style"}

        # Get the style for the layer
        for attr in STYLE_ATTRIBUTES:
            value = getattr(self, attr)
            if value is not None:
                dict_[attr] = value

        if self.property_styles:
            dict_["property_styles"] = [PropertyStyle.serialize(ps, 'dict') for ps in self.property_styles]
        return dict_
    # End def to_dict


    @staticmethod
    def _from_dict(data: dict) -> Style:
        if data.get("__type__", None) != "Style":
            raise ValueError(f"Invalid type '{data.get('__type__', None)}'")

        style = Style()
        for attr, value in data.items():
            if attr == "property_styles":
                for ps in value:
                    style.property_styles.append(PropertyStyle.deserialize(ps, 'dict'))
            else:
                setattr(style, attr, value)
        return style
    # End def from_dict
# End class Style

# ======================================================================================================================
# PropertyStyle
# ======================================================================================================================

class PropertyStyle:

    def __init__(self, key: str, value: str, **kwargs):
        super().__init__()
        self.key = key
        self.value = value

        self.stroke       : bool | None                          = kwargs.get("stroke", None)
        self.color        : str | None                           = kwargs.get("color", None)
        self.weight       : float | int | None                   = kwargs.get("weight", None)
        self.opacity      : float | int | None                   = kwargs.get("opacity", None)
        self.line_cap     : str | None                           = kwargs.get("line_cap", None)
        self.line_join    : str | None                           = kwargs.get("line_join", None)
        self.dash_array   : str | None                           = kwargs.get("dash_array", None)
        self.dash_offset  : str | None                           = kwargs.get("dash_offset", None)
        self.fill         : bool | None                          = kwargs.get("fill", None)
        self.fill_color   : str | None                           = kwargs.get("fill_color", None)
        self.fill_opacity : int | float | None                   = kwargs.get("fill_opacity", None)
        self.fill_rule    : str | None                           = kwargs.get("fill_rule", None)
        self.fill_pattern : StripePattern | CirclePattern | None = kwargs.get("fill_pattern", None)
    # End def __init__

    # ------------------------------------------------------------------------------------------------------------------
    # Magic Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __repr__(self):
        return repr_str(self)
    # End def __repr__

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def validate(self):
        """Validate the style."""
        if not isinstance(self.key, str):
            raise ValueError(f"Expected 'key' to be of type 'str', not '{type(self.key)}'")
        if not isinstance(self.value, str):
            raise ValueError(f"Expected 'value' to be of type 'str', not '{type(self.value)}'")
        validate_style_attributes({k: v for k, v in self.__dict__.items() if k in STYLE_ATTRIBUTES})
    # End def validate

    # ------------------------------------------------------------------------------------------------------------------
    # Model Conversion
    # ------------------------------------------------------------------------------------------------------------------

    def to_model(self) -> models.PropertyStyle:
        """Convert the Style object to a model"""
        raise NotImplementedError("This method has not been implemented yet")
    # End def to_model

    @staticmethod
    def from_model(model: models.PropertyStyle) -> PropertyStyle:
        if not isinstance(model, models.PropertyStyle):
            raise ValueError(f"Expected 'model' to be of a 'PropertyStyle' model, not '{type(model)}'")

        return PropertyStyle(
            key=model.key,
            value=model.value,
            stroke=model.stroke,
            color=model.color,
            weight=model.weight,
            opacity=model.opacity,
            line_cap=model.line_cap,
            line_join=model.line_join,
            dash_array=model.dash_array,
            dash_offset=model.dash_offset,
            fill=model.fill,
            fill_color=model.fill_color,
            fill_opacity=model.fill_opacity,
            fill_rule=model.fill_rule,
            fill_pattern=None  # TODO: Implement the fill pattern once supported by the model
        )
    # End def from_model

    # ------------------------------------------------------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------------------------------------------------------

    def serialize(self, method: Literal['json', 'dict'] = 'json', **kwargs) -> str | dict:
        """Serialize the style.

        Args:
            method (Literal['json', 'dict']): The method to use to serialize the style.
                If 'json', the style is serialized to a JSON string (see `json.dumps` for kwargs).
                If 'dict', the style is serialized to a dictionary.
                Default is 'json'.
        """
        if method == 'json':
            return json.dumps(self._to_dict(), **kwargs)
        if method == 'dict':
            return self._to_dict()
        raise ValueError(f"Invalid method '{method}'")

    @staticmethod
    def deserialize(data: str | dict, method: Literal['json', 'dict'] = 'json', **kwargs) -> PropertyStyle:
        """Deserialize the style.

        Args:
            data (str | dict): The data to deserialize.
            method (Literal['json', 'dict']): The method to use to deserialize the style.
                If 'json', the data is deserialized from a JSON string (see `json.loads` for kwargs).
                If 'dict', the data is deserialized from a dictionary.
                Default is 'json'.
        """

        if method == 'json':
            return PropertyStyle._from_dict(json.loads(data, **kwargs))
        if method == 'dict':
            return PropertyStyle._from_dict(data)
        raise ValueError(f"Invalid method '{method}'")
    # End def deserialize

    def _to_dict(self) -> dict:
        dict_ = {
            "__type__" : "__PropertyStyle__",
            "key" : self.key,
            "value" : self.value
        }
        for attr in STYLE_ATTRIBUTES:
            value = getattr(self, attr)
            if value is not None:
                dict_[attr] = value
        return dict_
    # End def to_dict

    @staticmethod
    def _from_dict(data: dict) -> PropertyStyle:
        if data.get("__type__", None) != "__PropertyStyle__":
            raise ValueError(f"Invalid type '{data.get('__type__', None)}'")

        return PropertyStyle(key=data.pop("key"), value=data.pop("value"), **data)
    # End def from_dict
# End class PropertyStyle

# ======================================================================================================================
# Methods
# ======================================================================================================================

def validate_style_attributes(attributes: dict):
    """Validate the style attributes."""
    # 1. Ensure that there is no attribute that do not belong to the style
    for attr in attributes:
        if attr not in STYLE_ATTRIBUTES:
            raise ValueError(f"Invalid attribute '{attr}'")

    # 2. Validate the style attributes
    for attr, value in attributes.items():
        if value is None:
            continue
        if attr not in STYLE_ATTRIBUTES:
            raise ValueError(f"Invalid attribute '{attr}'")

        match attr:
            case "stroke" | "fill":
                if not isinstance(value, bool):
                    raise ValueError(f"Expected '{attr}' to be of type 'bool', not '{type(value)}'")
            case "color" | "fill_color":
                if not isinstance(value, str):
                    raise ValueError(f"Expected 'color' to be of type 'str', not '{type(value)}'")
                elif not value.startswith("#") and len(value) != 7 and not all(c.lower() in "0123456789abcdef" for c in value[1:]):
                    raise ValueError(f"Expected 'color' to be a valid hex color, not '{value}'")
            case "weight":
                if not isinstance(value, (float, int)):
                    raise ValueError(f"Expected 'weight' to be of type 'float' or 'int', not '{type(value)}'")
            case "opacity" | "fill_opacity":
                if not isinstance(value, (float, int)):
                    raise ValueError(f"Expected '{attr}' to be of type 'float' or 'int', not '{type(value)}'")
                if not 0 <= value <= 1:
                    raise ValueError(f"Expected 'opacity' to be between 0 and 1, not '{value}'")
            case "line_cap":
                if value not in ['butt', 'round', 'square']:
                    raise ValueError(f"Expected 'line_cap' to be one of 'butt', 'round', 'square', not '{value}'")
            case "line_join":
                if value not in ['miter', 'round', 'bevel']:
                    raise ValueError(f"Expected 'line_join' to be one of 'miter', 'round', 'bevel', not '{value}'")

            # A dash array is a list of comma and/or white space separated <length>s and <percentage>s that
            # specify the lengths of alternating dashes and gaps.
            case "dash_array":
                if value is not None and not isinstance(value, str):
                    raise ValueError(f"Expected 'dash_array' to be of type 'str', not '{type(value)}'")
                dashes = value.replace(",", " ").replace("%", "").split()
                for dash in dashes:
                    try:
                        float(dash)
                    except ValueError:
                        raise ValueError(f"Expected 'dash_array' to be a list of comma and/or "
                                         f"white space separated <length>s and <percentage>s, not '{value}'") from None

            case "dash_offset":
                if value is not None and not isinstance(value, (float, int)):
                    raise ValueError(f"Expected 'dash_offset' to be of type 'float' or 'int', not '{type(value)}'")
            case "fill_rule":
                if value not in ['nonzero', 'evenodd']:
                    raise ValueError(f"Expected 'fill_rule' to be one of 'nonzero', 'evenodd', not '{value}'")
            case "fill_pattern":
                if not isinstance(value, (StripePattern, CirclePattern)):
                    raise ValueError(f"Expected 'fill_pattern' to be of type 'StripePattern' or 'CirclePattern', not '{type(value)}'")
    # End match
# End def validate_style_attributes


