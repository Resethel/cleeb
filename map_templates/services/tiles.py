# -*- coding: utf-8 -*-
"""
Tile layer service for the `map_templates` application.
"""
from __future__ import annotations

import json
from typing import Literal

from map_templates import models


class TileLayer:
    """Defines the different tiles that can be used."""

    def __init__(self,
                 name : str,
                 transparent: bool = False,
                 overlay: bool = True,
                 control: bool = True,
                 type: Literal['builtin', 'xyz'] = 'builtin',
                 *,
                 display_name: str | None = None,
                 url: str | None = None,
                 access_token: str | None = None,
                 attribution: str | None = None
                 ):
        self.name = name
        self.display_name : str | None = display_name if display_name is not None else name
        self.type : Literal['builtin', 'xyz'] = type

        # Display fields
        self.transparent : bool = transparent
        self.overlay : bool = overlay
        self.control : bool = control

        # WMS and XYZ fields
        self.url          : str | None = url
        self.access_token : str | None = access_token
        self.attribution  : str | None = attribution
    # End def __init__

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def validate(self):
        """Validate the tile layer."""
        pass
    # End def validate

    # ------------------------------------------------------------------------------------------------------------------
    # Model conversion
    # ------------------------------------------------------------------------------------------------------------------
    @staticmethod
    def from_model(tile_layer: models.TileLayer) -> TileLayer:
        return TileLayer(
                name=tile_layer.name,
                display_name=tile_layer.verbose_name,
                transparent=tile_layer.transparent,
                overlay=tile_layer.overlay,
                control=tile_layer.control,
                type=tile_layer.type,
                url=tile_layer.url,
                attribution=tile_layer.attribution
        )
    # End def from_model

    def to_model(self) -> models.TileLayer:
        """Convert the TileLayer object to a model"""
        raise NotImplementedError("This method has not been implemented yet")
    # End def to_model

    # ------------------------------------------------------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------------------------------------------------------

    def serialize(self, method: Literal['json', 'dict'] = 'json', **kwargs) -> str | dict:
        """Serialize the tile layer.

        Args:
            method (Literal['json', 'dict']): The method to use to serialize the tile layer.
                Default is 'json'.
        """
        if method == 'json':
            return json.dumps(self._to_dict(), **kwargs)
        if method == 'dict':
            return self._to_dict()
        raise ValueError(f"Invalid method '{method}'")
    # End def serialize

    @staticmethod
    def deserialize(data: str | dict, method: Literal['json', 'dict'] = 'json', **kwargs) -> TileLayer:
        """Deserialize the tile layer."""
        if method == 'json':
            return TileLayer._from_dict(json.loads(data, **kwargs))
        if method == 'dict':
            return TileLayer._from_dict(data)
        raise ValueError(f"Invalid method '{method}'")
    # End def deserialize

    def _to_dict(self) -> dict:
        """Convert the tile layer to a dictionary."""
        return {
            "__type__" : "__TileLayer__",
            "name" : self.name,
            "display_name" : self.display_name,
            "type" : self.type,
            "transparent" : self.transparent,
            "overlay" : self.overlay,
            "control" : self.control,
            "url" : self.url,
            "access_token" : self.access_token,
            "attribution" : self.attribution
        }
    # End def to_dict

    @staticmethod
    def _from_dict(data: dict) -> TileLayer:
        """Convert the dictionary to a tile layer."""
        if data.get("__type__", None) != "__TileLayer__":
            raise ValueError(f"Invalid type '{data.get('__type__', None)}'")

        return TileLayer(
            name=data["name"],
            display_name=data["display_name"],
            type=data["type"],
            transparent=data["transparent"],
            overlay=data["overlay"],
            control=data["control"],
            url=data["url"],
            fmt=data["format"],
            layers=data["layers"],
            attribution=data["attribution"]
        )
    # End def from_dict
