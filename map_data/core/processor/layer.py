# -*- coding: utf-8 -*-
"""
Module to process a dataset into a geojson layer.
"""
import geojson

from datasets.models import DatasetTechnicalInformation
from map_data.core.utils import geo
from map_data.core.utils.geo import EPSGProjection, Encoding
from map_layers.models import MapLayer
from shapes.models import Shape


# ======================================================================================================================
# Class
# ======================================================================================================================

class LayerProcessor:
    """The layer processor is responsible for converting a MapLayerTemplate to geojson and save them to the model."""

    def __init__(self, map_layer : MapLayer) -> None:
        if not isinstance(map_layer, MapLayer):
            raise ValueError(f"Invalid type for map_layer: {type(map_layer)}")
        self.template = map_layer
        self.dataset = map_layer.dataset
        self.dataset_file = map_layer.dataset.get_latest_version().file

        # Define the projection of the input and output data
        self.input_epsg_projection = EPSGProjection.EPSG_2154 # By default, assume it's in Lambert 93 (most common in France)
        projection_ti : DatasetTechnicalInformation | None = DatasetTechnicalInformation.objects.filter(dataset=self.dataset, key="projection").first()
        if self.dataset.format == "shapefile" and projection_ti is not None:
            projection = projection_ti.value.casefold().replace(" ", "")
            if projection in ("epsg:4326", "wgs84"):
                self.input_epsg_projection = EPSGProjection.EPSG_4326
            if projection in ("epsg:2154", "lambert93"):
                self.input_epsg_projection = EPSGProjection.EPSG_2154
        elif self.dataset.format == "geojson": # GeoJSON is always in WGS 84
            self.input_epsg_projection = EPSGProjection.EPSG_4326

        self.output_epsg_projection = EPSGProjection.EPSG_4326 # By default, assume it's in WGS 84 (most common in web mapping)

        # Define the encoding of the input data
        self.encoding = Encoding(self.dataset.encoding)

        # Internal variables. Should not be accessed directly
        self.__cached_features: geojson.FeatureCollection | None = None
    # End def __init__

    # ------------------------------------------------------------------------------------------------------------------
    # Magic Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self) -> str:
        return f"LayerProcessor for {self.template}"
    # End def __str__

    # ------------------------------------------------------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------------------------------------------------------

    def process(self):
        """Process the dataset into a geojson layer."""
        # 1. Clean the shapes related to the MapLayerTemplate
        self.__cached_features = None
        self.__delete_related_shapes()

        # NOTE: geojson datasets are not yet supported
        if self.dataset.format == "geojson":
            raise NotImplementedError("GeoJSON datasets are not yet supported")

        # 2. Process the dataset into a geojson layer
        data = geo.convert_shapefile_to_geojson(
            file_path=self.dataset_file.path,
            shapefile_name=self.template.shapefile,
            encoding=self.encoding,
            input_epsg_projection=self.input_epsg_projection,
            output_epsg_projection=self.output_epsg_projection,
        )

        # 3. Filter the features
        # TODO: Add support for filtering

        # 4. Save the data within the processor
        self.__cached_features = data

        # 5. Save the shapes to the database
        try:
            self.__save_shapes_to_database()
        finally:
            # 6. clean the feature collection
            self.__cached_features = None

        # 6. Update the template status
        # TODO: Implement the status update
    # End def process

    # ------------------------------------------------------------------------------------------------------------------
    # Private methods
    # ------------------------------------------------------------------------------------------------------------------

    def __delete_related_shapes(self) -> int:
        """Remove the shapes related to the Layer.

        If there is no layers, this functions does nothing

        Returns:
            (int): the number of deleted shapes
        """
        n_deletion = 0
        # 1. Remove all shapes related to the MapLayerTemplate
        for shape in Shape.objects.filter(parent_layer=self.template):
            shape.delete()
            n_deletion += 1
        return n_deletion
    # End def delete_related_shapes

    def __save_shapes_to_database(self) -> None:
        """Save the feature collection to the database."""
        if self.__cached_features is None:
            raise ValueError("No feature collection to save")

        # 1. Save the shapes to the database
        for feature in self.__cached_features.get("features"):
            shape = Shape(
                parent_layer=self.template,
                feature_type=feature.get("type"),
                geometry_type=feature.get("geometry").get("type"),
                geometry_coordinates=feature.get("geometry").get("coordinates"),
                properties=feature.get("properties")
            )
            shape.save()
    # End def save_shapes_to_database
# End class LayerProcessor

