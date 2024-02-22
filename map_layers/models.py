# -*- coding: utf-8 -*-
"""
Models for the `map_layers` application.
"""
from __future__ import annotations

from django.contrib import admin
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

import map_layers.tasks as tasks
from map_layers.choices import GenerationStatus


# ======================================================================================================================
# MapLayerCustomProperty Model
# ======================================================================================================================


class MapLayerCustomProperty(models.Model):
    """A custom property for a map layer."""

    # ------------------------------------------------------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------------------------------------------------------

    map_layer = models.ForeignKey(
        'MapLayer',
        on_delete=models.CASCADE,
        help_text="Couche à laquelle la propriété est associée. Si la couche est supprimée, la propriété sera également supprimée."
    )

    name = models.CharField(
        verbose_name="Nom",
        max_length=100,
        help_text="Nom de la propriété personnalisée."
    )

    value = models.CharField(
        verbose_name="Valeur",
        max_length=100,
        help_text="Valeur de la propriété."
        "Pour utiliser une propriété du jeu de données, utilisez la syntaxe suivante: ${nom_de_la_propriété}."
        "Exemple: \"${HECTARES} ha\" convertira la valeur de la propriété \"HECTARES\" en chaîne de caractères et ajoutera \" ha\" à la fin."
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return f"\"{self.name}\": \"{self.value}\""

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        verbose_name = "Propriété personnalisée"
        verbose_name_plural = "Propriétés personnalisées"
        ordering = ['name']
    # End class Meta
# End class MapLayerCustomProperty

# ======================================================================================================================
# MapLayer Model
# ======================================================================================================================


class MapLayer(models.Model):

    # ------------------------------------------------------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------------------------------------------------------

    # ----- Identification -----
    id = models.AutoField(primary_key=True)

    name = models.CharField(
        verbose_name="Nom",
        max_length=100,
        unique=True,
        help_text="Nom de la couche"
    )

    # ----- Description -----

    short_desc = models.CharField(
        verbose_name="Description courte",
        max_length=100,
        blank=True,
        null=True,
        default=None,
        help_text="Description courte de la couche. Optionnel. Utilisé pour générer l'aide contextuelle."
    )

    description = models.TextField(
        verbose_name="Description",
        blank=True,
        null=True,
        default=None,
        help_text="Description de la couche. Optionnel."
    )

    # ----- Relations -----

    dataset = models.ForeignKey(
        'datasets.Dataset',
        verbose_name="Jeu de données",
        on_delete=models.CASCADE,
        help_text=
            "Jeu de données utilisé pour la couche. La couche sera générée à partir de ce jeu de données."
            "Si le jeu de données est supprimé, la couche sera également supprimée."
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Shapefile specific fields
    # ------------------------------------------------------------------------------------------------------------------

    shapefile = models.CharField(
        verbose_name="Fichier shapefile",
        max_length=500,
        blank=True,
        null=True,
        default=None,
        help_text="Nom du fichier shapefile à utiliser."
    )

    max_polygons_points = models.IntegerField(
        verbose_name="Nombre maximum de points par polygone",
        blank=True,
        null=True,
        default=None,
        validators=[MinValueValidator(0)],
        help_text="Nombre maximum de points par polygone. Si un polygone contient plus de points, il sera ignoré."
        "Si la valeur est nulle, il n'y a pas de limite."
    )

    max_multipolygons_polygons = models.IntegerField(
        verbose_name="Nombre maximum de polygones par multipolygone",
        blank=True,
        null=True,
        default=None,
        validators=[MinValueValidator(0)],
        help_text="Nombre maximum de polygones par multipolygone.\n"
                  "Si un multipolygone contient plus de polygones, il sera ignoré.\n"
                  "Si la valeur est nulle, il n'y a pas de limite."
    )

    max_multiolygons_points = models.IntegerField(
        verbose_name="Nombre maximum de points par multipolygone",
        blank=True,
        null=True,
        default=None,
        validators=[MinValueValidator(0)],
        help_text="Nombre maximum de points par multipolygone.\n"
                  "Si un multipolygone contient plus de points, il sera ignoré.\n"
                  "Si la valeur est nulle, il n'y a pas de limite."
    )

    customize_properties = models.BooleanField(
        verbose_name="Personnaliser les propriétés",
        default=False,
        help_text="Personnalise les proppriétés de chaque feature du jeu de données selon les règles définies dans le champ 'Règles de conversion des propriétés'."
        "Les anciennes propriétés seront supprimées."
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Task specific fields
    # ------------------------------------------------------------------------------------------------------------------

    task_id = models.CharField(
        verbose_name="ID de la tâche",
        max_length=100,
        blank=True,
        null=True,
        default=None,
        help_text="ID de la tâche asynchrone utilisée pour générer les géométries de la couche."
    )

    generation_status = models.CharField(
        verbose_name="Statut de la génération",
        max_length=10,
        choices=GenerationStatus.choices,
        default=GenerationStatus.PENDING,
        help_text="Statut de la génération des géométries de la couche."
    )

    regenerate = models.BooleanField(
        verbose_name="Regénérer",
        default=False,
        help_text="Relance la génération des géométries de la couche."
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Non-Persistent Fields
    # ------------------------------------------------------------------------------------------------------------------

    @admin.display(description="Formes Générées")
    def has_shapes(self):
        """Return True if the map layer has shapes."""
        return self.shapes.exists()
    # End def has_shapes

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return self.name
    # End def __str__

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        verbose_name = "Couche"
        verbose_name_plural = "Couches"
        ordering = ['name']
    # End class Meta
# End class MapLayer

@receiver(post_save, sender=MapLayer)
def generate_map_layer_geometries(sender, instance, created, **kwargs):
    """Generate the geometries for the map layer."""
    print(f"{instance}: {instance.generation_status}, {instance.task_id}")
    if instance.generation_status in [None, GenerationStatus.PENDING]:
        tasks.generate_layer_geometries_task.delay(instance.id)

    # Edge case where something went wrong and a task was killed midway
    elif instance.generation_status == GenerationStatus.RUNNING:
        if instance.task_id is None:
            tasks.generate_layer_geometries_task.delay(instance.id)

    # In the case where the status is either COMPLETED or FAILED,
    # only submit a task if the user has requested to regenerate the geometries
    elif instance.regenerate:
        tasks.generate_layer_geometries_task.delay(instance.id)
        instance.regenerate = False
        instance.save()

# End def generate_map_layer_geometries