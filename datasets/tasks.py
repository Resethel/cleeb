# -*- coding: utf-8 -*-
"""
Tasks for the `datasets` application.
"""
from celery import shared_task
from django.apps import apps

from common.utils.tasks import TaskStatus
from datasets.services import generate_features

# ======================================================================================================================
# Tasks
# ======================================================================================================================

# noinspection PyPep8Naming
@shared_task(bind=True)
def generate_features_task(self, dataset_version_id: int) -> None:
    """Process the dataset into a layer."""

    # 1. Get the required models. This is done inside the function to avoid circular imports
    DatasetVersion = apps.get_model('datasets.DatasetVersion')

    # 2. Get the dataset version
    dataset_version = DatasetVersion.objects.get(id=dataset_version_id)
    if not dataset_version:
        raise ValueError(f"Dataset version with id '{dataset_version_id}' does not exist.")

    # 3. Set the task status to 'STARTED'
    # Use the `update` method to not trigger the `save` method nor the `pre_save` and `post_save` signals.
    # Otherwise, there would be an infinite loop of task creation.
    DatasetVersion.objects.filter(id=dataset_version_id).update(task_status=TaskStatus.STARTED,
                                                                task_id=self.request.id,
                                                                regenerate=False)

    # By default, assume the task will fail
    task_id = self.request.id
    task_status = TaskStatus.FAILURE
    try:
        generate_features(dataset_version_id)
    except Exception:
        # 4. Set the task status to 'FAILURE'
        # The task_id field is not cleared to allow tracking the task in the admin interface.
        task_id = self.request.id
        task_status = TaskStatus.FAILURE
        raise
    else:
        # 5. Set the task status to 'SUCCESS'. Clear the task_id and task_status fields.
        task_id = None
        task_status = TaskStatus.SUCCESS
    finally:
        # 6. Save the dataset version
        DatasetVersion.objects.filter(id=dataset_version_id).update(task_status=task_status,
                                                                    task_id=task_id,
                                                                    regenerate=False)
# End def generate_features_task





