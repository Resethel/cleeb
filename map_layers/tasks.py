# -*- coding: utf-8 -*-
"""
Tasks for the `map_layers` application.
"""
from __future__ import annotations

import celery
from django.apps import apps

from map_data.core.processor.layer import LayerProcessor
from map_layers.choices import GenerationStatus


@celery.shared_task(bind=True, throws=(ValueError, RuntimeError))
def generate_layer_geometries_task(self, map_layer_id: int):
    """Generate geometries for a map layer."""

    map_layer_model = apps.get_model("map_layers", "MapLayer")
    try:
        map_layer = map_layer_model.objects.get(id=map_layer_id)
    except map_layer_model.DoesNotExist:
        raise ValueError(f"MapLayer with ID '{map_layer_id}' does not exist.")

    # Update the status of the layer and its task ID
    map_layer.generation_status = GenerationStatus.RUNNING
    map_layer.task_id = self.request.id
    map_layer.save()

    try:
        # 1. Create the processor
        processor = LayerProcessor(map_layer)

        # 2. Generate the geometries
        processor.process()

        # 3. Ensure that the geometries are saved
        generated_shapes = map_layer.shapes.count()

        if generated_shapes == 0:
            raise RuntimeError("No geometries were generated.")
    except Exception as e:
        map_layer.generation_status = GenerationStatus.FAILED
        map_layer.task_id = None
        map_layer.regenerate = False
        map_layer.save()
        raise e

    # Mark the layer as completed
    map_layer.generation_status = GenerationStatus.COMPLETED
    map_layer.task_id = None
    map_layer.regenerate = False
    map_layer.save()
# End def generate_layer_geometries



