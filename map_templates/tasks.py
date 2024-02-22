# -*- coding: utf-8 -*-
"""
Tasks for the `map_templates` application.
"""
from __future__ import annotations

import celery
from django.apps import apps

from map_data.core.processor.template import TemplateProcessor
from map_layers.choices import GenerationStatus


@celery.shared_task(bind=True, throws=(ValueError, RuntimeError))
def generate_map_render_from_map_template_task(self, map_template_id: int):
    """Generate geometries for a map layer."""
    # Get the models.
    # Uses apps.get_model to avoid circular imports.
    map_template_model = apps.get_model("map_templates", "MapTemplate")
    map_layer_model = apps.get_model("map_layers", "MapLayer")

    try:
        map_template = map_template_model.objects.get(id=map_template_id)
    except map_layer_model.DoesNotExist:
        raise ValueError(f"MapTemplate with ID '{map_template_model}' does not exist.")

    # Update the status of the template and its task ID
    map_template.generation_status = GenerationStatus.RUNNING
    map_template.task_id = self.request.id
    map_template.save()

    try:
        # 1. Verify that all the layers of the map templates have been generated
        print("Verifying that all the layers of the map templates have been generated")
        for layer in map_template.layers.all():
            if layer.map_layer.generation_status != GenerationStatus.COMPLETED:
                raise RuntimeError(
                    f"Layer '{layer.name}' of the template '{map_template.name}' has not been generated.")

        print("All the layers of the map templates have been generated")
        print("Verifying that all the feature groups of the map templates have been generated")
        # 2. Perform the same verification for the feature groups
        for feature_group in map_template.feature_groups.all():
            for feature_group_layer in feature_group.layers.all():
                if feature_group_layer.map_layer.generation_status != GenerationStatus.COMPLETED:
                    raise RuntimeError(
                        f"Layer '{feature_group_layer.name}' of the feature group '{feature_group.name}' of the template '{map_template.name}' has not been generated.")
        print("All the feature groups of the map templates have been generated")
        # 3. Create the processor
        print("Creating the processor")
        try:
            processor = TemplateProcessor(map_template)
        except Exception as e:
            # Print the whole trace back
            import traceback
            print(e, traceback.format_exc())
            raise e
        print("Processor created")
        # 4. Generate the template
        print("Generating the template")
        processor.build()
        print("Template generated")
        print("Saving the processor")
        processor.save()
        print("Processor saved")

    except Exception as e:
        map_template.generation_status = GenerationStatus.FAILED
        map_template.task_id = None
        map_template.regenerate = False
        map_template.save()
        raise e

    # Mark the layer as completed
    map_template.generation_status = GenerationStatus.COMPLETED
    map_template.task_id = None
    map_template.regenerate = False
    map_template.save()
# End def generate_map_render_from_map_template_task



