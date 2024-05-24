# -*- coding: utf-8 -*-
"""
Models related to the templates for the `map_templates` application.
"""
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import Point
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext as _

from common.utils.tasks import TaskStatus
from map_templates import tasks
from map_templates.services.templates import MapTemplate as MapTemplateObject

# ======================================================================================================================
# Constants
# ======================================================================================================================

MIN_ZOOM = 5
MAX_ZOOM = 18

# ======================================================================================================================
# Map template
# ======================================================================================================================

class MapTemplate(models.Model):
    """Represents a map template.

    Used by the map creator to render a Leaflet map with the desired layers and features.
    Once defined, the map template is validated and saved in the database.
    A routine then generates the corresponding HTML file to be used in the web application.
    """

    # ID of the map template
    id = models.AutoField(primary_key=True)

    # Name of the map template
    name = models.CharField(
        unique=True,
        max_length=100,
        verbose_name=_("Name"),
        help_text=_("The name of the map template.")
    )

    # Zoom start of the map template
    zoom_start = models.SmallIntegerField(
        default=int(MIN_ZOOM + 2/3 * (MAX_ZOOM - MIN_ZOOM)),
        validators=[
            MinValueValidator(MIN_ZOOM),
            MaxValueValidator(MAX_ZOOM)
        ],
        verbose_name=_("Zoom Level at startup"),
        help_text=_("The zoom level of the map at startup.")
    )

    # Center of the map template
    # Defaults to Metz, France: lat=49.119308, lon=6.175715 (because why not?)
    center = gis_models.PointField(
        default=Point(6.175715, 49.119308, srid=4326),
        srid=4326, # Keep the SRID to 4326 for compatibility with Leaflet
        verbose_name=_("Center"),
        help_text=_("The center of the map at startup.")
    )

    # Enable layer control of the map template
    layer_control = models.BooleanField(
        default=True,
        verbose_name=_("Enable Layer Control"),
        help_text=_("Whether the layer control should be enabled.")
    )

    # Enable zoom control of the map template
    zoom_control = models.BooleanField(
        default=True,
        verbose_name=_("Enable Zoom Control"),
        help_text=_("Whether the zoom control should be enabled.")
    )

    # Tiles to load on the map
    tiles = models.ManyToManyField(
        'TileLayer',
        verbose_name=_("Tiles"),
        help_text=_("The tiles to load on the map.")
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Task specific fields
    # ------------------------------------------------------------------------------------------------------------------

    task_id = models.UUIDField(
        blank=True,
        null=True,
        default=None,
        verbose_name=_("Task ID"),
        help_text=_("ID of the task generating the map render.")
    )

    task_status = models.CharField(
        max_length=25,
        blank=True,
        null=True,
        default=None,
        choices=TaskStatus,
        verbose_name=_("Task Status"),
        help_text=_("Status of the task generating the map render.")
    )

    regenerate = models.BooleanField(
        default=False,
        verbose_name=_("Regenerate"),
        help_text=_("Whether the map render should be regenerated.")
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return self.name

    def as_template_object(self) -> MapTemplateObject:
        """Returns the map template object."""
        return MapTemplateObject.from_model(self)
    # End def as_template_object

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        verbose_name = _("Map Template")
        verbose_name_plural = _("Map Templates")
    # End class Meta
# End class MapTemplate


# ======================================================================================================================
# Signals
# ======================================================================================================================


@receiver(post_save, sender=MapTemplate)
def generate_map_render(sender, instance, created, **kwargs):
    """Generate the render of the map template."""
    if created:
        tasks.generate_maprender_from_maptemplate_task.delay(instance.id)
    elif instance.regenerate:
        # Revoke the previous task to avoid multiple renders
        if instance.task_id is not None:
            tasks.generate_maprender_from_maptemplate_task.AsyncResult(str(instance.task_id)).revoke()
        tasks.generate_maprender_from_maptemplate_task.delay(instance.id)
# End def generate_map_render