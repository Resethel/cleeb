# -*- coding: utf-8 -*-
"""
Tasks for the `map_templates` application.
"""
from __future__ import annotations

from celery import shared_task
from django.apps import apps

from common.utils.tasks import TaskStatus
from map_templates.services.processor import TemplateProcessor


# noinspection PyPep8Naming
@shared_task(bind=True)
def generate_maprender_from_maptemplate_task(self, map_template_id: int):
    """Generate geometries for a map layer."""
    # Get the models.
    # Uses apps.get_model to avoid circular imports.
    MapTemplate = apps.get_model("map_templates", "MapTemplate")

    try:
        map_template = MapTemplate.objects.get(id=map_template_id)
    except MapTemplate.DoesNotExist:
        raise ValueError(f"MapTemplate with ID '{MapTemplate}' does not exist.")

    # Update the status of the template and its task ID
    MapTemplate.objects.filter(id=map_template_id).update(task_status=TaskStatus.STARTED,
                                                          task_id=self.request.id,
                                                          regenerate=False)

    request_id = self.request.id
    task_status = TaskStatus.STARTED
    try:
        # 1. Create the processor
        try:
            processor = TemplateProcessor(map_template)
        except Exception as e:
            # Print the whole trace back
            import traceback
            print(e, traceback.format_exc())
            raise e
        print("Processor created")
        # 2. Generate the template
        print("Generating the template")
        processor.build()
        print("Template generated")
        print("Saving the processor")
        processor.save()
        print("Processor saved")

    except Exception:
        # Mark the task as failed and keep the task ID for debugging
        task_status = TaskStatus.FAILURE
        raise
    else:
        # Remove the task ID
        task_status = TaskStatus.SUCCESS
        request_id = None
    finally:
        MapTemplate.objects.filter(id=map_template_id).update(task_status=task_status,
                                                              task_id=request_id,
                                                              regenerate=False)
# End def generate_map_render_from_map_template_task



