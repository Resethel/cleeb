# -*- coding: utf-8 -*-
"""
Models for the `map_layers` application.
"""
from __future__ import annotations

from django.contrib.contenttypes.fields import GenericRelation
from django.core.validators import MinValueValidator
from django.db import models

from datasets.models import SHAPEFILE

# ======================================================================================================================
# MapLayer Model
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

class MapLayer(models.Model):

    # ------------------------------------------------------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------------------------------------------------------

    id = models.AutoField(primary_key=True)

    name = models.CharField(
        verbose_name="Nom",
        max_length=100,
        unique=True,
        help_text="Nom de la couche"
    )

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

    shapes = GenericRelation(
        'shapes.Shape',
        related_name='layer'
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return self.name

    def get_config_dict(self):
        """Return a dictionary containing the map layer's data.
        Used when generating the geojson file of the map layers.
        """
        # Create the config dictionary
        config_dict = {
            'name': self.name,
            'dataset': self.dataset.name,
            'dataset_format': self.dataset.format
        }

        if self.dataset.format == SHAPEFILE:
            config_dict.extend({
                'shapefile': self.shapefile,
                'encoding': self.dataset.encoding,
                'max_polygons_points': self.max_polygons_points,
                'max_multipolygons_polygons': self.max_multipolygons_polygons,
                'max_multiolygons_points': self.max_multiolygons_points
            })

        config_dict['customize_properties'] = True
        if self.customize_properties is True:
            config_dict['custom_properties'] = {key: value for key, value in self.custom_properties.values_list('name', 'value')}

        return config_dict
    # End def get_config_dict

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        verbose_name = "Couche"
        verbose_name_plural = "Couches"
        ordering = ['name']
    # End class Meta
# End class MapLayer