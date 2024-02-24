# -*- coding: utf-8 -*-
"""
Command to kill all running tasks from the `map_templates` application.
"""
from django.core.management import BaseCommand

from map_templates.choices import GenerationStatus
from map_templates.models import MapTemplate

from cleeb.celery import app as celery_app

class Command(BaseCommand):


    help = "Kill all running tasks from the `map_templates` application."

    def handle(self, **kwargs):
        revoke = celery_app.control.revoke
        inspect = celery_app.control.inspect
        for template in MapTemplate.objects.filter(generation_status=GenerationStatus.RUNNING):
            if template.task_id is None:
                continue
            try:
                for queues in (inspect.active(), inspect.reserved(), inspect.scheduled()):
                    for task_list in queues.values():
                        for task in task_list:
                            task_id = task.get("request", {}).get("id", None) or task.get("id", None)
                            if task_id == template.task_id:
                                self.stdout.write(self.style.WARNING(f"Revoking task {task_id} for template {template.name}"))
                                revoke(task_id)
                                break
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to kill task {template.task_id} for template {template.name}"))
                self.stdout.write(self.style.ERROR(str(e)))
                continue
            template.generation_status = GenerationStatus.FAILED
            template.regenerate = False
            template.save()
    # End def handle
# End class Command
